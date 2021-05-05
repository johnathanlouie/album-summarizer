const _ = require('lodash');
const angular = require('angular');
import MongoDbService from './mongodb.service.js';


class UsersService {

    /** @type {Array.<string>} */
    #users = [];
    #isLoaded = false;

    static $inject = ['$q', 'mongoDb'];
    $q;
    mongoDb;

    /**
     * 
     * @param {angular.IQService} $q 
     * @param {MongoDbService} mongoDb 
     */
    constructor($q, mongoDb) {
        this.$q = $q;
        this.mongoDb = mongoDb;
    }

    /**
     * 
     * @param {string} user 
     */
    add(user) {
        this.#users.push(user);
    }

    /**
     * 
     * @param {string} user 
     */
    remove(user) {
        _.pull(this.#users, user);
    }

    /**
     * Fetches compile options for the deep learning model
     * @param {boolean} reload Forces a refresh
     */
    async load(reload) {
        if (!this.#isLoaded || reload) {
            this.#isLoaded = false;
            return this.mongoDb.collections().then(users => {
                this.#users = users;
                this.remove('evaluations');
                this.#isLoaded = true;
            });
        }
        return this.$q.resolve();
    }

    get users() { return this.#users; }

}

export default UsersService;
