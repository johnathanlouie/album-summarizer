const angular = require('angular');
import history from './history.service.js';
import cwd from './cwd.service.js';
import screenView from './screen-view.service.js';
import queryServer from './query-server.service.js';
import options from './options.service.js';
import mongoDb from './mongodb.service.js';
import focusImage from './focus-image.service.js';
import mongoDbSettings from './mongodb-settings.service.js';


const module = angular.module('services', []);
module.factory('history', history);
module.factory('cwd', cwd);
module.factory('screenView', screenView);
module.factory('queryServer', queryServer);
module.factory('options', options);
module.factory('mongoDb', mongoDb);
module.factory('focusImage', focusImage);
module.factory('mongoDbSettings', mongoDbSettings);


export default module.name;
