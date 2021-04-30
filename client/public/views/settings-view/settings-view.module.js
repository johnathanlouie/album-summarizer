const angular = require('angular');
import core from '../../core/core.module.js';
import components from '../../components/components.module.js';
import services from '../../services/services.module.js';
import componentDef from './settings-view.component.js';


const module = angular.module('views.settingsView', [
    core,
    components,
    services,
]);
module.component('settingsView', componentDef);


export default module.name;
