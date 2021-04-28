const angular = require('angular');
import ModalService from '../../services/modal.service.js';
import SettingsService from '../../services/settings.service.js';


class SettingsViewController {

    $scope;
    settings;
    modal;

    static $inject = ['$scope', 'settings', 'modal'];

    /**
     * @param {angular.IScope} $scope 
     * @param {SettingsService} settings 
     * @param {ModalService} modal 
     */
    constructor($scope, settings, modal) {
        this.$scope = $scope;
        this.settings = settings;
        this.modal = modal;

        $scope.serverSettings = this.settings.server;
        $scope.settings = this.settings.mongodb;

        function load() {
            try {
                mongoDbSettings.load();
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
