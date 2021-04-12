function controllerFn($scope, $rootScope, mongoDb) {

    async function getSettings() {
        try {
            $scope.settings = await mongoDb.settings();
        }
        catch (e) { $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error while loading MongoDB settings file.', 'Error: MongoDB'); }
        $scope.$apply();
    }

    $scope.update = async function () {
        try {
            await $scope.settings.save();
            $('#toast1').toast('show');
            $scope.$apply();
        }
        catch (e) { $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Cannot write to MongoDB settings file.', 'Error: MongoDB'); }
    }

    getSettings();

}

controllerFn.$inject = ['$scope', '$rootScope', 'mongoDb'];


export default controllerFn;
