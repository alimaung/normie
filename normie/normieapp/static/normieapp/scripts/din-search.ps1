param(
    [Parameter(Mandatory=$true)]
    [string]$Query,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("10", "25", "50", "100")]
    [string]$HitsPerPage = "10",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "search.html"
)

# URL encode the query parameter - replace spaces with + for form encoding
function Encode-FormUrl {
    param($String)
    # Replace spaces with + and encode other special characters
    return $String -replace ' ', '+' -replace '&', '%26' -replace '=', '%3D'
}
$EncodedQuery = Encode-FormUrl $Query

# Create web session with cookies and headers
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"

# Add required cookies
$session.Cookies.Add((New-Object System.Net.Cookie("CM_SESSIONID", "NjUxOGMwNmQtNjBhMC00MmIzLTgyYWQtNDEzNmQyNzU4YTZi", "/", "www.dinmedia.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("recoEngineSession", "wf7ix7gmu", "/", "www.dinmedia.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("_gcl_au", "1.1.1238156835.1754319389", "/", ".dinmedia.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("dinmedia-en_consent_en", "%7B%22required%22%3Atrue%2C%22functional%22%3Afalse%2C%22personalization%22%3Afalse%7D", "/", "www.dinmedia.de")))
$session.Cookies.Add((New-Object System.Net.Cookie("cookie_consent", "1", "/", "www.dinmedia.de")))

# Build the search URL with parameters
$baseUrl = "https://www.dinmedia.de/en/erweiterte-suche/1046186!search"
$queryParams = @(
    "alx.searchType=complex",
    "alx.search.autoSuggest=false", 
    "searchAreaId=1",
    "query=$EncodedQuery",
    "facets%5B1046190%5D=",
    "hitsPerPage=$HitsPerPage"
)
$searchUrl = $baseUrl + "?" + ($queryParams -join "&")

Write-Host "Searching DIN Media for: $Query"
Write-Host "Encoded query: $EncodedQuery"
Write-Host "Results per page: $HitsPerPage"
Write-Host "URL: $searchUrl"
Write-Host "URL Length: $($searchUrl.Length)"

try {
    # Execute the web request
    $response = Invoke-WebRequest -UseBasicParsing -Uri $searchUrl -WebSession $session -Headers @{
        "authority" = "www.dinmedia.de"
        "method" = "GET"
        "scheme" = "https"
        "accept" = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        "accept-encoding" = "gzip, deflate, br, zstd"
        "accept-language" = "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
        "priority" = "u=0, i"
        "referer" = $searchUrl
        "sec-ch-ua" = "`"Not)A;Brand`";v=`"8`", `"Chromium`";v=`"138`", `"Google Chrome`";v=`"138`""
        "sec-ch-ua-mobile" = "?0"
        "sec-ch-ua-platform" = "`"Windows`""
        "sec-fetch-dest" = "document"
        "sec-fetch-mode" = "navigate"
        "sec-fetch-site" = "same-origin"
        "sec-fetch-user" = "?1"
        "upgrade-insecure-requests" = "1"
    }

    # Save the response content with proper UTF-8 encoding
    $response.Content | Out-File -FilePath $OutputFile -Encoding UTF8
    
    Write-Host "Search completed successfully!"
    Write-Host "Results saved to: $OutputFile"
    Write-Host "Response length: $($response.Content.Length) characters"
    
    # Return success exit code
    exit 0
    
} catch {
    Write-Error "Error executing search: $_"
    Write-Error "Error details: $($_.Exception.Message)"
    
    # Return error exit code
    exit 1
}
