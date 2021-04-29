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

    toString() {
        return `${this.architecture}-${this.dataset}-${this.loss}-${this.optimizer}-${this.metrics}-${this.epochs}-${this.patience}-${this.split}`;
    }

    static from(model) {
        return Object.assign(new ModelDescription(), model);
    }

}


class Metrics {

    /** @type {number} */
    accuracy;

    /** @type {number} */
    loss;

    static from(metrics) {
        return Object.assign(new Metrics(), metrics);
    }

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

    static from(evaluation) {
        /** @type {Evaluation} */
        let instance = Object.assign(new Evaluation(), evaluation);
        instance.model = ModelDescription.from(instance.model);
        instance.training = Metrics.from(instance.training);
        instance.validation = Metrics.from(instance.validation);
        instance.test = Metrics.from(instance.test);
        return instance;
    }

}


export { ModelDescription, Metrics, Evaluation };
