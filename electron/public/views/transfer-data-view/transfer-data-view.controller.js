const fs = require('fs');
const os = require('os');
const process = require('process');
const path = require('path');
const parseCsv = require('csv-parse/lib/sync');
const stringifyCsv = require('csv-stringify/lib/sync');
const angular = require('angular');
import MongoDbService from '../../services/mongodb.service.js';


class Controller {

    /** @type {angular.IScope} */
    #$scope;

    /** @type {angular.IRootScopeService} */
    #$rootScope;

    /** @type {MongoDbService} */
    #mongoDb;

    static $inject = ['$scope', '$rootScope', 'mongoDb'];
    constructor($scope, $rootScope, mongoDb) {
        this.#$scope = $scope;
        this.#$rootScope = $rootScope;
        this.#mongoDb = mongoDb;
        $scope.load = () => this.load();
        $scope.upload = () => this.upload();
        $scope.download = () => this.download();
        $scope.export = () => this.export();
        $scope.getImages = () => this.getImages();
        $scope.removeIds = () => this.removeIds();
        $scope.newData = {
            filepath: path.join(os.homedir(), 'Pictures'),
            recursive: true,
        };
        $scope.exportPath = path.join(process.cwd(), 'export.csv');
        $scope.data = null;
        this.getMongoCollections();
    }

    load() {
        this.#$scope.data = null;
        if (this.#$scope.file1.length > 0) {
            try {
                this.#$scope.data = parseCsv(fs.readFileSync(this.#$scope.file1[0].path), {
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
                this.#$rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: CSV', 'Loading or parsing error.');
            }
        }
    }

    async upload() {
        try {
            this.#$rootScope.$broadcast('LOADING_MODAL_SHOW', 'MongoDB', 'Uploading...');
            await this.#mongoDb.insertMany(this.#$scope.data, this.#$scope.collectionPush);
            await this.getMongoCollections();
            this.#$rootScope.$broadcast('LOADING_MODAL_HIDE');
        }
        catch (e) {
            console.error(e);
            this.#$rootScope.$broadcast('LOADING_MODAL_HIDE');
            this.#$rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: MongoDB Query', 'Something happened while uploading to MongoDB.');
        }
        this.#$scope.$apply();
    }

    async download() {
        this.#$scope.data = null;
        try {
            this.#$rootScope.$broadcast('LOADING_MODAL_SHOW', 'MongoDB', 'Downloading...');
            this.#$scope.data = await this.#mongoDb.getAll(this.#$scope.collectionPull);
            this.#$rootScope.$broadcast('LOADING_MODAL_HIDE');
        }
        catch (e) {
            console.error(e);
            this.#$rootScope.$broadcast('LOADING_MODAL_HIDE');
            this.#$rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: MongoDB Query', 'Something happened while downloading from MongoDB.');
        }
        this.#$scope.$apply();
    }

    export() {
        fs.writeFileSync(this.#$scope.exportPath, stringifyCsv(this.#$scope.data, {
            columns: [
                { key: 'image' },
                { key: 'rating' },
                { key: 'class' },
                { key: 'isLabeled' },
                { key: '_id' },
            ],
        }));
    }

    getImages() {
        this.#$scope.data = null;
        this.#$scope.data = fs.readdirSync(this.#$scope.newData.filepath, { withFileTypes: true }).
            filter(f => f.isFile() && ['.jpg', '.jpeg'].includes(path.extname(f.name).toLowerCase())).
            map(f => {
                return {
                    image: path.join(this.#$scope.newData.filepath, f.name),
                    isLabeled: false,
                };
            });
    }

    removeIds() {
        for (let i of this.#$scope.data) {
            delete i._id;
        }
    }

    async getMongoCollections() {
        this.#$scope.collections = await this.#mongoDb.collections();
        if (this.#$scope.collections.length > 0) {
            this.#$scope.collectionPull = this.#$scope.collections[0];
        }
        this.#$scope.$apply();
    }

}


export default Controller;
