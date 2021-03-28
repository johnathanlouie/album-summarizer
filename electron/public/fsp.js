const fs = require('fs');
const util = require('util');

const fsp = {
    writeFile: util.promisify(fs.writeFile),
    readFile: util.promisify(fs.readFile),
    readdir: util.promisify(fs.readdir),
    access: util.promisify(fs.access),
    mkdir: util.promisify(fs.mkdir),
    unlink: util.promisify(fs.unlink),
};

module.exports = fsp;
