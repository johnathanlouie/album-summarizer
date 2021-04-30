import RouteManager from '../../lib/routes.js';


function controllerFn($scope, $location) {
    $scope.routes = function () { return RouteManager.menu2() };
    $scope.isActive = function (route) { return $location.path() === route; };
}

controllerFn.$inject = ['$scope', '$location'];


export default controllerFn;
