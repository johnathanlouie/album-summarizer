function controllerFn($scope) {

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
        switch ($scope.rating) {
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

    $scope.submit = function (event) { };

    $scope.category = 'hybrid';
    $scope.image = 'image-placeholder.png';
    $scope.rating = 2;
    $scope.id = '####';

}

controllerFn.$inject = ['$scope'];


export default controllerFn;
