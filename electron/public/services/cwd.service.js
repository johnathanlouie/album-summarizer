const os = require('os');
import Directory from '../lib/directory.js';
import OrganizedDirFile from '../lib/organize.js';
import QueryServerService from './query-server.service.js';


class OrganizedImage {

    /** @type {number} */
    cluster;

    /** @type {string} */
    path;

    /** @type {number} */
    rating;

}


class CwdService {
    #HOME_DIR = os.homedir();

    /** @type {Directory} */
    #dir;

    /** @type {string} */
    #path;

    /** @type {?Array.<Array.<OrganizedImage>>} */
    #organization;

    #queryServer;

    static $inject = ['queryServer'];

    /**
     * @param {QueryServerService} queryServer
     */
    constructor(queryServer) {
        this.#queryServer = queryServer;
    }

    cd(dst) {
        this.#path = dst;
        this.#organization = null;
        this.#dir = new Directory(dst);
    }

    async goHome() { this.cd(this.#HOME_DIR); }

    async refresh() { this.cd(this.#path); }

    async organize() {
        this.#organization = null;
        this.#organization = await this.#queryServer.run(this.#path);
    }

    get organization() { return this.#organization; }

    get isOrganized() { return this.#organization !== null; }

    get regular() { return this.#dir; }

    get path() { return this.#path; }

    get home() { return this.#HOME_DIR; }

}


export default CwdService;
