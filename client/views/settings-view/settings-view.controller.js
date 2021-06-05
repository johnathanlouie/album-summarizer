const angular = require('angular');
import ModalService from '../../services/modal.service.js';
import SettingsService from '../../services/settings.service.js';
import OptionsService from '../../services/options.service.js';
import ClusterAlgorithmsService from '../../services/cluster-algorithms.service.js';


class SettingsViewController {

    static $inject = ['$scope', '$q', 'settings', 'modal', 'options', 'clusterAlgorithms'];
    #$scope;
    #$q;
    #settings;
    #modal;
    #options;
    #clusterAlgorithms;

    /**
     * @param {angular.IScope} $scope 
     * @param {angular.IQService} $q 
     * @param {SettingsService} settings 
     * @param {ModalService} modal 
     * @param {OptionsService} options 
     * @param {ClusterAlgorithmsService} clusterAlgorithms 
     */
    constructor($scope, $q, settings, modal, options, clusterAlgorithms) {

        /* === INJECTION VARIABLES === */
        this.#$scope = $scope;
        this.#$q = $q;
        this.#settings = settings;
        this.#modal = modal;
        this.#options = options;
        this.#clusterAlgorithms = clusterAlgorithms;

        /* === PRELOAD === */
        this.#modal.showLoading('PRELOADING....');
        this.#settings.load();
        this.#$q.all([
            this.#clusterAlgorithms.preload(),
            this.#options.load(),
        ]).then(() => {
            this.#$scope.settings = angular.copy(this.#settings);
            this.#modal.hideLoading();
        }, error => {
            this.#modal.hideLoading();
            this.#modal.showError(error, 'ERROR: Preload Error', 'Something happened during preloading');
        });

        /* === SCOPE VARIABLES === */
        this.#$scope.options = this.#options;
        this.#$scope.clusterAlgorithms = this.#clusterAlgorithms;
        this.#$scope.settings = angular.copy(this.#settings);

        /* === SCOPE FUNCTIONS === */
        this.#$scope.save = () => this.save();

        /* === MISCELLANEOUS === */
        $('#toast1').on('show.bs.toast', () => { this.#$scope.toastShow1 = true; });
        $('#toast1').on('hidden.bs.toast', () => { this.#$scope.toastShow1 = false; });
        $('#toast2').on('show.bs.toast', () => { this.#$scope.toastShow2 = true; });
        $('#toast2').on('hidden.bs.toast', () => { this.#$scope.toastShow2 = false; });
        this.exists();
        this.#$scope.$watch('settings.organizer.cluster', (newVal, oldVal, scope) => {
            if (newVal !== oldVal) {
                scope.settings.organizer.clusterArgs = Object();
                let algorithm = this.#clusterAlgorithms.get(newVal);
                if (algorithm) {
                    for (let [parameterName, parameterDetails] of Object.entries(algorithm.parameters)) {
                        scope.settings.organizer.clusterArgs[parameterName] = parameterDetails.default;
                    }
                }
            }
        });

    }

    save() {
        try {
            angular.copy(this.#$scope.settings, this.#settings);
            this.#settings.save();
            $('#toast1').toast('show');
        }
        catch (e) {
            console.error(e);
            modal.showError(e, 'ERROR: Settings File', 'Cannot write to settings file');
        }
    }

    exists() {
        if (!this.#settings.exists()) {
            $('#toast2').toast('show');
        }
    }

}


export default SettingsViewController;
