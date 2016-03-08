<Head>
<title> Network Host Response Report </title>
<style type="text/css">

table.table1 {
margin-left: 88%;
text-align: right;
}
table.table2, td{
font-family: Arial, Helvetica, sans-serif;
font-size: 1.1em;
margin-right: 50%;
text-align: center;
background-color: #003366; 
border-collapse: separate;
border: 1px solid #000;
padding: 10px;
}
body {
background-image: url("images/banner_logo.gif");
background-color: #666;
color: #FFF;
}

th.th1 {
font-family: Arial, Helvetica, sans-serif;
font-size: 1.em;
color: black;
background-color: #7FFF00;
color: #000;
padding: 2px 6px;
border-collapse: separate;
border: 1px solid #000;
text-align: right;
}
th.th2 {
font-family: Arial, Helvetica, sans-serif;
font-size: 1.em;
color: black;
background-color: #003366;
color: #000;
padding: 2px 6px;
border-collapse: separate;
border: 1px solid #000;
text-align: right;
}

</style>
<body>
<?php
include 'config/database.php';
// Connecting, selecting database
$link = mysql_connect('localhost', $username , $password)
    or die('Could not connect: ' . mysql_error());
echo "<th><table class=\"table1\">";
echo "<tr><th class=\"th1\">Status: Connected</th></tr>";
mysql_select_db($db_name) or die('Could not select database');

// Performing SQL query
$query = 'select c . Computer_IP_Address, p . Port_Number  from Computer_Info c, Ports_Table p where p.Comp_ID = c.Computer_ID ';
$result = mysql_query($query) or die('Query failed: ' . mysql_error());

// Printing results in HTML
echo "<table class=\"table2\">\n";
echo "<tr><td>Network Addresses That Responded to ICMP Response:</td></tr>";
echo "</table>";
echo "<table class=\"table2\">\n";
echo "\t<tr>\n";
echo "\t<th>Host Address</th>\t<th>Open Ports</th>\t<th>OS Detected</th>";
$cntup = 0;
$cntto = 0;
$cur_host = array();
while ($line = mysql_fetch_array($result, MYSQL_ASSOC)) {
$line_results[] = $line;

	$cur_host[] .= $line_results[$cntto]['Computer_IP_Address'];
	$current_host = $cur_host[$cntto];

    if ($lasthost == $current_host){
	echo "<td>";
        echo $line_results[$cntup]['Port_Number'];
    }else{
	echo "</tr>";
	echo "</td>";
	echo "<tr>";
	echo "<td>";
        echo $line_results[$cntto]['Computer_IP_Address'];
	echo "<td>";
        echo $line_results[$cntup]['Port_Number'];
    }
	$cntto++;
	$lasthost = $current_host;

	$cntup++;
}
echo "</table>\n";

// Free resultset
mysql_free_result($result);

// Closing connection
mysql_close($link);
?>
</body>
