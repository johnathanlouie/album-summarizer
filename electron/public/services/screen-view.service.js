const MAIN = 'MAIN';
const IMAGE = 'IMAGE_VIEWER';
const THUMBNAILS = 'THUMBNAILS';
const DETAILS = 'DETAILS';


function serviceFn() {
    class ScreenView {
        screen = MAIN;
        view = THUMBNAILS;
    }
    return new ScreenView();
}


export default serviceFn;
