const angular = require('angular');
import controller from './image-viewer.controller.mjs';


const module = angular.module('components.imageViewer', ['core', 'services']);
module.component('imageViewer', {
    templateUrl: 'components/image-viewer/image-viewer.template.html',
    controller: controller,
});


export default module;
