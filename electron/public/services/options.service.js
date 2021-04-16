const angular = require('angular');
import QueryServerService from './query-server.service.js';


class Options {

    #isLoaded = false;

    /** @type {Array.<string>} */
    architectures = [];

    /** @type {Array.<string>} */
    datasets = [];

    /** @type {Array.<string>} */
    losses = [];

    /** @type {Array.<string>} */
    optimizers = [];

    /** @type {Array.<string>} */
    clusters = [];

    #$rootScope;
    #queryServer;

    static $inject = ['$rootScope', 'queryServer'];

    /**
     * 
     * @param {angular.IRootScopeService} $rootScope 
     * @param {QueryServerService} queryServer 
     */
    constructor($rootScope, queryServer) {
        this.#$rootScope = $rootScope;
        this.#queryServer = queryServer;
        this.load(false);
    }

    clear() {
        this.#isLoaded = false;
        this.architectures = [];
        this.datasets = [];
        this.losses = [];
        this.optimizers = [];
        this.clusters = [];
    }

    /**
     * Fetches compile options for the deep learning model
     * @param {boolean} reload Forces a refresh
     */
    async load(reload) {
        if (!this.#isLoaded || reload) {
            this.clear();
            try {
                this.#$rootScope.$broadcast('LOADING_MODAL_SHOW', 'Deep Learning Options', 'Retrieving...');
                var response = await this.#queryServer.options();
                this.architectures = response.architectures;
                this.datasets = response.datasets;
                this.losses = response.losses;
                this.optimizers = response.optimizers;
                this.clusters = response.clusters;
                this.#isLoaded = true;
                this.#$rootScope.$broadcast('LOADING_MODAL_HIDE');
            }
            catch (e) {
                console.error(e);
                this.#$rootScope.$broadcast('LOADING_MODAL_HIDE');
                this.#$rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: Deep Learning Options', '');
            }
            this.#$rootScope.$apply();
        }
    }

}


export default Options;
