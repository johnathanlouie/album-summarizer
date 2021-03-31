'use strict';

const path = require('path');


angular.module('app', [
    'core',
    'components',
    'services',
]).controller('viewCtrl', function ($scope, History, Cwd, ScreenView, FocusImage) {
    $scope.cwd = Cwd;
    $scope.screenView = ScreenView;
    $scope.focusImage = FocusImage;

    async function goTo(dst) {
        $scope.address = dst;
        $scope.filterText = '';
        await Cwd.cd(dst);
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

    $scope.unfocusImage = function () { ScreenView.screen = 'MAIN'; };

    /**
     * 
     * @param {boolean} refresh
     */
    async function organize(refresh) {
        try {
            $scope.$broadcast('LOADING_MODAL_SHOW');
            if (refresh) { await Cwd.reorganize(); }
            else { await Cwd.organize(); }
            $scope.$broadcast('LOADING_MODAL_HIDE');
        }
        catch (err) {
            console.error(err);
            $scope.isOrganizeToggled = false;
            $scope.$broadcast('LOADING_MODAL_HIDE');
            $scope.$broadcast('ERROR_MODAL_SHOW');
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

    $scope.reorganize = function () {
        organize(true);
    }

    $scope.isOrganizeToggled = false;
    $scope.goHome();
});
