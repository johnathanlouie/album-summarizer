const angular = require('angular');
import componentOptions from './devtools-navbar.component.mjs'


const module = angular.module('components.devtoolsNavbar', []);
module.component('devtoolsNavbar', componentOptions);


export default module;
