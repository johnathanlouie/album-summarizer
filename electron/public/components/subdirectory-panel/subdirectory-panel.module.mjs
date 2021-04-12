const angular = require('angular');
import services from '../../services/services.module.mjs';
import core from '../../core/core.module.mjs';
import controller from './subdirectory-panel.controller.mjs';


const module = angular.module('components.subdirectoryPanel', [services, core]);
module.component('subdirectoryPanel', {
    templateUrl: 'components/subdirectory-panel/subdirectory-panel.template.html',
    controller: controller,
});


export default module.name;
