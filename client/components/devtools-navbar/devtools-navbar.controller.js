import RouteManager from '../../lib/routes.js';


function controllerFn($scope, $location, $window) {
    $scope.routes = function () { return RouteManager.menu2() };
    $scope.isActive = function (route) { return $location.path() === route; };
    $scope.reload = function () {
        $window.location = `index.html?reload=${(new Date()).getTime()}`;
    };
}

controllerFn.$inject = ['$scope', '$location', '$window'];


export default controllerFn;
