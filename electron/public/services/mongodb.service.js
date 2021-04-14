const mongodb = require('mongodb');
import MongoDbSettings from './mongodb-settings.service.js';


class MongoDbService {

    /** @type {mongodb.MongoClient} */
    #client;

    /** @type {mongodb.Db} */
    #db;

    /** @type {MongoDbSettings} */
    #mongoDbSettings;

    static $inject = ['mongoDbSettings'];

    constructor(mongoDbSettings) {
        this.#mongoDbSettings = mongoDbSettings;
        if (!this.#mongoDbSettings.isLoaded) {
            this.#mongoDbSettings.load();
        }
        this.#client = new mongodb.MongoClient(this.#mongoDbSettings.uri(), {
            useNewUrlParser: true,
            useUnifiedTopology: true,
        });
    }

    async connect() {
        if (!this.#client.isConnected()) {
            this.#client = await this.#client.connect();
            this.#db = this.#client.db('albumsummarizer');
        }
    }

    async close() {
        if (this.#client.isConnected()) {
            await this.#client.close();
        }
    }

    /**
     * Inserts an array of documents.
     * @param {Array.<Object>} docs Documents to insert.
     * @param {string} collection The collection name we wish to access.
     */
    async insertMany(docs, collection) {
        await this.connect();
        for (let i in docs) {
            docs[i]._id = mongodb.ObjectID(docs[i]._id);
        }
        let insertWriteOpResult = await this.#db.collection(collection).insertMany(docs);
        if (insertWriteOpResult.result.ok !== 1) { throw new Error(); }
    }

    /**
     * Gets all documents from a collection.
     * @param {string} collection The collection name we wish to access.
     * @returns {Array.<Object>}
     */
    async getAll(collection) {
        await this.connect();
        let cursor = this.#db.collection(collection).find();
        try {
            return await cursor.toArray();
        }
        finally {
            cursor.close();
        }
    }

    async collections() {
        await this.connect();
        let collections = await this.#db.collections();
        return collections.map(c => c.collectionName);
    }

    /**
     * Fetches the first document that matches the query
     * @param {Object} query Query for find operation
     * @param {string} collection The collection name we wish to access
     * @returns {Object}
     */
    async findOne(query, collection) {
        await this.connect();
        return await this.#db.collection(collection).findOne(query);
    }

    /**
     * Randomly fetches a number of documents that matches the query
     * @param {Object} query Query for find operation
     * @param {number} count Number of samples to return
     * @param {string} collection The collection name we wish to access
     * @returns {Array.<Object>}
     */
    async sample(query, count, collection) {
        await this.connect();
        let cursor;
        try {
            cursor = this.#db.collection(collection).aggregate([
                { $sample: { size: count } },
                { $match: query },
            ]);
            if (cursor === null) { throw new Error(); }
            return await cursor.toArray();
        }
        finally {
            if (cursor !== null) {
                cursor.close();
            }
        }
    }

    /**
     * Finds a document and update it in one atomic operation
     * @param {string} collection The name of the collection
     * @param {Object} filter A filter object to select the document to update
     * @param {Object} update The operations to be performed on the document
     */
    async findOneAndUpdate(collection, filter, update) {
        update = { $set: update };
        if ((await this.#db.collection(collection).findOneAndUpdate(filter, update)).ok !== 1) { throw new Error(); }
    }

}


export default MongoDbService;
