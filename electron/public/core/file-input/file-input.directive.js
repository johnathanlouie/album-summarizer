'use strict';


angular.module('core.fileInput').directive('fileInput', ['$parse', function ($parse) {
    return {
        restrict: 'A',
        link(scope, element, attrs) {
            function onChange(event) {
                $parse(attrs.fileInput).assign(scope, element.prop('files'));
                scope.$apply();
            }

            element.on('change', onChange);
        },
    };
}]);
