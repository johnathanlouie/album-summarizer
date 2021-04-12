function controllerFn($scope) {
    function keyEventHandler(event) {
        switch (event.key) {
            case "1":
                event.preventDefault();
                $("#a1").prop("checked", true);
                break;
            case "2":
                event.preventDefault();
                $("#a2").prop("checked", true);
                break;
            case "3":
                event.preventDefault();
                $("#a3").prop("checked", true);
                break;
            case "4":
                event.preventDefault();
                $("#a4").prop("checked", true);
                break;
            case "5":
                event.preventDefault();
                $("#a5").prop("checked", true);
                break;
            case "6":
                event.preventDefault();
                $("#a6").prop("checked", true);
                break;
            case "Enter":
                event.preventDefault();
                $("#form1").submit();
                break;
            case "+":
                event.preventDefault();
                $("#counter").val(function (index, value) {
                    return parseInt(value, 10) + 1;
                });
                $("#counter").change();
                break;
            case "-":
                event.preventDefault();
                $("#counter").val(function (index, value) {
                    return parseInt(value, 10) - 1;
                });
                $("#counter").change();
                break;
        }
    }

    function rateEventHandler(event) {
        switch ($("#counter").number()) {
            case 1:
                $("#ratingText").text("Worse Than Average");
                break;
            case 2:
                $("#ratingText").text("Average");
                break;
            case 3:
                $("#ratingText").text("Better Than Average");
                break;
        }
    }

    $("body").keypress(keyEventHandler);
    $("#counter").change(rateEventHandler);
}

controllerFn.$inject = ['$scope'];


export default controllerFn;
