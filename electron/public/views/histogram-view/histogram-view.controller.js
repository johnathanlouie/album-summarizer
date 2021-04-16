const angular = require('angular');
const os = require('os');
const path = require('path');
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';


/**
 * @param {angular.IScope} $scope 
 * @param {angular.IHttpService} $http 
 * @param {OptionsService} options 
 * @param {ModalService} modal 
 */
function controllerFn($scope, $http, options, modal) {

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
            modal.showError(e, 'ERROR: Deep Learning', 'Error while fetching compile options');
        }
        $scope.$apply();
    }

    loadOptions();

    $scope.submit = async function () {
        try {
            modal.showLoading('CLUSTERING...');
            $scope.clusters = [];
            var url = 'http://localhost:8080/cluster';
            var response = await $http.post(url, $scope.requestParameters);
            $scope.clusters = response.data;
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

}

controllerFn.$inject = ['$scope', '$http', 'options', 'modal'];


export default controllerFn;
