const angular = require('angular');
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import UsersService from '../../services/users.service.js';
import EvaluationsService from '../../services/evaluations.service.js';


const OK = 'OK';
const LOADING = 'LOADING...';
const FAIL = 'FAILED';


class Statuses {

    options = LOADING;
    users = LOADING;
    evaluations = LOADING;
    evaluationStatuses = LOADING;
    total = 4;

    reset() {
        this.options = LOADING;
        this.users = LOADING;
        this.evaluations = LOADING;
        this.evaluationStatuses = LOADING;
    }

    get succeeded() {
        let n = 0;
        if (this.options === OK) { n++; }
        if (this.users === OK) { n++; }
        if (this.evaluations === OK) { n++; }
        if (this.evaluationStatuses === OK) { n++; }
        return n;
    }

}


class LoadingViewController {

    #statuses = new Statuses();

    static $inject = ['$scope', '$location', '$q', 'modal', 'options', 'users', 'evaluations'];
    $scope;
    $location;
    $q;
    modal;
    options;
    users;
    evaluations;

    /**
     * @param {angular.IScope} $scope 
     * @param {angular.ILocationService} $location
     * @param {angular.IQService} $q
     * @param {ModalService} modal
     * @param {OptionsService} options
     * @param {UsersService} users
     * @param {EvaluationsService} evaluations
     */
    constructor($scope, $location, $q, modal, options, users, evaluations) {
        this.$scope = $scope;
        this.$location = $location;
        this.$q = $q;
        this.modal = modal;
        this.options = options;
        this.users = users;
        this.evaluations = evaluations;

        $scope.status = 'CONNECTING';
        $scope.connectionFailed = false;
        $scope.statuses = this.#statuses;
        $scope.retry = () => this.loadAll();

        this.loadAll();
    }

    $onDestroy() { }

    loadAll() {
        this.$scope.status = 'CONNECTING';
        this.$scope.connectionFailed = false;
        this.#statuses.reset();
        return this.$q.resolve(Promise.allSettled([
            this.$q.resolve(this.options.load()).then(
                () => { this.#statuses.options = OK; },
                e => { this.#statuses.options = FAIL; throw e; },
            ),
            this.$q.resolve(this.users.load()).then(
                () => { this.#statuses.users = OK; },
                e => { this.#statuses.users = FAIL; throw e; },
            ),
            this.$q.resolve(this.evaluations.fromMongoDb()).then(
                () => { this.#statuses.evaluations = OK; },
                e => { this.#statuses.evaluations = FAIL; throw e; },
            ),
            this.$q.resolve(this.evaluations.fetchStatuses()).then(
                () => { this.#statuses.evaluationStatuses = OK; },
                e => { this.#statuses.evaluationStatuses = FAIL; throw e; },
            ),
        ])).then(
            loadResults => {
                let errors = loadResults.filter(i => i.status === 'rejected').map(i => i.reason);
                if (errors.length > 0) {
                    console.table(loadResults);
                    this.$scope.status = 'DISCONNECTED';
                    this.$scope.connectionFailed = true;
                    this.modal.showError(errors, 'ERROR: Server/MongoDB Connection', 'Errors during loading of program.');
                }
                else {
                    this.$location.path('/organizer');
                }
            }
        );
    }

}


export default LoadingViewController;
