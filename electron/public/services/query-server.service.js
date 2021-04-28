const angular = require('angular');
const fs = require('fs');
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
     * @returns {Promise.<Array.<EvaluationReturnObject>>}
     */
    async evaluateAll() {
        return (await this.$http.get(`${this.#serverUrl}/evaluate/all/0`)).data;
    }

    /**
     * @param {ModelDescription} model
     * @returns {Promise.<EvaluationReturnObject>}
     */
    async evaluate(model) {
        return (await this.$http.post(`${this.#serverUrl}/evaluate`, model)).data;
    }

}


export default QueryServerService;
