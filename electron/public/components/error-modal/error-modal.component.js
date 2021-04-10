'use strict';


angular.module('components').component('errorModal', {
    templateUrl: 'components/error-modal/error-modal.template.html',
    controller: ['$scope', function ($scope) {
        $scope.$on('ERROR_MODAL_SHOW', function (event, error, message, title) {
            $scope.error = error;
            $scope.message = message;
            $scope.title = title;
            $('#errorModal').modal();
        });
    }],
});
