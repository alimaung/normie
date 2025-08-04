$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("CM_SESSIONID", "NjUxOGMwNmQtNjBhMC00MmIzLTgyYWQtNDEzNmQyNzU4YTZi", "/", "www.dinmedia.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("recoEngineSession", "wf7ix7gmu", "/", "www.dinmedia.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("_gcl_au", "1.1.1238156835.1754319389", "/", ".dinmedia.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("dinmedia-en_consent_en", "%7B%22required%22%3Atrue%2C%22functional%22%3Afalse%2C%22personalization%22%3Afalse%7D", "/", "www.dinmedia.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("cookie_consent", "1", "/", "www.dinmedia.de")))
$response = Invoke-WebRequest -UseBasicParsing -Uri "https://www.dinmedia.de/en/erweiterte-suche/1046186!search?alx.searchType=complex&alx.search.autoSuggest=false&searchAreaId=1&query=ASTM+E+192&facets%5B1046190%5D=&hitsPerPage=10" `
-WebSession $session `
-Headers @{
"authority"="www.dinmedia.de"
  "method"="GET"
  "path"="/en/erweiterte-suche/1046186!search?alx.searchType=complex&alx.search.autoSuggest=false&searchAreaId=1&query=ASTM+E+192&facets%5B1046190%5D=&hitsPerPage=10"
  "scheme"="https"
  "accept"="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
  "accept-encoding"="gzip, deflate, br, zstd"
  "accept-language"="de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
  "priority"="u=0, i"
  "referer"="https://www.dinmedia.de/en/1046186!search?alx.searchType=complex&alx.search.autoSuggest=false&searchAreaId=1&query=ASTM+E+192&facets%5B1046190%5D=&hitsPerPage=10"
  "sec-ch-ua"="`"Not)A;Brand`";v=`"8`", `"Chromium`";v=`"138`", `"Google Chrome`";v=`"138`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "sec-fetch-dest"="document"
  "sec-fetch-mode"="navigate"
  "sec-fetch-site"="same-origin"
  "sec-fetch-user"="?1"
  "upgrade-insecure-requests"="1"
}
$response.Content | Out-File -FilePath "search.html" -Encoding UTF8