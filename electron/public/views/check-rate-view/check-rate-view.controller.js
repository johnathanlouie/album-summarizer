const angular = require('angular');
import OptionsService from '../../services/options.service.js';
import ModalService from '../../services/modal.service.js';
import QueryServerService from '../../services/query-server.service.js';


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

/**
 * @param {angular.IScope} $scope 
 * @param {OptionsService} options 
 * @param {ModalService} modal
 * @param {QueryServerService} queryServer
 */
function controllerFn($scope, options, modal, queryServer) {

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
            modal.showLoading('PREDICTING...');
            $scope.prediction = [];
            $scope.keyGuide = null;
            var response = await queryServer.predict($scope.selectedOptions);
            $scope.keyGuide = response.keyGuide;
            if ($scope.keyGuide === null) {
                response.prediction.y.predicted = _.flatten(response.prediction.y.predicted);
            }
            for (let i in response.prediction.x) {
                $scope.prediction.push(new Prediction(
                    response.prediction.x[i],
                    response.prediction.y.predicted[i],
                    response.prediction.y.truth[i],
                    response.keyGuide,
                ));
            }
            modal.hideLoading();
            $scope.$apply();
        }
        catch (e) {
            console.error(e);
            modal.hideLoading();
            modal.showError(e, 'ERROR: Deep Learning', 'Error during prediction');
            $scope.$apply();
        }
    };

    $scope.selectedOptions = {
        phase: 'test',
        architecture: 'smi13a',
        dataset: 'ccrc',
        loss: 'bce',
        optimizer: 'sgd',
        metrics: 'acc',
        epochs: 0,
        patience: 3,
        split: 0,
    };

    $scope.retry = function () {
        $('#staticBackdrop').modal('hide');
        loadOptions();
    };

}

controllerFn.$inject = ['$scope', 'options', 'modal', 'queryServer'];


export default controllerFn;
