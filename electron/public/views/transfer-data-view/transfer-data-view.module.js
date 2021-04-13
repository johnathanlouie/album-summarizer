const angular = require('angular');
import devtoolsNavbar from '../../components/devtools-navbar/devtools-navbar.module.js';
import componentDef from './transfer-data-view.component.js';


const module = angular.module('views.transferDataView', [
    devtoolsNavbar,
]);
module.component('transferDataView', componentDef);


export default module.name;
