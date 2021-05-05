const angular = require('angular');
import devtoolsNavbar from '../../components/devtools-navbar/devtools-navbar.module.js';
import PhotoModal from '../../components/photo-modal/photo-modal.module.js';
import services from '../../services/services.module.js';
import componentDef from './label-data-view.component.js';


const module = angular.module('views.labelDataView', [
    devtoolsNavbar,
    services,
    PhotoModal,
]);
module.component('labelDataView', componentDef);


export default module.name;
