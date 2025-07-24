param(
    [Parameter(Mandatory=$true)]
    [string]$Name,
    
    [Parameter(Mandatory=$true)]
    [string]$Surname,
    
    [Parameter(Mandatory=$true)]
    [string]$Email
)

# Function to convert umlauts to PowerShell char codes
function Convert-UmlautsToChars {
    param([string]$text)
    
    $text = $text -replace 'ä', '$([char]228)'
    $text = $text -replace 'Ä', '$([char]196)'
    $text = $text -replace 'ö', '$([char]246)'
    $text = $text -replace 'Ö', '$([char]214)'
    $text = $text -replace 'ü', '$([char]252)'
    $text = $text -replace 'Ü', '$([char]220)'
    $text = $text -replace 'ß', '$([char]223)'
    
    return $text
}

# Convert parameters with umlauts
$NameConverted = Convert-UmlautsToChars $Name
$SurnameConverted = Convert-UmlautsToChars $Surname

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("BAPID", "dcf4b0c4aec1c98ac98898baba6f196e", "/", "app.chemscan.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("https-_csrf", "rGPiecNFFCCYrsIk1FAdnlvEMeeHVXgAA3sjBmxL8d4", "/", "app.chemscan.de")))

try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri "https://app.chemscan.de/user/create" `
    -Method "POST" `
    -WebSession $session `
    -Headers @{
    "authority"="app.chemscan.de"
      "method"="POST"
      "path"="/user/create"
      "scheme"="https"
      "accept"="application/json, text/javascript, */*; q=0.01"
      "accept-encoding"="gzip, deflate, br, zstd"
      "accept-language"="de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
      "cache-control"="no-cache, no-store"
      "origin"="https://app.chemscan.de"
      "priority"="u=1, i"
      "referer"="https://app.chemscan.de/user/create"
      "sec-ch-ua"="`"Not)A;Brand`";v=`"8`", `"Chromium`";v=`"138`", `"Google Chrome`";v=`"138`""
      "sec-ch-ua-mobile"="?0"
      "sec-ch-ua-platform"="`"Windows`""
      "sec-fetch-dest"="empty"
      "sec-fetch-mode"="cors"
      "sec-fetch-site"="same-origin"
      "x-csrf-header"="rGPiecNFFCCYrsIk1FAdnlvEMeeHVXgAA3sjBmxL8d4"
      "x-oro-hash-navigation"="true"
      "x-requested-with"="XMLHttpRequest"
    } `
    -ContentType "multipart/form-data; boundary=----WebKitFormBoundaryLKdarnhS9sIxEMk8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes("------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"input_action`"$([char]13)$([char]10)$([char]13)$([char]10){`"route`":`"oro_user_view`",`"params`":{`"id`":`"`$id`"}}$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[owner]`"$([char]13)$([char]10)$([char]13)$([char]10)54$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[enabled]`"$([char]13)$([char]10)$([char]13)$([char]10)1$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[username]`"$([char]13)$([char]10)$([char]13)$([char]10)$Email$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[namePrefix]`"$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[firstName]`"$([char]13)$([char]10)$([char]13)$([char]10)$NameConverted$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[middleName]`"$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[lastName]`"$([char]13)$([char]10)$([char]13)$([char]10)$SurnameConverted$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[nameSuffix]`"$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[birthday]`"$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form_birthday-uid-6881e43bef060`"$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[avatar][file]`"$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[avatar][emptyFile]`"$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[inviteUser]`"$([char]13)$([char]10)$([char]13)$([char]10)1$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[passwordGenerate]`"$([char]13)$([char]10)$([char]13)$([char]10)1$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[email]`"$([char]13)$([char]10)$([char]13)$([char]10)$Email$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[phone]`"$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[userRoles][]`"$([char]13)$([char]10)$([char]13)$([char]10)2$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[organizations][]`"$([char]13)$([char]10)$([char]13)$([char]10)16$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[businessUnits]`"$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[title]`"$([char]13)$([char]10)$([char]13)$([char]10)ATL$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[sign][file]`"$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[sign][emptyFile]`"$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_user_user_form[_token]`"$([char]13)$([char]10)$([char]13)$([char]10)6aefab257.qOymIGt_I77kUPR1M6NsDiAmKcr_HG2w0O4-yNtZi2E.4r3pelIUYfuxPJodUeJVV1ZXbIW4WFTKvaBOopdtwgTBmdxsMhhJ_6sUxA$([char]13)$([char]10)------WebKitFormBoundaryLKdarnhS9sIxEMk8--$([char]13)$([char]10)"))

    Write-Host "User creation request sent for: $Name $Surname ($Email)"
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
    
    return $response
    
} catch {
    Write-Host "Error creating user $Name $Surname ($Email): $($_.Exception.Message)"
    Write-Host "Full Error: $_"
    return $null
}