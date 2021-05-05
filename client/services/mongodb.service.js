const mongodb = require('mongodb');
const angular = require('angular');
import SettingsService from './settings.service.js';


class MongoDbService {

    /** @type {mongodb.MongoClient} */
    #client;

    /** @type {mongodb.Db} */
    #db;

    static $inject = ['$q', 'settings'];
    $q;
    settings;

    /**
     * 
     * @param {angular.IQService} $q 
     * @param {SettingsService} settings 
     */
    constructor($q, settings) {
        this.$q = $q;
        this.settings = settings;

        this.#client = new mongodb.MongoClient(this.settings.mongodb.uri(), {
            useNewUrlParser: true,
            useUnifiedTopology: true,
        });
    }

    connect() {
        if (!this.#client.isConnected()) {
            return this.$q.resolve(this.#client.connect()).then(client => {
                this.#client = client;
                this.#db = client.db('albumsummarizer');
            });
        }
        return this.$q.resolve();
    }

    close() {
        if (this.#client.isConnected()) {
            return this.$q.resolve(this.#client.close());
        }
        return this.$q.resolve();
    }

    /**
     * Inserts an array of documents.
     * @param {Array.<Object>} docs Documents to insert.
     * @param {string} collection The collection name we wish to access.
     */
    insertMany(docs, collection) {
        return this.connect().then(() => {
            for (let i in docs) {
                docs[i]._id = mongodb.ObjectID(docs[i]._id);
            }
            return this.#db.collection(collection).insertMany(docs);
        }).then(insertWriteOpResult => {
            if (insertWriteOpResult.result.ok !== 1) { throw new Error(); }
        });
    }

    /**
     * Gets all documents from a collection.
     * @param {string} collection The collection name we wish to access.
     */
    getAll(collection) {
        return this.connect().then(() => {
            let cursor = this.#db.collection(collection).find();
            return cursor.toArray().finally(() => cursor.close());
        });
    }

    collections() {
        return this.connect().
            then(() => this.#db.collections()).
            then(collections => collections.map(c => c.collectionName));
    }

    /**
     * Fetches the first document that matches the query
     * @param {Object} query Query for find operation
     * @param {string} collection The collection name we wish to access
     */
    findOne(query, collection) {
        return this.connect().
            then(() => this.#db.collection(collection).findOne(query));
    }

    /**
     * Randomly fetches a number of documents that matches the query
     * @param {Object} query Query for find operation
     * @param {number} count Number of samples to return
     * @param {string} collection The collection name we wish to access
     */
    sample(query, count, collection) {
        let cursor;
        return this.connect().then(() => {
            cursor = this.#db.collection(collection).aggregate([
                { $sample: { size: count } },
                { $match: query },
            ]);
            if (cursor === null) { throw new Error(); }
            return cursor.toArray();
        }).finally(() => {
            if (cursor !== null) {
                cursor.close();
            }
        });
    }

    /**
     * Finds a document and update it in one atomic operation
     * @param {string} collection The name of the collection
     * @param {Object} filter A filter object to select the document to update
     * @param {Object} update The operations to be performed on the document
     */
    findOneAndUpdate(collection, filter, update) {
        update = { $set: update };
        return this.connect().then(
            () => this.#db.collection(collection).findOneAndUpdate(filter, update)
        ).then(result => {
            if (result.ok !== 1) { throw new Error(); }
        });
    }

    /**
     * Finds a document and replace it in one atomic operation
     * @param {string} collection The name of the collection
     * @param {Object} filter A filter object to select the document to update
     * @param {Object} replacement The document that replaces the matching document
     */
    findOneAndReplace(collection, filter, replacement) {
        return this.connect().then(
            () => this.#db.collection(collection).findOneAndReplace(filter, replacement)
        ).then(result => {
            if (result.ok !== 1) { throw new Error(); }
        });
    }

    /**
     * Inserts data into MongoDB
     * @param {string} collection The name of the collection
     * @param {Object} doc Data to be inserted
     */
    insertOne(collection, doc) {
        return this.connect().then(
            () => this.#db.collection(collection).insertOne(doc)
        ).then(insertOneWriteOpResult => {
            if (insertOneWriteOpResult.result.ok !== 1) { throw new Error(); }
        });
    }

    /**
     * 
     * @param {string} collection 
     * @param {Object} filter 
     */
    deleteOne(collection, filter) {
        return this.connect().then(
            () => this.#db.collection(collection).deleteOne(filter)
        ).then(deleteWriteOpResult => {
            if (deleteWriteOpResult.result.ok !== 1) { throw new Error(); }
        });
    }

    /**
     * 
     * @param {string} collection 
     * @param {Object} filter 
     */
    findOneAndDelete(collection, filter) {
        return this.connect().then(
            () => this.#db.collection(collection).findOneAndDelete(filter)
        ).then(findAndModifyWriteOpResult => {
            if (findAndModifyWriteOpResult.ok !== 1) { throw new Error(); }
        });
    }

    /**
     * 
     * @param {string} collection 
     */
    dropCollection(collection) {
        return this.connect().then(
            () => this.#db.collection(collection).drop()
        ).then(wasDropped => {
            if (!wasDropped) { throw new Error(); }
        });
    }

}


export default MongoDbService;
