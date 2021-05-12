const angular = require('angular');
import SettingsService from './settings.service.js';
import { ModelDescription, Evaluation } from '../lib/evaluation.js';


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
     * @returns {angular.IPromise.<Array.<Array.<RunReturnObject>>>}
     */
    run(dir) {
        return this.$http.post(
            `${this.#serverUrl}/run`,
            Object.assign({ url: dir }, this.settings.organizer),
        ).then(httpReturnValue => httpReturnValue.data);
    }

    /**
     * Fetches compile options for the model
     * @returns {angular.IPromise.<OptionsReturnObject>}
     */
    options() {
        return this.$http.get(`${this.#serverUrl}/options`).then(httpReturnValue => httpReturnValue.data);
    }

    /**
     * Classifies or rates the model's training, validation, or test set
     * @param {ModelDescription} model Data object that describes that model to use
     * @returns {angular.IPromise.<PredictReturnObject>}
     */
    predict(model) {
        return this.$http.post(`${this.#serverUrl}/predict`, model).then(httpReturnValue => httpReturnValue.data);
    }

    /**
     * Clusters the images in a directory
     * @param {string} algorithm 
     * @param {string} directory 
     * @returns {angular.IPromise.<Array.<Array.<string>>>}
     */
    cluster(algorithm, directory) {
        return this.$http.post(`${this.#serverUrl}/cluster`, {
            cluster: algorithm,
            directory: directory,
        }).then(httpReturnValue => httpReturnValue.data);
    }

    /**
     * @returns {angular.IPromise.<Array.<Evaluation>>}
     */
    evaluateAll() {
        return this.$http.get(`${this.#serverUrl}/evaluate/all/0`).then(httpReturnValue => httpReturnValue.data.map(i => Evaluation.from(i)));
    }

    /**
     * @param {ModelDescription} model
     * @returns {angular.IPromise.<Evaluation>}
     */
    evaluate(model) {
        return this.$http.post(`${this.#serverUrl}/evaluate`, model).then(httpReturnValue => Evaluation.from(httpReturnValue.data));
    }

    /** @returns {angular.IPromise.<Array.<string>>} */
    trainingStatuses() {
        return this.$http.get(`${this.#serverUrl}/training-statuses`).then(httpReturnValue => httpReturnValue.data);
    }

}


export default QueryServerService;
