const angular = require('angular');
import QueryServerService from './query-server.service.js';


class ClusterAlgorithmsService {

    #container = [];
    #isLoaded = false;

    static $inject = ['$q', 'queryServer'];
    $q;
    queryServer;

    /**
     * @param {angular.IQService} $q
     * @param {QueryServerService} queryServer 
     */
    constructor($q, queryServer) {
        this.$q = $q;
        this.queryServer = queryServer;
    }

    preload() {
        if (this.#isLoaded) { return this.$q.resolve(); }
        this.#isLoaded = false;
        this.#container = [];
        return this.queryServer.clusterAlgorithms().then(data => {
            this.#isLoaded = true;
            this.#container = data;
        });
    }

    items() {
        return this.#container;
    }

    /**
     * 
     * @param {string} name 
     * @returns {Object}
     */
    get(name) {
        return this.#container.find(element => element.name === name);
    }

    /**
     * 
     * @param {string} clusterName 
     * @returns {Object}
     */
    getDefaultArgs(clusterName) {
        let defaultArgs = Object();
        for (let [paramName, details] of Object.entries(this.get(clusterName).parameters)) {
            defaultArgs[paramName] = details.default;
        }
        return defaultArgs;
    }

    isLoaded() {
        return this.#isLoaded;
    }

}


export default ClusterAlgorithmsService;
