param(
    [Parameter(Mandatory=$true)]
    [int]$UserId
)

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("BAPID", "dcf4b0c4aec1c98ac98898baba6f196e", "/", "app.chemscan.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("https-_csrf", "IO5IADnt0Q287thO6pQyN6tJGAWF2aGAPCEVMoy4o-A", "/", "app.chemscan.de")))

try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri "https://app.chemscan.de/ajax/operation/execute/reset_password?entityClass=Oro%5CBundle%5CUserBundle%5CEntity%5CUser&entityId=$UserId&route=&datagrid=users-grid&group%5B0%5D=&group%5B1%5D=datagridRowAction" `
    -Method "POST" `
    -WebSession $session `
    -Headers @{
    "authority"="app.chemscan.de"
      "method"="POST"
      "path"="/ajax/operation/execute/reset_password?entityClass=Oro%5CBundle%5CUserBundle%5CEntity%5CUser&entityId=$UserId&route=&datagrid=users-grid&group%5B0%5D=&group%5B1%5D=datagridRowAction"
      "scheme"="https"
      "accept"="application/json, text/javascript, */*; q=0.01"
      "accept-encoding"="gzip, deflate, br, zstd"
      "accept-language"="de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
      "cache-control"="no-cache, no-store"
      "origin"="https://app.chemscan.de"
      "priority"="u=1, i"
      "referer"="https://app.chemscan.de/user?grid%5Busers-grid%5D=i%3D1%26p%3D25%26s%255BcreatedAt%255D%3D1%26f%255Benabled%255D%255Bvalue%255D%3D1%26c%3DfirstName1.lastName1.email1.username1.enabled0.authStatus1.createdAt1.updatedAt1.roles1%26v%3Duser.active%26a%3Dgrid%26g%255BoriginalRoute%255D%3Doro_user_index"
      "sec-ch-ua"="`"Not)A;Brand`";v=`"8`", `"Chromium`";v=`"138`", `"Google Chrome`";v=`"138`""
      "sec-ch-ua-mobile"="?0"
      "sec-ch-ua-platform"="`"Windows`""
      "sec-fetch-dest"="empty"
      "sec-fetch-mode"="cors"
      "sec-fetch-site"="same-origin"
      "x-csrf-header"="IO5IADnt0Q287thO6pQyN6tJGAWF2aGAPCEVMoy4o-A"
      "x-requested-with"="XMLHttpRequest"
    } `
    -ContentType "application/x-www-form-urlencoded; charset=UTF-8" `
    -Body "oro_action_operation_execution%5Boperation_execution_csrf_token%5D=942959248523251e4a.ETERnEecM1YIBY88jWjfdu84DlMPi9sXbzhxG_JAmEY.aVRF_3GkagM8R79Ru1GJPddTYRFfw7cnXgAyYZgu6CRwdl75Ce5fMjp_7A"

    Write-Host "Password reset request sent for user ID: $UserId"
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
    
    return $response
    
} catch {
    Write-Host "Error resetting password for user ID $UserId`: $($_.Exception.Message)"
    Write-Host "Full Error: $_"
    return $null
}