const angular = require('angular');
import devtoolsNavbar from '../../components/devtools-navbar/devtools-navbar.module.js';
import services from '../../services/services.module.js';
import fileInput from '../../core/file-input/file-input.module.js';
import componentDef from './transfer-data-view.component.js';


const module = angular.module('views.transferDataView', [
    devtoolsNavbar,
    services,
    fileInput,
]);
module.component('transferDataView', componentDef);


export default module.name;
