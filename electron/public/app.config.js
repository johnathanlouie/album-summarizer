'use strict';


angular.module('app').config(['$routeProvider', function ($routeProvider) {
    $routeProvider.
        when('/organizer', { template: '<organizer-view></organizer-view>' }).
        otherwise('/organizer');
}]);
