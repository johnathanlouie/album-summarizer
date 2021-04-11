const angular = require('angular');
import fileInput from './file-input.directive.mjs';


const module = angular.module('core.fileInput', []);
module.directive('fileInput', fileInput);


export default module;
