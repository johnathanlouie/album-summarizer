const angular = require('angular');
import History from './history.service.js';
import Cwd from './cwd.service.js';
import ScreenView from './screen-view.service.js';
import QueryServer from './query-server.service.js';
import Options from './options.service.js';
import MongoDb from './mongodb.service.js';
import FocusImage from './focus-image.service.js';
import MongoDbSettings from './mongodb-settings.service.js';
import Modal from './modal.service.js';
import Users from './users.service.js';


const module = angular.module('services', []);
module.factory('history', History);
module.factory('cwd', Cwd);
module.factory('screenView', ScreenView);
module.factory('queryServer', QueryServer);
module.factory('options', Options);
module.factory('mongoDb', MongoDb);
module.factory('focusImage', FocusImage);
module.factory('mongoDbSettings', MongoDbSettings);
module.factory('modal', Modal);
module.factory('users', Users);


export default module.name;
