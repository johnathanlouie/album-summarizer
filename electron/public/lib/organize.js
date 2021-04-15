const path = require('path');
const fs = require('fs');


/**
 * Interface for the cached organized view for the current directory.
 */
class OrganizedDirFile {
    #dir;

    constructor(dir) {
        this.#dir = dir;
    }

    url() {
        return path.normalize(`public/data/${encodeURIComponent(this.#dir)}.json`);
    }

    async mkdir() {
        try {
            return await fs.promises.access('public/data');
        }
        catch (err) {
            return await fs.promises.mkdir('public/data');
        }
    }

    async read() {
        await this.mkdir();
        return await fs.promises.readFile(this.url());
    }

    /**
     * @param {string} json Organization data
     */
    async write(json) {
        await this.mkdir();
        return await fs.promises.writeFile(this.url(), json);
    }

    async delete() {
        await this.mkdir();
        try {
            await fs.promises.unlink(this.url());
            return true;
        }
        catch (err) {
            return false;
        }
    }

    exists() {
        return fs.existsSync(this.url());
    }
}


export default OrganizedDirFile;
