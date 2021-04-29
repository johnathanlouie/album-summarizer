const path = require('path');
const angular = require('angular');
import HistoryService from '../../services/cwd.service.js';
import CwdService from '../../services/cwd.service.js';
import ScreenViewService from '../../services/cwd.service.js';
import FocusImageService from '../../services/cwd.service.js';
import ModalService from '../../services/modal.service.js';


class OrganizerViewController {

    $scope;
    history;
    cwd;
    screenView;
    focusImage;
    modal;

    static $inject = ['$scope', 'history', 'cwd', 'screenView', 'focusImage', 'modal'];

    /**
     * @param {angular.IScope} $scope 
     * @param {HistoryService} history 
     * @param {CwdService} cwd 
     * @param {ScreenViewService} screenView 
     * @param {FocusImageService} focusImage 
     * @param {ModalService} modal
     */
    constructor($scope, history, cwd, screenView, focusImage, modal) {
        this.$scope = $scope;
        this.history = history;
        this.cwd = cwd;
        this.screenView = screenView;
        this.focusImage = focusImage;
        this.modal = modal;

        $scope.cwd = cwd;
        $scope.screenView = screenView;
        $scope.focusImage = focusImage;

        function goTo(dst) {
            $scope.address = dst;
            $scope.filterText = '';
            cwd.cd(dst);
        }

        $scope.goTo = function (dst = $scope.address) { goTo(history.push(dst)); };

        $scope.goHome = function () { goTo(history.push(cwd.home)); };

        $scope.refresh = function () { goTo(history.current); };

        $scope.goParent = function () { goTo(history.push(path.dirname(history.current))); };

        $scope.goBack = function () { goTo(history.goBack()); };

        $scope.goForward = function () { goTo(history.goForward()); };

        $scope.hasBack = function () { return history.hasBack; };

        $scope.hasNext = function () { return history.hasNext; };

        $scope.focusOnImage = function (url) {
            focusImage.image = url;
            screenView.screen = 'IMAGE_VIEWER';
        };

        /**
         * 
         * @param {boolean} refresh
         */
        async function organize(refresh) {
            try {
                modal.showLoading('ORGANIZING...');
                if (refresh) { await cwd.reorganize(); }
                else { await cwd.organize(); }
                modal.hideLoading();
            }
            catch (err) {
                console.error(err);
                $scope.isOrganizeToggled = false;
                modal.hideLoading();
                modal.showError(err, 'ERROR: Smart Organizer', 'Error while organizing');
            }
            finally {
                $scope.$apply();
            }
        }

        $scope.toggleOrganize = function () {
            // If user switches to organized view
            if ($scope.isOrganizeToggled) {
                organize(false);
            }
        };

        $scope.reorganize = function () { organize(true); };

        $scope.$on('CHANGE_DIRECTORY', function (event, dst) {
            $scope.goTo(dst);
        });

        $scope.isOrganizeToggled = false;
        $scope.goHome();
    }

}


export default OrganizerViewController;
