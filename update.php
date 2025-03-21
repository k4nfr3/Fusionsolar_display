<?php
// this script is to be hosted on a external web site, to pass a status to the display
// It can be called like the following :
// https://mywebsite.com/boiler/update.php?auth_key=changeme&status=on
// https://mywebsite.com/boiler/update.php?auth_key=changeme&status=off
// The goal of the timestamp is to check if the status is up to date or is old

$debug = false;
$auth_key = "changeme"; 
$GET_auth_key = isset($_GET['auth_key']) ? $_GET['auth_key'] : null;
if ($GET_auth_key !== $auth_key) {
    die("8.8.8.8 #Drop Crawlers"); 
}
$GET_status = isset($_GET['status']) ? $_GET['status'] : null;
if ($GET_status === "on" || $GET_status === "off") {
    echo "received status = $GET_status";
    $jsonData = [
        "lastupdate" => time(), // Current Unix timestamp
        "status" => $GET_status
    ];
    
    $jsonOutput = json_encode($jsonData, JSON_PRETTY_PRINT);
    
    file_put_contents("status.json", $jsonOutput); 
} else {
    die("error in getting stat"); 
}
?>