'use strict';


angular.module('services').factory('ScreenView', function () {
    const MAIN = 'MAIN';
    const IMAGE = 'IMAGE_VIEWER';
    const THUMBNAILS = 'THUMBNAILS';
    const DETAILS = 'DETAILS';

    class ScreenView {
        screen = MAIN;
        view = THUMBNAILS;
    }

    return new ScreenView();
});
