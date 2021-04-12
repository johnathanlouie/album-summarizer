const angular = require('angular');
import fileInput from '../../core/file-input/file-input.module.mjs';
import devtoolsNavbar from '../../components/devtools-navbar/devtools-navbar.module.mjs';
import services from '../../services/services.module.mjs';


const module = angular.module('views.histogramView', [
    devtoolsNavbar,
    services,
    fileInput,
]);


export default module.name;
