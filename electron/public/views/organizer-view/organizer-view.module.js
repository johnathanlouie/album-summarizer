const angular = require('angular');
import core from '../../core/core.module.js';
import components from '../../components/components.module.js';
import services from '../../services/services.module.js';
import componentDef from './organizer-view.component.js';


const module = angular.module('views.organizerView', [
    core,
    components,
    services,
]);
angular.module('views.organizerView').component('organizerView', componentDef);


export default module.name;
