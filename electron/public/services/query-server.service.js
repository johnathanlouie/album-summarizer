function serviceFn($http) {

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

serviceFn.$inject = ['$http'];


export default serviceFn;
