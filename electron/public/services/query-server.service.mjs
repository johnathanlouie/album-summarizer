function f($http) {

    /**
     * 
     * @param {string} dir 
     */
    async function queryServer(dir) {
        var response = await $http.post('http://localhost:8080/run', { url: dir });
        return response.data.data;
    }

    return queryServer;
}

f.$inject = ['$http'];


export default f;
