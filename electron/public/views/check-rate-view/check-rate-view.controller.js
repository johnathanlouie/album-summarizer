function maxIndex(a) {
    return a.reduce((iMax, x, i, arr) => x > arr[iMax] ? i : iMax, 0);
}


class OneHotValue {
    #value;
    #name;
    isMax;

    constructor(value, name, isMax) {
        if (typeof value !== 'number') { throw new TypeError(value); }
        this.#name = name;
        this.#value = value;
        this.isMax = isMax;
    }

    get name() { return this.#name; }
    get cssWidth() { return { width: `${this.percentage}%` }; }
    get value() { return this.#value; }
    get percentage() { return this.#value * 100; }
}


class OneHot {
    arr;
    ans;

    constructor(arr, keyGuide) {
        if (!Array.isArray(arr)) { console.error(arr); throw new TypeError(); }
        if (!Array.isArray(keyGuide)) { console.error(keyGuide); throw new TypeError(); }
        this.ans = maxIndex(arr);
        this.arr = arr.map((v, i) => new OneHotValue(v, keyGuide[i], i === this.ans));
    }

    get label() { return this.arr[this.ans].name; }
}


class Prediction {
    x;
    y = {
        predicted: undefined,
        truth: undefined,
    };

    constructor(x, yPred, yTruth, keyGuide) {
        this.x = x;
        if (keyGuide === null) {
            this.y.truth = yTruth;
            this.y.predicted = yPred;
        }
        else {
            this.y.truth = new OneHot(yTruth, keyGuide);
            this.y.predicted = new OneHot(yPred, keyGuide);
        }
    }
}


function controllerFn($scope, $http, $rootScope, options) {

    $scope.options = options;

    $scope.submit = async function () {
        try {
            $rootScope.$broadcast('LOADING_MODAL_SHOW', 'Deep Learning', 'Predicting...');
            var url = 'http://localhost:8080/predict';
            $scope.prediction = [];
            $scope.keyGuide = null;
            var response = await $http.post(url, $scope.selectedOptions);
            $scope.keyGuide = response.data.keyGuide;
            if ($scope.keyGuide === null) {
                response.data.prediction.y.predicted = _.flatten(response.data.prediction.y.predicted);
            }
            for (let i in response.data.prediction.x) {
                $scope.prediction.push(new Prediction(
                    response.data.prediction.x[i],
                    response.data.prediction.y.predicted[i],
                    response.data.prediction.y.truth[i],
                    response.data.keyGuide,
                ));
            }
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
            $scope.$apply();
        }
        catch (e) {
            console.error(e);
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
            $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: Deep Learning', '');
            $scope.$apply();
        }
    };

    $scope.selectedOptions = {
        phase: 'test',
        architecture: 'vgg16',
        dataset: 'ccc',
        loss: 'rmse',
        optimizer: 'sgd1',
        metrics: 'acc',
        epochs: 0,
        patience: 3,
        split: 0,
    };

}

controllerFn.$inject = ['$scope', '$http', '$rootScope', 'options'];


export default controllerFn;
