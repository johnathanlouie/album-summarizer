const angular = require('angular');
import componentDef from './menu-view.component.js';


const module = angular.module('views.menuView', []);
module.component('menuView', componentDef);


export default module.name;
