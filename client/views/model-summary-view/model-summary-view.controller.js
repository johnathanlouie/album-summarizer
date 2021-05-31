const angular = require('angular');
import OptionsService from '../../services/options.service.js';
import ModalService from '../../services/modal.service.js';
import QueryServerService from '../../services/query-server.service.js';


class ModelSummaryViewController {

    static $inject = ['$scope', '$location', 'options', 'modal', 'queryServer'];

    /**
     * @param {angular.IScope} $scope 
     * @param {angular.ILocationService} $location 
     * @param {OptionsService} options 
     * @param {ModalService} modal
     * @param {QueryServerService} queryServer
     */
    constructor($scope, $location, options, modal, queryServer) {

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

        $scope.nnSvgStyle = 'alexnet';
        $scope.modelSummary = null;

        function alexnet() {
            var architecture = [];
            var architecture2 = [];
            for (let layer of $scope.modelSummary.layers) {
                switch (layer.output_shape.length) {
                    case 3:
                        let filter = [1, 1];
                        if (layer.pool_size) { filter = layer.pool_size; }
                        else if (layer.kernel_size) { filter = layer.kernel_size; }
                        architecture.push({
                            width: layer.output_shape[0],
                            height: layer.output_shape[1],
                            depth: layer.output_shape[2],
                            filterWidth: filter[0],
                            filterHeight: filter[1],
                            rel_y: 0,
                            rel_x: 0,
                        });
                        break;
                    case 1:
                        architecture2.push(layer.output_shape[0]);
                        break;
                    default:
                        throw new Error('Unknown layer type', layer);
                }
            }
            window.ALEXNET.redraw({
                architecture_: architecture,
                architecture2_: architecture2,
            });
        }

        function lenet() {
            var architecture = [];
            var architecture2 = [];
            var betweenLayers = [];
            var layerId = 0;
            for (let layer of $scope.modelSummary.layers) {
                switch (layer.output_shape.length) {
                    case 3:
                        let filter = [1, 1];
                        if (layer.pool_size) { filter = layer.pool_size; }
                        else if (layer.kernel_size) { filter = layer.kernel_size; }
                        architecture.push({
                            squareHeight: layer.output_shape[0],
                            squareWidth: layer.output_shape[1],
                            numberOfSquares: layer.output_shape[2],
                            filterHeight: filter[0],
                            filterWidth: filter[1],
                            layer: layerId,
                            op: layer.layer_type,
                        });
                        betweenLayers.push(20);
                        break;
                    case 1:
                        architecture2.push(layer.output_shape[0]);
                        break;
                    default:
                        throw new Error('Unknown layer type', layer);
                }
                layerId++;
            }
            window.LENET.redraw({
                architecture_: architecture,
                architecture2_: architecture2,
            });
            window.LENET.redistribute({
                // betweenLayers_: betweenLayers,
                // betweenSquares_: 1,
            });
        }

        function draw() {
            if ($scope.modelSummary !== null) {
                if ($scope.nnSvgStyle === 'alexnet') {
                    alexnet();
                }
                else if ($scope.nnSvgStyle === 'lenet') {
                    lenet();
                }
            }
        }

        $scope.$watch('nnSvgStyle', () => draw());

        $scope.submit = function () {
            modal.showLoading('FETCHING...');
            $scope.modelSummary = null;
            return queryServer.modelSummary($scope.selectedOptions).then(
                response => {
                    $scope.modelSummary = response;
                    draw();
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

        Object.assign($scope.selectedOptions, $location.search());

        $scope.retry = function () {
            $('#staticBackdrop').modal('hide');
            loadOptions();
        };

    }

}


export default ModelSummaryViewController;
