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
