const path = require('path');
const os = require('os');
const fsp = require('./fsp');

class File_ {
    #path;
    #isFile;
    #isDirectory;

    constructor(dirent, dirname) {
        this.#path = path.join(dirname, dirent.name);
        this.#isFile = dirent.isFile();
        this.#isDirectory = dirent.isDirectory();
    }

    get path() {
        return this.#path;
    }

    get extension() {
        return path.extname(this.#path);
    }

    isImage() {
        const validExt = ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.apng', '.avif'];
        var ext = this.extension.toLowerCase();
        return this.isFile() && validExt.some(e => e === ext);
    }

    isFile() {
        return this.#isFile;
    }

    isDirectory() {
        return this.#isDirectory;
    }
}

class Directory_ extends Array {
    #path = '';
    #directories = null;
    #files = null;
    #images = null;
    #exists = false;
    #organization = null;

    static factory(path, direntArray = [], exists = false) {
        var instance = Directory_.from(direntArray.map(e => new File_(e, path)));
        instance.#path = path;
        instance.#exists = exists;
        return instance;
    }

    get exists() {
        return this.#exists;
    }

    get path() {
        return this.#path;
    }

    get directories() {
        if (this.#directories === null) {
            this.#directories = this.filter(e => e.isDirectory());
        }
        return this.#directories;
    }

    get files() {
        if (this.#files === null) {
            this.#files = this.filter(e => e.isFile());
        }
        return this.#files;
    }

    get images() {
        if (this.#images === null) {
            this.#images = this.files.filter(e => e.isImage());
        }
        return this.#images;
    }

    get organization() {
        return this.#organization;
    }

    get isOrganized() {
        return this.#organization !== null;
    }

    organize(val) {
        this.#organization = val;
    }

    unorganize() {
        this.#organization = null;
    }

    hasDirectories() {
        return this.directories.length > 0;
    }

    hasImages() {
        return this.images.length > 0;
    }
}

function viewCtrl($scope, $http) {
    const homeDir = os.homedir();
    $scope.cwd = Directory_.factory(homeDir);

    const history = {
        _history: [],
        _future: [],
        _current: undefined,
        get hasBack() { return this._history.length === 0; },
        get hasNext() { return this._future.length === 0; },
        get current() { return this._current; },

        push(dir) {
            dir = path.normalize(dir);
            if (this._current !== dir) {
                this._future = [];
                if (this._current !== undefined) { this._history.push(this._current); }
                this._current = dir;
            }
            return this._current;
        },

        goBack() {
            this._future.push(this._current);
            this._current = this._history.pop();
            return this._current;
        },

        goForward() {
            this._history.push(this._current);
            this._current = this._future.pop();
            return this._current;
        }
    };

    async function goTo(dst) {
        $scope.filterText = '';
        try {
            var dirEnts = await fsp.readdir(dst, { withFileTypes: true });
            $scope.cwd = Directory_.factory(dst, dirEnts, true);
            $scope.$apply();
        }
        catch (err) {
            $scope.cwd = Directory_.factory(dst);
            $scope.$apply();
        }
    }

    $scope.goTo = function (dst = $scope.address) {
        goTo($scope.address = history.push(dst));
    };

    $scope.goHome = function () {
        goTo($scope.address = history.push(homeDir));
    };

    $scope.refresh = function () {
        goTo($scope.address = history.current);
    };

    $scope.goParent = function () {
        goTo($scope.address = history.push(path.dirname(history.current)));
    };

    $scope.goBack = function () {
        goTo($scope.address = history.goBack());
    };

    $scope.goForward = function () {
        goTo($scope.address = history.goForward());
    };

    $scope.hasBack = function () {
        return history.hasBack;
    };

    $scope.hasNext = function () {
        return history.hasNext;
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

angular.module('app', ['core', 'components']).controller('viewCtrl', viewCtrl);
