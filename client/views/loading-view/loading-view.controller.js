const angular = require('angular');
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import UsersService from '../../services/users.service.js';
import EvaluationsService from '../../services/evaluations.service.js';


class LoadingViewController {

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
        $scope.retry = () => this.loadAll();

        this.loadAll();
    }

    $onDestroy() { }

    loadAll() {
        this.$scope.status = 'CONNECTING';
        this.$scope.connectionFailed = false;
        return this.$q.all([
            this.options.load(),
            this.users.load(),
            this.evaluations.fetchStatuses(),
            this.evaluations.fromMongoDb(),
        ]).then(
            () => this.$location.path('/organizer')
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
