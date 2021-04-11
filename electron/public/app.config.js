const angular = require('angular');


angular.module('app').config(['$routeProvider', function ($routeProvider) {
    $routeProvider.
        when('/', { template: '<organizer-view></organizer-view>' }).
        when('/organizer', { template: '<organizer-view></organizer-view>' }).
        when('/menu', { template: '<menu-view></menu-view>' }).
        when('/devtools/check-rate', { template: '<check-rate-view></check-rate-view>' }).
        when('/devtools/histogram', { template: '<histogram-view></histogram-view>' }).
        when('/devtools/label-data', { template: '<label-data-view></label-data-view>' }).
        when('/devtools/preview', { template: '<preview-view></preview-view>' }).
        when('/devtools/sift-similarity', { template: '<sift-similarity-view></sift-similarity-view>' }).
        when('/settings', { template: '<settings-view></settings-view>' }).
        otherwise('/menu');
}]);
