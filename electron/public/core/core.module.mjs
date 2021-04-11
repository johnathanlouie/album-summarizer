const angular = require('angular');
import fileUrl from './file-url.filter.mjs';
import filename from './filename.filter.mjs';
import normalizeRating from './normalize-rating.filter.mjs';
import './file-input/file-input.module.mjs'


const module = angular.module('core', ['core.fileInput']);
module.filter('fileUrl', fileUrl);
module.filter('filename', filename);
module.filter('normalizeRating', normalizeRating);


export default module.name;
