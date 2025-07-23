$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
Invoke-WebRequest -UseBasicParsing -Uri "https://gestis-api.dguv.de/api/search/de?stoffname=NAME&nummern=CAS&summenformel=FORMEL&volltextsuche=VOLLTEXT&branche=&risikogruppe=&kategorie=&anmerkung=&erweitert=false&exact=false" `
-WebSession $session `
-Headers @{
"authority"="gestis-api.dguv.de"
  "method"="GET"
  "path"="/api/search/de?stoffname=NAME&nummern=CAS&summenformel=FORMEL&volltextsuche=VOLLTEXT&branche=&risikogruppe=&kategorie=&anmerkung=&erweitert=false&exact=false"
  "scheme"="https"
  "accept"="application/json, text/plain, */*"
  "accept-encoding"="gzip, deflate, br, zstd"
  "accept-language"="de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
  "authorization"="Bearer dddiiasjhduuvnnasdkkwUUSHhjaPPKMasd"
  "cache-control"="no-cache"
  "origin"="https://gestis.dguv.de"
  "pragma"="no-cache"
  "priority"="u=1, i"
  "referer"="https://gestis.dguv.de/"
  "sec-ch-ua"="`"Not)A;Brand`";v=`"8`", `"Chromium`";v=`"138`", `"Google Chrome`";v=`"138`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "sec-fetch-dest"="empty"
  "sec-fetch-mode"="cors"
  "sec-fetch-site"="same-site"
}