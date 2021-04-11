function controller($scope, $rootScope, cwd) {
    $scope.cwd = cwd;
    $scope.goTo = function (dst) { $rootScope.$broadcast('CHANGE_DIRECTORY', dst); };
}

controller.$inject = ['$scope', '$rootScope', 'cwd'];


export default controller;
