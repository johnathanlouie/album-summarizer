const fs = require('fs');
const os = require('os');
const mongodb = require('mongodb');
const _ = require('lodash');
const process = require('process');
const path = require('path');
const parseCsv = require('csv-parse/lib/sync');
const stringifyCsv = require('csv-stringify/lib/sync');
const angular = require('angular');
import MongoDbService from '../../services/mongodb.service.js';
import ModalService from '../../services/modal.service.js';
import UsersService from '../../services/users.service.js';
import FocusImageService from '../../services/focus-image.service.js';


class Datum {

    /** @type {mongodb.ObjectID} */
    _id;

    /** @type {string} */
    image;

    /** @type {number} */
    rating;

    /** @type {string} */
    class;

    /** @type {boolean} */
    isLabeled;

}


class DataContainer {

    /** @type {Array.<Datum>} */
    container = [];

    /** Removes the _id property of documents so they can be inserted into MongoDB */
    removeIds() {
        for (let i of this.container) {
            delete i._id;
        }
    }

    randomRating() {
        for (let doc of this.container) {
            doc.rating = Math.round(Math.random() * 2) + 1;
        }
    }

    randomClass() {
        for (let doc of this.container) {
            doc.class = _.sample([
                'environment',
                'people',
                'object',
                'hybrid',
                'animal',
                'food',
            ]);
        }
    }

    get isEmpty() { return this.container.length === 0; }

}


class Controller {

    #data = new DataContainer();

    static $inject = ['$scope', 'mongoDb', 'modal', 'users', 'focusImage'];
    $scope;
    mongoDb;
    modal;
    users;
    focusImage;

    /**
     * @param {angular.IScope} $scope 
     * @param {MongoDbService} mongoDb 
     * @param {ModalService} modal
     * @param {UsersService} users
     * @param {FocusImageService} focusImage
     */
    constructor($scope, mongoDb, modal, users, focusImage) {
        this.$scope = $scope;
        this.mongoDb = mongoDb;
        this.modal = modal;
        this.users = users;
        this.focusImage = focusImage;

        $scope.users = users;
        $scope.newData = {
            filepath: path.join(os.homedir(), 'Pictures'),
            recursive: true,
        };
        $scope.exportPath = path.join(process.cwd(), 'export.csv');
        $scope.data = this.#data;
        $scope.load = () => this.readCsv();
        $scope.upload = () => this.writeMongoDb();
        $scope.download = () => this.readMongoDb();
        $scope.export = () => this.writeCsv();
        $scope.getImages = () => this.getImages();
        $scope.removeIds = () => this.#data.removeIds();
        $scope.randomRating = () => this.#data.randomRating();
        $scope.randomClass = () => this.#data.randomClass();
        $scope.focusOnImage = function (url) {
            focusImage.image = url;
            modal.showPhoto();
        };

        this.getMongoCollections();
    }

    readCsv() {
        this.#data.container = [];
        if (this.$scope.file1.length > 0) {
            try {
                this.#data.container = parseCsv(fs.readFileSync(this.$scope.file1[0].path), {
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
                this.modal.showError(e, 'ERROR: CSV', 'Loading or parsing error');
            }
        }
    }

    writeMongoDb() {
        this.modal.showLoading('UPLOADING...');
        return this.mongoDb.insertMany(this.#data.container, this.$scope.collectionPush).then(
            () => this.users.load(true)
        ).then(() => {
            if (this.users.users.length > 0) {
                this.$scope.collectionPull = this.users.users[0];
            }
            else {
                this.$scope.collectionPull = null;
            }
            this.modal.hideLoading();
        }).catch(e => {
            console.error(e);
            this.modal.hideLoading();
            this.modal.showError(e, 'ERROR: MongoDB', 'Error while inserting many');
        });
    }

    readMongoDb() {
        this.#data.container = [];
        this.modal.showLoading('RETRIEVING...');
        return this.mongoDb.getAll(this.$scope.collectionPull).then(x => {
            this.#data.container = x;
            this.modal.hideLoading();
        }).catch(e => {
            console.error(e);
            this.modal.hideLoading();
            this.modal.showError(e, 'ERROR: MongoDB', 'Error while fetching collection');
        });
    }

    writeCsv() {
        fs.writeFileSync(this.$scope.exportPath, stringifyCsv(this.#data.container, {
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
        this.#data.container = [];
        this.#data.container = fs.readdirSync(this.$scope.newData.filepath, { withFileTypes: true }).
            filter(f => f.isFile() && ['.jpg', '.jpeg'].includes(path.extname(f.name).toLowerCase())).
            map(f => ({
                image: path.join(this.$scope.newData.filepath, f.name),
                isLabeled: false,
            }));
    }

    /**
     * Gets the names of all the collections in MongoDB so the user can select which collection to pull from
     */
    getMongoCollections() {
        this.modal.showLoading('RETRIEVING...');
        return this.users.load(false).then(() => {
            if (this.users.users.length > 0) {
                this.$scope.collectionPull = this.users.users[0];
            }
            else {
                this.$scope.collectionPull = null;
            }
            this.modal.hideLoading();
        }).catch(e => {
            console.error(e);
            this.modal.hideLoading();
            this.modal.showError(e, 'ERROR: MongoDB', 'Error while fetching users');
        });
    }

}


export default Controller;
