const angular = require('angular');
import fileInputFn from './file-input.directive.js';


const module = angular.module('core.fileInput', []);
module.directive('fileInput', fileInputFn);


export default module.name;
