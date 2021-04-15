const os = require('os');
import Directory from '../lib/directory.js';
import OrganizedDirFile from '../lib/organize.js';


class CwdService {
    #HOME_DIR = os.homedir();

    /** @type {Directory} */
    #dir;

    /** @type {string} */
    #path;
    #organization;

    /** @type {OrganizedDirFile} */
    #dirFile;
    #queryServer;

    static $inject = ['queryServer'];
    constructor(queryServer) {
        this.#queryServer = queryServer;
    }

    async cd(dst) {
        this.#path = dst;
        this.#organization = null;
        this.#dirFile = new OrganizedDirFile(dst);
        this.#dir = await Directory.factory(dst);
    }

    async goHome() { await this.cd(this.#HOME_DIR); }

    async refresh() { await this.cd(this.#path); }

    /**
     * 
     * @param {boolean} refresh
     */
    async #organize(refresh) {
        this.#organization = null;
        if (refresh || !this.#dirFile.exists()) {
            await this.#dirFile.delete();
            var data = await this.#queryServer(this.#path);
            this.#organization = data;
            var json = JSON.stringify(data);
            this.#dirFile.write(json);
        }
        else {
            var json = await this.#dirFile.read();
            this.#organization = JSON.parse(json);
        }
    }

    async organize() { await this.#organize(false); }

    async reorganize() { await this.#organize(true); }

    get organization() { return this.#organization; }

    get isOrganized() { return this.#organization !== null; }

    get regular() { return this.#dir; }

    get path() { return this.#path; }

    get home() { return this.#HOME_DIR; }

}


export default CwdService;
