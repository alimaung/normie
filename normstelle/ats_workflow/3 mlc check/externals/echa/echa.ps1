$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("ApplicationGatewayAffinityCORS", "372040b2dec5ad78183ee367a67d270c", "/", "echa.europa.eu")))
$session.Cookies.Add((New-Object System.Net.Cookie("ApplicationGatewayAffinity", "372040b2dec5ad78183ee367a67d270c", "/", "echa.europa.eu")))
$session.Cookies.Add((New-Object System.Net.Cookie("JSESSIONID", "BE0A80063BAE46908DFF698655EDFC3E.live-1", "/", "echa.europa.eu")))
$session.Cookies.Add((New-Object System.Net.Cookie("COOKIE_SUPPORT", "true", "/", "echa.europa.eu")))
$session.Cookies.Add((New-Object System.Net.Cookie("GUEST_LANGUAGE_ID", "en_GB", "/", "echa.europa.eu")))
$session.Cookies.Add((New-Object System.Net.Cookie("cck1", "%7B%22cm%22%3Afalse%2C%22all1st%22%3Afalse%7D", "/", ".echa.europa.eu")))
$session.Cookies.Add((New-Object System.Net.Cookie("_pk_ses.c9cba231-694a-48ae-b6c0-eeb7777b02e3.bd53", "*", "/", "echa.europa.eu")))
$session.Cookies.Add((New-Object System.Net.Cookie("disclaimer", "true", "/", "echa.europa.eu")))
$session.Cookies.Add((New-Object System.Net.Cookie("_pk_id.c9cba231-694a-48ae-b6c0-eeb7777b02e3.bd53", "d317c438494281fe.1753125119.1.1753126116.1753125119.", "/", "echa.europa.eu")))
$session.Cookies.Add((New-Object System.Net.Cookie("LFR_SESSION_STATE_10140", "1753126116345", "/", "echa.europa.eu")))
Invoke-WebRequest -UseBasicParsing -Uri "https://echa.europa.eu/information-on-chemicals/ec-inventory?p_p_id=disslists_WAR_disslistsportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&_disslists_WAR_disslistsportlet_javax.portlet.action=searchDissLists" `
-Method "POST" `
-WebSession $session `
-Headers @{
"Accept"="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
  "Accept-Encoding"="gzip, deflate, br, zstd"
  "Accept-Language"="de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
  "Cache-Control"="no-cache"
  "Origin"="https://echa.europa.eu"
  "Pragma"="no-cache"
  "Referer"="https://echa.europa.eu/information-on-chemicals/ec-inventory?p_p_id=disslists_WAR_disslistsportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&_disslists_WAR_disslistsportlet_javax.portlet.action=searchDissLists"
  "Sec-Fetch-Dest"="document"
  "Sec-Fetch-Mode"="navigate"
  "Sec-Fetch-Site"="same-origin"
  "Sec-Fetch-User"="?1"
  "Upgrade-Insecure-Requests"="1"
  "sec-ch-ua"="`"Not)A;Brand`";v=`"8`", `"Chromium`";v=`"138`", `"Google Chrome`";v=`"138`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
} `
-ContentType "application/x-www-form-urlencoded" `
-Body "_disslists_WAR_disslistsportlet_formDate=1753126115784&_disslists_WAR_disslistsportlet_substance_identifier_field_key=CAS&_disslists_WAR_disslistsportlet_diss_description=DESC&_disslists_WAR_disslistsportlet_diss_mol_formula=FORMULA&_disslists_WAR_disslistsportlet_deltaParamValue=50&doSearch=true&p_auth="