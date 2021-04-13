function configFn($routeProvider) {
    $routeProvider.when('/', { template: '<organizer-view></organizer-view>' });
    $routeProvider.when('/menu', { template: '<menu-view></menu-view>' });
    $routeProvider.when('/organizer', { template: '<organizer-view></organizer-view>' });
    $routeProvider.when('/settings', { template: '<settings-view></settings-view>' });
    $routeProvider.when('/devtools/check-rate', { template: '<check-rate-view></check-rate-view>' });
    $routeProvider.when('/devtools/histogram', { template: '<histogram-view></histogram-view>' });
    $routeProvider.when('/devtools/label-data', { template: '<label-data-view></label-data-view>' });
    $routeProvider.when('/devtools/data-transfer', { template: '<transfer-data-view></transfer-data-view>' });
    $routeProvider.otherwise('/menu');
}

configFn.$inject = ['$routeProvider'];


export default configFn;
