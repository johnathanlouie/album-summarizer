const angular = require('angular');


class Options {

    #isLoaded = false;
    architectures = [];
    datasets = [];
    losses = [];
    optimizers = [];
    clusters = [];

    /** @type angular.IRootScopeService */
    #$rootScope;

    /** @type angular.IHttpService */
    #$http;

    static $inject = ['$rootScope', '$http'];
    constructor($rootScope, $http) {
        this.#$rootScope = $rootScope;
        this.#$http = $http;
        this.load(false);
    }

    async load(reload) {
        if (!this.#isLoaded || reload) {
            try {
                this.#isLoaded = false;
                this.#$rootScope.$broadcast('LOADING_MODAL_SHOW', 'Deep Learning Options', 'Retrieving...');
                this.architectures = [];
                this.datasets = [];
                this.losses = [];
                this.optimizers = [];
                this.clusters = [];
                var response = await this.#$http.get('http://localhost:8080/options');
                this.architectures = response.data.architectures;
                this.datasets = response.data.datasets;
                this.losses = response.data.losses;
                this.optimizers = response.data.optimizers;
                this.clusters = response.data.clusters;
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
