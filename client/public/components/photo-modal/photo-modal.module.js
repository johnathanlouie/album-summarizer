const angular = require('angular');
import services from '../../services/services.module.js';
import componentDef from './photo-modal.component.js';


const module = angular.module('components.photoModal', [services]);
module.component('photoModal', componentDef);


export default module.name;
