<?php
session_start();

include "php/main-ponuka.php";
// include "privacy.php";
?>


<!DOCTYPE HTML>
<html xmlns="https://www.w3.org/1999/xhtml" xml:lang="sk" lang="sk">

<head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <meta http-equiv="Cache-Control" content="only-if-cached" />

    <title><?php if ($nazov_produktu) {
                echo $nazov_produktu . " – Gašparík - mäso s dobrým menom";
            } else {
                echo 'NAŠA PONUKA | GAŠPARÍK – Mäso s dobrým menom';
            } ?></title>
    <meta name="description" content="<?php if ($nazov_kat) {
                                            echo $nazov_kat;
                                        } else {
                                            echo 'Aktuálna ponuka';
                                        } ?>" />
    <meta name="googlebot" content="index,follow" />
    <meta name="author" content="Milan Martiš info@appdesign.sk" />

    <meta property="og:type" content="website" />
    <meta property="og:title" content="<?php if ($nazov_produktu) {
                                            echo $nazov_produktu;
                                        } else {
                                            echo 'NAŠA PONUKA | GAŠPARÍK – Mäso s dobrým menom';
                                        } ?>" />
    <meta property="og:description" content="<?php if ($nazov_kat) {
                                                    echo $nazov_kat;
                                                } else {
                                                    echo 'Aktuálna ponuka';
                                                } ?>" />
    <meta property="og:image" content="<?php if ($url_obrazok_maly) {
                                            echo $url_obrazok_maly;
                                        } else {
                                            echo 'https://www.gasparikmasovyroba.sk/img/logo-plocha.png';
                                        } ?>" />
    <meta property="og:url" content="https://www.gasparikmasovyroba.sk/ponuka/<?php echo $slug ?>" />
    <meta property="og:locale" content="sk_SK" />
    <meta property="og:site_name" content="GAŠPARÍK – Mäso s dobrým menom">
    <link rel="canonical" href="https://www.gasparikmasovyroba.sk/ponuka/<?php echo $slug ?>" />

    <link rel="schema.dcterms" href="https://purl.org/dc/terms/">
    <meta name="DC.title" content="<?php if ($nazov_produktu) {
                                        echo $nazov_produktu;
                                    } else {
                                        echo 'NAŠA PONUKA | MÄSOVÝROBA GAŠPARÍK | Mäso s dobrým menom';
                                    } ?>" />
    <meta name="DC.subject" content="MÄSOVÝROBA GAŠPARÍK" />
    <meta name="DC.description" content="<?php if ($nazov_kat) {
                                                echo $nazov_kat;
                                            } else {
                                                echo 'Aktuálna ponuka';
                                            } ?>" />
    <meta name="DC.language" content="sk-SK" />

    <meta name="robots" content="index, follow" />

    <meta name="viewport" content="width=device-width, initial-scale=1.0" />


    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-KyZXEAg3QhqLMpG8r+8fhAXLRk2vvoC2f3B09zVXn8CA5QIVfZOJ3BCsw2P0p/We" crossorigin="anonymous">

    <link rel="stylesheet" type="text/css" media="all" href="css/style.css" />

    <link rel="stylesheet" type="text/css" media="all" href="../style/style.css" />
    <link rel="stylesheet" href="../style/fancybox/jquery.fancybox.css">


    <link href="https://cdn.jsdelivr.net/npm/bootstrap@4.4.1/dist/css/bootstrap.min.css" rel="stylesheet">


    <link rel="stylesheet" href="css/fancybox.css">


    <style>
        input[type="submit"] {
            padding: 0 30px;
            background: #7e4332;
            color: #fff;
            cursor: pointer;
            border: none;
            text-transform: uppercase;
            font-weight: bold;
            line-height: 50px;
            border-radius: 30px;
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
        }
    </style>
</head>

<!--
  <img src="../ponuka/img/bezlepku.png" title="bez lepku" alt="bez lepku">
  <img src="../ponuka/img/dym.png" title="údené na bukovej štiepke" alt="údené na bukovej štiepke">
  <img src="../ponuka/img/para-cierna.png" title="varené v pare" alt="varené v pare">
  <img src="../ponuka/img/ruka.png" title="ručne spracované" alt="ručne spracované">
  <img src="../ponuka/img/bezecok.png" title="bez éčok" alt="bez éčok">
  
  
  <img src="../ponuka/img/ruka.png" title="ocenené na Danubius Gastro" alt="ocenené na Danubius Gastro">
  <img src="../ponuka/img/znacka1.png" title="značka kvality 1. stupňa" alt="značka kvality 1. stupňa">
  <img src="../ponuka/img/znacka2.png" title="značka kvality 2. stupňa" alt="značka kvality 2. stupňa">

