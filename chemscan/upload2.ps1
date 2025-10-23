$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("BAPRM", "YUtHOFUwTWcxTjduemd1UnA4VHdMTEpMTktXSkdrdjFOUzVWbjc1aVUzOGR3dUlZa1NLa1cxOUNSdmk2aUhSQWtIZDh1T3lremYyTEY3dndsZ2xDcUE9PTptQjFWR3pGbU9HWUtXZHpwKzhVSjZpcXIxYXdmOW1ON0FUdkVrWWt5V2l1TC9BZUljVzNuazJwUkx3RmpBLzErbW9IZHFmTFVYQ2ZkOHYvMTNQQzVGdz09", "/", "app.chemscan.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("BAPID", "e201cf681d7e8ebbba545d5ae6b74b64", "/", "app.chemscan.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("https-_csrf", "JBnOGd4wgi_RMmkQnoOZjlGT8wvqI2Albb03a0L4fGc", "/", "app.chemscan.de")))
Invoke-WebRequest -UseBasicParsing -Uri "https://app.chemscan.de/attachment/create/UUB_Bundle_CadasterBundle_Entity_HazardSubstanceOrganization/2177?_widgetContainer=dialog&_wid=b920dec1-cb3f-4917-b410-28ce74a13fe5&_widgetInit=1" `
-Method "POST" `
-WebSession $session `
-Headers @{
"authority"="app.chemscan.de"
  "method"="POST"
  "path"="/attachment/create/UUB_Bundle_CadasterBundle_Entity_HazardSubstanceOrganization/2177?_widgetContainer=dialog&_wid=b920dec1-cb3f-4917-b410-28ce74a13fe5&_widgetInit=1"
  "scheme"="https"
  "accept"="*/*"
  "accept-encoding"="gzip, deflate, br, zstd"
  "accept-language"="de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
  "cache-control"="no-cache, no-store"
  "origin"="https://app.chemscan.de"
  "priority"="u=1, i"
  "referer"="https://app.chemscan.de/cadaster/organization/view/2177?grid%5Buub-hazard-substance-organization-with-actions-grid%5D=i%3D1%26p%3D25%26s%255Bactive%255D%3D-1%26f%255Bname%255D%255Bvalue%255D%3Dtest%26f%255Bname%255D%255Btype%255D%3D1%26c%3Dactive1.hsSds1.hsHa1.hsWaterHazardClass1.internalName1.name1.alternativeName1.manufacturerName1.symbolSigns1.catalogRRates1.substanceName1.hazardSubstanceAssessmentBU1.responsibleUserGroup1.hsNumber0.additionalInfo10.additionalInfo20.catalogWarehouseClass0.catalogUnNumber0.hsForm0.hsBoilingPoint0.hsFlamePoint0.sdsRequested0.sdsPrinted0.hsVocAmount0%26v%3D__all__%26a%3Dgrid%26g%255BoriginalRoute%255D%3Duub_cadaster_organization_index"
  "sec-ch-ua"="`"Google Chrome`";v=`"141`", `"Not?A_Brand`";v=`"8`", `"Chromium`";v=`"141`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "sec-fetch-dest"="empty"
  "sec-fetch-mode"="cors"
  "sec-fetch-site"="same-origin"
  "x-csrf-header"="JBnOGd4wgi_RMmkQnoOZjlGT8wvqI2Albb03a0L4fGc"
  "x-requested-with"="XMLHttpRequest"
} `
-ContentType "multipart/form-data; boundary=----WebKitFormBoundaryRKswcJQHqrCDUevz" `
-Body ([System.Text.Encoding]::UTF8.GetBytes("------WebKitFormBoundaryRKswcJQHqrCDUevz$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_attachment[file][file]`"; filename=`"077-2025_01043569.pdf`"$([char]13)$([char]10)Content-Type: application/pdf$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryRKswcJQHqrCDUevz$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_attachment[file][emptyFile]`"$([char]13)$([char]10)$([char]13)$([char]10)$([char]13)$([char]10)------WebKitFormBoundaryRKswcJQHqrCDUevz$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_attachment[comment]`"$([char]13)$([char]10)$([char]13)$([char]10)TEST2$([char]13)$([char]10)------WebKitFormBoundaryRKswcJQHqrCDUevz$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_attachment[owner]`"$([char]13)$([char]10)$([char]13)$([char]10)303$([char]13)$([char]10)------WebKitFormBoundaryRKswcJQHqrCDUevz$([char]13)$([char]10)Content-Disposition: form-data; name=`"oro_attachment[_token]`"$([char]13)$([char]10)$([char]13)$([char]10)2e44a187.Z3V_mDb_AD65tTuIPGs0nnQ9y9dN9yUFhSYoXv4Osfg.JiIuoQTGdgyM8grQblJNySdHgIZ-rkNj1AtEDYY81cEkNi_NWao0D4HFbg$([char]13)$([char]10)------WebKitFormBoundaryRKswcJQHqrCDUevz$([char]13)$([char]10)Content-Disposition: form-data; name=`"_widgetContainer`"$([char]13)$([char]10)$([char]13)$([char]10)dialog$([char]13)$([char]10)------WebKitFormBoundaryRKswcJQHqrCDUevz$([char]13)$([char]10)Content-Disposition: form-data; name=`"_wid`"$([char]13)$([char]10)$([char]13)$([char]10)b920dec1-cb3f-4917-b410-28ce74a13fe5$([char]13)$([char]10)------WebKitFormBoundaryRKswcJQHqrCDUevz$([char]13)$([char]10)Content-Disposition: form-data; name=`"_widgetInit`"$([char]13)$([char]10)$([char]13)$([char]10)0$([char]13)$([char]10)------WebKitFormBoundaryRKswcJQHqrCDUevz--$([char]13)$([char]10)"))