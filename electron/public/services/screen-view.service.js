class Screen {

    static MAIN = 'MAIN';
    static IMAGE = 'IMAGE_VIEWER';

}

class View {

    static THUMBNAILS = 'THUMBNAILS';
    static DETAILS = 'DETAILS';

}

class ScreenView {

    screen;
    view;

    static $inject = [];
    constructor() {
        this.screen = Screen.MAIN;
        this.view = View.THUMBNAILS;
    }

}


export default ScreenView;
export { Screen, View, ScreenView };
