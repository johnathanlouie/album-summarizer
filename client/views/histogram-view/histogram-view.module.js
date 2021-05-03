const angular = require('angular');
import fileInput from '../../core/file-input/file-input.module.js';
import devtoolsNavbar from '../../components/devtools-navbar/devtools-navbar.module.js';
import services from '../../services/services.module.js';
import PhotoModal from '../../components/photo-modal/photo-modal.module.js';
import componentDef from './histogram-view.component.js';


const module = angular.module('views.histogramView', [
    devtoolsNavbar,
    services,
    fileInput,
    PhotoModal,
]);
module.component('histogramView', componentDef);


export default module.name;
