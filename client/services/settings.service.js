const fs = require('fs');


class MongoDbSettings {

    hostname = 'localhost';
    port = 27017;
    username = '';
    password = '';

    uri() {
        if (this.username || this.password) {
            return `mongodb://${encodeURIComponent(this.username)}:${encodeURIComponent(this.password)}@${this.hostname}:${this.port}`;
        }
        return `mongodb://${this.hostname}:${this.port}`;
    }

}


class ServerSettings {

    url = 'http://localhost:8080';

}


class OrganizerSettings {

    architecture = 'smi13a';
    dataset = 'ccrc';
    loss = 'bce';
    optimizer = 'sgd';
    metrics = 'acc';
    epochs = 0;
    patience = 3;
    split = 0;
    cluster = 'sift4';
    clusterArgs = {
        nfeatures: 300,
        nOctaveLayers: 3,
        contrastThreshold: 0.04,
        edgeThreshold: 10,
        sigma: 1.6,
        ratio: 0.8,
        similarity_metric: 'inverse_distance',
        damping: 0.5,
        max_iter: 200,
        convergence_iter: 15,
        affinity: 'euclidean',
    };

}


class SettingsService {

    #saveFile = 'settings.json';
    mongodb = new MongoDbSettings();
    server = new ServerSettings();
    organizer = new OrganizerSettings();

    static $inject = [];
    constructor() {
        this.load();
    }

    save() {
        fs.writeFileSync(this.#saveFile, JSON.stringify(this));
    }

    load() {
        if (this.exists()) {
            var loadObj = JSON.parse(fs.readFileSync(this.#saveFile));
            Object.assign(this.mongodb, loadObj.mongodb);
            Object.assign(this.server, loadObj.server);
            Object.assign(this.organizer, loadObj.organizer);
        }
    }

    exists() {
        return fs.existsSync(this.#saveFile);
    }

}


export default SettingsService;
