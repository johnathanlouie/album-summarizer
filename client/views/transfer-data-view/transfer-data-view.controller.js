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


class Controller {

    #scope;
    #mongoDb;
    #modal;
    #users;

    static $inject = ['$scope', 'mongoDb', 'modal', 'users'];

    /**
     * @param {angular.IScope} $scope 
     * @param {MongoDbService} mongoDb 
     * @param {ModalService} modal
     * @param {UsersService} users
     */
    constructor($scope, mongoDb, modal, users) {
        this.#scope = $scope;
        this.#mongoDb = mongoDb;
        this.#modal = modal;
        this.#users = users;

        $scope.users = users;
        this.#scope.newData = {
            filepath: path.join(os.homedir(), 'Pictures'),
            recursive: true,
        };
        this.#scope.exportPath = path.join(process.cwd(), 'export.csv');
        this.#scope.data = null;
        this.#scope.load = () => this.readCsv();
        this.#scope.upload = () => this.writeMongoDb();
        this.#scope.download = () => this.readMongoDb();
        this.#scope.export = () => this.writeCsv();
        this.#scope.getImages = () => this.getImages();
        this.#scope.removeIds = () => this.removeIds();
        this.getMongoCollections();
    }

    readCsv() {
        this.#scope.data = null;
        if (this.#scope.file1.length > 0) {
            try {
                this.#scope.data = parseCsv(fs.readFileSync(this.#scope.file1[0].path), {
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
                this.#modal.showError(e, 'ERROR: CSV', 'Loading or parsing error');
            }
        }
    }

    async writeMongoDb() {
        try {
            this.#modal.showLoading('UPLOADING...');
            await this.#mongoDb.insertMany(this.#scope.data, this.#scope.collectionPush);
            await this.#users.load(true);
            if (this.#users.users.length > 0) {
                this.#scope.collectionPull = this.#users.users[0];
            }
            else {
                this.#scope.collectionPull = null;
            }
            this.#modal.hideLoading();
        }
        catch (e) {
            console.error(e);
            this.#modal.hideLoading();
            this.#modal.showError(e, 'ERROR: MongoDB', 'Error while inserting many');
        }
        this.#scope.$apply();
    }

    async readMongoDb() {
        this.#scope.data = null;
        try {
            this.#modal.showLoading('RETRIEVING...');
            this.#scope.data = await this.#mongoDb.getAll(this.#scope.collectionPull);
            this.#modal.hideLoading();
        }
        catch (e) {
            console.error(e);
            this.#modal.hideLoading();
            this.#modal.showError(e, 'ERROR: MongoDB', 'Error while fetching collection');
        }
        this.#scope.$apply();
    }

    writeCsv() {
        fs.writeFileSync(this.#scope.exportPath, stringifyCsv(this.#scope.data, {
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
        this.#scope.data = null;
        this.#scope.data = fs.readdirSync(this.#scope.newData.filepath, { withFileTypes: true }).
            filter(f => f.isFile() && ['.jpg', '.jpeg'].includes(path.extname(f.name).toLowerCase())).
            map(f => ({
                image: path.join(this.#scope.newData.filepath, f.name),
                isLabeled: false,
            }));
    }

    /** Removes the _id property of documents so they can be inserted into MongoDB */
    removeIds() {
        for (let i of this.#scope.data) {
            delete i._id;
        }
    }

    /**
     * Gets the names of all the collections in MongoDB so the user can select which collection to pull from
     */
    async getMongoCollections() {
        try {
            this.#modal.showLoading('RETRIEVING...');
            await this.#users.load(false);
            if (this.#users.users.length > 0) {
                this.#scope.collectionPull = this.#users.users[0];
            }
            else {
                this.#scope.collectionPull = null;
            }
            this.#modal.hideLoading();
        }
        catch (e) {
            console.error(e);
            this.#modal.hideLoading();
            this.#modal.showError(e, 'ERROR: MongoDB', 'Error while fetching users');
        }
        this.#scope.$apply();
    }

}


export default Controller;
