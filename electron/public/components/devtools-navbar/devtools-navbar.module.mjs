const angular = require('angular');
import controller from './devtools-navbar.controller.mjs';


const module = angular.module('components.devtoolsNavbar', []);
module.component('devtoolsNavbar', {
    templateUrl: 'components/devtools-navbar/devtools-navbar.template.html',
    controller: controller,
});


export default module;
