const angular = require('angular');
const mongodb = require('mongodb');
import QueryServerService from '../../services/query-server.service.js';
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import MongoDbService from '../../services/mongodb.service.js';
import EvaluationsService from '../../services/evaluations.service.js';


class ProgressBar {

    total = 0;
    current = 0;
    #state = 'stopped';

    stop() { this.#state = 'stopped'; }
    run() { this.#state = 'running'; }
    complete() { this.#state = 'complete'; }

    percentage() {
        if (this.total === 0) { return 0; }
        return Math.round(this.current / this.total * 100);
    }

    style() { return { width: `${this.percentage()}%` }; }

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


class Controller {

    #scope;
    #queryServer;
    #modal;
    #options;
    #mongoDb;
    #evaluations;

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

    static $inject = ['$scope', 'queryServer', 'modal', 'options', 'mongoDb', 'evaluations'];

    /**
     * @param {angular.IScope} $scope 
     * @param {QueryServerService} queryServer
     * @param {ModalService} modal
     * @param {OptionsService} options
     * @param {MongoDbService} mongoDb
     * @param {EvaluationsService} evaluations
     */
    constructor($scope, queryServer, modal, options, mongoDb, evaluations) {
        this.#scope = $scope;
        this.#queryServer = queryServer;
        this.#modal = modal;
        this.#options = options;
        this.#mongoDb = mongoDb;
        this.#evaluations = evaluations;

        $scope.options = options;
        $scope.search = this.#search;
        $scope.sort = this.#sort;

        $scope.progressBar = this.#progressBar;
        $scope.optionsLoaded = () => options.isLoaded;
        $scope.evaluations = this.#evaluations;

        $scope.retry = () => this.#retry();
        $scope.reevaluatePending = () => this.#reevaluatePending();

        this.#preInit();
    }

    $onDestroy() { this.#quit = true; }

    /**
     * @deprecated
     */
    async #evaluateAll() {
        this.#modal.showLoading('EVALUATING...');
        this.#evaluations.isLoaded = false;
        for (let i of await this.#queryServer.evaluateAll()) {
            this.#evaluations.set(i);
        }
        this.#evaluations.isLoaded = true;
        this.#modal.hideLoading();
        this.#scope.$apply();
    }

    async #evaluate() {
        this.#progressBar.run();
        this.#progressBar.current = 0;
        this.#progressBar.total = this.#options.modelCount();
        this.#scope.$apply();
        for (let model of this.#options.models()) {
            if (this.#quit) { return; }
            if (!this.#evaluations.has(model)) {
                try {
                    let result = await this.#queryServer.evaluate(model);
                    await this.#mongoDb.insertOne('evaluations', result);
                    this.#evaluations.set(result);
                    this.#progressBar.current++;
                    this.#scope.$apply();
                }
                catch (e) {
                    console.error(e);
                    if (e.status === -1 || e instanceof mongodb.MongoServerSelectionError) {
                        this.#progressBar.stop();
                        this.#modal.showError(e, 'ERROR: Connection', 'Disconnected from MongoDB or server');
                        this.#scope.$apply();
                        return;
                    }
                    else if (e.status === 500) {
                        // Ignore 500 errors
                    }
                    else {
                        this.#progressBar.stop();
                        this.#modal.showError(e, 'ERROR: Deep Learning', 'Error while evaluating');
                        this.#scope.$apply();
                        return;
                    }
                }
            }
            else {
                this.#progressBar.current++;
            }
        }
        this.#progressBar.complete();
        this.#scope.$apply();
    }

    async #reevaluatePending() {
        this.#progressBar.run();
        this.#progressBar.current = 0;
        this.#progressBar.total = this.#options.modelCount();
        for (let eval_ of this.#evaluations.toArray()) {
            if (this.#quit) { return; }
            if (eval_.status === 'TrainingStatus.PENDING') {
                try {
                    let result = await this.#queryServer.evaluate(eval_.model);
                    await this.#mongoDb.findOneAndReplace('evaluations', { model: eval_.model }, result);
                    this.#evaluations.set(result);
                    this.#progressBar.current++;
                    this.#scope.$apply();
                }
                catch (e) {
                    console.error(e);
                    if (e.status === -1 || e instanceof mongodb.MongoServerSelectionError) {
                        this.#progressBar.stop();
                        this.#modal.showError(e, 'ERROR: Connection', 'Disconnected from MongoDB or server');
                        this.#scope.$apply();
                        return;
                    }
                    else if (e.status === 500) {
                        // Ignore 500 errors
                    }
                    else {
                        this.#progressBar.stop();
                        this.#modal.showError(e, 'ERROR: Deep Learning', 'Error while evaluating');
                        this.#scope.$apply();
                        return;
                    }
                }
            }
            else {
                this.#progressBar.current++;
            }
        }
        this.#progressBar.complete();
        this.#scope.$apply();
    }

    async #loadOptions() {
        await this.#options.load();
    }

    async #getEvaluated() {
        if (!this.#evaluations.isLoaded) {
            let x = await this.#mongoDb.getAll('evaluations');
            for (let i of x) {
                this.#evaluations.set(i);
            }
            this.#evaluations.isLoaded = true;
        }
    }

    async #preInit() {
        try {
            this.#modal.showLoading('RETRIEVING...');
            await Promise.all([this.#getEvaluated(), this.#loadOptions()]);
            this.#modal.hideLoading();
            this.#scope.$apply();
            this.#evaluate();
        }
        catch (e) {
            console.error(e);
            this.#modal.hideLoading();
            $('#staticBackdrop').modal();
        }
    }

    #retry() {
        $('#staticBackdrop').modal('hide');
        this.#preInit();
    }

}


export default Controller;
