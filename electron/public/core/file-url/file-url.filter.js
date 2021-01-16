const fileUrl = require('file-url');

angular.module('core').filter('fileUrl', function () {
    return function (url) {
        return url;
    };
});