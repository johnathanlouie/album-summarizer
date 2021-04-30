const _ = require('lodash');
import MongoDbService from './mongodb.service.js';


class UsersService {

    #mongoDb;

    /** @type {Array.<string>} */
    #users = [];
    #isLoaded = false;

    static $inject = ['mongoDb'];

    /**
     * 
     * @param {MongoDbService} mongoDb 
     */
    constructor(mongoDb) {
        this.#mongoDb = mongoDb;
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
            this.#users = await this.#mongoDb.collections();
            this.remove('evaluations');
            this.#isLoaded = true;
        }
    }

    get users() { return this.#users; }

}

export default UsersService;
