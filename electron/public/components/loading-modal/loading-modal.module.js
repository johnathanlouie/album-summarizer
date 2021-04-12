const angular = require('angular');
import componentDef from './loading-modal.component.js';


const module = angular.module('components.loadingModal', []);
module.component('loadingModal', componentDef);


export default module.name;
