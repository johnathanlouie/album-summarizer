'use strict';


angular.module('components').component('errorModal', {
    templateUrl: 'components/error-modal/error-modal.template.html',
    controller: ['$rootScope', function ($rootScope) {
        $rootScope.$on('ERROR_MODAL_SHOW', () => { $('#errorModal').modal(); });
    }],
});
