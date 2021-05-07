const fs = require('fs');
const os = require('os');
const process = require('process');
const path = require('path');
const parseCsv = require('csv-parse/lib/sync');
const stringifyCsv = require('csv-stringify/lib/sync');
const angular = require('angular');
import MongoDbService from '../../services/mongodb.service.js';
import ModalService from '../../services/modal.service.js';
import UsersService from '../../services/users.service.js';
import FocusImageService from '../../services/focus-image.service.js';


class Controller {

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
        this.$scope.newData = {
            filepath: path.join(os.homedir(), 'Pictures'),
            recursive: true,
        };
        this.$scope.exportPath = path.join(process.cwd(), 'export.csv');
        this.$scope.data = null;
        this.$scope.load = () => this.readCsv();
        this.$scope.upload = () => this.writeMongoDb();
        this.$scope.download = () => this.readMongoDb();
        this.$scope.export = () => this.writeCsv();
        this.$scope.getImages = () => this.getImages();
        this.$scope.removeIds = () => this.removeIds();
        $scope.focusOnImage = function (url) {
            focusImage.image = url;
            modal.showPhoto();
        };
        this.getMongoCollections();
    }

    readCsv() {
        this.$scope.data = null;
        if (this.$scope.file1.length > 0) {
            try {
                this.$scope.data = parseCsv(fs.readFileSync(this.$scope.file1[0].path), {
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
        return this.mongoDb.insertMany(this.$scope.data, this.$scope.collectionPush).then(
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
        this.$scope.data = null;
        this.modal.showLoading('RETRIEVING...');
        return this.mongoDb.getAll(this.$scope.collectionPull).then(x => {
            this.$scope.data = x;
            this.modal.hideLoading();
        }).catch(e => {
            console.error(e);
            this.modal.hideLoading();
            this.modal.showError(e, 'ERROR: MongoDB', 'Error while fetching collection');
        });
    }

    writeCsv() {
        fs.writeFileSync(this.$scope.exportPath, stringifyCsv(this.$scope.data, {
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
        this.$scope.data = null;
        this.$scope.data = fs.readdirSync(this.$scope.newData.filepath, { withFileTypes: true }).
            filter(f => f.isFile() && ['.jpg', '.jpeg'].includes(path.extname(f.name).toLowerCase())).
            map(f => ({
                image: path.join(this.$scope.newData.filepath, f.name),
                isLabeled: false,
            }));
    }

    /** Removes the _id property of documents so they can be inserted into MongoDB */
    removeIds() {
        for (let i of this.$scope.data) {
            delete i._id;
        }
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
