import fileUrl from './file-url.filter.mjs';


const module = angular.module('core', ['core.fileInput']);
module.filter('fileUrl', fileUrl);


export default module;
