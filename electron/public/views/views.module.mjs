const angular = require('angular');


const module = angular.module('views', [
    'views.organizerView',
    'views.menuView',
    'views.checkRateView',
    'views.histogramView',
    'views.labelDataView',
    'views.settingsView',
]);


export default module.name;
