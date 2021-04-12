const angular = require('angular');
const ngRoute = require('angular-route');
import components from './components/components.module.js';
import services from './services/services.module.js';
import views from './views/views.module.js';
import configFn from './app.config.js';
import controllerFn from './app.controller.js';


const module = angular.module('app', [
    ngRoute,
    components,
    services,
    views,
]);

module.controller('appCtrl', controllerFn);
module.config(configFn);


export default module.name;
