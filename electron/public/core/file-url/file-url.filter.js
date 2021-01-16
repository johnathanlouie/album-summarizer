angular.module('core').filter('fileUrl', function () {
    const fileUrl = require('file-url');
    return function (url) {
        return fileUrl(url);
    };
});