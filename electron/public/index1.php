<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Album Summarizer - Rate Images</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" crossorigin="anonymous">
        <script>window.jQuery = window.$ = require('jquery');</script>
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js" crossorigin="anonymous"></script>
    </head>

    <body>

        <nav class="navbar navbar-expand-sm navbar-dark bg-dark shadow mb-3">
            <a class="navbar-brand" href="index.html">
                <svg class="bi mb-1" width="18" height="18" fill="currentColor">
                <use xlink:href="bootstrap-icons.svg#house-fill"/>
                </svg>
            </a>
            <ul class="navbar-nav">
                <li class="nav-item">
                    <a class="nav-link" href="checkrate.html">Check Rate</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="hist.html">Histogram</a>
                </li>
                <li class="nav-item active">
                    <a class="nav-link" href="index1.php">Rate Images</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="preview.html">Preview</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="siftsimilarity.html">SIFT Similarity</a>
                </li>
            </ul>
        </nav>

        <div class="container-fluid">
            <?php
            $mysqli = new mysqli("localhost", "root", "", "photodata");
            $res = $mysqli->query("SELECT * FROM table1 WHERE done=0 ORDER BY RAND() LIMIT 1;");
            $row = $res->fetch_assoc();
            $url = $row["url"];
            $urlen = str_replace('#', '%23', $url);
            $id = $row["id"];
            echo "<img src='$urlen' style='float: left;'>";
            ?>
            <form name="classrating" method="post" id="form1">
                <input type="radio" name="phototype" id="a1" value="environment">1 environment<br>
                <input type="radio" name="phototype" id="a2" value="people">2 people<br>
                <input type="radio" name="phototype" id="a3" value="object">3 object<br>
                <input type="radio" name="phototype" id="a4" value="hybrid" checked>4 hybrid<br>
                <input type="radio" name="phototype" id="a5" value="animal">5 animal<br>
                <input type="radio" name="phototype" id="a6" value="food">6 food<br>
                <input type="number" min="1" max="3" step="1" id="counter" name="rating" value="2" size="1" style="font-size:50px; width:50px;"> rating<br>
                <input value="<?php echo $url; ?>" name="photourl" size="100" readonly><br>
                <input value="<?php echo $id; ?>" name="photoid" size="100" readonly><br>
                <input type="submit">
            </form>
            <?php
            if (isset($_POST["photoid"]) && isset($_POST["phototype"]) && isset($_POST["rating"])) {
            $postid = $_POST["photoid"];
            $posttype = $_POST["phototype"];
            $postrating = $_POST["rating"];
            echo "$postid, $posttype, $postrating<br>";
            if (!$mysqli->query("UPDATE table1 SET rating=$postrating, class='$posttype', done=1 WHERE id=$postid;")) {
            echo "update fail";
            } else {
            echo "update good";
            }
            }
            ?>
        </div>

        <script>
            function keyEventHandler(event)
            {
                event.preventDefault();
                switch (event.which)
                {
                    case 49:
                        $("#a1").prop("checked", true);
                        break;
                    case 50:
                        $("#a2").prop("checked", true);
                        break;
                    case 51:
                        $("#a3").prop("checked", true);
                        break;
                    case 52:
                        $("#a4").prop("checked", true);
                        break;
                    case 53:
                        $("#a5").prop("checked", true);
                        break;
                    case 54:
                        $("#a6").prop("checked", true);
                        break;
                    case 13:
                        $("#form1").submit();
                        break;
                    case 43:
                        $('#counter').val(function (i, oldval) {
                            return parseInt(oldval, 10) + 1;
                        });
                        break;
                    case 45:
                        $('#counter').val(function (i, oldval) {
                            return parseInt(oldval, 10) - 1;
                        });
                        break;
                }
            }

            $("body").keypress(keyEventHandler);
        </script>

    </body>
</html>
