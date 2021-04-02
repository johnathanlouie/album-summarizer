'use strict';


angular.module('components.devtoolsNavbar').component('devtoolsNavbar', {
    templateUrl: 'components/devtools-navbar/devtools-navbar.template.html',
    controller: ['$scope', '$location', function ($scope, $location) {
        $scope.isCheckRate = function () { return $location.path() === '/devtools/checkrate'; };
        $scope.isHist = function () { return $location.path() === '/devtools/hist'; };
        $scope.isRate = function () { return $location.path() === '/devtools/rate'; };
        $scope.isPreview = function () { return $location.path() === '/devtools/preview'; };
        $scope.isSiftSimilarity = function () { return $location.path() === '/devtools/siftsimilarity'; };
    }],
});
