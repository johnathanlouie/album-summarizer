const angular = require('angular');
import controller from './subdirectory-panel.controller.mjs';


const module = angular.module('components.subdirectoryPanel', ['services', 'core']);
module.component('subdirectoryPanel', {
    templateUrl: 'components/subdirectory-panel/subdirectory-panel.template.html',
    controller: controller,
});


export default module;
