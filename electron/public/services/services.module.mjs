import History from './history.service.mjs';
import cwd from './cwd.service.mjs';


const module = angular.module('services', []);
module.factory('History', History);
module.factory('Cwd', cwd);


export default module;
