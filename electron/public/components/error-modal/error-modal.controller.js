const angular = require('angular');


class Controller {

    static $inject = ['$scope'];

    /**
     * @param {angular.IScope} $scope
     */
    constructor($scope) {
        $scope.$on('ERROR_MODAL_SHOW', (event, error, title, message) => {
            $scope.error = error;
            $scope.message = message;
            $scope.title = title;
            $('#errorModal').modal();
        });
    }

}


export default Controller;
