const angular = require('angular');
import checkRateView from './check-rate-view/check-rate-view.module.mjs';
import histogramView from './histogram-view/histogram-view.module.mjs';
import labelDataView from './label-data-view/label-data-view.module.mjs';
import menuView from './menu-view/menu-view.module.mjs';
import organizerView from './organizer-view/organizer-view.module.mjs';
import settingsView from './settings-view/settings-view.module.mjs';


const module = angular.module('views', [
    checkRateView,
    histogramView,
    labelDataView,
    menuView,
    organizerView,
    settingsView,
]);


export default module.name;
