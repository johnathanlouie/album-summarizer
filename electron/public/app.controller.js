const angular = require('angular');
import { Screen, ScreenView } from './services/screen-view.service.js'

class Controller {

    static $inject = ['$scope', 'screenView'];

    /**
     * @param {angular.IScope} $scope
     * @param {ScreenView} screenView
     */
    constructor($scope, screenView) {
        $scope.screenView = screenView;
        $scope.isMain = () => screenView.screen === Screen.MAIN;
        $scope.isImage = () => screenView.screen === Screen.IMAGE;
    }

}


export default Controller;
