const fs = require('fs');
const path = require('path');
const util = require('util');
const os = require('os');
const childProcess = require('child_process');
const { ipcRenderer } = require('electron');

const fsp = {};
fsp.writeFile = util.promisify(fs.writeFile);
fsp.readFile = util.promisify(fs.readFile);

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

function viewCtrl($scope, $interval, $http) {
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

    $scope.loadingOverlay = {
        _isLoading: false,
        _stopwatch: {
            _time: 0,
            _interval: null,
            get time() { return this._time; },
            reset() { this._time = 0; },

            stop() {
                if (this._interval !== null) {
                    $interval.cancel(this._interval);
                    this._interval = null;
                }
            },

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
            $scope.$apply();
        }
    };

    function goTo(dst) {
        $scope.filterText = '';
        fs.readdir(dst, { withFileTypes: true }, (err, dirEnts) => {
            if (err) {
                $scope.cwd = Directory_.factory(dst);
                $scope.$apply();
            } else {
                $scope.cwd = Directory_.factory(dst, dirEnts, true);
                $scope.$apply();
            }
        });
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

    async function reorganize() {
        $scope.cwd.unorganize();
        var data = {
            model: {
                architecture: 'smi13',
                dataset: 'ccr',
                loss: 'rmse',
                optimizer: 'sgd1',
                metrics: 'acc',
                epochs: 0,
                patience: 3,
                split: 0,
            },
            cluster: 'sift',
            url: $scope.cwd.path,
        };
        try {
            var response = await $http.post('http://localhost:8080/run', data);
            if (response.data.status === 0) {
                dataFile = path.normalize(`public/data/${encodeURIComponent($scope.cwd.path)}.json`);
                var json = JSON.stringify(response.data.data);
                await fsp.writeFile(dataFile, json);
                organize(true);
            }
            else if (response.data.status === 2) {
                // TODO architecture/dataset mismatch
            }
            else {
                // TODO some other error
            }
        }
        catch (e) {
            // TODO what if internal server error
        }
    }

    /** @deprecated */
    function reorganize2() {
        $scope.cwd.unorganize();
        var command = `conda run -n album pythonw "${path.normalize('python/run.py')}" "${$scope.cwd.path}"`;
        var options = { cwd: '..', windowsHide: true };
        var proc = childProcess.exec(command, options);
        ipcRenderer.send('add-pid', proc.pid);

        proc.on('exit', (code, signal) => {
            ipcRenderer.send('remove-pid', proc.pid);
            if (code !== 0) {
                // TODO error handling
                console.error('Organize subprocess error');
            } else {
                organize(true);
            }
        });
    }

    async function organize(pythoned) {
        dataFile = path.normalize(`public/data/${encodeURIComponent($scope.cwd.path)}.json`);
        try {
            var data = await fsp.readFile(dataFile);
            $scope.cwd.organize(JSON.parse(data));
            $scope.loadingOverlay.hide();
        }
        catch (err) {
            if (pythoned) {
                console.error('Cannot read organized data file');
                $scope.isOrganizeToggled = false;
                $scope.loadingOverlay.hide();
            } else {
                reorganize();
            }
        }
    }

    $scope.toggleOrganize = function () {
        if ($scope.isOrganizeToggled) {
            $scope.loadingOverlay.show();
            organize(false);
        }
    };

    $scope.reorganize = function () {
        $scope.loadingOverlay.show();
        reorganize();
    }

    $scope.isOrganizeToggled = false;
    $scope.screen = 'main';
    $scope.focusedImage = 'public/image-placeholder.png';
    $scope.view = 'thumbnails';
    $scope.goHome();
}

angular.module('app', ['core']).controller('viewCtrl', viewCtrl);