const angular = require('angular');
const _ = require('lodash');
const $ = require('jquery');
import ModalService from '../../services/modal.service.js';
import MongoDbService from '../../services/mongodb.service.js';
import UsersService from '../../services/users.service.js';


/**
 * @param {angular.IScope} $scope 
 * @param {MongoDbService} mongoDb 
 * @param {ModalService} modal 
 * @param {UsersService} users 
 */
function LabelDataViewController($scope, mongoDb, modal, users) {

    $scope.selectUserScreen = true;
    $scope.users = users;

    function keyHandler(event) {
        switch (event.key) {
            case '1':
                $scope.unlabeledData.class = 'environment';
                $scope.$apply();
                break;
            case '2':
                $scope.unlabeledData.class = 'people';
                $scope.$apply();
                break;
            case '3':
                $scope.unlabeledData.class = 'object';
                $scope.$apply();
                break;
            case '4':
                $scope.unlabeledData.class = 'hybrid';
                $scope.$apply();
                break;
            case '5':
                $scope.unlabeledData.class = 'animal';
                $scope.$apply();
                break;
            case '6':
                $scope.unlabeledData.class = 'food';
                $scope.$apply();
                break;
            case '+':
                if ($scope.unlabeledData.rating < 3) {
                    $scope.unlabeledData.rating++;
                    $scope.$apply();
                }
                break;
            case '-':
                if ($scope.unlabeledData.rating > 1) {
                    $scope.unlabeledData.rating--;
                    $scope.$apply();
                }
                break;
            case 'Enter':
                $scope.submit();
                break;
        }
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

    function getMongoCollections() {
        $scope.selectedCollection = null;
        modal.showLoading('RETRIEVING...');
        return users.load().then(
            () => modal.hideLoading(),
            e => {
                console.error(e);
                modal.hideLoading();
                modal.showError(e, 'ERROR: MongoDB', 'Error while fetching users');
            },
        );
    }

    const nullData = {
        class: 'hybrid',
        image: 'image-placeholder.png',
        rating: 2,
        _id: '####',
    };

    function getUnlabeledData() {
        $scope.unlabeledData = nullData;
        modal.showLoading('RETRIEVING...');
        return mongoDb.sample({ isLabeled: false }, 1, $scope.selectedCollection).then(
            data => {
                modal.hideLoading();
                if (data.length === 0) {
                    $scope.unlabeledData = nullData;
                    modal.showError(null, 'NOTICE: MongoDB', 'All data points in this collection were labeled');
                }
                else {
                    $scope.selectUserScreen = false;
                    $scope.unlabeledData = data[0];
                    $scope.unlabeledData.rating = 2;
                    $scope.unlabeledData.class = 'hybrid';
                    $scope.unlabeledData.collection = $scope.selectedCollection;
                }
            },
            e => {
                console.error(e);
                modal.hideLoading();
                modal.showError(e, 'ERROR: MongoDB', 'Error while fetching an unlabeled document from MongoDB');
            },
        );
    }

    $scope.getUnlabeledData = getUnlabeledData;

    function updateOne() {
        modal.showLoading('UPDATING...');
        return mongoDb.findOneAndUpdate(
            $scope.unlabeledData.collection,
            { _id: $scope.unlabeledData._id },
            {
                rating: $scope.unlabeledData.rating,
                class: $scope.unlabeledData.class,
                isLabeled: true,
            },
        ).catch(e => {
            console.error(e);
            modal.hideLoading();
            modal.showError(e, 'ERROR: MongoDB', 'Error while updating an document');
        });
    }

    $scope.submit = function (event) {
        return updateOne().then(() => getUnlabeledData());
    };

    $scope.isNullData = function () { return $scope.unlabeledData === nullData; };

    $scope.confirmDeleteUser = () => $('#deleteUserModal').modal();

    $scope.deleteUser = function () {
        modal.showLoading('Removing user...');
        return mongoDb.dropCollection($scope.selectedCollection).then(
            () => users.load(true)
        ).then(
            () => modal.hideLoading()
        ).catch(
            e => {
                console.error(e);
                modal.hideLoading();
                modal.showError(e, 'ERROR: Delete User', 'Error during deleting a user')
            }
        );
    };

    $scope.unlabeledData = nullData;
    $scope.selectedCollection = null;
    getMongoCollections();

}

LabelDataViewController.$inject = ['$scope', 'mongoDb', 'modal', 'users'];


export default LabelDataViewController;
