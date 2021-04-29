const angular = require('angular');
import SettingsService from './settings.service.js';


/**
 * Model settings
 * @typedef {Object} ModelDescription
 * @property {string} phase
 * @property {string} architecture
 * @property {string} dataset
 * @property {string} loss
 * @property {string} optimizer
 * @property {string} metrics
 * @property {number} epochs
 * @property {number} patience
 * @property {number} split
 */


/**
 * Prediction results
 * @typedef {Object} PredictReturnObject
 * @property {Object} prediction
 * @property {Array.<string>} prediction.x
 * @property {Object} prediction.y
 * @property {Array.<string> | Array.<number>} prediction.y.predicted
 * @property {Array.<string> | Array.<number>} prediction.y.truth
 * @property {Array.<string>} keyGuide
 */


/**
 * A data object returned by the python server
 * @typedef {Object} RunReturnObject
 * @property {string} path
 * @property {number} rating
 * @property {number} cluster
 */


/**
 * Compile options for the deep learning model
 * @typedef {Object} OptionsReturnObject
 * @property {Array.<string>} architectures
 * @property {Array.<string>} datasets
 * @property {Array.<string>} losses
 * @property {Array.<string>} optimizers
 * @property {Array.<string>} clusters
 */


/**
 * Which clustering algorithm to use on which directory
 * @typedef {Object} ClusterParameters
 * @property {string} cluster
 * @property {string} directory
 */


/**
 * Evaluation and status of a deep learning model
 * @typedef {Object} EvaluationReturnObject
 * @property {ModelDescription} model
 * @property {string} status
 * @property {?Object} training
 * @property {?Object} validation
 * @property {?Object} test
 */


class ModelDescription {

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

    toString() {
        return `${this.architecture}-${this.dataset}-${this.loss}-${this.optimizer}-${this.metrics}-${this.epochs}-${this.patience}-${this.split}`;
    }

    static from(model) {
        return Object.assign(new ModelDescription(), model);
    }

}


class Metrics {

    /** @type {number} */
    accuracy;

    /** @type {number} */
    loss;

    static from(metrics) {
        return Object.assign(new Metrics(), metrics);
    }

}


class Evaluation {

    /** @type {ModelDescription} */
    model;

    /** @type {string} */
    status;

    /** @type {Metrics} */
    training;

    /** @type {Metrics} */
    validation;

    /** @type {Metrics} */
    test;

    /** @type {EvaluationReturnObject} */
    static from(evaluation) {
        /** @type {Evaluation} */
        let instance = Object.assign(new Evaluation(), evaluation);
        instance.model = ModelDescription.from(instance.model);
        instance.training = Metrics.from(instance.training);
        instance.validation = Metrics.from(instance.validation);
        instance.test = Metrics.from(instance.test);
        return instance;
    }

}


/**
 * An interface to the python server
 */
class QueryServerService {

    $http;
    settings;

    static $inject = ['$http', 'settings'];

    /**
     * @param {angular.IHttpService} $http 
     * @param {SettingsService} settings 
     */
    constructor($http, settings) {
        this.$http = $http;
        this.settings = settings;
    }

    get #serverUrl() { return this.settings.server.url; }

    /**
     * Rates and clusters images
     * @param {string} dir Filepath of the directory of images to rate and cluster
     * @returns {Promise.<Array.<Array.<RunReturnObject>>>}
     */
    async run(dir) {
        return (await this.$http.post(`${this.#serverUrl}/run`, { url: dir })).data;
    }

    /**
     * Fetches compile options for the model
     * @returns {Promise.<OptionsReturnObject>}
     */
    async options() {
        return (await this.$http.get(`${this.#serverUrl}/options`)).data;
    }

    /**
     * Classifies or rates the model's training, validation, or test set
     * @param {ModelDescription} model Data object that describes that model to use
     * @returns {Promise.<PredictReturnObject>}
     */
    async predict(model) {
        return (await this.$http.post(`${this.#serverUrl}/predict`, model)).data;
    }

    /**
     * Clusters the images in a directory
     * @param {string} algorithm 
     * @param {string} directory 
     * @returns {Promise.<Array.<Array.<string>>>}
     */
    async cluster(algorithm, directory) {
        return (await this.$http.post(`${this.#serverUrl}/cluster`, {
            cluster: algorithm,
            directory: directory,
        })).data;
    }

    /**
     * @returns {Promise.<Array.<Evaluation>>}
     */
    async evaluateAll() {
        return (await this.$http.get(`${this.#serverUrl}/evaluate/all/0`)).data.
            map(i => Evaluation.from(i));
    }

    /**
     * @param {ModelDescription} model
     * @returns {Promise.<Evaluation>}
     */
    async evaluate(model) {
        return Evaluation.from((await this.$http.post(`${this.#serverUrl}/evaluate`, model)).data);
    }

}


export default QueryServerService;
export { ModelDescription, Metrics, Evaluation, QueryServerService };
