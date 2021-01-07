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

class DirEntArrayWrapper {
    #o;
    #path;
    #directories = null;
    #files = null;
    #images = null;

    constructor(o, path) {
        this.#o = o;
        this.#path = path;
    }

    static fromUnwrapped(o, cwd) {
        return new DirEntArrayWrapper(o.map(e => new DirEntWrapper(e, cwd)), cwd);
    }

    get path() {
        return this.#path;
    }

    get directories() {
        if (this.#directories === null) {
            this.#directories = new DirEntArrayWrapper(this.#o.filter(e => e.isDirectory()))
        }
        return this.#directories;
    }

    get files() {
        if (this.#files === null) {
            this.#files = new DirEntArrayWrapper(this.#o.filter(e => e.isFile()))
        }
        return this.#files;
    }

    get images() {
        if (this.#images === null) {
            this.#images = new DirEntArrayWrapper(this.#o.filter(e => e.isImage()))
        }
        return this.#images;
    }

    get names() {
        return this.#o.map(e => e.name);
    }

    get fileUris() {
        return this.#o.map(e => e.fileUri);
    }

    hasDirectories() {
        return this.directories.#o.length > 0;
    }

    hasImages() {
        return this.images.#o.length > 0;
    }

}

function viewCtrl($scope, $http) {
    const homeDir = path.resolve(os.homedir(), 'Pictures');
    var dir = DirEntArrayWrapper.fromUnwrapped([], homeDir);
    var history = [];
    var future = [];

    function go(makeHistory) {
        $scope.isCwdMissing = false;
        $scope.photos = [];
        var cwd = $scope.cwd;
        fs.readdir(cwd, { withFileTypes: true }, (err, dirEnts) => {
            if (err) {
                $scope.isCwdMissing = true;
                $scope.$apply();
            } else {
                if (makeHistory) {
                    future = [];
                    history.push(dir.path);
                }
                dir = DirEntArrayWrapper.fromUnwrapped(dirEnts, cwd);
                $scope.photos = dir.images.fileUris;
                $scope.$apply();
            }
        });
    }

    $scope.submit = function () {
        $scope.cwd = path.normalize($scope.cwd);
        if ($scope.cwd === dir.path) {
            $scope.refresh();
        } else {
            go(true);
        }
    };

    $scope.goHome = function () {
        $scope.cwd = homeDir;
        $scope.submit();
    };

    $scope.refresh = function () {
        $scope.cwd = dir.path;
        go(false);
    };

    $scope.goParent = function () {
        $scope.cwd = path.dirname(dir.path);
        $scope.submit();
    };

    $scope.goBack = function () {
        $scope.cwd = history.pop();
        future.push(dir.path);
        go(false);
    };

    $scope.goForward = function () {
        $scope.cwd = future.pop();
        history.push(dir.path);
        go(false);
    };

    $scope.isHistoryEmpty = function () {
        return history.length === 0;
    };

    $scope.isFutureEmpty = function () {
        return future.length === 0;
    };

    $scope.hasDirectories = function () {
        return dir.hasDirectories();
    };

    $scope.hasImages = function () {
        return dir.hasImages();
    };

    $scope.cwd = homeDir;
    $scope.submit();
}

var app = angular.module('app', []);
app.controller('viewCtrl', viewCtrl);