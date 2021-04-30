const angular = require('angular');
import RouteManager from '../../lib/routes.js';


class Controller {

    static $inject = ['$scope'];

    /**
     * @param {angular.IScope} $scope 
     */
    constructor($scope) {
        $scope.routes1 = () => RouteManager.menu1();
        $scope.routes2 = () => RouteManager.menu2();
    }

}


export default Controller;
