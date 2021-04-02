'use strict';


angular.module('app').config(['$routeProvider', function ($routeProvider) {
    $routeProvider.
        when('/organizer', { template: '<organizer-view></organizer-view>' }).
        when('/menu', { template: '<menu-view></menu-view>' }).
        when('/devtools/preview', { template: '<preview-view></preview-view>' }).
        otherwise('/organizer');
}]);
