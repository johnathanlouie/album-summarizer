'use strict';


angular.module('services').factory('MongoDB', ['$rootScope', function ($rootScope) {
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
            try {
                await fs.promises.writeFile('mongodb.json', JSON.stringify(this));
                this.#loaded = true;
            }
            catch (e) { $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Cannot write to MongoDB settings file.', 'Error: MongoDB'); }
        }

        async load() {
            try {
                this.#loaded = false;
                var json = await fs.promises.readFile('mongodb.json');
                var obj = JSON.parse(json);
                this.hostname = obj.hostname;
                this.username = obj.username;
                this.password = obj.password;
                this.#loaded = true;
            }
            catch (e) { $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error while loading MongoDB settings file.', 'Error: MongoDB'); }
        }

        get uri() {
            if (this.username || this.password) {
                return `mongodb+srv://${this.username}:${this.password}@${this.hostname}:${this.port}`;
            }
            return `mongodb+srv://${this.hostname}:${this.port}`;
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

    return new MongoDB();
}]);
