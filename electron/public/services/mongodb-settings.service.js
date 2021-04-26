const fs = require('fs');


class MongoDbSettings {

    hostname = 'localhost';
    port = 27017;
    username = '';
    password = '';
    #loaded = false;

    static $inject = [];
    constructor() { }

    save() {
        fs.writeFileSync('mongodb.json', JSON.stringify(this));
        this.#loaded = true;
    }

    load() {
        this.#loaded = false;
        if (fs.existsSync()) {
            var json = fs.readFileSync('mongodb.json');
            var obj = JSON.parse(json);
            this.hostname = obj.hostname;
            this.username = obj.username;
            this.password = obj.password;
            this.#loaded = true;
        }
        else {
            this.save();
        }
    }

    uri() {
        if (this.username || this.password) {
            return `mongodb://${encodeURIComponent(this.username)}:${encodeURIComponent(this.password)}@${this.hostname}:${this.port}`;
        }
        return `mongodb://${this.hostname}:${this.port}`;
    }

    get isLoaded() { return this.#loaded; }

}


export default MongoDbSettings;
