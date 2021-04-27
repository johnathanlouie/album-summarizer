const _ = require('lodash');
import MongoDbService from './mongodb.service.js';


class ModelDescription {

    /** @type {string} */
    architecture;

    /** @type {string} */
    dataset;

    /** @type {string} */
    loss;

    /** @type {string} */
    optimizer;

    /** @type {string} */
    metrics;

    /** @type {number} */
    epochs;

    /** @type {number} */
    patience;

    /** @type {number} */
    split;

    /**
     * 
     * @param {ModelDescription} model 
     */
    static toString(model) {
        return `${model.architecture}-${model.dataset}-${model.loss}-${model.optimizer}-${model.metrics}-${model.epochs}-${model.patience}-${model.split}`;
    }

}


class Metrics {

    /** @type {number} */
    accuracy;

    /** @type {number} */
    loss;

}


class Evaluation {

    /** @type {ModelDescription} */
    model;

    /** @type {string} */
    status;

    /** @type {Metrics} */
    training;

    /** @type {Metrics} */
    validation;

    /** @type {Metrics} */
    test;

}


class Evaluations {

    #mongoDb;

    /** @type {Map.<ModelDescription, Evaluation>} */
    #container = new Map();

    #isLoaded = false;

    static $inject = ['mongoDb'];

    /**
     * @param {MongoDbService} mongoDb
     */
    constructor(mongoDb) {
        this.#mongoDb = mongoDb;
    }

    /**
     * 
     * @param {Evaluation} evaluation 
     */
    #set(evaluation) {
        this.#container.set(ModelDescription.toString(evaluation.model), evaluation);
    }

    /**
     * 
     * @param {Evaluation} evaluation 
     */
    async add(evaluation) {
        await this.#mongoDb.insertOne('evaluations', evaluation);
        this.#set(evaluation);
    }

    /**
     * 
     * @param {Evaluation} evaluation 
     */
    async update(evaluation) {
        await this.#mongoDb.findOneAndReplace('evaluations', { model: evaluation.model }, evaluation);
        this.#set(evaluation);
    }

    /**
     * 
     * @param {ModelDescription} model 
     * @returns {boolean}
     */
    has(model) {
        return this.#container.has(ModelDescription.toString(model));
    }

    statuses() {
        return _.uniq(this.toArray().map(e => e.status));
    }

    toArray() {
        return Array.from(this.#container.values());
    }

    async fromMongoDb() {
        if (!this.#isLoaded) {
            for (let i of await this.#mongoDb.getAll('evaluations')) {
                this.#set(i);
            }
            this.#isLoaded = true;
        }
    }

}


export default Evaluations;
