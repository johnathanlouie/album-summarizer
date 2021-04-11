const angular = require('angular');


angular.module('views.histogramView').component('histogramView', {
    templateUrl: 'views/histogram-view/histogram-view.template.html',
    controller: ['$scope', '$http', '$rootScope', 'options', function ($scope, $http, $rootScope, options) {

        const os = require('os');
        const path = require('path');
        $scope.options = options;

        $scope.submit = async function () {
            try {
                $rootScope.$broadcast('LOADING_MODAL_SHOW');
                $scope.clusters = [];
                var url = 'http://localhost:8080/cluster';
                var response = await $http.post(url, $scope.requestParameters);
                $scope.clusters = response.data;
                $rootScope.$broadcast('LOADING_MODAL_HIDE');
            }
            catch (e) {
                console.error(e);
                $rootScope.$broadcast('LOADING_MODAL_HIDE');
                $rootScope.$broadcast('ERROR_MODAL_SHOW');
            }
            $scope.$apply();
        };

        $scope.requestParameters = {
            cluster: 'sift',
            directory: path.join(os.homedir(), 'Pictures'),
        };

        $scope.clusters = [];

    }],
});
