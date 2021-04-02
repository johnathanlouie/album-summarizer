'use strict';


angular.module('app', [
    'ngRoute',
    'components',
    'services',
    'views',
]).controller('appCtrl', function ($scope, ScreenView) {
    $scope.screenView = ScreenView;
});
