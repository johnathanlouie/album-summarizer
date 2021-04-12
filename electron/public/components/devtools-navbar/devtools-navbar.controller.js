function controllerFn($scope, $location) {
    $scope.isCheckRate = function () { return $location.path() === '/devtools/check-rate'; };
    $scope.isHist = function () { return $location.path() === '/devtools/histogram'; };
    $scope.isRate = function () { return $location.path() === '/devtools/label-data'; };
}

controllerFn.$inject = ['$scope', '$location'];


export default controllerFn;
