const angular = require('angular');
const _ = require('lodash');
const mongodb = require('mongodb');
import QueryServerService from '../../services/query-server.service.js';
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import MongoDbService from '../../services/mongodb.service.js';


class Model {

    /** @type {string} */
    architecture;

    /** @type {string} */
    dataset;

    /** @type {string} */
    loss;

    /** @type {string} */
    optimizer;

    /** @type {string} */
    metrics;

    /** @type {number} */
    epochs;

    /** @type {number} */
    patience;

    /** @type {number} */
    split;

    /**
     * 
     * @param {Model} model 
     */
    static toString(model) {
        return `${model.architecture}-${model.dataset}-${model.loss}-${model.optimizer}-${model.metrics}-${model.epochs}-${model.patience}-${model.split}`;
    }

}


class Metrics {

    /** @type {number} */
    accuracy;

    /** @type {number} */
    loss;

}


class Evaluation {

    /** @type {Model} */
    model;

    /** @type {string} */
    status;

    /** @type {Metrics} */
    training;

    /** @type {Metrics} */
    validation;

    /** @type {Metrics} */
    test;

}


class Evaluations {

    /** @type {Map.<Model, Evaluation>} */
    #container = new Map();

    isLoaded = false;

    /**
     * 
     * @param {Evaluation} evaluation 
     */
    set(evaluation) {
        this.#container.set(Model.toString(evaluation.model), evaluation);
    }

    /**
     * 
     * @param {Model} model 
     * @returns {boolean}
     */
    has(model) {
        return this.#container.has(Model.toString(model));
    }

    statuses() {
        return _.uniq(this.toArray().map(e => e.status));
    }

    toArray() {
        return Array.from(this.#container.values());
    }

}


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

    static #evaluations = new Evaluations();
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

    static $inject = ['$scope', 'queryServer', 'modal', 'options', 'mongoDb'];

    /**
     * @param {angular.IScope} $scope 
     * @param {QueryServerService} queryServer
     * @param {ModalService} modal
     * @param {OptionsService} options
     * @param {MongoDbService} mongoDb
     */
    constructor($scope, queryServer, modal, options, mongoDb) {
        this.#scope = $scope;
        this.#queryServer = queryServer;
        this.#modal = modal;
        this.#options = options;
        this.#mongoDb = mongoDb;

        $scope.options = options;
        $scope.search = this.#search;
        $scope.sort = this.#sort;

        $scope.progressBar = this.#progressBar;
        $scope.optionsLoaded = () => options.isLoaded;
        $scope.evaluations = Controller.#evaluations;

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
        Controller.#evaluations.isLoaded = false;
        for (let i of await this.#queryServer.evaluateAll()) {
            Controller.#evaluations.set(i);
        }
        Controller.#evaluations.isLoaded = true;
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
            if (!Controller.#evaluations.has(model)) {
                try {
                    let result = await this.#queryServer.evaluate(model);
                    await this.#mongoDb.insertOne('evaluations', result);
                    Controller.#evaluations.set(result);
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
        for (let eval_ of Controller.#evaluations.toArray()) {
            if (this.#quit) { return; }
            if (eval_.status === 'TrainingStatus.PENDING') {
                try {
                    let result = await this.#queryServer.evaluate(eval_.model);
                    await this.#mongoDb.findOneAndReplace('evaluations', { model: eval_.model }, result);
                    Controller.#evaluations.set(result);
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
        if (!Controller.#evaluations.isLoaded) {
            let x = await this.#mongoDb.getAll('evaluations');
            for (let i of x) {
                Controller.#evaluations.set(i);
            }
            Controller.#evaluations.isLoaded = true;
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
