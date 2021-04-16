const angular = require('angular');


class Controller {

    #scope;

    static $inject = ['$scope'];

    /**
     * @param {angular.IScope} $scope 
     */
    constructor($scope) {
        this.#scope = $scope;
    }

}


export default Controller;
