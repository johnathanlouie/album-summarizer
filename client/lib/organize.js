const path = require('path');
const fs = require('fs');


/**
 * Interface for the cached organized view for the current directory.
 */
class OrganizedDirFile {

    /** @type {string} */
    #dir;

    constructor(dir) {
        this.#dir = dir;
    }

    url() {
        return path.normalize(`data/${encodeURIComponent(this.#dir)}.json`);
    }

    mkdir() {
        if (!fs.existsSync('data')) {
            fs.mkdirSync('data');
        }
    }

    read() {
        this.mkdir();
        return fs.readFileSync(this.url(), 'utf8');
    }

    /**
     * @param {string} json Organization data
     */
    write(json) {
        this.mkdir();
        fs.writeFileSync(this.url(), json);
    }

    delete() {
        this.mkdir();
        fs.unlinkSync(this.url());
    }

    exists() {
        return fs.existsSync(this.url());
    }
}


export default OrganizedDirFile;
