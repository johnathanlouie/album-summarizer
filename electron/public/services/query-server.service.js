const angular = require('angular');


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
 * An interface to the python server
 */
class QueryServerService {

    #http;
    #serverUrl = 'http://localhost:8080';

    static $inject = ['$http'];

    /**
     * @param {angular.IHttpService} $http 
     */
    constructor($http) {
        this.#http = $http;
    }

    /**
     * Rates and clusters images
     * @param {string} dir Filepath of the directory of images to rate and cluster
     * @returns {Promise.<Array.<Array.<RunReturnObject>>>}
     */
    async run(dir) {
        return (await this.#http.post(`${this.#serverUrl}/run`, { url: dir })).data;
    }

    /**
     * Fetches compile options for the model
     * @returns {Promise.<OptionsReturnObject>}
     */
    async options() {
        return (await this.#http.get(`${this.#serverUrl}/options`)).data;
    }

}


export default QueryServerService;
