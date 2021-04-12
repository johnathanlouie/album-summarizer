const angular = require('angular');
import core from '../../core/core.module.mjs';
import devtoolsNavbar from '../../components/devtools-navbar/devtools-navbar.module.mjs';
import services from '../../services/services.module.mjs';


const module = angular.module('views.checkRateView', [
    devtoolsNavbar,
    core,
    services,
]);


export default module.name;
