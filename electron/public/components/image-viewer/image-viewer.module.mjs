const angular = require('angular');
import controller from './image-viewer.controller.mjs';
import core from '../../core/core.module.mjs';
import services from '../../services/services.module.mjs';


const module = angular.module('components.imageViewer', [core, services]);
module.component('imageViewer', {
    templateUrl: 'components/image-viewer/image-viewer.template.html',
    controller: controller,
});


export default module.name;
