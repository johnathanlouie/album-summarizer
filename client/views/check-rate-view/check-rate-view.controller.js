const angular = require('angular');
const _ = require('lodash');
import OptionsService from '../../services/options.service.js';
import ModalService from '../../services/modal.service.js';
import QueryServerService from '../../services/query-server.service.js';
import FocusImageService from '../../services/focus-image.service.js';

/**
 * 
 * @param {Array.<number>} a 
 * @returns 
 */
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


class PredictionUnit {
    x;
    y = {
        predicted: undefined,
        truth: undefined,
    };

    /**
     * 
     * @param {string} x 
     * @param {number|Array.<number>} yPred 
     * @param {number|Array.<number>} yTruth 
     * @param {Array.<string>} keyGuide 
     */
    constructor(x, yPred, yTruth, keyGuide) {
        if (!Array.isArray(keyGuide)) { throw new TypeError(keyGuide); }
        this.x = x;
        if (keyGuide.length === 0) {
            this.y.truth = yTruth;
            this.y.predicted = yPred;
        }
        else {
            this.y.truth = new OneHot(yTruth, keyGuide);
            this.y.predicted = new OneHot(yPred, keyGuide);
        }
    }
}


class ConfusionMatrix {

    classes = [];
    container = [];

    /**
     * 
     * @param {Array.<string>} classes 
     */
    constructor(classes) {
        this.classes = classes;
        this.container = classes.map(() => classes.map(() => 0));
    }

    /**
     * 
     * @param {number} truth 
     * @param {number} predicted 
     */
    add(truth, predicted) {
        if (!Number.isInteger(truth)) { throw new TypeError(); }
        if (!Number.isInteger(predicted)) { throw new TypeError(); }
        this.container[truth][predicted]++;
    }

}


class CheckRateViewController {

    static $inject = ['$scope', '$location', 'options', 'modal', 'queryServer', 'focusImage'];

    /**
     * @param {angular.IScope} $scope 
     * @param {angular.ILocationService} $location 
     * @param {OptionsService} options 
     * @param {ModalService} modal
     * @param {QueryServerService} queryServer
     * @param {FocusImageService} focusImage
     */
    constructor($scope, $location, options, modal, queryServer, focusImage) {

        $scope.options = options;
        $scope.confusionMatrix = null;

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

        $scope.submit = function () {
            modal.showLoading('PREDICTING...');
            $scope.prediction = [];
            $scope.keyGuide = [];
            $scope.confusionMatrix = null;
            return queryServer.predict($scope.selectedOptions).then(
                response => {
                    $scope.keyGuide = response.keyGuide;
                    if ($scope.keyGuide.length === 0) {
                        response.prediction.y.predicted = _.flatten(response.prediction.y.predicted);
                    }
                    else {
                        $scope.confusionMatrix = new ConfusionMatrix(response.keyGuide);
                    }
                    for (let [x, truth, predicted] of _.zip(response.prediction.x, response.prediction.y.truth, response.prediction.y.predicted)) {
                        $scope.prediction.push(new PredictionUnit(
                            x,
                            predicted,
                            truth,
                            response.keyGuide,
                        ));
                        if (response.keyGuide.length > 0) {
                            $scope.confusionMatrix.add(
                                maxIndex(truth),
                                maxIndex(predicted),
                            );
                        }
                    }
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

        Object.assign($scope.selectedOptions, $location.search());

        $scope.retry = function () {
            $('#staticBackdrop').modal('hide');
            loadOptions();
        };

        $scope.focusOnImage = function (url) {
            focusImage.image = url;
            modal.showPhoto();
        };

    }

}


export default CheckRateViewController;
