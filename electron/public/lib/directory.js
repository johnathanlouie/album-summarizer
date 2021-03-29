const File = require('./file');

class Directory extends Array {
    #path = '';
    #directories = null;
    #files = null;
    #images = null;
    #exists = false;
    #organization = null;

    static factory(path, direntArray = [], exists = false) {
        var instance = Directory.from(direntArray.map(e => new File(e, path)));
        instance.#path = path;
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
        if (this.#directories === null) {
            this.#directories = this.filter(e => e.isDirectory());
        }
        return this.#directories;
    }

    get files() {
        if (this.#files === null) {
            this.#files = this.filter(e => e.isFile());
        }
        return this.#files;
    }

    get images() {
        if (this.#images === null) {
            this.#images = this.files.filter(e => e.isImage());
        }
        return this.#images;
    }

    get organization() {
        return this.#organization;
    }

    get isOrganized() {
        return this.#organization !== null;
    }

    organize(val) {
        this.#organization = val;
    }

    unorganize() {
        this.#organization = null;
    }

    hasDirectories() {
        return this.directories.length > 0;
    }

    hasImages() {
        return this.images.length > 0;
    }
}

module.exports = Directory;
