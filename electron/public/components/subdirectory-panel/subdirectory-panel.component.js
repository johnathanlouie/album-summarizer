'use strict';


angular.module('components.subdirectoryPanel').component('subdirectoryPanel', {
    templateUrl: 'components/subdirectory-panel/subdirectory-panel.template.html',
    controller: ['$scope', '$rootScope', 'Cwd', function ($scope, $rootScope, Cwd) {
        $scope.cwd = Cwd;
        $scope.goTo = function (dst) { $rootScope.$broadcast('CHANGE_DIRECTORY', dst); };
    }],
});
