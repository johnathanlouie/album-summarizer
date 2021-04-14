const mongodb = require('mongodb');


function serviceFn(mongoDbSettings) {

    class MongoDb {

        /** @type {mongodb.MongoClient} */
        #client;

        /** @type {mongodb.Db} */
        #db;

        constructor() {
            if (!mongoDbSettings.isLoaded) {
                mongoDbSettings.load();
            }
            this.#client = new mongodb.MongoClient(mongoDbSettings.uri(), {
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

    }

    return new MongoDb();

}

serviceFn.$inject = ['mongoDbSettings'];


export default serviceFn;
