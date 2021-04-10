'use strict';


angular.module('views.settingsView').component('settingsView', {
    templateUrl: 'views/settings-view/settings-view.template.html',
    controller: ['$scope', '$rootScope', 'MongoDB', function ($scope, $rootScope, MongoDB) {

        async function getSettings() {
            try {
                $scope.settings = await MongoDB.settings();
            }
            catch (e) { $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error while loading MongoDB settings file.', 'Error: MongoDB'); }
            $scope.$apply();
        }

        $scope.update = async function () {
            try {
                await $scope.settings.save();
                $('#toast1').toast('show');
                $scope.$apply();
            }
            catch (e) { $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Cannot write to MongoDB settings file.', 'Error: MongoDB'); }
        }

        getSettings();

    }],
});
