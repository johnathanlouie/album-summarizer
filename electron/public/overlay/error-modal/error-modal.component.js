'use strict';

function ErrorCtrl($scope) {
    $scope.$on('ERROR_MODAL_SHOW', () => { $('#errorModal').modal(); });
}

angular.module('overlay').component('errorModal', {
    templateUrl: 'overlay/error-modal/error-modal.template.html',
    controller: ErrorCtrl,
});
