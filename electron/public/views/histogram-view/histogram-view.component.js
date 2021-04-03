'use strict';


angular.module('views.histogramView').component('histogramView', {
    templateUrl: 'views/histogram-view/histogram-view.template.html',
    controller: ['$scope', function ($scope) {
        for (let i of ["file1", "file2"]) {
            $(`#${i}`).change(function () {
                let filename = $(`#${i}`).prop("files")[0].name;
                $(`label[for="${i}"]`).text(filename);
            });
        }

        function upsert(map, index, value) {
            let arr = map.get(index);
            if (!arr) {
                arr = [];
                map.set(index, arr);
            }
            arr.push(value);
        }

        function toMap(imgs, clusterIds) {
            var m = new Map();
            for (let i in imgs) {
                var v = imgs[i];
                var k = clusterIds[i];
                upsert(m, k, v);
            }
            return m;
        }

        function drawClusters(clusters) {
            for (let i of clusters.entries()) {
                let clusterId = i[0];
                let cluster = i[1];
                let card = $("<div>").addClass("card mb-3").appendTo("#p1");
                let head = $("<h5>").addClass("card-header text-center").text(clusterId).appendTo(card);
                var body = $("<div>").addClass("card-body").appendTo(card);
                for (let url of cluster) {
                    $("<img>").attr("src", url).addClass("img-thumbnail hist-thumbnail").appendTo(body);
                }
            }
        }

        $("#loadButton").click(function (event) {
            event.preventDefault();
            $("#p1").empty();
            // read files, then parse
            let images = $("#file1").readText().then(file => file[0].split("\n"));
            let clusters = $("#file2").readText().then(file => file[0].split("\n"));
            // then wait for both, send file data to controller
            Promise.all([images, clusters]).then(retVal => drawClusters(toMap(...retVal)));
        });
    }],
});
