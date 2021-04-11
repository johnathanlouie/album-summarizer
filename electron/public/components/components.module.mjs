const angular = require('angular');
import './devtools-navbar/devtools-navbar.module.mjs';
import './error-modal/error-modal.module.mjs';
import './image-viewer/image-viewer.module.mjs';
import './loading-modal/loading-modal.module.mjs';
import './subdirectory-panel/subdirectory-panel.module.mjs';


const module = angular.module('components', [
    'components.devtoolsNavbar',
    'components.errorModal',
    'components.imageViewer',
    'components.loadingModal',
    'components.subdirectoryPanel',
]);


export default module;
