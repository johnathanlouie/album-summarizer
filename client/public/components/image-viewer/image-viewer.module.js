const angular = require('angular');
import core from '../../core/core.module.js';
import services from '../../services/services.module.js';
import componentDef from './image-viewer.component.js';


const module = angular.module('components.imageViewer', [core, services]);
module.component('imageViewer', componentDef);


export default module.name;
