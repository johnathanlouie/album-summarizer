angular.module('core').filter('fileUrl', function () {
    const fileUrl = require('file-url');
    return function (url) {
        if (typeof url !== 'string') {
            console.error('fileUrl: Not string', url);
            return '';
        }
        return fileUrl(url);
    };
});
