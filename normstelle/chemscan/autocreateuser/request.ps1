param(
    [Parameter(Mandatory=$true)]
    [string]$Name
)

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("BAPID", "dcf4b0c4aec1c98ac98898baba6f196e", "/", "app.chemscan.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("https-_csrf", "JYQm1LvfC6TMjIoz8dsAwARTJ5J58Jg2Indvi-h-f24", "/", "app.chemscan.de")))
Invoke-WebRequest -UseBasicParsing -Uri "https://app.chemscan.de/datagrid/users-grid?users-grid%5BoriginalRoute%5D=oro_user_index&appearanceType=grid&users-grid%5B_pager%5D%5B_page%5D=1&users-grid%5B_pager%5D%5B_per_page%5D=25&users-grid%5B_parameters%5D%5Bview%5D=user.active&users-grid%5B_appearance%5D%5B_type%5D=grid&users-grid%5B_sort_by%5D%5Busername%5D=ASC&users-grid%5B_filter%5D%5BlastName%5D%5Bvalue%5D=$Name&users-grid%5B_filter%5D%5BlastName%5D%5Btype%5D=1&users-grid%5B_filter%5D%5Benabled%5D%5Bvalue%5D=1&users-grid%5B_columns%5D=firstName1.lastName1.email1.username1.enabled0.authStatus1.createdAt1.updatedAt1.roles1" `
-WebSession $session `
-Headers @{
"authority"="app.chemscan.de"
  "method"="GET"
  "path"="/datagrid/users-grid?users-grid%5BoriginalRoute%5D=oro_user_index&appearanceType=grid&users-grid%5B_pager%5D%5B_page%5D=1&users-grid%5B_pager%5D%5B_per_page%5D=25&users-grid%5B_parameters%5D%5Bview%5D=user.active&users-grid%5B_appearance%5D%5B_type%5D=grid&users-grid%5B_sort_by%5D%5Busername%5D=ASC&users-grid%5B_filter%5D%5BlastName%5D%5Bvalue%5D=$Name&users-grid%5B_filter%5D%5BlastName%5D%5Btype%5D=1&users-grid%5B_filter%5D%5Benabled%5D%5Bvalue%5D=1&users-grid%5B_columns%5D=firstName1.lastName1.email1.username1.enabled0.authStatus1.createdAt1.updatedAt1.roles1"
  "scheme"="https"
  "accept"="application/json, text/javascript, */*; q=0.01"
  "accept-encoding"="gzip, deflate, br, zstd"
  "accept-language"="de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
  "cache-control"="no-cache, no-store"
  "priority"="u=1, i"
  "referer"="https://app.chemscan.de/user?grid%5Busers-grid%5D=i%3D1%26p%3D25%26s%255Busername%255D%3D-1%26f%255BlastName%255D%255Bvalue%255D%3D$Name%26f%255BlastName%255D%255Btype%255D%3D1%26f%255Benabled%255D%255Bvalue%255D%3D1%26c%3DfirstName1.lastName1.email1.username1.enabled0.authStatus1.createdAt1.updatedAt1.roles1%26v%3Duser.active%26a%3Dgrid%26g%255BoriginalRoute%255D%3Doro_user_index"
  "sec-ch-ua"="`"Not)A;Brand`";v=`"8`", `"Chromium`";v=`"138`", `"Google Chrome`";v=`"138`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "sec-fetch-dest"="empty"
  "sec-fetch-mode"="cors"
  "sec-fetch-site"="same-origin"
  "x-csrf-header"="JYQm1LvfC6TMjIoz8dsAwARTJ5J58Jg2Indvi-h-f24"
  "x-requested-with"="XMLHttpRequest"
}