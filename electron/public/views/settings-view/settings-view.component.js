'use strict';


angular.module('views.settingsView').component('settingsView', {
    templateUrl: 'views/settings-view/settings-view.template.html',
    controller: ['$scope', 'MongoDB', function ($scope, MongoDB) {

        async function getSettings() {
            $scope.settings = await MongoDB.settings();
            $scope.$apply();
        }

        $scope.update = async function () { await $scope.settings.save(); }

        getSettings();
    }],
});
