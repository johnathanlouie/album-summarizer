const angular = require('angular');
import componentDef from './error-modal.component.js';


const module = angular.module('components.errorModal', []);
module.component('errorModal', componentDef);


export default module.name;
