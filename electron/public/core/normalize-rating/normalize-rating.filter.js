angular.module('core').filter('normalizeRating', function () {
    return function (rating) {
        return (rating - 1) * 5;
    };
});