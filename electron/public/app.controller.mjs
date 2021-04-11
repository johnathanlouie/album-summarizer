function controllerFn($scope, screenView) {
    $scope.screenView = screenView;
}

controllerFn.$inject = ['$scope', 'screenView'];


export default controllerFn;
