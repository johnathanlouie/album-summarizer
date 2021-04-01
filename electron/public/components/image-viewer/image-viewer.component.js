'use strict';


function imageviewerSizeHandler() {
    var whole = $('#imageviewer').height();
    var top = $('#imageviewerButtonbar').outerHeight();
    $('#imageviewerImagecontainer').height(whole - top);
}

$(window).resize(imageviewerSizeHandler);
$('#imageviewer').ready(imageviewerSizeHandler);

angular.module('components.imageViewer').component('imageViewer', {
    templateUrl: 'components/image-viewer/image-viewer.template.html',
    controller: ['$scope', 'ScreenView', 'FocusImage', function ($scope, ScreenView, FocusImage) {
        $scope.screenView = ScreenView;
        $scope.focusImage = FocusImage;

        var lastState;
        var watchValue = 0;

        function onVisible() {
            var currentState = $('#imageviewer').is(':visible');
            if (currentState === lastState) { return watchValue; } // If no change; stops infinite propagation
            lastState = currentState; // Keeps track of toggling
            if (currentState) { return ++watchValue; } // On visible
            return watchValue; // On invisible
        }

        $scope.$watch(onVisible, imageviewerSizeHandler, true);

        $scope.unfocusImage = function () { ScreenView.screen = 'MAIN'; };
    }],
});
