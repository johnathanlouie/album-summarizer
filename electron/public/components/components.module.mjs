const angular = require('angular');
import devtoolsNavbar from './devtools-navbar/devtools-navbar.module.mjs';
import errorModal from './error-modal/error-modal.module.mjs';
import imageViewer from './image-viewer/image-viewer.module.mjs';
import loadingModal from './loading-modal/loading-modal.module.mjs';
import subdirectoryPanel from './subdirectory-panel/subdirectory-panel.module.mjs';


const module = angular.module('components', [
    devtoolsNavbar.name,
    errorModal.name,
    imageViewer.name,
    loadingModal.name,
    subdirectoryPanel.name,
]);


export default module;
