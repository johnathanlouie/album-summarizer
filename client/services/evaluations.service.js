const _ = require('lodash');
const angular = require('angular');
import DatabaseService from './database.service.js';
import QueryServerService from './query-server.service.js';
import { Evaluation, ModelDescription } from '../lib/evaluation.js';


class EvaluationsService {

    /** @type {Map.<ModelDescription, Evaluation>} */
    #container = new Map();
    #isLoaded = false;

    /** @type {Array.<string>} */
    #statuses = [];

    static $inject = ['$q', 'database', 'queryServer'];
    $q;
    database;
    queryServer;

    /**
     * @param {angular.IQService} $q
     * @param {DatabaseService} database
     * @param {QueryServerService} queryServer
     */
    constructor($q, database, queryServer) {
        this.$q = $q;
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
    add(evaluation) {
        return this.database.addEvaluation(evaluation).then(() => this.set(evaluation));
    }

    /**
     * @param {Evaluation} evaluation 
     */
    update(evaluation) {
        return this.database.updateEvaluation(evaluation).then(() => this.set(evaluation));
    }

    /**
     * 
     * @param {ModelDescription} model 
     * @returns {boolean}
     */
    has(model) {
        return this.#container.has(model.toString());
    }

    fetchStatuses() {
        return this.queryServer.trainingStatuses().then(statuses => this.#statuses = statuses);
    }

    statuses() {
        return this.#statuses;
    }

    toArray() {
        return Array.from(this.#container.values());
    }

    fromMongoDb() {
        if (!this.#isLoaded) {
            return this.database.getAllEvaluations().then(evaluations => {
                for (let i of evaluations) {
                    this.set(i);
                }
                this.#isLoaded = true;
            });
        }
        return this.$q.resolve();
    }

    removeMongoDbDuplicates() {
        return this.database.getAllEvaluations().then(evaluations => {
            let copy = new Map();
            for (let evaluation of evaluations) {
                if (copy.has(evaluation.model.toString())) {
                    console.log(evaluation);
                    this.database.deleteEvaluation(evaluation);
                }
                else {
                    copy.set(evaluation.model.toString(), evaluation);
                }
            }
        });

    }

    /**
     * 
     * @param {ModelDescription} model 
     * @returns {Evaluation}
     */
    get(model) {
        return this.#container.get(model.toString());
    }

}


export default EvaluationsService;
