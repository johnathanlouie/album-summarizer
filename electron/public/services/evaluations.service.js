const _ = require('lodash');
import DatabaseService from './database.service.js';
import QueryServerService from './query-server.service.js';
import { Evaluation, ModelDescription } from '../lib/evaluation.js';


class EvaluationsService {

    /** @type {Map.<ModelDescription, Evaluation>} */
    #container = new Map();
    #isLoaded = false;

    /** @type {Array.<string>} */
    #statuses = [];

    static $inject = ['database', 'queryServer'];
    database;
    queryServer;

    /**
     * @param {DatabaseService} database
     * @param {QueryServerService} queryServer
     */
    constructor(database, queryServer) {
        this.database = database;
        this.queryServer = queryServer;
    }

    /**
     * 
     * @param {Evaluation} evaluation 
     */
    set(evaluation) {
        this.#container.set(evaluation.model.toString(), evaluation);
    }

    /**
     * @param {Evaluation} evaluation 
     */
    async add(evaluation) {
        this.database.addEvaluation(evaluation);
        this.set(evaluation);
    }

    /**
     * @param {Evaluation} evaluation 
     */
    async update(evaluation) {
        this.database.updateEvaluation(evaluation);
        this.set(evaluation);
    }

    /**
     * 
     * @param {ModelDescription} model 
     * @returns {boolean}
     */
    has(model) {
        return this.#container.has(model.toString());
    }

    async fetchStatuses() {
        this.#statuses = await this.queryServer.trainingStatuses();
    }

    statuses() {
        return this.#statuses;
    }

    toArray() {
        return Array.from(this.#container.values());
    }

    async fromMongoDb() {
        if (!this.#isLoaded) {
            for (let i of await this.database.getAllEvaluations()) {
                this.set(i);
            }
            this.#isLoaded = true;
        }
    }

    async removeMongoDbDuplicates() {
        let copy = new Map();
        for (let evaluation of await this.database.getAllEvaluations()) {
            if (copy.has(evaluation.model.toString())) {
                console.log(evaluation);
                this.database.deleteEvaluation(evaluation);
            }
            else {
                copy.set(evaluation.model.toString(), evaluation);
            }
        }
    }

}


export default EvaluationsService;
