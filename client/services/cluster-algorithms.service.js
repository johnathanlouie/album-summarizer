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

    get(name) {
        return this.#container.find(element => element.name === name);
    }

    isLoaded() {
        return this.#isLoaded;
    }

}


export default ClusterAlgorithmsService;
