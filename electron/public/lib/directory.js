const fs = require('fs');
import File from './file.js';


class Directory {

    #path;

    /** @type {Array.<File>} */
    #directories;

    /** @type {Array.<File>} */
    #files;

    /** @type {Array.<File>} */
    #images;

    #exists = false;

    /**
     * @param {string} filepath The path of the directory
     */
    constructor(filepath) {
        try {
            this.#path = filepath;
            let fileArray = fs.readdirSync(filepath, { withFileTypes: true }).
                map(e => new File(e, filepath));
            this.#directories = fileArray.filter(e => e.isDirectory());
            this.#files = fileArray.filter(e => e.isFile());
            this.#images = this.#files.filter(e => e.isImage());
            this.#exists = true;
        }
        catch { }
    }

    get exists() {
        return this.#exists;
    }

    get path() {
        return this.#path;
    }

    get directories() {
        return this.#directories;
    }

    get files() {
        return this.#files;
    }

    get images() {
        return this.#images;
    }

    hasDirectories() {
        return this.directories.length > 0;
    }

    hasImages() {
        return this.images.length > 0;
    }

}


export default Directory;
