const _ = require('lodash');


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

    /** @type {Map.<ModelDescription, Evaluation>} */
    #container = new Map();

    isLoaded = false;

    /**
     * 
     * @param {Evaluation} evaluation 
     */
    set(evaluation) {
        this.#container.set(ModelDescription.toString(evaluation.model), evaluation);
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

}


export default Evaluations;
