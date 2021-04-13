const path = require('path');


function controllerFn($scope, $rootScope, history, cwd, screenView, focusImage) {
    $scope.cwd = cwd;
    $scope.screenView = screenView;
    $scope.focusImage = focusImage;

    async function goTo(dst) {
        $rootScope.$broadcast('LOADING_MODAL_SHOW', 'Directory Change', 'Loading...');
        $scope.address = dst;
        $scope.filterText = '';
        await cwd.cd(dst);
        $rootScope.$broadcast('LOADING_MODAL_HIDE');
        $scope.$apply();
    }

    $scope.goTo = function (dst = $scope.address) { goTo(history.push(dst)); };

    $scope.goHome = function () { goTo(history.push(cwd.home)); };

    $scope.refresh = function () { goTo(history.current); };

    $scope.goParent = function () { goTo(history.push(path.dirname(history.current))); };

    $scope.goBack = function () { goTo(history.goBack()); };

    $scope.goForward = function () { goTo(history.goForward()); };

    $scope.hasBack = function () { return history.hasBack; };

    $scope.hasNext = function () { return history.hasNext; };

    $scope.focusOnImage = function (url) {
        focusImage.image = url;
        screenView.screen = 'IMAGE_VIEWER';
    };

    /**
     * 
     * @param {boolean} refresh
     */
    async function organize(refresh) {
        try {
            $rootScope.$broadcast('LOADING_MODAL_SHOW', 'Smart Organizer', 'Organizing...');
            if (refresh) { await cwd.reorganize(); }
            else { await cwd.organize(); }
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
        }
        catch (err) {
            console.error(err);
            $scope.isOrganizeToggled = false;
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
            $rootScope.$broadcast('ERROR_MODAL_SHOW', err, 'Error: Smart Organizer', 'Failed to organize.');
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

    $scope.$on('CHANGE_DIRECTORY', function (event, dst) {
        $scope.goTo(dst);
    });

    $scope.isOrganizeToggled = false;
    $scope.goHome();
}

controllerFn.$inject = ['$scope', '$rootScope', 'history', 'cwd', 'screenView', 'focusImage'];


export default controllerFn;
