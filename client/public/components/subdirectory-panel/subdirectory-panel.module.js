const angular = require('angular');
import services from '../../services/services.module.js';
import core from '../../core/core.module.js';
import componentDef from './subdirectory-panel.component.js';


const module = angular.module('components.subdirectoryPanel', [services, core]);
module.component('subdirectoryPanel', componentDef);


export default module.name;
