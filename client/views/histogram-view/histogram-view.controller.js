const angular = require('angular');
const os = require('os');
const path = require('path');
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import QueryServerService from '../../services/query-server.service.js';
import FocusImageService from '../../services/focus-image.service.js';


/**
 * @param {angular.IScope} $scope 
 * @param {OptionsService} options 
 * @param {ModalService} modal 
 * @param {QueryServerService} queryServer
 * @param {FocusImageService} focusImage
 */
function controllerFn($scope, options, modal, queryServer, focusImage) {

    $scope.options = options;

    async function loadOptions() {
        try {
            modal.showLoading('RETRIEVING...');
            await options.load();
            modal.hideLoading();
        }
        catch (e) {
            console.error(e);
            modal.hideLoading();
            $('#staticBackdrop').modal();
        }
        $scope.$apply();
    }

    loadOptions();

    $scope.submit = async function () {
        try {
            modal.showLoading('CLUSTERING...');
            $scope.clusters = [];
            $scope.clusters = await queryServer.cluster(
                $scope.requestParameters.cluster,
                $scope.requestParameters.directory,
            );
            modal.hideLoading();
        }
        catch (e) {
            console.error(e);
            modal.hideLoading();
            modal.showError(e, 'ERROR: Clustering Algorithms', 'Error while clustering');
        }
        $scope.$apply();
    };

    $scope.requestParameters = {
        cluster: 'sift',
        directory: path.join(os.homedir(), 'Pictures'),
    };

    $scope.clusters = [];

    $scope.retry = function () {
        $('#staticBackdrop').modal('hide');
        loadOptions();
    };

    $scope.focusOnImage = function (url) {
        focusImage.image = url;
        modal.showPhoto();
    };

}

controllerFn.$inject = ['$scope', 'options', 'modal', 'queryServer', 'focusImage'];


export default controllerFn;
