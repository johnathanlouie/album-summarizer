'use strict';


angular.module('core.fileInput').directive('fileInput', [function () {
    return {
        restrict: 'A',
        link(scope, element, attrs) {
            function setVar() { scope[attrs.fileInput] = element.prop('files'); }
            setVar();
            element.change(setVar);
        },
    };
}]);
