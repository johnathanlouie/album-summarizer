const _ = require('lodash');
import DatabaseService from './database.service.js';
import { Evaluation, Metrics, ModelDescription } from '../lib/evaluation.js';


class EvaluationsService {

    /** @type {Map.<ModelDescription, Evaluation>} */ #container = new Map();
    #isLoaded = false;

    database;

    static $inject = ['database'];

    /**
     * @param {DatabaseService} database
     */
    constructor(database) {
        this.database = database;
    }

    /**
     * 
     * @param {Evaluation} evaluation 
     */
    set(evaluation) {
        this.#container.set(evaluation.model.toString(), evaluation);
    }

    /**
     * @deprecated
     * @param {Evaluation} evaluation 
     */
    async add(evaluation) {
        await this.database.addEvaluation(evaluation);
        this.set(evaluation);
    }

    /**
     * @deprecated
     * @param {Evaluation} evaluation 
     */
    async update(evaluation) {
        await this.database.updateEvaluation(evaluation);
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

    statuses() {
        return _.uniq(this.toArray().map(e => e.status));
    }

    toArray() {
        return Array.from(this.#container.values());
    }

    /**
     * @deprecated
     */
    async fromMongoDb() {
        if (!this.#isLoaded) {
            for (let i of await this.database.getAllEvaluations()) {
                this.set(i);
            }
            this.#isLoaded = true;
        }
    }

    /**
     * @deprecated
     */
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
