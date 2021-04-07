'use strict';

const path = require('path');


function OrganizerViewCtrl($scope, $rootScope, History, Cwd, ScreenView, FocusImage) {
    $scope.cwd = Cwd;
    $scope.screenView = ScreenView;
    $scope.focusImage = FocusImage;

    async function goTo(dst) {
        $rootScope.$broadcast('LOADING_MODAL_SHOW');
        $scope.address = dst;
        $scope.filterText = '';
        await Cwd.cd(dst);
        $rootScope.$broadcast('LOADING_MODAL_HIDE');
        $scope.$apply();
    }

    $scope.goTo = function (dst = $scope.address) { goTo(History.push(dst)); };

    $scope.goHome = function () { goTo(History.push(Cwd.home)); };

    $scope.refresh = function () { goTo(History.current); };

    $scope.goParent = function () { goTo(History.push(path.dirname(History.current))); };

    $scope.goBack = function () { goTo(History.goBack()); };

    $scope.goForward = function () { goTo(History.goForward()); };

    $scope.hasBack = function () { return History.hasBack; };

    $scope.hasNext = function () { return History.hasNext; };

    $scope.focusOnImage = function (url) {
        FocusImage.image = url;
        ScreenView.screen = 'IMAGE_VIEWER';
    };

    /**
     * 
     * @param {boolean} refresh
     */
    async function organize(refresh) {
        try {
            $rootScope.$broadcast('LOADING_MODAL_SHOW');
            if (refresh) { await Cwd.reorganize(); }
            else { await Cwd.organize(); }
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
        }
        catch (err) {
            console.error(err);
            $scope.isOrganizeToggled = false;
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
            $rootScope.$broadcast('ERROR_MODAL_SHOW');
        }
        finally {
            $scope.$apply();
        }
    }

    $scope.toggleOrganize = function () {
        // If user switches to organized view
        if ($scope.isOrganizeToggled) {
            organize(false);
        }
    };

    $scope.reorganize = function () { organize(true); };

    $rootScope.$on('CHANGE_DIRECTORY', function (event, dst) {
        $scope.goTo(dst);
    });

    $scope.isOrganizeToggled = false;
    $scope.goHome();
}

angular.module('views.organizerView').component('organizerView', {
    templateUrl: 'views/organizer-view/organizer-view.template.html',
    controller: ['$scope', '$rootScope', 'History', 'Cwd', 'ScreenView', 'FocusImage', OrganizerViewCtrl],
});
