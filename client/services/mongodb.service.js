const mongodb = require('mongodb');
import SettingsService from './settings.service.js';


class MongoDbService {

    /** @type {mongodb.MongoClient} */
    #client;

    /** @type {mongodb.Db} */
    #db;

    settings;

    static $inject = ['settings'];

    /**
     * 
     * @param {SettingsService} settings 
     */
    constructor(settings) {
        this.settings = settings;

        this.#client = new mongodb.MongoClient(this.settings.mongodb.uri(), {
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
     * @returns {Promise.<Array.<Object>>}
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
     * @returns {Promise.<Object>}
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
     * @returns {Promise.<Array.<Object>>}
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
        await this.connect();
        update = { $set: update };
        if ((await this.#db.collection(collection).findOneAndUpdate(filter, update)).ok !== 1) { throw new Error(); }
    }

    /**
     * Finds a document and replace it in one atomic operation
     * @param {string} collection The name of the collection
     * @param {Object} filter A filter object to select the document to update
     * @param {Object} replacement The document that replaces the matching document
     */
    async findOneAndReplace(collection, filter, replacement) {
        await this.connect();
        if ((await this.#db.collection(collection).findOneAndReplace(filter, replacement)).ok !== 1) { throw new Error(); }
    }

    /**
     * Inserts data into MongoDB
     * @param {string} collection The name of the collection
     * @param {Object} doc Data to be inserted
     */
    async insertOne(collection, doc) {
        await this.connect();
        if ((await this.#db.collection(collection).insertOne(doc)).result.ok !== 1) { throw new Error(); }
    }

    /**
     * 
     * @param {string} collection 
     * @param {Object} filter 
     */
    async deleteOne(collection, filter) {
        await this.connect();
        if ((await this.#db.collection(collection).deleteOne(filter)).result.ok !== 1) { throw new Error(); }
    }

    /**
     * 
     * @param {string} collection 
     * @param {Object} filter 
     */
    async findOneAndDelete(collection, filter) {
        await this.connect();
        if ((await this.#db.collection(collection).findOneAndDelete(filter)).ok !== 1) { throw new Error(); }
    }

    /**
     * 
     * @param {string} collection 
     */
    async dropCollection(collection) {
        await this.connect();
        if (!await this.#db.collection(collection).drop()) { throw new Error(); }
    }

}


export default MongoDbService;
