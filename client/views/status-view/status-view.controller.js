const angular = require('angular');
const mongodb = require('mongodb');
const _ = require('lodash');
import QueryServerService from '../../services/query-server.service.js';
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import EvaluationsService from '../../services/evaluations.service.js';


class ProgressBar {

    total = 0;
    complete = 0;
    pending = 0;
    bad = 0;
    resource = 0;
    #state = 'stopped';

    stop() { this.#state = 'stopped'; }
    run() { this.#state = 'running'; }
    end() { this.#state = 'complete'; }

    reset(total) {
        this.total = total;
        this.complete = 0;
        this.pending = 0;
        this.bad = 0;
        this.resource = 0;
    }

    get current() {
        return this.complete +
            this.pending +
            this.bad +
            this.resource;
    }

    #percentage(value) {
        if (this.total === 0) { return 0; }
        return Math.round(value / this.total * 100);
    }

    #cssWidth(value) { return { width: `${this.#percentage(value)}%` }; }

    totalWidth() { return this.#cssWidth(this.current); }
    completeWidth() { return this.#cssWidth(this.complete); }
    pendingWidth() { return this.#cssWidth(this.pending); }
    resourceWidth() { return this.#cssWidth(this.resource); }
    badWidth() { return this.#cssWidth(this.bad); }

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


class QuitError extends Error { }


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

    static $inject = ['$scope', '$q', 'queryServer', 'modal', 'options', 'evaluations'];
    $scope;
    $q;
    queryServer;
    modal;
    options;
    evaluations;

    /**
     * @param {angular.IScope} $scope 
     * @param {angular.IQService} $q 
     * @param {QueryServerService} queryServer
     * @param {ModalService} modal
     * @param {OptionsService} options
     * @param {EvaluationsService} evaluations
     */
    constructor($scope, $q, queryServer, modal, options, evaluations) {
        this.$scope = $scope;
        this.$q = $q;
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

    /**
     * 
     * @param {string} status 
     */
    updateProgressBar(status) {
        switch (status) {
            case 'TrainingStatus.COMPLETE':
                this.#progressBar.complete++;
                break;
            case 'TrainingStatus.PENDING':
            case 'TrainingStatus.TRAINING':
                this.#progressBar.pending++;
                break;
            case 'TrainingStatus.RESOURCE':
            case 'TrainingStatus.RESOURCE2':
                this.#progressBar.resource++;
                break;
            default:
                this.#progressBar.bad++;
        }
    }

    #evaluate() {
        this.#progressBar.run();
        this.#progressBar.reset(this.options.modelCount());
        let promiseChain = this.$q.resolve();
        let notEvaluated = Array.from(this.options.models()).
            filter(
                model => {
                    if (this.evaluations.has(model)) {
                        this.updateProgressBar(this.evaluations.get(model).status);
                        return false;
                    }
                    return true;
                }
            );
        for (let chunk of _.chunk(notEvaluated, 5)) {
            promiseChain = promiseChain.then(
                () => {
                    if (this.#quit) {
                        throw new QuitError();
                    }
                }
            ).then(
                () => Promise.allSettled(chunk.map(
                    model => this.queryServer.evaluate(model).then(
                        evaluation => {
                            this.evaluations.add(evaluation);
                            this.updateProgressBar(evaluation.status);
                        },
                        e => {
                            if (e.status !== 500) { throw e; } // Ignore 500 errors
                        },
                    )
                ))
            ).then(
                results => {
                    for (let i of results) {
                        if (i.status === 'rejected') { throw i.reason; }
                    }
                }
            );
        }
        return promiseChain.then(() => {
            this.#progressBar.end();
        }).catch(e => {
            this.#progressBar.stop();
            if (e instanceof QuitError) {
                this.#progressBar.end();
                return;
            }
            console.error(e);
            if (e.status === -1 || e instanceof mongodb.MongoServerSelectionError) {
                this.#progressBar.stop();
                this.modal.showError(e, 'ERROR: Connection', 'Disconnected from MongoDB or server');
            }
            else {
                this.#progressBar.stop();
                this.modal.showError(e, 'ERROR: Deep Learning', 'Error while evaluating');
            }
        });
    }

    #reevaluatePending() {
        this.#progressBar.run();
        this.#progressBar.reset(this.options.modelCount());
        let promiseChain = this.$q.resolve();
        let pending = Array.from(this.evaluations.toArray()).
            filter(
                evaluation => {
                    if (evaluation.status !== 'TrainingStatus.PENDING') {
                        this.updateProgressBar(evaluation.status);
                        return false;
                    }
                    return true;
                }
            );
        for (let chunk of _.chunk(pending, 5)) {
            promiseChain = promiseChain.then(
                () => {
                    if (this.#quit) {
                        throw new QuitError();
                    }
                }
            ).then(
                () => Promise.allSettled(chunk.map(
                    evaluation => this.queryServer.evaluate(evaluation.model).then(
                        reevaluation => {
                            this.evaluations.update(reevaluation);
                            this.updateProgressBar(reevaluation.status);
                        },
                        e => {
                            if (e.status !== 500) { throw e; } // Ignore 500 errors
                        },
                    )
                ))
            ).then(
                results => {
                    for (let i of results) {
                        if (i.status === 'rejected') { throw i.reason; }
                    }
                }
            );
        }
        return promiseChain.then(() => {
            this.#progressBar.end();
        }).catch(e => {
            this.#progressBar.stop();
            if (e instanceof QuitError) {
                this.#progressBar.end();
                return;
            }
            console.error(e);
            if (e.status === -1 || e instanceof mongodb.MongoServerSelectionError) {
                this.#progressBar.stop();
                this.modal.showError(e, 'ERROR: Connection', 'Disconnected from MongoDB or server');
            }
            else {
                this.#progressBar.stop();
                this.modal.showError(e, 'ERROR: Deep Learning', 'Error while evaluating');
            }
        });
    }

    #removeMongoDbDuplicates() {
        this.modal.showLoading('DELETING...');
        return this.evaluations.removeMongoDbDuplicates().then(
            () => this.modal.hideLoading(),
            e => {
                console.error(e);
                this.modal.hideLoading();
                this.modal.showError(e, 'ERROR: MongoDB', 'Error while deleting duplicates');
            }
        );
    }

    #preInit() {
        this.modal.showLoading('RETRIEVING...');
        return this.$q.all([
            this.options.load(),
            this.evaluations.fetchStatuses(),
            this.evaluations.fromMongoDb(),
        ]).then(() => {
            this.modal.hideLoading();
            this.#evaluate();
        }, e => {
            console.error(e);
            this.modal.hideLoading();
            $('#staticBackdrop').modal();
        });
    }

    #retry() {
        $('#staticBackdrop').modal('hide');
        return this.#preInit();
    }

}


export default StatusViewController;
