const angular = require('angular');


class NullableInputController {

    /** @type {?angular.INgModelController} */
    ngModelController;

    static $inject = ['$scope'];
    #$scope;

    /**
     * 
     * @param {angular.IScope} $scope 
     */
    constructor($scope) {
        this.#$scope = $scope;
    }

    $onInit() {
        if (this.ngModelController !== null) {
            this.ngModelController.$render = () => {
                if (this.ngModelController.$modelValue === null) {
                    this.#$scope.isNotNull = false;
                } else {
                    this.#$scope.isNotNull = true;
                    this.#$scope.floatValue = this.ngModelController.$modelValue;
                }
            };
            this.#$scope.$watchGroup([
                'isNotNull',
                'floatValue',
            ], ([isNotNull, floatValue]) => {
                this.ngModelController.$setViewValue(isNotNull ? floatValue : null);
            });
        }
    }

}


export default NullableInputController;
