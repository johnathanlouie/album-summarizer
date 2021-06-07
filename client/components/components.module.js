const angular = require('angular');
import devtoolsNavbar from './devtools-navbar/devtools-navbar.module.js';
import errorModal from './error-modal/error-modal.module.js';
import imageViewer from './image-viewer/image-viewer.module.js';
import loadingModal from './loading-modal/loading-modal.module.js';
import subdirectoryPanel from './subdirectory-panel/subdirectory-panel.module.js';
import photoModal from './photo-modal/photo-modal.module.js';
import nullableInput from './nullable-input/nullable-input.module.js';


const module = angular.module('components', [
    devtoolsNavbar,
    errorModal,
    imageViewer,
    loadingModal,
    subdirectoryPanel,
    photoModal,
    nullableInput,
]);


export default module.name;
