const angular = require('angular');
const ngRoute = require('angular-route');
import components from './components/components.module.mjs';
import services from './services/services.module.mjs';
import views from './views/views.module.mjs';
import configFn from './app.config.mjs';
import controllerFn from './app.controller.mjs';


const module = angular.module('app', [
    ngRoute,
    components,
    services,
    views,
]);

module.controller('appCtrl', controllerFn);
module.config(configFn);


export default module.name;
