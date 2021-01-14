const fs = require('fs');
const fileUrl = require('file-url');
const path = require('path');
const os = require('os');

class DirEntWrapper {
    #o;
    #path;

    constructor(o, cwd) {
        this.#o = o;
        this.#path = cwd;
    }

    get name() {
        return this.#o.name;
    }

    get absolutePath() {
        return path.resolve(this.#path, this.#o.name);
    }

    get fileUri() {
        return fileUrl(this.absolutePath);
    }

    get extension() {
        return path.extname(this.#o.name).toLowerCase();
    }

    isImage() {
        const validExt = ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.apng', '.avif'];
        var ext = path.extname(this.#o.name).toLowerCase();
        return validExt.some(e => e === ext);
    }

    isFile() {
        return this.#o.isFile();
    }

    isDirectory() {
        return this.#o.isDirectory();
    }

}

class DirEntArrayWrapper extends Array {
    #path;
    #directories = null;
    #files = null;
    #images = null;

    static fromUnwrapped(o, path) {
        var x = DirEntArrayWrapper.from(o.map(e => new DirEntWrapper(e, path)));
        x.#path = path;
        return x;
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

    get names() {
        return this.map(e => e.name);
    }

    get fileUris() {
        return this.map(e => e.fileUri);
    }

    hasDirectories() {
        return this.directories.length > 0;
    }

    hasImages() {
        return this.images.length > 0;
    }

}

function viewCtrl($scope, $interval) {
    const homeDir = path.resolve(os.homedir(), 'Pictures');
    $scope.dir = DirEntArrayWrapper.fromUnwrapped([], homeDir);

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

    $scope.loadingOverlay = {
        _isLoading: false,
        _stopwatch: {
            _time: 0,
            _interval: null,
            get time() { return this._time; },
            reset() { this._time = 0; },
            stop() { $interval.cancel(this._interval); },
            start() { this._interval = $interval(() => { this._time += .01; }, 10); },

            restart() {
                this.stop();
                this.reset();
                this.start();
            }
        },

        get isLoading() { return this._isLoading; },

        get timeElapsed() { return this._stopwatch.time; },

        show() {
            this._stopwatch.restart();
            this._isLoading = true;
        },

        hide() {
            this._stopwatch.stop();
            this._isLoading = false;
        }
    }

    function goTo(dst) {
        $scope.isCwdMissing = false;
        fs.readdir(dst, { withFileTypes: true }, (err, dirEnts) => {
            if (err) {
                $scope.isCwdMissing = true;
                $scope.$apply();
            } else {
                $scope.dir = DirEntArrayWrapper.fromUnwrapped(dirEnts, dst);
                $scope.$apply();
            }
        });
    }

    $scope.goTo = function (dst = $scope.cwd) {
        goTo($scope.cwd = history.push(dst));
    };

    $scope.goHome = function () {
        goTo($scope.cwd = history.push(homeDir));
    };

    $scope.refresh = function () {
        goTo($scope.cwd = history.current);
    };

    $scope.goParent = function () {
        goTo($scope.cwd = history.push(path.dirname(history.current)));
    };

    $scope.goBack = function () {
        goTo($scope.cwd = history.goBack());
    };

    $scope.goForward = function () {
        goTo($scope.cwd = history.goForward());
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
    }

    $scope.unfocusImage = function () {
        $scope.screen = 'main';
    }

    $scope.screen = 'main';
    $scope.focusedImage = 'image-placeholder.png';
    $scope.view = 'thumbnails';
    $scope.goHome();
}

var app = angular.module('app', []);
app.controller('viewCtrl', viewCtrl);