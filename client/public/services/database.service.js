import MongoDbService from './mongodb.service.js';
import { Evaluation, Metrics, ModelDescription } from '../lib/evaluation.js';


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
    async addEvaluation(evaluation) {
        await this.mongoDb.insertOne('evaluations', evaluation);
    }

    /**
     * 
     * @param {Evaluation} evaluation 
     */
    async updateEvaluation(evaluation) {
        await this.mongoDb.findOneAndReplace('evaluations', { model: evaluation.model }, evaluation);
    }

    async getAllEvaluations() {
        return (await this.mongoDb.getAll('evaluations')).map(i => Evaluation.from(i));
    }

    /**
     * 
     * @param {Evaluation} evaluation 
     */
    async deleteEvaluation(evaluation) {
        await this.mongoDb.deleteOne('evaluations', evaluation);
    }

}


export default DatabaseService;
