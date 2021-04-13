const fs = require('fs');
const parse = require('csv-parse/lib/sync');
const angular = require('angular');


class DeepLearningData {

    _id;
    image;
    rating;
    class;
    isLabeled;

    constructor(_id, image, rating, class_, isLabeled) {
        this._id = Number(_id);
        this.image = image;
        this.rating = Number(rating);
        this.class = class_;
        this.isLabeled = Boolean(isLabeled);
    }

}

function controllerFn($scope, $rootScope, mongoDb) {

    let DATA;

    $scope.load = function () {
        if ($scope.file1.length > 0) {
            let csv = parse(fs.readFileSync($scope.file1[0].path));
            DATA = csv.map(row => new DeepLearningData(row[4], row[0], row[1], row[2], row[3]));
            $scope.data = angular.copy(DATA);
        }
    };

    $scope.upload = async function () {
        try {
            $rootScope.$broadcast('LOADING_MODAL_SHOW', 'MongoDB', 'Uploading...');
            await mongoDb.insertMany(DATA, $scope.db, $scope.collection);
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
        }
        catch (e) {
            console.error(e);
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
            $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: MongoDB Upload', 'Something happened while uploading to MongoDB.');
        }
        $scope.$apply();
    };

}

controllerFn.$inject = ['$scope', '$rootScope', 'mongoDb'];


export default controllerFn;
