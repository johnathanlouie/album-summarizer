'use strict';


angular.module('components.subdirectoryPanel').component('subdirectoryPanel', {
    templateUrl: 'components/subdirectory-panel/subdirectory-panel.template.html',
    controller: ['$scope', 'Cwd', function ($scope, Cwd) {
        $scope.cwd = Cwd;
        $scope.goTo = function (dst) { $scope.$emit('CHANGE_DIRECTORY', dst); };
    }],
});
