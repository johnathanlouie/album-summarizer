const angular = require('angular');
const mongodb = require('mongodb');
import QueryServerService from '../../services/query-server.service.js';
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import EvaluationsService from '../../services/evaluations.service.js';


class ProgressBar {

    total = 0;
    current = 0;
    finished = 0;
    pending = 0;
    bad = 0;
    error = 0;
    #state = 'stopped';

    stop() { this.#state = 'stopped'; }
    run() { this.#state = 'running'; }
    complete() { this.#state = 'complete'; }

    #percentage(value) {
        if (this.total === 0) { return 0; }
        return Math.round(value / this.total * 100);
    }

    #cssWidth(value) { return { width: `${this.#percentage(value)}%` }; }

    totalWidth() { return this.#cssWidth(this.current); }
    completeWidth() { return this.#cssWidth(this.finished); }
    pendingWidth() { return this.#cssWidth(this.pending); }
    badWidth() { return this.#cssWidth(this.bad); }
    errorWidth() { return this.#cssWidth(this.error); }

    animate() {
        if (this.#state === 'running') { return ['progress-bar-striped', 'progress-bar-animated'] };
        return [];
    }

    classes() {
        switch (this.#state) {
            case 'running':
                return ['progress-bar-striped', 'progress-bar-animated'];
            case 'complete':
                return ['bg-success'];
            case 'stopped':
                return ['bg-danger'];
        }
        throw new Error();
    }

}


class StatusViewController {

    #quit = false;
    #search = {
        model: {
            architecture: '',
            dataset: '',
            loss: '',
            optimizer: '',
        },
        status: 'TrainingStatus.COMPLETE',
    };
    #sort = {
        phase: 'test.accuracy',
        reverse: true,
    };
    #progressBar = new ProgressBar();

    static $inject = ['$scope', 'queryServer', 'modal', 'options', 'evaluations'];
    $scope;
    queryServer;
    modal;
    options;
    evaluations;

    /**
     * @param {angular.IScope} $scope 
     * @param {QueryServerService} queryServer
     * @param {ModalService} modal
     * @param {OptionsService} options
     * @param {EvaluationsService} evaluations
     */
    constructor($scope, queryServer, modal, options, evaluations) {
        this.$scope = $scope;
        this.queryServer = queryServer;
        this.modal = modal;
        this.options = options;
        this.evaluations = evaluations;

        $scope.options = options;
        $scope.search = this.#search;
        $scope.sort = this.#sort;

        $scope.progressBar = this.#progressBar;
        $scope.optionsLoaded = () => options.isLoaded;
        $scope.evaluations = this.evaluations;
        $scope.removeMongoDbDuplicates = () => this.#removeMongoDbDuplicates();
        $scope.reevaluatePending = () => this.#reevaluatePending();

        $scope.retry = () => this.#retry();

        this.#preInit();
    }

    $onDestroy() { this.#quit = true; }

    async #evaluate() {
        this.#progressBar.run();
        this.#progressBar.current = 0;
        this.#progressBar.finished = 0;
        this.#progressBar.pending = 0;
        this.#progressBar.bad = 0;
        this.#progressBar.error = 0;
        this.#progressBar.total = this.options.modelCount();
        this.$scope.$apply();
        for (let model of this.options.models()) {
            if (this.#quit) { return; }
            if (!this.evaluations.has(model)) {
                try {
                    let evaluation = await this.queryServer.evaluate(model);
                    this.evaluations.add(evaluation);
                    switch (evaluation.status) {
                        case 'TrainingStatus.COMPLETE':
                            this.#progressBar.finished++;
                            break;
                        case 'TrainingStatus.PENDING':
                        case 'TrainingStatus.TRAINING':
                            this.#progressBar.pending++;
                            break;
                        default:
                            this.#progressBar.bad++;
                    }
                    this.#progressBar.current++;
                    this.$scope.$apply();
                }
                catch (e) {
                    console.error(e);
                    if (e.status === -1 || e instanceof mongodb.MongoServerSelectionError) {
                        this.#progressBar.stop();
                        this.modal.showError(e, 'ERROR: Connection', 'Disconnected from MongoDB or server');
                        this.$scope.$apply();
                        return;
                    }
                    else if (e.status === 500) {
                        this.#progressBar.error++;
                    }
                    else {
                        this.#progressBar.stop();
                        this.modal.showError(e, 'ERROR: Deep Learning', 'Error while evaluating');
                        this.$scope.$apply();
                        return;
                    }
                }
            }
            else {
                this.#progressBar.current++;
                switch (this.evaluations.get(model).status) {
                    case 'TrainingStatus.COMPLETE':
                        this.#progressBar.finished++;
                        break;
                    case 'TrainingStatus.PENDING':
                    case 'TrainingStatus.TRAINING':
                        this.#progressBar.pending++;
                        break;
                    default:
                        this.#progressBar.bad++;
                }
            }
        }
        this.#progressBar.complete();
        this.$scope.$apply();
    }

    async #reevaluatePending() {
        this.#progressBar.run();
        this.#progressBar.current = 0;
        this.#progressBar.total = this.options.modelCount();
        for (let evaluation of this.evaluations.toArray()) {
            if (this.#quit) { return; }
            if (evaluation.status === 'TrainingStatus.PENDING') {
                try {
                    await this.evaluations.update(await this.queryServer.evaluate(evaluation.model));
                    this.#progressBar.current++;
                    this.$scope.$apply();
                }
                catch (e) {
                    console.error(e);
                    if (e.status === -1 || e instanceof mongodb.MongoServerSelectionError) {
                        this.#progressBar.stop();
                        this.modal.showError(e, 'ERROR: Connection', 'Disconnected from MongoDB or server');
                        this.$scope.$apply();
                        return;
                    }
                    else if (e.status === 500) {
                        // Ignore 500 errors
                    }
                    else {
                        this.#progressBar.stop();
                        this.modal.showError(e, 'ERROR: Deep Learning', 'Error while evaluating');
                        this.$scope.$apply();
                        return;
                    }
                }
            }
            else {
                this.#progressBar.current++;
            }
        }
        this.#progressBar.complete();
        this.$scope.$apply();
    }

    async #removeMongoDbDuplicates() {
        try {
            this.modal.showLoading('DELETING...');
            await this.evaluations.removeMongoDbDuplicates();
            this.modal.hideLoading();
        }
        catch (e) {
            console.error(e);
            this.modal.hideLoading();
            this.modal.showError(e, 'ERROR: MongoDB', 'Error while deleting duplicates');
        }
        this.$scope.$apply();
    }

    async #preInit() {
        try {
            this.modal.showLoading('RETRIEVING...');
            await Promise.all([
                this.options.load(),
                this.evaluations.fetchStatuses(),
                this.evaluations.fromMongoDb(),
            ])
            this.modal.hideLoading();
            this.$scope.$apply();
            this.#evaluate();
        }
        catch (e) {
            console.error(e);
            this.modal.hideLoading();
            $('#staticBackdrop').modal();
        }
    }

    #retry() {
        $('#staticBackdrop').modal('hide');
        this.#preInit();
    }

}


export default StatusViewController;
