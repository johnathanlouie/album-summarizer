import history from './history.service.mjs';
import cwd from './cwd.service.mjs';
import screenView from './cwd.service.mjs';
import queryServer from './cwd.service.mjs';
import options from './cwd.service.mjs';
import mongoDb from './cwd.service.mjs';
import focusImage from './cwd.service.mjs';


const module = angular.module('services', []);
module.factory('history', history);
module.factory('cwd', cwd);
module.factory('screenView', screenView);
module.factory('queryServer', queryServer);
module.factory('options', options);
module.factory('mongoDb', mongoDb);
module.factory('focusImage', focusImage);


export default module;
