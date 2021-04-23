const angular = require('angular');
const _ = require('lodash');
const mongodb = require('mongodb');
import QueryServerService from '../../services/query-server.service.js';
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import MongoDbService from '../../services/mongodb.service.js';


class Controller {

    #scope;
    #queryServer;
    #modal;
    #options;
    #mongoDb;
    #location;

    static $inject = ['$scope', '$location', 'queryServer', 'modal', 'options', 'mongoDb'];

    /**
     * @param {angular.IScope} $scope 
     * @param {angular.ILocationService} $location
     * @param {QueryServerService} queryServer
     * @param {ModalService} modal
     * @param {OptionsService} options
     * @param {MongoDbService} mongoDb
     */
    constructor($scope, $location, queryServer, modal, options, mongoDb) {
        this.#scope = $scope;
        this.#location = $location;
        this.#queryServer = queryServer;
        this.#modal = modal;
        this.#options = options;
        this.#mongoDb = mongoDb;

        $scope.status = 'CONNECTING';
        $scope.connectionFailed = false;
        $scope.retry = () => this.loadAll();

        this.loadAll();
    }

    $onDestroy() { }

    async loadAll() {
        try {
            this.#scope.status = 'CONNECTING';
            this.#scope.connectionFailed = false;
            await Promise.all([this.#mongoDb.connect(), this.#options.load()]);
            this.#location.path('/organizer');
        }
        catch (e) {
            this.#scope.status = 'DISCONNECTED';
            this.#scope.connectionFailed = true;
            this.#modal.showError(e, 'ERROR: Server/MongoDB Connection', 'Errors during loading of program.');
        }
        this.#scope.$apply();
    }

}


export default Controller;