-->

<body>
    <header class="large">



        <div id="header" style="z-index:2;">

            <div id="logo" class="tranzzz">
                <a href="../"><img src="../app/images/gasparik-logo-zastera.svg" alt="GAŠPARÍK | Mäso a mäsové lahôdky" class="logo" /></a>
            </div>

            <div id="pattern" class="pattern">
                <a href="#menu" class="menu-link">MENU</a>
                <div id="menu" class="menu" role="navigation">
                    <ul class='level-1'>
                        <!--   <li><a href='./' title="ÚVOD">ÚVOD</a></li> -->
                        <li><a href='../o-nas' title="O NÁS">O nás</a></li>
                        <li><a href='../nakupna-karta' title="Nákupná karta">Vernostná karta</a></li>
                        <li><a class=' active' href='../ponuka/' title="NAŠA PONUKA">Naša ponuka</a></li>
                        <li><a href='../recepty' title="Tradičné recepty">Tradičné recepty</a></li>
                        <li><a href='../nase-predajne' title="NAŠE PREDAJNE">Naše predajne</a></li>
                        <!-- <li><a href='pracovne-ponuky' title="PRACOVNÉ PONUKY">PRACOVNÉ PONUKY</a></li> -->
                        <li><a href='https://www.gasparikmasovyroba.sk/#obedove-menu' title="Obedové menu">BISTRO</a></li>     

                        <li><a href='../kontakt' title="KONTAKT">Kontakt</a></li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="kolaz-podstranka" style="background-image:url(../img/titulky/nasa-ponuka.jpg)" width="100%">
        </div>
    </header>







    <div id="content">



        <div class="biela" id="bek">



            <div class="obsah" style="margin-top:-70px;">


                <div class="container">

                    <?php include_once "php/panel.php"; ?>


                    <!-- ak sa nenajde produkt -->
                    <?php

                    // if ($_GET["id"] == "" AND $url_obrazok_maly == "") {
                    //     echo '

                    //     <div id="itemz-view" class="container">
                    //     <div class="card">
                    //     <div class="card-body">
                    //     <div class="row" style="text-align:center"><h5>
                    //     Nenašiel sa žiadny produkt. <a href="/ponuka/">Pozri všetky kategórie</a>
                    //     </h5></div>
                    //     </div>
                    //     </div>
                    //     </div>

                    //     ';
                    // }
                    ?>

                </div>


                <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">

                <div id="itemz-view" class="container" <?php if ($_GET["id"] != "" and $url_obrazok_maly) {
                                                            echo "style=\"display:block;\"";
                                                        } else {
                                                            echo "style=\"display:none;\"";
                                                        }
                                                        ?>>



                    <div class="card">

                        <div class="card-body">

                            <div class="row">
                                <?php
                                if ($label2 != "") {
                                    if ($label2 == 1) {
                                        echo "<div style=\"z-index:1;position:absolute;width: 100%;display:block;\"><img src=\"../img/produkty/znacka-sk-1st.png\" alt=\Značka kvality 1. stupeň\" title=\"Značka kvality 1. stupeň\" width=\"50\"></div>";
                                    } else {
                                        echo "<div style=\"z-index:1;position:absolute;width: 100%;display:block;\"><img src=\"../img/produkty/znacka-sk-2st.png\" alt=\Značka kvality 2. stupeň\" title=\"Značka kvality 2. stupeň\" width=\"50\"></div>";
                                    }
                                }
                                //  echo $label2;

                                ?>
                                <div style="margin-top:-20px;" class="col-lg-7 col-sm-6">





                                    <!-- ####  obrazok -->
                                    <div class="white-box text-center" style="padding:20px;">


                                        <div id="znackamiesto">
                                            <img <?php echo $znacka1image; ?> src="../ponuka/img/znacka1.png" title="značka kvality 1. stupňa" alt="značka kvality 1. stupňa">
                                            <img <?php echo $znacka2image; ?> src="../ponuka/img/znacka2.png" title="značka kvality 2. stupňa" alt="značka kvality 2. stupňa">
                                        </div>
                                        <div id="novinkamiesto">
                                            <img <?php echo $novinkaimage; ?> src='../ponuka/img/novinka.png' title='novinka' alt='novinka'>
                                        </div>

                                        <div id="danubiusmiesto">
                                            <img <?php echo $danubiusimage; ?> src="../ponuka/img/danubius-gastro.png" title="značka kvality 2. stupňa" alt="značka kvality 2. stupňa">
                                        </div>

                                        <div id="bezecokmiesto">
                                            <img <?php echo $bezecokimage; ?> src="../ponuka/img/bezpridanychecok.svg" title="bez pridaných éčok" alt="bez pridaných éčok">
                                        </div>
                                        <div id="grilmiesto">
                                            <img <?php echo $grilimage; ?> src="../ponuka/img/hodmanagril-gasparik.svg" title="vhodné na gril" alt="vhodné na gril">
                                        </div>


                                        <h4 <?php if ($dostupnost == "") {
                                                echo "style=\"display:none;\"";
                                            } else {
                                                echo "style=\"display:inline;\"";
                                            } ?> class="box-title mt-5"><?php echo $dostupnost; ?></h4>





                                        <a href="<?php if ($url_obrazok_maly) {
                                                        echo $url_obrazok_velky;
                                                    } else {
                                                        echo "img/logo-gasparik.png";
                                                    } ?>" data-fancybox="images"><img style="max-width: none;" id="alpha-image" src="<?php if ($url_obrazok_maly) {
                                                                                                                                            echo $url_obrazok_maly;
                                                                                                                                        } else {
                                                                                                                                            echo "img/logo-gasparik.png";
                                                                                                                                        } ?>" class="watermark" width="100%"></a>


                                    </div>
                                    <!-- ####  koniec obrazok -->

                                </div>
                                <div class="col-lg-5 col-sm-6">

                                    <h2><?php echo $nazov_produktu; ?></h2>






                                    <p <?php if ($part_img == "") {
                                            echo "style=\"display:none;\"";
                                        } else {
                                            echo "style=\"display:inline;\"";
                                        } ?>><img src="img/delenie/<?php echo $part_img; ?>" width=200>
                                    </p>


                                    <h6 <?php if ($part_name == "") {
                                            echo "style=\"display:none;\"";
                                        } else {
                                            echo "style=\"display:inline;text-align:center;\"";
                                        } ?> class="box-title mt-5"><?php //echo $part_name; 
                                                                    ?>

                                    </h6>


                                    <h5 <?php if ($nazov_popis == "") {
                                            echo "style=\"display:none;padding:0px;margin:0px;\"";
                                        } else {
                                            echo "style=\"display:inline;padding:0px;margin:0px;\"";
                                        } ?> class="box-title mt-5"></h5>
                                    <div class="popiska"><?php echo $nazov_popis; ?></div>
                                    <br>


                                    <h5 <?php if ($zlozenie == "") {
                                            echo "style=\"display:none;padding:0px;margin:0px;\"";
                                        } else {
                                            echo "style=\"display:inline;padding:0px;margin:0px;\"";
                                        } ?> class="box-title mt-5">Zloženie výrobku:</h5>
                                    <p><?php echo $zlozenie; ?></p>



                                    <h5 <?php if ($vyziva == "") {
                                            echo "style=\"display:none;padding:0px;margin:0px;\"";
                                        } else {
                                            echo "style=\"display:inline;padding:0px;margin:0px;\"";
                                        } ?> class="box-title mt-5">Výživové údaje</h5>
                                    <p><?php echo $vyziva; ?></p>



                                    <h5 <?php if ($poznamka == "") {
                                            echo "style=\"display:none;padding:0px;margin:0px;\"";
                                        } else {
                                            echo "style=\"display:none;padding:0px;margin:0px;\"";
                                        } ?> class="box-title mt-5">Poznámka</h5>
                                    <p><?php echo $poznamka; ?></p>

                                    <div>
                                        <h4 <?php echo $priceonoff; ?>><input type="submit" onclick="javascript:location.href='https://www.gasparikmasovyroba.sk/app/mapa-app-full.html'" value="Tel. Objednávka"></h4>
                                    </div>



                                    <?php if ($part_img != "") {
                                        include "db2.php";
                                        $db = new PDO($dsn, $username, $password, $options);



                                        $stmt3 = $db->query("SELECT rn.id AS id, rn.shortname AS shortname, rn.img AS img FROM recipe_ingredients AS ring 
                                LEFT JOIN recipe AS re ON re.ingid = ring.id
                                JOIN recipe_name AS rn ON rn.id = re.recid
                                WHERE ring.ideitem = $id
                                GROUP BY ring.id
    ");

                                        echo "<div class='row'>";



                                        while ($row = $stmt3->fetch(PDO::FETCH_ASSOC)) {

                                            echo "<div class='column'><center><span>Pozrite si recept:</span>
    <a class='link-viac2' href='../recepty#nazov-receptu' onclick='recept(" . $row["id"] . ");'>
    <img width='222' src='/img/recepty/" . $row["img"] . "'>
    
    <div></div>
    
    </a></center></div>
    ";
                                        }

                                        echo "</div>";
                                    } ?>



                                    <div style="opacity:1;">
                                        <h4 class="box-title mt-5"></h4>
                                        <div <?php echo $varime_parky; ?>><img width=65 src="../ponuka/img/varimeparky.svg" title="ako variť párky" alt="ako variť párky">ohrievajte 5 min. pri 90°C</div>

                                        <div <?php echo $bezlepkuimage; ?>><img width=45 src="../ponuka/img/bezlepku.png" title="bez lepku" alt="bez lepku">&nbsp bez lepku</div>
                                        <div <?php echo $udeneimage; ?>><img width=45 src="../ponuka/img/dym.png" title="údené na bukovej štiepke" alt="údené na bukovej štiepke">&nbsp údené na bukovej štiepke</div>
                                        <div <?php echo $paraimage; ?>><img width=45 src="../ponuka/img/para-cierna.png" title="varené v pare" alt="varené v pare">&nbsp varené v pare</div>
                                        <div <?php echo $rucneimage; ?>><img width=45 src="../ponuka/img/ruka.png" title="ručne spracované" alt="ručne spracované">&nbsp ručne spracované</div>
                                        <div <?php echo $bezecokimage; ?>><img width=45 src="../ponuka/img/bezpridanychecok.svg" title="bez pridaných éčok" alt="bez éčok">&nbsp bez pridaných éčok</div>
                                    </div>


                                    <div>
                                        <h1 <?php echo $priceonoff; ?>><?php echo "" . $price . " <font style=\"padding:0px;font-size:45%;opacity:0.3;\">€ /ks</font>" ?></h1>
                                    </div>


                                    <!--  id="vernostnacenamiesto"  -->
                                    <div <?php echo $price2onoff; ?>>
                                        <?php echo $price2 ?>
                                    </div>



                                </div>
                                <div class="col-lg-12 col-md-12 col-sm-12">

                                    <?php if ($trvanlivost || $weight  ||  $skladovanie) {
                                        echo '<h5 class="box-title mt-5">Ďalšie informácie</h5>';
                                    }
                                    ?>
                                    <div class="table-responsive">
                                        <table class="table table-striped table-product">
                                            <tbody>
                                                <tr>
                                                    <?php if ($weight) {
                                                        echo "<td width=\"190\">Váha</td>";
                                                    } ?>
                                                    <?php if ($trvanlivost) {
                                                        echo "<td width=\"190\">Trvanlivosť</td>";
                                                    } ?>
                                                    <?php if ($skladovanie) {
                                                        echo "<td width=\"190\">Skladovanie</td>";
                                                    } ?>


                                                </tr>
                                                <tr>
                                                    <?php if ($weight) {
                                                        if ($weight > 999) {
                                                            echo "<td>" . ($weight / 1000) . " kg</td>";
                                                        } else {
                                                            echo "<td>" . ($weight) . " g</td>";
                                                        }
                                                    } ?>
                                                    <?php if ($trvanlivost) {
                                                        echo "<td>" . $trvanlivost . " </td>";
                                                    }
                                                    ?>
                                                    <?php if ($skladovanie) {
                                                        echo "<td>" . $skladovanie . " </td>";
                                                    }
                                                    ?>


                                                </tr>


                                            </tbody>
                                        </table>
                                        <?php
                                        if ($alergeny) {
                                        ?>
                                            <table class="table table-striped table-product">
                                                <tbody>
                                                    <tr>
                                                        <td width="190">Alergény</td>
                                                    </tr>
                                                    <tr>
                                                        <td><?php echo $alergeny; ?></td>
                                                    </tr>

                                                </tbody>
                                            </table>
                                        <?php
                                        }
                                        ?>

                                    </div>
                                </div>
                            </div>
                        </div>


                        <center><img src="img/gasparik-maso.svg" width="80%" alt=""></center>

                        <center>
                            <h3 class="box-title mt-5">Ďalšie produkty</h3>
                        </center>
                        <div class="row pt-3 pb-5 mb-3">


                            <div <?php if ($ideminus == "") {
                                        echo "style=\"display:inline;\"";
                                        $minus = "#";
                                    } else {
                                        echo "style=\"display:inline;\"";
                                        $minus = $ideminus;
                                    } ?> class="col-sm-6 mb-3">

                                <center><?php if ($nameminus) { ?> <a href="<?php echo $minus ?>"><img src="<?php if ($imageminus) {
                                                                                                                echo $imageminus;
                                                                                                            } else {
                                                                                                                echo "img/logo-gasparik.png";
                                                                                                            } ?>" class="img-responsive" width="60%"></a><?php } ?>
                                    <h5><?php if ($nameminus) { ?><a class="link-viac3" id="prevLink" href="<?php echo $minus ?>">
                                                <?php echo "<< " . $nameminus; ?></a><?php } else { ?><img src="img/logo-gasparik.png" class="img-responsive" width="60%"><?php  } ?>
                                    </h5>
                                </center>

                            </div>

                            <div <?php if ($ideplus == "") {
                                        echo "style=\"display:inline;\"";
                                        $plus = "#";
                                    } else {
                                        echo "style=\"display:inline;\"";
                                        $plus = $ideplus;
                                    } ?> class="col-sm-6 mb-3">
                                <center><?php if ($nameplus) { ?> <a href="<?php echo $plus ?>"><img src="<?php if ($imageplus) {
                                                                                                                echo $imageplus;
                                                                                                            } else {
                                                                                                                echo "img/logo-gasparik.png";
                                                                                                            } ?>" class="img-responsive" width="60%"></a><?php } ?>
                                    <h5><?php if ($nameplus) { ?><a class="link-viac3" id="nextLink" href="<?php echo $plus ?>"><?php echo $nameplus; ?> >></a><?php } else { ?><img src="img/logo-gasparik.png" class="img-responsive" width="60%"><?php  } ?></h5>
                                </center>

                            </div>

                        </div>

                    </div>
                </div>





                <div id="itemz-list" class="container" <?php if ($_GET["id"] != "") {
                                                            echo "style=\"display:none;\"";
                                                        } else {
                                                            echo "style=\"display:block;\"";
                                                        } ?>>



                    <div class="card">



                        <div class="card-body">
                            <center>
                                <div class="itemz"></div>
                            </center>

                        </div>
                    </div>


                </div>

            </div>

        </div>
    </div>



    <?php require_once("../scripty.php"); ?>
    <?php require_once("../scripty2.php"); ?>
    <?php require_once("../bottom.php"); ?>


    <script type="text/javascript">
        document.addEventListener("keyup", function(e) {
            var key = e.which || e.keyCode;
            switch (key) {
                //left arrow
                case 37:
                    document.getElementById("prevLink").click();
                    break;
                    //right arrow
                case 39:
                    document.getElementById("nextLink").click();
                    break;
            }
        });
    </script>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.4.1/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-1.10.2.min.js"></script>
    <script src="js/main.js"></script>
    <script src="js/fancybox1.js"></script>
    <script src="js/fancybox2.js"></script>
    <script src="js/watermark.jquery.min.js"></script>


    <?php
    if (isset($_GET['cat'])) {

        echo "<script>  itemzList('cat', '" . $_GET['cat'] . "');</script>";
    }
    if (isset($_GET['id'])) {

        //echo '<script>  itemzList(type2, what2)</script>';

    }

    if (isset($_POST['search'])) {

        echo '<script>  itemzList("search", "' . $_POST['search'] . '")</script>';
    }




    ?>

    <script src="../privacy/src/bootstrap-cookie-consent-settings.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-U1DAWAznBHeqEIlVSCgzq+c9gqGAJn5c/t99JyeKa9xxaYpSvHU5awsuZVVFIhvj" crossorigin="anonymous"></script>

    <script>
        var cookieSettings = new BootstrapCookieConsentSettings({
            contentURL: "../privacy/content",
            postSelectionCallback: function() {
                location.reload() // reload after selection
            }
        })

        function showSettingsDialog() {
            cookieSettings.showDialog()
        }

        $(document).ready(function() {
            $("#settingsOutput").text(JSON.stringify(cookieSettings.getSettings()))
            $("#settingsAnalysisOutput").text(cookieSettings.getSettings("analyses"))
        })
    </script>
    <?php include("../gril.php"); ?>

    <div class='top'> </div>
</body>

</html>