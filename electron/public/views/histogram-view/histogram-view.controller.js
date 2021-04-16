const os = require('os');
const path = require('path');


function controllerFn($scope, $http, $rootScope, options) {

    $scope.options = options;

    async function loadOptions() {
        try {
            $rootScope.$broadcast('LOADING_MODAL_SHOW', 'Deep Learning Options', 'Retrieving...');
            await options.load();
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
        }
        catch (e) {
            console.error(e);
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
            $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: Deep Learning Options', '');
        }
        $scope.$apply();
    }

    loadOptions();

    $scope.submit = async function () {
        try {
            $rootScope.$broadcast('LOADING_MODAL_SHOW', 'Cluster Algorithms', 'Clustering...');
            $scope.clusters = [];
            var url = 'http://localhost:8080/cluster';
            var response = await $http.post(url, $scope.requestParameters);
            $scope.clusters = response.data;
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
        }
        catch (e) {
            console.error(e);
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
            $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: Clustering Algorithms', '');
        }
        $scope.$apply();
    };

    $scope.requestParameters = {
        cluster: 'sift',
        directory: path.join(os.homedir(), 'Pictures'),
    };

    $scope.clusters = [];

}

controllerFn.$inject = ['$scope', '$http', '$rootScope', 'options'];


export default controllerFn;
