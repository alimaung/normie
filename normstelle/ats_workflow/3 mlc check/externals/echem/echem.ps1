$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("_ga", "GA1.1.409936561.1753123475", "/", ".echemportal.org")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_K93T9C7HRS", "GS2.1.s1753123474`$o1`$g1`$t1753123576`$j60`$l0`$h0", "/", ".echemportal.org")))
Invoke-WebRequest -UseBasicParsing -Uri "https://www.echemportal.org/echemportal/api/substance-search" `
-Method "POST" `
-WebSession $session `
-Headers @{
"authority"="www.echemportal.org"
  "method"="POST"
  "path"="/echemportal/api/substance-search"
  "scheme"="https"
  "accept"="application/json, text/plain, */*"
  "accept-encoding"="gzip, deflate, br, zstd"
  "accept-language"="en"
  "cache-control"="no-cache"
  "origin"="https://www.echemportal.org"
  "pragma"="no-cache"
  "priority"="u=1, i"
  "referer"="https://www.echemportal.org/echemportal/substance-search"
  "sec-ch-ua"="`"Not)A;Brand`";v=`"8`", `"Chromium`";v=`"138`", `"Google Chrome`";v=`"138`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "sec-fetch-dest"="empty"
  "sec-fetch-mode"="cors"
  "sec-fetch-site"="same-origin"
} `
-ContentType "application/json" `
-Body "{`"query_term`":`"237-137-2`",`"paging`":{`"offset`":0,`"limit`":50},`"filtering`":[],`"sorting`":[],`"participants`":[40,661,320,101,3,380,181,600,701,781,761,420,5,280,260,640,8,10,660,440,11,340,480,60,12,7,14,742,1,220,620,16,17,18],`"ghs_blocks`":[],`"new_query`":true}"