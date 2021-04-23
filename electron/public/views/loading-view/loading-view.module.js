const angular = require('angular');
import componentDef from './loading-view.component.js';


const module = angular.module('views.loadingView', []);
module.component('loadingView', componentDef);


export default module.name;
