const fs = require('fs');
const process = require('process');
const path = require('path');
const parseCsv = require('csv-parse/lib/sync');
const stringifyCsv = require('csv-stringify/lib/sync');
const angular = require('angular');


function controllerFn($scope, $rootScope, mongoDb) {

    let DATA;

    $scope.load = function () {
        DATA = null;
        $scope.data = null;
        if ($scope.file1.length > 0) {
            DATA = parseCsv(fs.readFileSync($scope.file1[0].path), {
                columns: ['image', 'rating', 'class', 'isLabeled', '_id'],
                cast: function (value, context) {
                    switch (context.column) {
                        case 'rating':
                        case '_id':
                            return Number(value);
                        case 'isLabeled':
                            return Boolean(value);
                        default:
                            return value;
                    }
                },
            });
            $scope.data = angular.copy(DATA);
        }
    };

    $scope.upload = async function () {
        try {
            $rootScope.$broadcast('LOADING_MODAL_SHOW', 'MongoDB', 'Uploading...');
            await mongoDb.insertMany(DATA, $scope.collection);
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
        }
        catch (e) {
            console.error(e);
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
            $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: MongoDB Query', 'Something happened while uploading to MongoDB.');
        }
        $scope.$apply();
    };

    $scope.download = async function () {
        DATA = null;
        $scope.data = null;
        try {
            $rootScope.$broadcast('LOADING_MODAL_SHOW', 'MongoDB', 'Downloading...');
            DATA = await mongoDb.getAll($scope.collection);
            $scope.data = angular.copy(DATA);
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
        }
        catch (e) {
            console.error(e);
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
            $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: MongoDB Query', 'Something happened while downloading from MongoDB.');
        }
        $scope.$apply();
    };

    $scope.export = function () {
        fs.writeFileSync($scope.exportPath, stringifyCsv(DATA, {
            columns: [
                { key: 'image' },
                { key: 'rating' },
                { key: 'class' },
                { key: 'isLabeled' },
                { key: '_id' },
            ],
        }));
    };

    $scope.exportPath = path.join(process.cwd(), 'export.csv');

}

controllerFn.$inject = ['$scope', '$rootScope', 'mongoDb'];


export default controllerFn;
