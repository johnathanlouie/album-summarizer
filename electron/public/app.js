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

    $scope.go = function () {
        $scope.isCwdMissing = false;
        $scope.photos = [];
        var cwd = $scope.cwd;
        fs.readdir(cwd, {withFileTypes: true}, (err, dirEnts) => {
            if (err) {
                $scope.isCwdMissing = true;
                $scope.$apply();
            } else {
                var dir = DirEntArrayWrapper.fromUnwrapped(dirEnts, cwd);
                var x = dir.images;
                var v = x.fileUris;
                $scope.photos = v;
                $scope.$apply();
            }
        });
    };

    $scope.goHome = function () {
        $scope.cwd = homeDir;
        $scope.go();
    };

    $scope.cwd = homeDir;
    $scope.go();
}

var app = angular.module('app', []);
app.controller('viewCtrl', viewCtrl);