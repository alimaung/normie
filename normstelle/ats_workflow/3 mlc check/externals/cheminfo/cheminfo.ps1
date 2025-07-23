$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("cid", "130612b1-655d-49ac-b5eb-1a14b1d62b63", "/", "recherche.chemikalieninfo.de")))
$session.Cookies.Add((New-Object System.Net.Cookie(".AspNetCore.Antiforgery.VyLW6ORzMgk", "CfDJ8FiOp0KqTgFBlsYRVzcF3NUuoKOsQLe6RZRS7ENlbyizDJJWyhxHl16EcfHDwv5YCdWMrOdRmBqkE6H8M1SfUvte4bPp8SiYb5i--ryHjD5iDl6yr024xxuRDYnFqim-p9JLy4ZbL88uv2_JGGm_v8A", "/", "recherche.chemikalieninfo.de")))
Invoke-WebRequest -UseBasicParsing -Uri "https://recherche.chemikalieninfo.de/public?sid=83ec0fa7-2ce2-46b1-9fe4-7996f55bd149&sv=s6&o=GSBL.STAR&o=RNAME.RNAME&ps=25" `
-Method "POST" `
-WebSession $session `
-Headers @{
"Accept"="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
  "Accept-Encoding"="gzip, deflate, br, zstd"
  "Accept-Language"="de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
  "Cache-Control"="no-cache"
  "Origin"="https://recherche.chemikalieninfo.de"
  "Pragma"="no-cache"
  "Referer"="https://recherche.chemikalieninfo.de/public?sid=83ec0fa7-2ce2-46b1-9fe4-7996f55bd149&sv=s6&o=GSBL.STAR&o=RNAME.RNAME&ps=25"
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
-Body "Params%5BINDEX.NAME%2BHe0b5ZkX-Eq%5D=Stoffname&Params%5BFINF.SUFO-Eq%5D=Summenformel&Params%5BDBVER.RN%2BbCTMyfDn-EndsWith%5D=&Params%5BCASRN.CASRN-Eq%5D=69011-36-5&Struktur.Struktur=&Params%5BINDEX.BASIC-Fulltext%5D=Volltextsuche&__RequestVerificationToken=CfDJ8FiOp0KqTgFBlsYRVzcF3NU_VYnjeHNKZb68TZ116pg6F3KyAbmr8NMJIYqjf4_KUanp9kvZFIUYnAwuhy2Yg69rjQ2klhUPrqhDPkDMsczaVAOVuKxrtwGIvJoNgSEyhup0cu8IikEXgwFsvBXx-wc"