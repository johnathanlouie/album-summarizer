function imageviewerSizeHandler() {
    var whole = $('#imageviewer').height();
    var top = $('#imageviewerButtonbar').outerHeight();
    $('#imageviewerImagecontainer').height(whole - top);
}


function controller($scope, screenView, focusImage) {
    $scope.screenView = screenView;
    $scope.focusImage = focusImage;

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

    $scope.unfocusImage = function () { screenView.screen = 'MAIN'; };
}

controller.$inject = ['$scope', 'screenView', 'focusImage'];


$(window).resize(imageviewerSizeHandler);
$('#imageviewer').ready(imageviewerSizeHandler);


export default controller;
