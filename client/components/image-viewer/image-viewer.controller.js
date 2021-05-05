const $ = require('jquery');


function imageviewerSizeHandler() {
    var whole = $('#imageviewer').height();
    var top = $('#imageviewerButtonbar').outerHeight();
    $('#imageviewerImagecontainer').height(whole - top);
}


class ImageViewerController {

    static $inject = ['$scope', 'screenView', 'focusImage'];

    constructor($scope, screenView, focusImage) {
        $scope.screenView = screenView;
        $scope.focusImage = focusImage;

        function isVisible() {
            return $('#imageviewer').is(':visible');
        }

        $scope.$watch(isVisible, imageviewerSizeHandler);

        $scope.unfocusImage = function () { screenView.screen = 'MAIN'; };
    }

}


export default ImageViewerController;
