const os = require('os');
import Directory from '../lib/directory.js';
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

    static $inject = ['queryServer'];
    queryServer;

    /**
     * @param {QueryServerService} queryServer
     */
    constructor(queryServer) {
        this.queryServer = queryServer;
    }

    cd(dst) {
        this.#path = dst;
        this.#organization = null;
        this.#dir = new Directory(dst);
    }

    goHome() { this.cd(this.#HOME_DIR); }

    refresh() { this.cd(this.#path); }

    organize() {
        return this.queryServer.run(this.#path).then(
            x => { this.#organization = x; },
            () => { this.#organization = null; },
        );
    }

    get organization() { return this.#organization; }

    get isOrganized() { return this.#organization !== null; }

    get regular() { return this.#dir; }

    get path() { return this.#path; }

    get home() { return this.#HOME_DIR; }

}


export default CwdService;
