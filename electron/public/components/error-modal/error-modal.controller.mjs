function controller($scope) {
    $scope.$on('ERROR_MODAL_SHOW', function (event, error, message, title) {
        $scope.error = error;
        $scope.message = message;
        $scope.title = title;
        $('#errorModal').modal();
    });
}

controller.$inject = ['$scope'];


export default controller;
