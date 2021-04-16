const angular = require('angular');
import navbar from '../../components/devtools-navbar/devtools-navbar.module.js';
import componentDef from './status-view.component.js';


const module = angular.module('views.statusView', [navbar]);
module.component('statusView', componentDef);


export default module.name;
