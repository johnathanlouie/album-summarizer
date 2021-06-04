const angular = require('angular');
import ModalService from '../../services/modal.service.js';
import SettingsService from '../../services/settings.service.js';
import OptionsService from '../../services/options.service.js';


class SettingsViewController {

    static $inject = ['$scope', 'settings', 'modal', 'options'];
    $scope;
    settings;
    modal;
    options;

    /**
     * @param {angular.IScope} $scope 
     * @param {SettingsService} settings 
     * @param {ModalService} modal 
     * @param {OptionsService} options 
     */
    constructor($scope, settings, modal, options) {

        this.$scope = $scope;
        this.settings = settings;
        this.modal = modal;
        this.options = options;

        $scope.options = options;
        $scope.settings = this.settings;
        $scope.save = () => this.save();

        $('#toast1').on('show.bs.toast', function () { $scope.toastShow1 = true; });
        $('#toast1').on('hidden.bs.toast', function () { $scope.toastShow1 = false; });
        $('#toast2').on('show.bs.toast', function () { $scope.toastShow2 = true; });
        $('#toast2').on('hidden.bs.toast', function () { $scope.toastShow2 = false; });
        this.exists();

    }

    save() {
        try {
            this.settings.save();
            $('#toast1').toast('show');
        }
        catch (e) {
            console.error(e);
            modal.showError(e, 'ERROR: Settings File', 'Cannot write to settings file');
        }
    }

    exists() {
        if (!this.settings.exists()) {
            $('#toast2').toast('show');
        }
    }

}


export default SettingsViewController;
