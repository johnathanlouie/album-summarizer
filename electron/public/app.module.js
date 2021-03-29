const path = require('path');
const os = require('os');
const fsp = require('./lib/fsp');
const Directory = require('./lib/directory');

function viewCtrl($scope, $http, History) {
    const homeDir = os.homedir();
    $scope.cwd = Directory.factory(homeDir);

    async function goTo(dst) {
        $scope.filterText = '';
        try {
            var dirEnts = await fsp.readdir(dst, { withFileTypes: true });
            $scope.cwd = Directory.factory(dst, dirEnts, true);
            $scope.$apply();
        }
        catch (err) {
            $scope.cwd = Directory.factory(dst);
            $scope.$apply();
        }
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
     * Interface for the cached organized view for the current directory.
     */
    const organizedDirFile = {
        url: function () {
            return path.normalize(`public/data/${encodeURIComponent($scope.cwd.path)}.json`);
        },
        mkdir: async function () {
            try {
                return await fsp.access('public/data');
            }
            catch (err) {
                return await fsp.mkdir('public/data');
            }
        },
        read: async function () {
            await this.mkdir();
            return await fsp.readFile(this.url());
        },
        /**
         * @param {string} json Organization data
         */
        write: async function (json) {
            await this.mkdir();
            return await fsp.writeFile(this.url(), json);
        },
        delete: async function () {
            await this.mkdir();
            try {
                await fsp.unlink(this.url());
                return true;
            }
            catch (err) {
                return false;
            }
        },
        exists: async function () {
            try {
                await fsp.access(this.url());
                return true;
            }
            catch (err) {
                return false;
            }
        },
    };

    /**
     * 
     * @param {string} dir 
     */
    async function queryServer(dir) {
        var response = await $http.post('http://localhost:8080/run', { url: dir });
        if (response.data.status === 0) {
            return response.data.data;
        }
        else if (response.data.status === 2) {
            throw new Error('Architecture/dataset mismatch');
        }
        else {
            throw new Error('Unknown server error');
        }
    }

    /**
     * 
     * @param {boolean} refresh
     */
    async function organize(refresh) {
        try {
            var data;
            $scope.cwd.unorganize();
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
