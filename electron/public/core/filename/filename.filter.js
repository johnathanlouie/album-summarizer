const path = require('path');

angular.module('core').filter('filename', function () {
    return function (url) {
        return path.basename(url);
    };
});