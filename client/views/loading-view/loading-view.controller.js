const angular = require('angular');
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import UsersService from '../../services/users.service.js';
import EvaluationsService from '../../services/evaluations.service.js';


class Statuses {

    options = false;
    users = false;
    evaluations = false;
    evaluationStatuses = false;
    total = 4;

    reset() {
        this.options = false;
        this.users = false;
        this.evaluations = false;
        this.evaluationStatuses = false;
    }

    get succeeded() {
        let n = 0;
        if (this.options) { n++; }
        if (this.users) { n++; }
        if (this.evaluations) { n++; }
        if (this.evaluationStatuses) { n++; }
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
            this.$q.resolve(this.options.load()).then(() => { this.#statuses.options = true; }),
            this.$q.resolve(this.users.load()).then(() => { this.#statuses.users = true; }),
            this.$q.resolve(this.evaluations.fromMongoDb()).then(() => { this.#statuses.evaluations = true; }),
            this.$q.resolve(this.evaluations.fetchStatuses()).then(() => { this.#statuses.evaluationStatuses = true; }),
        ])).then(
            loadResults => {
                for (let i of loadResults) {
                    if (i.status === 'rejected') {
                        throw new Error();
                    }
                }
                this.$location.path('/organizer');
            }
        ).catch(
            e => {
                console.error(e);
                this.$scope.status = 'DISCONNECTED';
                this.$scope.connectionFailed = true;
                this.modal.showError(e, 'ERROR: Server/MongoDB Connection', 'Errors during loading of program.');
            }
        );
    }

}


export default LoadingViewController;
