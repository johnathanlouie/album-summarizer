const angular = require('angular');
const $ = require('jquery');
import FocusImageService from '../../services/focus-image.service.js';


class PhotoModalController {

    static $inject = ['$scope', 'focusImage'];

    /**
     * 
     * @param {angular.IScope} $scope 
     * @param {FocusImageService} focusImage
     */
    constructor($scope, focusImage) {
        $scope.focusImage = focusImage;

        $scope.$on('PHOTO_MODAL_SHOW', function (event) {
            $('#photoModal').modal();
        });
    }

}


export default PhotoModalController;
