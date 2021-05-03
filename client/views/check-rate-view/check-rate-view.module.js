const angular = require('angular');
import core from '../../core/core.module.js';
import devtoolsNavbar from '../../components/devtools-navbar/devtools-navbar.module.js';
import services from '../../services/services.module.js';
import PhotoModal from '../../components/photo-modal/photo-modal.module.js';
import componentDef from './check-rate-view.component.js';


const module = angular.module('views.checkRateView', [
    devtoolsNavbar,
    core,
    services,
    PhotoModal,
]);

module.component('checkRateView', componentDef);


export default module.name;
