angular.module('services').factory('queryServer', ['$http', function ($http) {
    /**
    * 
    * @param {string} dir 
    */
    async function queryServer(dir) {
        var response = await $http.post('http://localhost:8080/run', { url: dir });
        if (response.data.status === 0) {
            return response.data.data;
        }
        else if (response.data.status === 2) {
            throw new Error('Architecture/dataset mismatch');
        }
        else {
            throw new Error('Unknown server error');
        }
    }

    return queryServer;
}]);
