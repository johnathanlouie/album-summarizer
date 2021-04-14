function controllerFn($scope, $rootScope, mongoDb) {

    function keyHandler(event) {
        switch (event.key) {
            case "1":
                $scope.category = 'environment';
                break;
            case "2":
                $scope.category = 'people';
                break;
            case "3":
                $scope.category = 'object';
                break;
            case "4":
                $scope.category = 'hybrid';
                break;
            case "5":
                $scope.category = 'animal';
                break;
            case "6":
                $scope.category = 'food';
                break;
            case "+":
                if ($scope.rating < 3) { $scope.rating++; }
                break;
            case "-":
                if ($scope.rating > 1) { $scope.rating--; }
                break;
            case "Enter":
                $scope.submit();
                break;
        }
        $scope.$apply();
    }

    $(document).keydown(keyHandler);

    this.$onDestroy = function () {
        $(document).off('keydown', keyHandler);
    };

    $scope.ratingText = function () {
        switch ($scope.unlabeledData.rating) {
            case 1:
                return 'Worse Than Average';
            case 2:
                return 'Average';
            case 3:
                return 'Better Than Average';
            default:
                return 'Error: Unknown value'
        }
    };

    async function getMongoCollections() {
        $scope.dbCollections = null;
        $scope.selectedCollection = null;
        try {
            $rootScope.$broadcast('LOADING_MODAL_SHOW', 'MongoDB', 'Retrieving list...');
            $scope.dbCollections = await mongoDb.collections();
            if ($scope.dbCollections.length > 0) {
                $scope.selectedCollection = $scope.dbCollections[0];
            }
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
        }
        catch (e) {
            console.error(e);
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
            $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: MongoDB Query', 'Something happened while retrieving collections from MongoDB.');
        }
        $scope.$apply();
    }

    const nullData = {
        class: 'hybrid',
        image: 'image-placeholder.png',
        rating: 2,
        _id: '####',
    };

    async function getUnlabeledData() {
        $scope.unlabeledData = nullData;
        try {
            $rootScope.$broadcast('LOADING_MODAL_SHOW', 'MongoDB', 'Querying...');
            let data = await mongoDb.sample({ isLabeled: false }, 1, $scope.selectedCollection);
            if (data.length === 0) {
                $scope.unlabeledData = nullData;
                $rootScope.$broadcast('LOADING_MODAL_HIDE');
                $rootScope.$broadcast('ERROR_MODAL_SHOW', null, 'Notice: MongoDB Query', 'All data points in this collection were labeled.');
            }
            else {
                $scope.unlabeledData = data[0];
                $scope.unlabeledData.rating = 2;
                $scope.unlabeledData.class = 'hybrid';
                $rootScope.$broadcast('LOADING_MODAL_HIDE');
            }
        }
        catch (e) {
            console.error(e);
            $rootScope.$broadcast('LOADING_MODAL_HIDE');
            $rootScope.$broadcast('ERROR_MODAL_SHOW', e, 'Error: MongoDB Query', 'Something happened while getting an unlabeled document from MongoDB.');
        }
        $scope.$apply();
    }

    $scope.getUnlabeledData = getUnlabeledData;

    $scope.submit = async function (event) { getUnlabeledData(); };

    $scope.unlabeledData = nullData;
    $scope.dbCollections = null;
    $scope.selectedCollection = null;
    getMongoCollections();

}

controllerFn.$inject = ['$scope', '$rootScope', 'mongoDb'];


export default controllerFn;
