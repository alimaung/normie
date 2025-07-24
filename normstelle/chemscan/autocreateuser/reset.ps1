$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("BAPID", "dcf4b0c4aec1c98ac98898baba6f196e", "/", "app.chemscan.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("https-_csrf", "PWxXURLiOrjJ01M__Ikjxe1IV0vGotsUgNKQ3q8nMWo", "/", "app.chemscan.de")))
Invoke-WebRequest -UseBasicParsing -Uri "https://app.chemscan.de/api/rest/latest/windows/3852" `
-Method "DELETE" `
-WebSession $session `
-Headers @{
"authority"="app.chemscan.de"
  "method"="DELETE"
  "path"="/api/rest/latest/windows/3852"
  "scheme"="https"
  "accept"="application/json, text/javascript, */*; q=0.01"
  "accept-encoding"="gzip, deflate, br, zstd"
  "accept-language"="de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
  "cache-control"="no-cache, no-store"
  "origin"="https://app.chemscan.de"
  "priority"="u=1, i"
  "referer"="https://app.chemscan.de/user/view/360"
  "sec-ch-ua"="`"Not)A;Brand`";v=`"8`", `"Chromium`";v=`"138`", `"Google Chrome`";v=`"138`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "sec-fetch-dest"="empty"
  "sec-fetch-mode"="cors"
  "sec-fetch-site"="same-origin"
  "x-csrf-header"="PWxXURLiOrjJ01M__Ikjxe1IV0vGotsUgNKQ3q8nMWo"
  "x-requested-with"="XMLHttpRequest"
}