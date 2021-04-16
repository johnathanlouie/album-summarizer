const angular = require('angular');


/**
 * A data object returned by the python server
 * @typedef {Object} RunReturnObject
 * @property {string} path
 * @property {number} rating
 * @property {number} cluster
 */


/**
 * An interface to the python server
 */
class QueryServerService {

    #http;

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
        return (await this.#http.post('http://localhost:8080/run', { url: dir })).data;
    }

}


export default QueryServerService;
