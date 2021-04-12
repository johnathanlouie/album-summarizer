const angular = require('angular');
import core from '../../core/core.module.mjs';
import components from '../../components/components.module.mjs';
import services from '../../services/services.module.mjs';


const module = angular.module('views.organizerView', [
    core,
    components,
    services,
]);


export default module.name;
