'use strict';


angular.module('components.devtoolsNavbar').component('devtoolsNavbar', {
    templateUrl: 'components/devtools-navbar/devtools-navbar.template.html',
    controller: ['$scope', '$location', function ($scope, $location) {
        $scope.isCheckRate = function () { return $location.path() === '/devtools/check-rate'; };
        $scope.isHist = function () { return $location.path() === '/devtools/histogram'; };
        $scope.isRate = function () { return $location.path() === '/devtools/label-data'; };
        $scope.isPreview = function () { return $location.path() === '/devtools/preview'; };
        $scope.isSiftSimilarity = function () { return $location.path() === '/devtools/sift-similarity'; };
    }],
});
