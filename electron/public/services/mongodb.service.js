const fs = require('fs');


class Settings {

    hostname = 'localhost';
    port = 27017;
    username = '';
    password = '';
    #loaded = false;

    async exists() {
        try {
            await fs.promises.access('mongodb.json');
            return true;
        }
        catch (e) { return false; }
    }

    async save() {
        await fs.promises.writeFile('mongodb.json', JSON.stringify(this));
        this.#loaded = true;
    }

    async load() {
        this.#loaded = false;
        var json = await fs.promises.readFile('mongodb.json');
        var obj = JSON.parse(json);
        this.hostname = obj.hostname;
        this.username = obj.username;
        this.password = obj.password;
        this.#loaded = true;
    }

    get uri() {
        if (this.username || this.password) {
            return `mongodb://${this.username}:${this.password}@${this.hostname}:${this.port}`;
        }
        return `mongodb://${this.hostname}:${this.port}`;
    }

    get isLoaded() { return this.#loaded; }

}


class MongoDB {

    #settings = new Settings();

    async settings() {
        if (this.#settings.isLoaded) { return this.#settings; }
        else if (await this.#settings.exists()) { await this.#settings.load(); }
        else { await this.#settings.save(); }
        return this.#settings;
    }

}


function serviceFn() { return new MongoDB(); }


export default serviceFn;
