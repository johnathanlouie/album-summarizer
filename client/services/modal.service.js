const angular = require('angular');


class ModalService {

    #root;

    static $inject = ['$rootScope'];

    /**
     * @param {angular.IRootScopeService} $rootScope 
     */
    constructor($rootScope) {
        this.#root = $rootScope;
    }

    /**
     * Shows the error modal
     * @param {Error} error 
     * @param {string} title 
     * @param {string} message 
     */
    showError(error, title, message) {
        this.#root.$broadcast('ERROR_MODAL_SHOW', error, title, message);
    }

    /**
     * Shows the loading modal
     * @param {string} status Short message to display while loading
     */
    showLoading(status) {
        this.#root.$broadcast('LOADING_MODAL_SHOW', status);
    }

    hideLoading() {
        this.#root.$broadcast('LOADING_MODAL_HIDE');
    }

    showPhoto() {
        this.#root.$broadcast('PHOTO_MODAL_SHOW');
    }

}


export default ModalService;
