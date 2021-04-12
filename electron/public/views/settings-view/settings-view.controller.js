function controllerFn($scope, $rootScope, mongoDbSettings) {

    function load() {
        try {
            $scope.settings = mongoDbSettings;
            if (!mongoDbSettings.isLoaded) {
                mongoDbSettings.load();
            }
        }
        catch (e) {
            console.warn(e);
            $scope.toast2 = e;
            $('#toast2').toast('show');
        }
    }

    $scope.update = function () {
        try {
            mongoDbSettings.save();
            $('#toast1').toast('show');
        }
        catch (e) {
            console.error(e);
            $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Cannot write to MongoDB settings file.', 'Error: MongoDB');
        }
    }

    $('#toast1').on('show.bs.toast', function () { $scope.toastShow1 = true; });
    $('#toast1').on('hidden.bs.toast', function () { $scope.toastShow1 = false; });
    $('#toast2').on('show.bs.toast', function () { $scope.toastShow2 = true; });
    $('#toast2').on('hidden.bs.toast', function () { $scope.toastShow2 = false; });
    load();

}

controllerFn.$inject = ['$scope', '$rootScope', 'mongoDbSettings'];


export default controllerFn;
