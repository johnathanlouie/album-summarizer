const angular = require('angular');
import fileInput from './file-input/file-input.module.js'
import fileUrlFn from './file-url.filter.js';
import filenameFn from './filename.filter.js';
import normalizeRatingFn from './normalize-rating.filter.js';


const module = angular.module('core', [fileInput]);
module.filter('fileUrl', fileUrlFn);
module.filter('filename', filenameFn);
module.filter('normalizeRating', normalizeRatingFn);


export default module.name;
