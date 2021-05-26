const angular = require('angular');
import OptionsService from '../../services/options.service.js';
import ModalService from '../../services/modal.service.js';
import QueryServerService from '../../services/query-server.service.js';


class ModelSummaryViewController {

    static $inject = ['$scope', 'options', 'modal', 'queryServer'];

    /**
     * @param {angular.IScope} $scope 
     * @param {OptionsService} options 
     * @param {ModalService} modal
     * @param {QueryServerService} queryServer
     */
    constructor($scope, options, modal, queryServer) {

        $scope.options = options;

        function loadOptions() {
            modal.showLoading('RETRIEVING...');
            return options.load().then(
                () => modal.hideLoading(),
                e => {
                    console.error(e);
                    modal.hideLoading();
                    $('#staticBackdrop').modal();
                }
            );
        }

        loadOptions();

        $scope.submit = function () {
            modal.showLoading('FETCHING...');
            var architecture = [];
            var architecture2 = [];
            return queryServer.modelSummary($scope.selectedOptions).then(
                response => {
                    for (let layer of response.layers) {
                        switch (layer.layer_type) {
                            case 'InputLayer':
                            case 'Conv2D':
                            case 'BatchNormalization':
                            case 'MaxPooling2D':
                                let s = [1, 1];
                                if (layer.pool_size) { s = layer.pool_size; }
                                else if (layer.kernel_size) { s = layer.kernel_size; }
                                architecture.push({
                                    width: layer.input_shape[0],
                                    height: layer.input_shape[1],
                                    depth: layer.input_shape[2],
                                    filterWidth: s[0],
                                    filterHeight: s[1],
                                    rel_y: 0,
                                    rel_x: 0,
                                });
                                break;
                            case 'Flatten':
                            case 'Dense':
                                architecture2.push(layer.input_shape[0]);
                                break;
                            default:
                                throw new Error('Unknown layer type', layer);
                        }
                    }
                    window.ALEXNET.redraw({ 'architecture_': architecture, 'architecture2_': architecture2 });
                    modal.hideLoading();
                },
                e => {
                    console.error(e);
                    modal.hideLoading();
                    modal.showError(e, 'ERROR: Deep Learning', 'Error during prediction');
                }
            );
        };

        $scope.selectedOptions = {
            architecture: 'smi13a',
            dataset: 'ccrc',
            loss: 'bce',
            optimizer: 'sgd',
            metrics: 'acc',
            epochs: 0,
            patience: 3,
        };

        $scope.retry = function () {
            $('#staticBackdrop').modal('hide');
            loadOptions();
        };

    }

}


export default ModelSummaryViewController;
