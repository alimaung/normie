$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("BAPRM", "YUtHOFUwTWcxTjduemd1UnA4VHdMTEpMTktXSkdrdjFOUzVWbjc1aVUzOGR3dUlZa1NLa1cxOUNSdmk2aUhSQWtIZDh1T3lremYyTEY3dndsZ2xDcUE9PTptQjFWR3pGbU9HWUtXZHpwKzhVSjZpcXIxYXdmOW1ON0FUdkVrWWt5V2l1TC9BZUljVzNuazJwUkx3RmpBLzErbW9IZHFmTFVYQ2ZkOHYvMTNQQzVGdz09", "/", "app.chemscan.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("BAPID", "e201cf681d7e8ebbba545d5ae6b74b64", "/", "app.chemscan.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("https-_csrf", "JBnOGd4wgi_RMmkQnoOZjlGT8wvqI2Albb03a0L4fGc", "/", "app.chemscan.de")))
Invoke-WebRequest -UseBasicParsing -Uri "https://app.chemscan.de/datagrid/attachment-grid?attachment-grid%5BentityId%5D=2177&attachment-grid%5BentityField%5D=hazard_substance_organization_3af9230e&appearanceType=grid&attachment-grid%5B_pager%5D%5B_page%5D=1&attachment-grid%5B_pager%5D%5B_per_page%5D=25&attachment-grid%5B_parameters%5D%5Brefresh%5D=true&attachment-grid%5B_parameters%5D%5Bview%5D=__all__&attachment-grid%5B_appearance%5D%5B_type%5D=grid&attachment-grid%5B_columns%5D=originalFilename1.fileSize1.createdAt1.comment1" `
-WebSession $session `
-Headers @{
"authority"="app.chemscan.de"
  "method"="GET"
  "path"="/datagrid/attachment-grid?attachment-grid%5BentityId%5D=2177&attachment-grid%5BentityField%5D=hazard_substance_organization_3af9230e&appearanceType=grid&attachment-grid%5B_pager%5D%5B_page%5D=1&attachment-grid%5B_pager%5D%5B_per_page%5D=25&attachment-grid%5B_parameters%5D%5Brefresh%5D=true&attachment-grid%5B_parameters%5D%5Bview%5D=__all__&attachment-grid%5B_appearance%5D%5B_type%5D=grid&attachment-grid%5B_columns%5D=originalFilename1.fileSize1.createdAt1.comment1"
  "scheme"="https"
  "accept"="application/json, text/javascript, */*; q=0.01"
  "accept-encoding"="gzip, deflate, br, zstd"
  "accept-language"="de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
  "cache-control"="no-cache, no-store"
  "priority"="u=1, i"
  "referer"="https://app.chemscan.de/cadaster/organization/view/2177?grid%5Buub-hazard-substance-organization-with-actions-grid%5D=i%3D1%26p%3D25%26s%255Bactive%255D%3D-1%26f%255Bname%255D%255Bvalue%255D%3Dtest%26f%255Bname%255D%255Btype%255D%3D1%26c%3Dactive1.hsSds1.hsHa1.hsWaterHazardClass1.internalName1.name1.alternativeName1.manufacturerName1.symbolSigns1.catalogRRates1.substanceName1.hazardSubstanceAssessmentBU1.responsibleUserGroup1.hsNumber0.additionalInfo10.additionalInfo20.catalogWarehouseClass0.catalogUnNumber0.hsForm0.hsBoilingPoint0.hsFlamePoint0.sdsRequested0.sdsPrinted0.hsVocAmount0%26v%3D__all__%26a%3Dgrid%26g%255BoriginalRoute%255D%3Duub_cadaster_organization_index&grid%5Battachment-grid%5D=i%3D1%26p%3D25%26c%3DoriginalFilename1.fileSize1.createdAt1.comment1%26v%3D__all__%26a%3Dgrid%26g%255BentityId%255D%3D2177%26g%255BentityField%255D%3Dhazard_substance_organization_3af9230e%26g%255Brefresh%255D%3Dtrue"
  "sec-ch-ua"="`"Google Chrome`";v=`"141`", `"Not?A_Brand`";v=`"8`", `"Chromium`";v=`"141`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "sec-fetch-dest"="empty"
  "sec-fetch-mode"="cors"
  "sec-fetch-site"="same-origin"
  "x-csrf-header"="JBnOGd4wgi_RMmkQnoOZjlGT8wvqI2Albb03a0L4fGc"
  "x-requested-with"="XMLHttpRequest"
}