angular.module('core').filter('filename', function () {
    return function (url) {
        return require('path').basename(url);
    };
});