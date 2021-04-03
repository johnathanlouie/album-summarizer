'use strict';


angular.module('views.siftSimilarityView').component('siftSimilarityView', {
    templateUrl: 'views/sift-similarity-view/sift-similarity-view.template.html',
    controller: ['$scope', function ($scope) {
        const MODEL = {
            url: null,
            rating: null,
            isReady: false,
            render: function () {
                if (this.isReady) {
                    $("#tbl1").empty();
                    let arr = [];
                    for (let i in this.url) {
                        let picId = $("#id1").number();
                        arr.push({
                            rating: this.rating[picId][i],
                            url: this.url[i],
                            id: i
                        });
                    }
                    arr.sort((a, b) => b.rating - a.rating);
                    for (let i of arr) {
                        var tr = $("<tr>").appendTo('#tbl1');
                        var tdId = $("<td>").text(i.id).appendTo(tr);
                        var tdImg = $("<td>").appendTo(tr);
                        $("<img>").attr("src", i.url).appendTo(tdImg);
                        var tdRate = $("<td>").text(i.rating).appendTo(tr);
                    }
                }
            }
        };

        $scope.loadFiles = function () {
            MODEL.isReady = false;
            // read files, then parse
            let urlFile = $("#file1").readText().then(file => file[0].trim().split("\n"));
            let ratingFile = $("#file2").readText().then(file => JSON.parse(file[0].trim()));
            // then wait for both, send file data to controller
            Promise.all([urlFile, ratingFile]).then(retVal => {
                [MODEL.url, MODEL.rating] = retVal;
                MODEL.isReady = true;
            });
        };

        function decInc(event) {
            let newVal = $("#id1").number();
            switch (event.keyCode) {
                case 43:
                    $("#id1").val(newVal + 1);
                    break;
                case 45:
                    $("#id1").val(newVal - 1);
                    break;
            }
            MODEL.render();
        }

        $("body").keypress(decInc);
    }],
});
