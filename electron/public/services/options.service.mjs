function f($rootScope, $http) {

    class Options {

        #isLoaded = false;
        architectures = [];
        datasets = [];
        losses = [];
        optimizers = [];
        clusters = [];

        constructor() { this.load(false); }

        async load(reload) {
            if (!this.#isLoaded || reload) {
                try {
                    this.#isLoaded = false;
                    $rootScope.$broadcast('LOADING_MODAL_SHOW');
                    this.architectures = [];
                    this.datasets = [];
                    this.losses = [];
                    this.optimizers = [];
                    this.clusters = [];
                    var response = await $http.get('http://localhost:8080/options');
                    this.architectures = response.data.architectures;
                    this.datasets = response.data.datasets;
                    this.losses = response.data.losses;
                    this.optimizers = response.data.optimizers;
                    this.clusters = response.data.clusters;
                    this.#isLoaded = true;
                    $rootScope.$broadcast('LOADING_MODAL_HIDE');
                }
                catch (e) {
                    console.error(e);
                    $rootScope.$broadcast('LOADING_MODAL_HIDE');
                    $rootScope.$broadcast('ERROR_MODAL_SHOW');
                }
                $rootScope.$apply();
            }
        }

    }

    return new Options();

}


f.$inject = ['$rootScope', '$http'];


export default f;
