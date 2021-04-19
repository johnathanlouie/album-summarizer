const angular = require('angular');
const _ = require('lodash');
import QueryServerService from '../../services/query-server.service.js';
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import MongoDbService from '../../services/mongodb.service.js';


class Controller {

    #scope;
    #queryServer;
    #modal;

    static $inject = ['$scope', 'queryServer', 'modal', 'options', 'mongoDb'];

    /**
     * @param {angular.IScope} $scope 
     * @param {QueryServerService} queryServer
     * @param {ModalService} modal
     * @param {OptionsService} options
     * @param {MongoDbService} mongoDb
     */
    constructor($scope, queryServer, modal, options, mongoDb) {
        this.#scope = $scope;
        this.#queryServer = queryServer;
        this.#modal = modal;

        $scope.evaluations = [];

        async function loadOptions() {
            await options.load();
        }

        async function getEvaluated() {
            $scope.evaluations = await mongoDb.getAll('evaluations');
        }


        function isEvaluated(model) {
            for (let i of $scope.evaluations) {
                if (_.isEqual(i.model, model)) { return true; }
            }
            return false;
        }

        let progressBar = {
            total() { return options.modelCount(); },
            current() { return $scope.evaluations.length; },
            percentage() { return Math.round(this.current() / this.total() * 100); },
            style() { return { width: `${this.percentage()}%` }; },
        };

        $scope.progressBar = progressBar;

        async function doAll() {
            for (let model of options.models()) {
                if (!isEvaluated(model)) {
                    try {
                        let result = await queryServer.evaluate(model);
                        await mongoDb.insertOne('evaluations', result);
                        $scope.evaluations.push(result);
                        $scope.$apply();
                    }
                    catch (e) {
                        console.error(e);
                    }
                }
            }
        }

        async function init() {
            try {
                modal.showLoading('RETRIEVING...');
                await Promise.all([getEvaluated(), loadOptions()]);
                modal.hideLoading();
                await doAll();
            } catch (e) {
                console.error(e);
                modal.hideLoading();
                modal.showError(e, 'ERROR: Deep Learning', 'Error while evaluating');
            }
        }

        init();
    }

    async evaluateAll() {
        this.#modal.showLoading('EVALUATING...');
        this.#scope.evaluations = await this.#queryServer.evaluateAll();
        this.#modal.hideLoading();
        this.#scope.$apply();
    }

}


export default Controller;
