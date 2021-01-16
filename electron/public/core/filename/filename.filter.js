angular.module('core').filter('filename', function () {
    const path = require('path');
    return function (url) {
        return path.basename(url);
    };
});