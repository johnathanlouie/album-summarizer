import RouteManager from './lib/routes.js';


function configFn($routeProvider) {
    $routeProvider.otherwise('/');
    for (let route of RouteManager.ROUTES) {
        $routeProvider.when(route.path, { template: route.view });
    }
}

configFn.$inject = ['$routeProvider'];


export default configFn;
