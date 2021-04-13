const mongodb = require('mongodb');


function serviceFn(mongoDbSettings) {

    class MongoDb {

        #client;

        constructor() {
            if (!mongoDbSettings.isLoaded) {
                mongoDbSettings.load();
            }
            this.#client = new mongodb.MongoClient(mongoDbSettings.uri(), {
                useNewUrlParser: true,
                useUnifiedTopology: true,
            });
        }

        async connect() { await this.#client.connect(); }

        async close() { await this.#client.close(); }

        /**
         * 
         * @param {*} docs Documents to insert.
         * @param {string} db The name of the database we want to use. If not provided, use database name from connection string.
         * @param {string} collection The collection name we wish to access.
         */
        async insertMany(docs, db, collection) {
            try {
                await this.connect();
                let insertWriteOpResult = await this.#client.db(db).collection(collection).insertMany(docs);
                if (insertWriteOpResult.result.ok !== 1) { throw new Error(); }
            }
            finally { await this.close(); }
        }

    }

    return new MongoDb();

}

serviceFn.$inject = ['mongoDbSettings'];


export default serviceFn;
