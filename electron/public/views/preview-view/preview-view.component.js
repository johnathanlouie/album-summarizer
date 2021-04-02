'use strict';


angular.module('views.previewView').component('previewView', {
    templateUrl: 'views/preview-view/preview-view.template.html',
    controller: ['$scope', function ($scope) {
        for (let i of ["file1", "file2"]) {
            $(`#${i}`).change(function () {
                let filename = $(`#${i}`).prop("files")[0].name;
                $(`label[for="${i}"]`).text(filename);
            });
        }


        const DICT = {
            1: "Environment",
            2: "People",
            3: "Object",
            4: "Hybrid",
            5: "Animal",
            6: "Food",
        };


        class Data {
            constructor() {
                this.images = undefined;
                this.classes = undefined;
                this.queue = [];
            }

            next() {
                if (!Array.isArray(this.images)) {
                    alert("Image list not found.");
                } else if (this.images.length === 0) {
                    alert("Image list is empty.");
                } else if (this.images.length === 1) {
                    $("#img1").attr("src", this.images[0]);
                    $("#classification").text(DICT[Number(this.classes[0])]);
                } else {
                    if (this.queue.length === 0) {
                        this.queue = _.shuffle(_.range(this.images.length));
                    }
                    let i = this.queue.pop();
                    let imgUrl = this.images[i];
                    let class_ = Number(this.classes[i]);
                    $("#img1").attr("src", imgUrl);
                    $("#classification").text(DICT[class_]);
                }
            }

            set(images, classes) {
                this.images = images;
                this.classes = classes;
                this.queue = [];
                this.next();
            }
        }


        const DATA = new Data();


        function reset() {
            $("#img1").attr("src", "image-placeholder.png");
            $("#classification").text("Class");
        }


        $("#loadButton").click(function (event) {
            event.preventDefault();
            reset();
            // read files, then parse
            let images = $("#file1").readText().then(file => file[0].split("\n"));
            let classes = $("#file2").readText().then(file => file[0].split("\n"));
            // then wait for both, send file data to controller
            Promise.all([images, classes]).then(retVal => DATA.set(...retVal));
        });

        
        $("#nextButton").click(event => DATA.next());
    }],
});
