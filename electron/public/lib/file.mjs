const path = require('path');


class File {
    #path;
    #isFile;
    #isDirectory;

    constructor(dirent, dirname) {
        this.#path = path.join(dirname, dirent.name);
        this.#isFile = dirent.isFile();
        this.#isDirectory = dirent.isDirectory();
    }

    get path() {
        return this.#path;
    }

    get extension() {
        return path.extname(this.#path);
    }

    isImage() {
        const validExt = ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.apng', '.avif'];
        var ext = this.extension.toLowerCase();
        return this.isFile() && validExt.some(e => e === ext);
    }

    isFile() {
        return this.#isFile;
    }

    isDirectory() {
        return this.#isDirectory;
    }
}


export default File;
