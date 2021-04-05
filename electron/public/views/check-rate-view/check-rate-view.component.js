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
    controller: ['$scope', '$http', function ($scope, $http) {
        async function getOptions() {
            var response = await $http.get('http://localhost:8080/options');
            if (response.status !== 200) {
            }
            else {
                $scope.options = response.data;
                $scope.$apply();
            }
        }

        $scope.submit = async function () {
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
            $scope.$apply();
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
