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
        return path.normalize(`public/data/${encodeURIComponent(this.#dir)}.json`);
    }

    async mkdir() {
        if (!fs.existsSync('public/data')) {
            await fs.promises.mkdir('public/data');
        }
    }

    async read() {
        await this.mkdir();
        return await fs.promises.readFile(this.url(), 'utf8');
    }

    /**
     * @param {string} json Organization data
     */
    async write(json) {
        await this.mkdir();
        await fs.promises.writeFile(this.url(), json);
    }

    async delete() {
        await this.mkdir();
        await fs.promises.unlink(this.url());
    }

    exists() {
        return fs.existsSync(this.url());
    }
}


export default OrganizedDirFile;
