const angular = require('angular');
const _ = require('lodash');
const mongodb = require('mongodb');
import QueryServerService from '../../services/query-server.service.js';
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import MongoDbService from '../../services/mongodb.service.js';
import UsersService from '../../services/users.service.js';
import EvaluationsService from '../../services/evaluations.service.js';


class Controller {

    #scope;
    #queryServer;
    #modal;
    #options;
    #mongoDb;
    #location;
    #users;
    #evaluations;

    static $inject = ['$scope', '$location', 'queryServer', 'modal', 'options', 'mongoDb', 'users', 'evaluations'];

    /**
     * @param {angular.IScope} $scope 
     * @param {angular.ILocationService} $location
     * @param {QueryServerService} queryServer
     * @param {ModalService} modal
     * @param {OptionsService} options
     * @param {MongoDbService} mongoDb
     * @param {MongoDbService} mongoDb
     * @param {UsersService} users
     * @param {EvaluationsService} evaluations
     */
    constructor($scope, $location, queryServer, modal, options, mongoDb, users, evaluations) {
        this.#scope = $scope;
        this.#location = $location;
        this.#queryServer = queryServer;
        this.#modal = modal;
        this.#options = options;
        this.#mongoDb = mongoDb;
        this.#users = users;
        this.#evaluations = evaluations;

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
            await Promise.all([
                this.#options.load(),
                this.#users.load(),
                this.#evaluations.fetchStatuses(),
            ]);
            this.#location.path('/organizer');
        }
        catch (e) {
            console.error(e);
            this.#scope.status = 'DISCONNECTED';
            this.#scope.connectionFailed = true;
            this.#modal.showError(e, 'ERROR: Server/MongoDB Connection', 'Errors during loading of program.');
        }
        this.#scope.$apply();
    }

}


export default Controller;
