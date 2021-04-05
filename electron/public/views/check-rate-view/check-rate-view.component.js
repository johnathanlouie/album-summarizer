'use strict';


class Prediction {
    x;
    y = {
        predicted: undefined,
        truth: undefined,
    };

    constructor(x, yPred, yTruth) {
        this.x = x;
        this.y.predicted = yPred;
        this.y.truth = yTruth;
    }
}

angular.module('views.checkRateView').component('checkRateView', {
    templateUrl: 'views/check-rate-view/check-rate-view.template.html',
    controller: ['$scope', '$http', '$rootScope', function ($scope, $http, $rootScope) {

        async function getOptions() {
            try {
                $rootScope.$broadcast('LOADING_MODAL_SHOW');
                var response = await $http.get('http://localhost:8080/options');
                $scope.options = response.data;
                $rootScope.$broadcast('LOADING_MODAL_HIDE');
                $scope.$apply();
            }
            catch (e) {
                $rootScope.$broadcast('LOADING_MODAL_HIDE');
                $rootScope.$broadcast('ERROR_MODAL_SHOW');
                $scope.$apply();
            }
        }

        $scope.submit = async function () {
            try {
                $rootScope.$broadcast('LOADING_MODAL_SHOW');
                var url = `http://localhost:8080/predict/${$scope.selectedOptions.phase}`;
                var response = await $http.post(url, $scope.selectedOptions);
                $scope.prediction = [];
                for (let i in response.data.x) {
                    $scope.prediction.push(new Prediction(
                        response.data.x[i],
                        response.data.y.predicted[i],
                        response.data.y.truth[i],
                    ));
                }
                $rootScope.$broadcast('LOADING_MODAL_HIDE');
                $scope.$apply();
            }
            catch (e) {
                $rootScope.$broadcast('LOADING_MODAL_HIDE');
                $rootScope.$broadcast('ERROR_MODAL_SHOW');
                $scope.$apply();
            }
        };

        $scope.selectedOptions = {
            phase: 'test',
            architecture: 'smi13',
            dataset: 'ccr',
            loss: 'rmse',
            optimizer: 'sgd1',
            metrics: 'acc',
            epochs: 0,
            patience: 3,
            split: 0,
        };

        getOptions();

    }],
});
