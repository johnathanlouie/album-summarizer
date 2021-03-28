'use strict';

function ErrorCtrl($scope) {
    $scope.$on('ERROR_MODAL_SHOW', () => { $('#errorModal').modal(); });
}

angular.module('components').component('errorModal', {
    templateUrl: 'components/error-modal/error-modal.template.html',
    controller: ErrorCtrl,
});
