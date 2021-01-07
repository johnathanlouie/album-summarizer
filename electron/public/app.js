class DirEntWrapper {

    constructor(o, cwd) {
        this.o = o;
        this.cwd = cwd;
    }

    get name() {
        return this.o.name;
    }

    get fileUri() {
        return fileUrl(path.resolve(this.cwd, this.o.name));
    }

    isImage() {
        const validExt = ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.apng', '.avif'];
        var ext = path.extname(this.o.name).toLowerCase();
        return validExt.some(e => e === ext);
    }

    isFile() {
        return this.o.isFile();
    }

    isDirectory() {
        return this.o.isDirectory();
    }

}

class DirEntArrayWrapper {

    constructor(o, cwd) {
        this.o = o;
        this.cwd = cwd;
    }

    static fromUnwrapped(o, cwd) {
        return new DirEntArrayWrapper(o.map(e => new DirEntWrapper(e, cwd)), cwd);
    }

    get directories() {
        return new DirEntArrayWrapper(this.o.filter(e => e.isDirectory()));
    }

    get files() {
        return new DirEntArrayWrapper(this.o.filter(e => e.isFile()));
    }

    get images() {
        return new DirEntArrayWrapper(this.o.filter(e => e.isImage()));
    }

    get names() {
        return this.o.map(e => e.name);
    }

    get fileUris() {
        return this.o.map(e => e.fileUri);
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
        fs.readdir(cwd, {withFileTypes: true}, (err, dirEnts) => {
            if (err) {
                $scope.isCwdMissing = true;
                $scope.$apply();
            } else {
                if (makeHistory) {
                    future = [];
                    history.push(dir.cwd);
                }
                dir = DirEntArrayWrapper.fromUnwrapped(dirEnts, cwd);
                $scope.photos = dir.images.fileUris;
                $scope.$apply();
            }
        });
    }

    $scope.submit = function () {
        $scope.cwd = path.normalize($scope.cwd);
        if ($scope.cwd === dir.cwd) {
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
        $scope.cwd = dir.cwd;
        go(false);
    };

    $scope.goParent = function () {
        $scope.cwd = path.dirname(dir.cwd);
        $scope.submit();
    };

    $scope.goBack = function () {
        $scope.cwd = history.pop();
        future.push(dir.cwd);
        go(false);
    };

    $scope.goForward = function () {
        $scope.cwd = future.pop();
        history.push(dir.cwd);
        go(false);
    };

    $scope.isHistoryEmpty = function () {
        return history.length === 0;
    };

    $scope.isFutureEmpty = function () {
        return future.length === 0;
    };

    $scope.cwd = homeDir;
    $scope.submit();
}

var app = angular.module('app', []);
app.controller('viewCtrl', viewCtrl);