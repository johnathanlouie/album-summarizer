const angular = require('angular');
import controller from './error-modal.controller.mjs';


const module = angular.module('components.errorModal', []);
module.component('errorModal', {
    templateUrl: 'components/error-modal/error-modal.template.html',
    controller: controller,
});


export default module;
