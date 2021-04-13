function controllerFn($scope, $location) {
    $scope.isCheckRate = function () { return $location.path() === '/devtools/check-rate'; };
    $scope.isHist = function () { return $location.path() === '/devtools/histogram'; };
    $scope.isRate = function () { return $location.path() === '/devtools/label-data'; };
    $scope.isTransfer = function () { return $location.path() === '/devtools/data-transfer'; };
}

controllerFn.$inject = ['$scope', '$location'];


export default controllerFn;
