const angular = require('angular');
const _ = require('lodash');
import OptionsService from '../../services/options.service.js';
import ModalService from '../../services/modal.service.js';
import QueryServerService from '../../services/query-server.service.js';
import FocusImageService from '../../services/focus-image.service.js';


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
        if (keyGuide.length === 0) {
            console.log('asdf');
            this.y.truth = yTruth;
            this.y.predicted = yPred;
        }
        else {
            console.log('456');
            this.y.truth = new OneHot(yTruth, keyGuide);
            this.y.predicted = new OneHot(yPred, keyGuide);
        }
        console.log(this.y.truth);
        console.log(this.y.predicted);
    }
}


class CheckRateViewController {

    static $inject = ['$scope', 'options', 'modal', 'queryServer', 'focusImage'];

    /**
     * @param {angular.IScope} $scope 
     * @param {OptionsService} options 
     * @param {ModalService} modal
     * @param {QueryServerService} queryServer
     * @param {FocusImageService} focusImage
     */
    constructor($scope, options, modal, queryServer, focusImage) {

        $scope.options = options;

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
            $scope.keyGuide = null;
            return queryServer.predict($scope.selectedOptions).then(
                response => {
                    $scope.keyGuide = response.keyGuide;
                    if ($scope.keyGuide.length === 0) {
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
