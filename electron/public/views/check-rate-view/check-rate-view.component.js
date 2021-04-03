'use strict';


angular.module('views.checkRateView').component('checkRateView', {
    templateUrl: 'views/check-rate-view/check-rate-view.template.html',
    controller: ['$scope', function ($scope) {
        for (let i of ["file1", "file2", "file3"]) {
            $(`#${i}`).change(function () {
                let filename = $(`#${i}`).prop("files")[0].name;
                $(`label[for="${i}"]`).text(filename);
            });
        }

        function readerCallback(retVal) {
            let [images, truth, pred] = retVal;
            for (let i in images) {
                let tr = $("<tr>").appendTo("#table1");
                let td1 = $("<td>").appendTo(tr);
                let td2 = $("<td>").text(truth[i]).appendTo(tr);
                let td3 = $("<td>").text(pred[i]).appendTo(tr);
                let img = $("<img>").attr("src", images[i]).addClass("rate-thumbnail img-thumbnail").appendTo(td1);
            }
        }

        $("#loadButton").click(function (e) {
            e.preventDefault();
            $("#table1").empty();
            // read files, then parse
            let images = $("#file1").readText().then(file => file[0].split("\n"));
            let truths = $("#file2").readText().then(file => file[0].split("\n"));
            let predic = $("#file3").readText().then(file => file[0].split("\n"));
            // then wait for both, send file data to controller
            Promise.all([images, truths, predic]).then(readerCallback);
        });
    }],
});
