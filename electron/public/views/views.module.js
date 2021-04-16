const angular = require('angular');
import checkRateView from './check-rate-view/check-rate-view.module.js';
import histogramView from './histogram-view/histogram-view.module.js';
import labelDataView from './label-data-view/label-data-view.module.js';
import menuView from './menu-view/menu-view.module.js';
import organizerView from './organizer-view/organizer-view.module.js';
import settingsView from './settings-view/settings-view.module.js';
import transferDataView from './transfer-data-view/transfer-data-view.module.js';
import statusView from './status-view/status-view.module.js';


const module = angular.module('views', [
    checkRateView,
    histogramView,
    labelDataView,
    menuView,
    organizerView,
    settingsView,
    transferDataView,
    statusView,
]);


export default module.name;
