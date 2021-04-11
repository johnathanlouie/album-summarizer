const fileUrl = require('file-url');


function f(url) {
    if (typeof url !== 'string') {
        console.error('fileUrl: Not string', url);
        return '';
    }
    return fileUrl(url);
}


function filter() { return f; }


export default filter;
