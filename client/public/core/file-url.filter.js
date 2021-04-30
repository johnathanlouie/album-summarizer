const fileUrl = require('file-url');


function filterFn() {
    return function (url) {
        if (typeof url !== 'string') {
            console.error('fileUrl: Not string', url);
            return '';
        }
        return fileUrl(url);
    };
}


export default filterFn;
