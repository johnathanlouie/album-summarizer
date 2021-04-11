import fileUrl from './file-url.filter.mjs';
import filename from './filename.filter.mjs';
import normalizeRating from './normalize-rating.filter.mjs';
import fileInput from './file-input/file-input.module.mjs'


const module = angular.module('core', [fileInput.name]);
module.filter('fileUrl', fileUrl);
module.filter('filename', filename);
module.filter('normalizeRating', normalizeRating);


export default module;
