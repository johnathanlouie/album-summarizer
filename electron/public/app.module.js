'use strict';


angular.module('app', [
    'components',
    'services',
    'views',
]).controller('appCtrl', function ($scope, ScreenView) {
    $scope.screenView = ScreenView;
});
