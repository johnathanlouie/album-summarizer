const path = require('path');
const os = require('os');
const Directory = require('./lib/directory');
const OrganizedDirFile = require('./lib/organize');

function viewCtrl($scope, History, queryServer) {
    const homeDir = os.homedir();
    $scope.cwd = Directory.factory(homeDir);

    async function goTo(dst) {
        $scope.filterText = '';
        $scope.cwd = await Directory.factory(dst);
        $scope.$apply();
    }

    $scope.goTo = function (dst = $scope.address) {
        goTo($scope.address = History.push(dst));
    };

    $scope.goHome = function () {
        goTo($scope.address = History.push(homeDir));
    };

    $scope.refresh = function () {
        goTo($scope.address = History.current);
    };

    $scope.goParent = function () {
        goTo($scope.address = History.push(path.dirname(History.current)));
    };

    $scope.goBack = function () {
        goTo($scope.address = History.goBack());
    };

    $scope.goForward = function () {
        goTo($scope.address = History.goForward());
    };

    $scope.hasBack = function () {
        return History.hasBack;
    };

    $scope.hasNext = function () {
        return History.hasNext;
    };

    $scope.focusOnImage = function (url) {
        $scope.focusedImage = url;
        $scope.screen = 'imageViewer';
    };

    $scope.unfocusImage = function () {
        $scope.screen = 'main';
    };

    /**
     * 
     * @param {boolean} refresh
     */
    async function organize(refresh) {
        try {
            var data;
            $scope.cwd.unorganize();
            organizedDirFile = new OrganizedDirFile($scope.cwd.path);
            if (refresh || !await organizedDirFile.exists()) {
                await organizedDirFile.delete();
                data = await queryServer($scope.cwd.path);
                var json = JSON.stringify(data);
                await organizedDirFile.write(json);
            }
            else {
                var json = await organizedDirFile.read();
                data = JSON.parse(json);
            }
            $scope.cwd.organize(data);
            $scope.$broadcast('LOADING_MODAL_HIDE');
            $scope.$apply();
        }
        catch (err) {
            console.error(err);
            $scope.isOrganizeToggled = false;
            $scope.$broadcast('LOADING_MODAL_HIDE');
            $scope.$broadcast('ERROR_MODAL_SHOW');
            $scope.$apply();
        }
    }

    $scope.toggleOrganize = function () {
        // If user switches to organized view
        if ($scope.isOrganizeToggled) {
            $scope.$broadcast('LOADING_MODAL_SHOW');
            organize(false);
        }
    };

    $scope.reorganize = function () {
        $scope.$broadcast('LOADING_MODAL_SHOW');
        organize(true);
    }

    $scope.isOrganizeToggled = false;
    $scope.screen = 'main';
    $scope.focusedImage = 'public/image-placeholder.png';
    $scope.view = 'thumbnails';
    $scope.goHome();
}

angular.module('app', [
    'core',
    'components',
    'services',
]).controller('viewCtrl', viewCtrl);
