const mongodb = require('mongodb');


function serviceFn(mongoDbSettings) {

    class MongoDb {

        #client;
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
         * 
         * @param {*} docs Documents to insert.
         * @param {string} db The name of the database we want to use. If not provided, use database name from connection string.
         * @param {string} collection The collection name we wish to access.
         */
        async insertMany(docs, collection) {
            await this.connect();
            let insertWriteOpResult = await this.#db.collection(collection).insertMany(docs);
            if (insertWriteOpResult.result.ok !== 1) { throw new Error(); }
        }

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

    }

    return new MongoDb();

}

serviceFn.$inject = ['mongoDbSettings'];


export default serviceFn;
