function imageviewerSizeHandler() {
    var whole = $('#imageviewer').height();
    var top = $('#imageviewerButtonbar').outerHeight();
    $('#imageviewerImagecontainer').height(whole - top);
}

$(window).resize(imageviewerSizeHandler);
$('#imageviewer').ready(imageviewerSizeHandler);