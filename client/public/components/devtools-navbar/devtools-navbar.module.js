const angular = require('angular');
import componentDef from './devtools-navbar.component.js'


const module = angular.module('components.devtoolsNavbar', []);
module.component('devtoolsNavbar', componentDef);


export default module.name;
