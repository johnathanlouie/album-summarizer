const angular = require('angular');
import RouteManager from '../../lib/routes.js';


class Controller {

    static $inject = ['$scope'];

    /**
     * @param {angular.IScope} $scope 
     */
    constructor($scope) {
        $scope.routes = RouteManager;
    }

}


export default Controller;
