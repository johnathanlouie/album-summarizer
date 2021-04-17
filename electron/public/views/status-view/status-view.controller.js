const angular = require('angular');
import QueryServerService from '../../services/query-server.service.js';
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';


class Controller {

    #scope;
    #queryServer;
    #modal;

    static $inject = ['$scope', 'queryServer', 'modal', 'options'];

    /**
     * @param {angular.IScope} $scope 
     * @param {QueryServerService} queryServer
     * @param {ModalService} modal
     * @param {OptionsService} options
     */
    constructor($scope, queryServer, modal, options) {
        this.#scope = $scope;
        this.#queryServer = queryServer;
        this.#modal = modal;

        async function loadOptions() {
            try {
                modal.showLoading('RETRIEVING...');
                await options.load();
                modal.hideLoading();
            }
            catch (e) {
                console.error(e);
                modal.hideLoading();
                modal.showError(e, 'ERROR: Deep Learning', 'Error during fetching compile options');
            }
        }

        $scope.evaluations = [];

        async function doAll() {
            for (let a of options.architectures) {
                for (let d of options.datasets) {
                    for (let l of options.losses) {
                        for (let o of options.optimizers) {
                            let model = {
                                architecture: a,
                                dataset: d,
                                loss: l,
                                optimizer: o,
                                metrics: 'acc',
                                epochs: 0,
                                patience: 3,
                                split: 0,
                            };
                            let result = await queryServer.evaluate(model);
                            $scope.evaluations.push(result);
                            $scope.$apply();
                        }
                    }
                }
            }
        }

        loadOptions().then(() => doAll());
    }

    async evaluateAll() {
        this.#modal.showLoading('EVALUATING...');
        this.#scope.evaluations = await this.#queryServer.evaluateAll();
        this.#modal.hideLoading();
        this.#scope.$apply();
    }

}


export default Controller;
