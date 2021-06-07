const angular = require('angular');

import services from '../../services/services.module.js';

import componentDef from './nullable-input.component.js';


const module = angular.module('components.nullableInput', [services]);
module.component('nullableInput', componentDef);


export default module.name;
