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

function viewCtrl($scope, $http) {
    const homeDir = path.resolve(os.homedir(), 'Pictures');
    $scope.dir = DirEntArrayWrapper.fromUnwrapped([], homeDir);
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
                    history.push($scope.dir.path);
                }
                asdf = $scope.dir = DirEntArrayWrapper.fromUnwrapped(dirEnts, cwd);
                $scope.$apply();
            }
        });
    }

    $scope.submit = function () {
        $scope.cwd = path.normalize($scope.cwd);
        if ($scope.cwd === $scope.dir.path) {
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
        $scope.cwd = $scope.dir.path;
        go(false);
    };

    $scope.goParent = function () {
        $scope.cwd = path.dirname($scope.dir.path);
        $scope.submit();
    };

    $scope.goBack = function () {
        $scope.cwd = history.pop();
        future.push($scope.dir.path);
        go(false);
    };

    $scope.goForward = function () {
        $scope.cwd = future.pop();
        history.push($scope.dir.path);
        go(false);
    };

    $scope.isHistoryEmpty = function () {
        return history.length === 0;
    };

    $scope.isFutureEmpty = function () {
        return future.length === 0;
    };

    $scope.goTo = function (path) {
        $scope.cwd = path;
        $scope.submit();
    };

    $scope.view = 'thumbnails';
    $scope.cwd = homeDir;
    $scope.submit();
}

var app = angular.module('app', []);
app.controller('viewCtrl', viewCtrl);