const angular = require('angular');
import ModalService from '../../services/modal.service.js';
import OptionsService from '../../services/options.service.js';
import UsersService from '../../services/users.service.js';
import EvaluationsService from '../../services/evaluations.service.js';


class LoadingViewController {

    static $inject = ['$scope', '$location', 'modal', 'options', 'users', 'evaluations'];
    $scope;
    $location;
    modal;
    options;
    users;
    evaluations;

    /**
     * @param {angular.IScope} $scope 
     * @param {angular.ILocationService} $location
     * @param {ModalService} modal
     * @param {OptionsService} options
     * @param {UsersService} users
     * @param {EvaluationsService} evaluations
     */
    constructor($scope, $location, modal, options, users, evaluations) {
        this.$scope = $scope;
        this.$location = $location;
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

    async loadAll() {
        try {
            this.$scope.status = 'CONNECTING';
            this.$scope.connectionFailed = false;
            await Promise.all([
                this.options.load(),
                this.users.load(),
                this.evaluations.fetchStatuses(),
                this.evaluations.fromMongoDb(),
            ]);
            this.$location.path('/organizer');
        }
        catch (e) {
            console.error(e);
            this.$scope.status = 'DISCONNECTED';
            this.$scope.connectionFailed = true;
            this.modal.showError(e, 'ERROR: Server/MongoDB Connection', 'Errors during loading of program.');
        }
        this.$scope.$apply();
    }

}


export default LoadingViewController;
