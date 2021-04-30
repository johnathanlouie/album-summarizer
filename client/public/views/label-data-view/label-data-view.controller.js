const angular = require('angular');
const _ = require('lodash');
import ModalService from '../../services/modal.service.js';
import MongoDbService from '../../services/mongodb.service.js';
import UsersService from '../../services/users.service.js';


/**
 * @param {angular.IScope} $scope 
 * @param {MongoDbService} mongoDb 
 * @param {ModalService} modal 
 * @param {UsersService} users 
 */
function controllerFn($scope, mongoDb, modal, users) {

    $scope.selectUserScreen = true;
    $scope.users = users;

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
        $scope.selectedCollection = null;
        try {
            modal.showLoading('RETRIEVING...');
            await users.load();
            modal.hideLoading();
        }
        catch (e) {
            console.error(e);
            modal.hideLoading();
            modal.showError(e, 'ERROR: MongoDB', 'Error while fetching users');
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
            modal.showLoading('RETRIEVING...');
            let data = await mongoDb.sample({ isLabeled: false }, 1, $scope.selectedCollection);
            if (data.length === 0) {
                $scope.unlabeledData = nullData;
                modal.hideLoading();
                modal.showError(null, 'NOTICE: MongoDB', 'All data points in this collection were labeled');
            }
            else {
                $scope.selectUserScreen = false;
                $scope.unlabeledData = data[0];
                $scope.unlabeledData.rating = 2;
                $scope.unlabeledData.class = 'hybrid';
                $scope.unlabeledData.collection = $scope.selectedCollection;
                modal.hideLoading();
            }
        }
        catch (e) {
            console.error(e);
            modal.hideLoading();
            modal.showError(e, 'ERROR: MongoDB', 'Error while fetching an unlabeled document from MongoDB');
        }
        $scope.$apply();
    }

    $scope.getUnlabeledData = getUnlabeledData;

    async function updateOne() {
        try {
            modal.showLoading('UPDATING...');
            await mongoDb.findOneAndUpdate(
                $scope.unlabeledData.collection,
                { _id: $scope.unlabeledData._id },
                {
                    rating: $scope.unlabeledData.rating,
                    class: $scope.unlabeledData.class,
                    isLabeled: true,
                },
            );
        }
        catch (e) {
            console.error(e);
            modal.hideLoading();
            modal.showError(e, 'ERROR: MongoDB', 'Error while updating an document');
        }
    }

    $scope.submit = async function (event) {
        await updateOne();
        await getUnlabeledData();
    };

    $scope.isNullData = function () { return $scope.unlabeledData === nullData; }

    $scope.unlabeledData = nullData;
    $scope.selectedCollection = null;
    getMongoCollections();

}

controllerFn.$inject = ['$scope', 'mongoDb', 'modal', 'users'];


export default controllerFn;
