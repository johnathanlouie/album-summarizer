const angular = require('angular');
const ngRoute = require('angular-route');


angular.module('app', [
    'ngRoute',
    'components',
    'services',
    'views',
]).controller('appCtrl', function ($scope, screenView) {
    $scope.screenView = screenView;
});
