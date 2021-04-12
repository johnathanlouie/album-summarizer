const fs = require('fs');


class Settings {

    hostname = 'localhost';
    port = 27017;
    username = '';
    password = '';
    #loaded = false;

    save() {
        fs.writeFileSync('mongodb.json', JSON.stringify(this));
        this.#loaded = true;
    }

    load() {
        this.#loaded = false;
        var json = fs.readFileSync('mongodb.json');
        var obj = JSON.parse(json);
        this.hostname = obj.hostname;
        this.username = obj.username;
        this.password = obj.password;
        this.#loaded = true;
    }

    get uri() {
        if (this.username || this.password) {
            return `mongodb://${encodeURIComponent(this.username)}:${encodeURIComponent(this.password)}@${this.hostname}:${this.port}`;
        }
        return `mongodb://${this.hostname}:${this.port}`;
    }

    get isLoaded() { return this.#loaded; }

}

function serviceFn() { return new Settings(); }


export default serviceFn;
