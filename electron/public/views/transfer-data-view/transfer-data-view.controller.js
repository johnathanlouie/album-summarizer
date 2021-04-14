const fs = require('fs');
const os = require('os');
const process = require('process');
const path = require('path');
const parseCsv = require('csv-parse/lib/sync');
const stringifyCsv = require('csv-stringify/lib/sync');


function controllerFn($scope, $rootScope, mongoDb) {

    $scope.load = function () {
        $scope.data = null;
        if ($scope.file1.length > 0) {
            try {
                $scope.data = parseCsv(fs.readFileSync($scope.file1[0].path), {
                    columns: ['image', 'rating', 'class', 'isLabeled', '_id'],
                    cast: function (value, context) {
                        switch (context.column) {
                            case 'rating':
                                return Number(value);
                            case 'isLabeled':
                                return Boolean(value);
                            default:
                                return value;
                        }
                    },
                });
            }
            catch (e) {
                console.error(e);
                $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: CSV', 'Loading or parsing error.');
            }
        }
    };

    $scope.upload = async function () {
        try {
            $rootScope.$broadcast('LOADING_MODAL_SHOW', 'MongoDB', 'Uploading...');
            await mongoDb.insertMany($scope.data, $scope.collectionPush);
            await getMongoCollections();
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
        $scope.data = null;
        try {
            $rootScope.$broadcast('LOADING_MODAL_SHOW', 'MongoDB', 'Downloading...');
            $scope.data = await mongoDb.getAll($scope.collectionPull);
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
        fs.writeFileSync($scope.exportPath, stringifyCsv($scope.data, {
            columns: [
                { key: 'image' },
                { key: 'rating' },
                { key: 'class' },
                { key: 'isLabeled' },
                { key: '_id' },
            ],
        }));
    };

    $scope.getImages = function () {
        $scope.data = null;
        $scope.data = fs.readdirSync($scope.newData.filepath, { withFileTypes: true }).
            filter(f => f.isFile() && ['.jpg', '.jpeg'].includes(path.extname(f.name).toLowerCase())).
            map(f => {
                return {
                    image: path.join($scope.newData.filepath, f.name),
                    isLabeled: false,
                };
            });
    };

    $scope.removeIds = function () {
        for (let i of $scope.data) {
            delete i._id;
        }
    };

    async function getMongoCollections() {
        $scope.collections = await mongoDb.collections();
        if ($scope.collections.length > 0) {
            $scope.collectionPull = $scope.collections[0];
        }
        $scope.$apply();
    }

    $scope.newData = {
        filepath: path.join(os.homedir(), 'Pictures'),
        recursive: true,
    };

    $scope.exportPath = path.join(process.cwd(), 'export.csv');
    getMongoCollections();
    $scope.data = null;

}

controllerFn.$inject = ['$scope', '$rootScope', 'mongoDb'];


export default controllerFn;
