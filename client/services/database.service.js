import MongoDbService from './mongodb.service.js';
import { Evaluation } from '../lib/evaluation.js';


class DatabaseService {

    mongoDb;

    static $inject = ['mongoDb'];

    /**
     * @param {MongoDbService} mongoDb 
     */
    constructor(mongoDb) {
        this.mongoDb = mongoDb;
    }

    /**
     * 
     * @param {Evaluation} evaluation 
     */
    addEvaluation(evaluation) {
        return this.mongoDb.insertOne('evaluations', evaluation);
    }

    /**
     * 
     * @param {Evaluation} evaluation 
     */
    updateEvaluation(evaluation) {
        return this.mongoDb.findOneAndReplace('evaluations', { model: evaluation.model }, evaluation);
    }

    getAllEvaluations() {
        return this.mongoDb.getAll('evaluations').then(
            evaluations => evaluations.map(i => Evaluation.from(i))
        );
    }

    /**
     * 
     * @param {Evaluation} evaluation 
     */
    deleteEvaluation(evaluation) {
        return this.mongoDb.findOneAndDelete('evaluations', { _id: evaluation._id });
    }

}


export default DatabaseService;
