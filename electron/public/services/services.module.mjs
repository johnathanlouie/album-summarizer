const angular = require('angular');
import history from './history.service.mjs';
import cwd from './cwd.service.mjs';
import screenView from './screen-view.service.mjs';
import queryServer from './query-server.service.mjs';
import options from './options.service.mjs';
import mongoDb from './mongodb.service.mjs';
import focusImage from './focus-image.service.mjs';


const module = angular.module('services', []);
module.factory('history', history);
module.factory('cwd', cwd);
module.factory('screenView', screenView);
module.factory('queryServer', queryServer);
module.factory('options', options);
module.factory('mongoDb', mongoDb);
module.factory('focusImage', focusImage);


export default module;
