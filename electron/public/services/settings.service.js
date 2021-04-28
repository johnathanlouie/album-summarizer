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


class SettingsService {

    #saveFile = 'settings.json';
    mongodb = new MongoDbSettings();
    server = new ServerSettings();

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
        }
    }

    exists() {
        return fs.existsSync(this.#saveFile);
    }

}


export default SettingsService;
