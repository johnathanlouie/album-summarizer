'use strict';

const File = require('./file');
const fsp = require('./fsp');


class Directory extends Array {
    #path;
    #directories;
    #files;
    #images;
    #exists;

    static async factory(url) {
        var direntArray = [];
        var exists = false;
        var instance;
        try {
            direntArray = await fsp.readdir(url, { withFileTypes: true });
            instance = Directory.from(direntArray.map(e => new File(e, url)));
            exists = true;
        }
        catch (err) {
            instance = new Directory();
        }
        instance.#path = url;
        instance.#exists = exists;
        return instance;
    }

    get exists() {
        return this.#exists;
    }

    get path() {
        return this.#path;
    }

    get directories() {
        if (this.#directories === undefined) {
            this.#directories = this.filter(e => e.isDirectory());
        }
        return this.#directories;
    }

    get files() {
        if (this.#files === undefined) {
            this.#files = this.filter(e => e.isFile());
        }
        return this.#files;
    }

    get images() {
        if (this.#images === undefined) {
            this.#images = this.files.filter(e => e.isImage());
        }
        return this.#images;
    }

    hasDirectories() {
        return this.directories.length > 0;
    }

    hasImages() {
        return this.images.length > 0;
    }
}

module.exports = Directory;
