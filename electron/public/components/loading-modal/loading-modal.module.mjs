const angular = require('angular');
import controller from './loading-modal.controller.mjs';


const module = angular.module('components.loadingModal', []);
const component = module.component('loadingModal', {
    templateUrl: 'components/loading-modal/loading-modal.template.html',
    controller: controller,
});


export default module;
