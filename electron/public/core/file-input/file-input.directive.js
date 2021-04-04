'use strict';


angular.module('core.fileInput').directive('fileInput', [function () {
    return {
        restrict: 'A',
        link(scope, element, attrs) {
            function onChange(event) {
                scope[attrs.fileInput] = element.prop('files');
                scope.$apply();
            }

            element.on('change', onChange);
        },
    };
}]);
