const angular = require('angular');
import ModalService from '../../services/modal.service.js';
import MongoDbSettingsService from '../../services/mongodb-settings.service.js';
import QueryServerService from '../../services/query-server.service.js';


class SettingsViewController {

    static $inject = ['$scope', 'mongoDbSettings', 'modal', 'queryServer'];

    /**
     * @param {angular.IScope} $scope 
     * @param {MongoDbSettingsService} mongoDbSettings 
     * @param {ModalService} modal 
     * @param {QueryServerService} queryServer 
     */
    constructor($scope, mongoDbSettings, modal, queryServer) {

        $scope.queryServerSettings = queryServer.settings;

        function load() {
            try {
                $scope.settings = mongoDbSettings;
                if (!mongoDbSettings.isLoaded) {
                    mongoDbSettings.load();
                }
            }
            catch (e) {
                console.warn(e);
                $scope.toast2 = e;
                $('#toast2').toast('show');
            }
        }

        $scope.update = function () {
            try {
                mongoDbSettings.save();
                $('#toast1').toast('show');
            }
            catch (e) {
                console.error(e);
                modal.showError(e, 'ERROR: Settings File', 'Cannot write to MongoDB settings file');
            }
        }

        $('#toast1').on('show.bs.toast', function () { $scope.toastShow1 = true; });
        $('#toast1').on('hidden.bs.toast', function () { $scope.toastShow1 = false; });
        $('#toast2').on('show.bs.toast', function () { $scope.toastShow2 = true; });
        $('#toast2').on('hidden.bs.toast', function () { $scope.toastShow2 = false; });
        load();

    }

}


export default SettingsViewController;
