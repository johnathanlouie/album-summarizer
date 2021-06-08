const angular = require('angular');
const os = require('os');
const path = require('path');
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import QueryServerService from '../../services/query-server.service.js';
import FocusImageService from '../../services/focus-image.service.js';
import ClusterAlgorithmsService from '../../services/cluster-algorithms.service.js';


/**
 * @param {angular.IScope} $scope 
 * @param {angular.IQService} $q 
 * @param {OptionsService} options 
 * @param {ModalService} modal 
 * @param {QueryServerService} queryServer
 * @param {FocusImageService} focusImage
 * @param {ClusterAlgorithmsService} clusterAlgorithms
 */
function controllerFn($scope, $q, options, modal, queryServer, focusImage, clusterAlgorithms) {

    $scope.options = options;
    $scope.clusterAlgorithms = clusterAlgorithms;

    function preload() {
        modal.showLoading('RETRIEVING...');
        return $q.all([options.load(), clusterAlgorithms.preload()]).then(
            () => {
                $scope.$watch('requestArgs.cluster', (newVal, oldVal, scope) => {
                    scope.requestArgs.args = clusterAlgorithms.getDefaultArgs(newVal);
                });

                $scope.requestArgs = {
                    cluster: 'hybrid3',
                    directory: path.join(os.homedir(), 'Pictures'),
                    args: clusterAlgorithms.getDefaultArgs('hybrid3'),
                };

                modal.hideLoading();
            },
            e => {
                console.error(e);
                modal.hideLoading();
                $('#staticBackdrop').modal();
            },
        );
    }

    preload();

    $scope.submit = function () {
        modal.showLoading('CLUSTERING...');
        $scope.clusters = [];
        return queryServer.cluster(
            $scope.requestArgs.cluster,
            $scope.requestArgs.directory,
            $scope.requestArgs.args,
        ).then(
            clusters => {
                $scope.clusters = clusters;
                modal.hideLoading();
            },
            e => {
                console.error(e);
                modal.hideLoading();
                modal.showError(e, 'ERROR: Clustering Algorithms', 'Error while clustering');
            },
        );
    };

    $scope.clusters = [];

    $scope.retry = function () {
        $('#staticBackdrop').modal('hide');
        return preload();
    };

    $scope.focusOnImage = function (url) {
        focusImage.image = url;
        modal.showPhoto();
    };

}

controllerFn.$inject = ['$scope', '$q', 'options', 'modal', 'queryServer', 'focusImage', 'clusterAlgorithms'];


export default controllerFn;
