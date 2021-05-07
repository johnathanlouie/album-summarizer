const angular = require('angular');
import devtoolsNavbar from '../../components/devtools-navbar/devtools-navbar.module.js';
import services from '../../services/services.module.js';
import fileInput from '../../core/file-input/file-input.module.js';
import PhotoModal from '../../components/photo-modal/photo-modal.module.js';
import componentDef from './transfer-data-view.component.js';


const module = angular.module('views.transferDataView', [
    devtoolsNavbar,
    services,
    fileInput,
    PhotoModal,
]);
module.component('transferDataView', componentDef);


export default module.name;
