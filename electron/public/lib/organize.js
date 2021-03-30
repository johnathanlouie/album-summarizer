'use strict';

const path = require('path');
const fsp = require('./fsp');

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
            return await fsp.access('public/data');
        }
        catch (err) {
            return await fsp.mkdir('public/data');
        }
    }

    async read() {
        await this.mkdir();
        return await fsp.readFile(this.url());
    }

    /**
     * @param {string} json Organization data
     */
    async write(json) {
        await this.mkdir();
        return await fsp.writeFile(this.url(), json);
    }

    async delete() {
        await this.mkdir();
        try {
            await fsp.unlink(this.url());
            return true;
        }
        catch (err) {
            return false;
        }
    }

    async exists() {
        try {
            await fsp.access(this.url());
            return true;
        }
        catch (err) {
            return false;
        }
    }
}

module.exports = OrganizedDirFile;
