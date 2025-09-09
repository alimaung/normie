#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Check URL availability and create list of unavailable URLs
.DESCRIPTION
    Reads URLs from urls_cleaned.txt, tests each for availability, and creates a list of unavailable URLs
.PARAMETER InputFile
    Input file containing URLs (default: urls_cleaned.txt)
.PARAMETER OutputFile
    Output file for unavailable URLs (default: urls_unavailable.txt)
.PARAMETER LogFile
    Log file for detailed results (default: url_check_log.txt)
.PARAMETER MaxConcurrent
    Maximum number of concurrent checks (default: 10)
#>

param(
    [string]$InputFile = "urls_cleaned.txt",
    [string]$OutputFile = "urls_unavailable.txt", 
    [string]$LogFile = "url_check_log.txt",
    [int]$MaxConcurrent = 10
)

# Function to test if a URL/path is accessible
function Test-URLAvailability {
    param(
        [string]$Url,
        [int]$LineNumber
    )
    
    $result = @{
        Url = $Url
        LineNumber = $LineNumber
        Available = $false
        Error = $null
        Type = "Unknown"
        TestMethod = "None"
    }
    
    try {
        # Skip empty or null URLs
        if ([string]::IsNullOrWhiteSpace($Url)) {
            $result.Error = "Empty URL"
            return $result
        }
        
        # Handle different URL types
        if ($Url.StartsWith("file:///")) {
            # File URL - convert to local path
            $result.Type = "File URL"
            $result.TestMethod = "Test-Path"
            
            # Convert file:/// URL to local path
            $localPath = $Url -replace "^file:///", ""
            
            # Handle UNC paths (\\server\share)
            if ($localPath.StartsWith("\\")) {
                $testPath = $localPath
            } else {
                # Handle local paths (C:\...)
                $testPath = $localPath -replace "/", "\"
            }
            
            $result.Available = Test-Path -Path $testPath -ErrorAction SilentlyContinue
            
        } elseif ($Url.StartsWith("\\")) {
            # UNC path
            $result.Type = "UNC Path"
            $result.TestMethod = "Test-Path"
            $result.Available = Test-Path -Path $Url -ErrorAction SilentlyContinue
            
        } elseif ($Url -match "^[A-Za-z]:\\") {
            # Local Windows path
            $result.Type = "Local Path"
            $result.TestMethod = "Test-Path"
            $result.Available = Test-Path -Path $Url -ErrorAction SilentlyContinue
            
        } elseif ($Url.StartsWith("http://") -or $Url.StartsWith("https://")) {
            # HTTP/HTTPS URL
            $result.Type = "HTTP URL"
            $result.TestMethod = "Invoke-WebRequest"
            
            try {
                $response = Invoke-WebRequest -Uri $Url -Method Head -TimeoutSec 10 -ErrorAction Stop
                $result.Available = ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400)
            } catch {
                $result.Available = $false
                $result.Error = $_.Exception.Message
            }
            
        } elseif ($Url.StartsWith("ftp://")) {
            # FTP URL
            $result.Type = "FTP URL"
            $result.TestMethod = "FTP Test"
            
            try {
                $ftpRequest = [System.Net.FtpWebRequest]::Create($Url)
                $ftpRequest.Method = [System.Net.WebRequestMethods+Ftp]::GetFileSize
                $ftpRequest.Timeout = 10000
                $ftpResponse = $ftpRequest.GetResponse()
                $result.Available = $true
                $ftpResponse.Close()
            } catch {
                $result.Available = $false
                $result.Error = $_.Exception.Message
            }
            
        } else {
            # Try as file path anyway
            $result.Type = "Unknown Path"
            $result.TestMethod = "Test-Path (fallback)"
            $result.Available = Test-Path -Path $Url -ErrorAction SilentlyContinue
        }
        
    } catch {
        $result.Available = $false
        $result.Error = $_.Exception.Message
    }
    
    return $result
}

# Function to write log entry
function Write-LogEntry {
    param(
        [string]$Message,
        [string]$LogPath
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    
    Write-Host $logEntry
    Add-Content -Path $LogPath -Value $logEntry -Encoding UTF8
}

# Main script
Write-Host "URL Availability Checker" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host ""

# Check if input file exists
if (-not (Test-Path $InputFile)) {
    Write-Error "Input file '$InputFile' not found!"
    exit 1
}

# Initialize
$startTime = Get-Date
$unavailableUrls = @()
$stats = @{
    Total = 0
    Available = 0
    Unavailable = 0
    Errors = 0
}

# Clear/create log file
if (Test-Path $LogFile) {
    Remove-Item $LogFile -Force
}
New-Item $LogFile -ItemType File -Force | Out-Null

Write-LogEntry "Starting URL availability check" $LogFile
Write-LogEntry "Input file: $InputFile" $LogFile
Write-LogEntry "Output file: $OutputFile" $LogFile
Write-LogEntry "Max concurrent checks: $MaxConcurrent" $LogFile

# Read all URLs
Write-Host "Reading URLs from $InputFile..." -ForegroundColor Yellow
$urls = Get-Content -Path $InputFile -Encoding UTF8

$stats.Total = $urls.Count
Write-LogEntry "Total URLs to check: $($stats.Total)" $LogFile

# Process URLs in batches for better performance
$batchSize = $MaxConcurrent
$processedCount = 0

Write-Host "Starting URL checks..." -ForegroundColor Yellow

for ($i = 0; $i -lt $urls.Count; $i += $batchSize) {
    $batch = $urls[$i..([Math]::Min($i + $batchSize - 1, $urls.Count - 1))]
    $jobs = @()
    
    # Start batch of jobs
    foreach ($url in $batch) {
        $lineNumber = $i + $batch.IndexOf($url) + 1
        
        $job = Start-Job -ScriptBlock {
            param($url, $lineNumber, $testFunction)
            
            # Re-define the function in the job scope
            function Test-URLAvailability {
                param(
                    [string]$Url,
                    [int]$LineNumber
                )
                
                $result = @{
                    Url = $Url
                    LineNumber = $LineNumber
                    Available = $false
                    Error = $null
                    Type = "Unknown"
                    TestMethod = "None"
                }
                
                try {
                    if ([string]::IsNullOrWhiteSpace($Url)) {
                        $result.Error = "Empty URL"
                        return $result
                    }
                    
                    if ($Url.StartsWith("file:///")) {
                        $result.Type = "File URL"
                        $result.TestMethod = "Test-Path"
                        
                        $localPath = $Url -replace "^file:///", ""
                        
                        if ($localPath.StartsWith("\\")) {
                            $testPath = $localPath
                        } else {
                            $testPath = $localPath -replace "/", "\"
                        }
                        
                        $result.Available = Test-Path -Path $testPath -ErrorAction SilentlyContinue
                        
                    } elseif ($Url.StartsWith("\\")) {
                        $result.Type = "UNC Path"
                        $result.TestMethod = "Test-Path"
                        $result.Available = Test-Path -Path $Url -ErrorAction SilentlyContinue
                        
                    } elseif ($Url -match "^[A-Za-z]:\\") {
                        $result.Type = "Local Path"
                        $result.TestMethod = "Test-Path"
                        $result.Available = Test-Path -Path $Url -ErrorAction SilentlyContinue
                        
                    } elseif ($Url.StartsWith("http://") -or $Url.StartsWith("https://")) {
                        $result.Type = "HTTP URL"
                        $result.TestMethod = "Invoke-WebRequest"
                        
                        try {
                            $response = Invoke-WebRequest -Uri $Url -Method Head -TimeoutSec 10 -ErrorAction Stop
                            $result.Available = ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400)
                        } catch {
                            $result.Available = $false
                            $result.Error = $_.Exception.Message
                        }
                        
                    } else {
                        $result.Type = "Unknown Path"
                        $result.TestMethod = "Test-Path (fallback)"
                        $result.Available = Test-Path -Path $Url -ErrorAction SilentlyContinue
                    }
                    
                } catch {
                    $result.Available = $false
                    $result.Error = $_.Exception.Message
                }
                
                return $result
            }
            
            return Test-URLAvailability -Url $url -LineNumber $lineNumber
            
        } -ArgumentList $url, $lineNumber, ${function:Test-URLAvailability}
        
        $jobs += $job
    }
    
    # Wait for batch to complete and collect results
    $results = $jobs | Wait-Job | Receive-Job
    $jobs | Remove-Job
    
    # Process results
    foreach ($result in $results) {
        $processedCount++
        
        if ($result.Available) {
            $stats.Available++
        } else {
            $stats.Unavailable++
            $unavailableUrls += $result
            
            # Log unavailable URL
            $errorMsg = if ($result.Error) { " - Error: $($result.Error)" } else { "" }
            Write-LogEntry "UNAVAILABLE (Line $($result.LineNumber)): $($result.Url) [$($result.Type)]$errorMsg" $LogFile
        }
        
        if ($result.Error) {
            $stats.Errors++
        }
        
        # Progress update
        if ($processedCount % 100 -eq 0 -or $processedCount -eq $stats.Total) {
            $percentComplete = [Math]::Round(($processedCount / $stats.Total) * 100, 1)
            Write-Host "Progress: $processedCount/$($stats.Total) ($percentComplete%) - Available: $($stats.Available), Unavailable: $($stats.Unavailable)" -ForegroundColor Cyan
        }
    }
}

# Save unavailable URLs to file
Write-Host "`nSaving unavailable URLs to $OutputFile..." -ForegroundColor Yellow

if ($unavailableUrls.Count -gt 0) {
    $unavailableUrls | ForEach-Object { "Line $($_.LineNumber): $($_.Url)" } | Out-File -FilePath $OutputFile -Encoding UTF8
    Write-LogEntry "Saved $($unavailableUrls.Count) unavailable URLs to $OutputFile" $LogFile
} else {
    "# No unavailable URLs found" | Out-File -FilePath $OutputFile -Encoding UTF8
    Write-LogEntry "No unavailable URLs found" $LogFile
}

# Final statistics
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n" -NoNewline
Write-Host "URL Availability Check Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "Total URLs checked: $($stats.Total)" -ForegroundColor White
Write-Host "Available: $($stats.Available)" -ForegroundColor Green
Write-Host "Unavailable: $($stats.Unavailable)" -ForegroundColor Red
Write-Host "Errors: $($stats.Errors)" -ForegroundColor Yellow
Write-Host "Duration: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor White
Write-Host "Results saved to: $OutputFile" -ForegroundColor White
Write-Host "Detailed log: $LogFile" -ForegroundColor White

Write-LogEntry "Check completed. Total: $($stats.Total), Available: $($stats.Available), Unavailable: $($stats.Unavailable), Errors: $($stats.Errors)" $LogFile
Write-LogEntry "Duration: $($duration.ToString('hh\:mm\:ss'))" $LogFile

# Summary by URL type
Write-Host "`nURL Type Summary:" -ForegroundColor Yellow
$typeStats = $unavailableUrls | Group-Object Type | Sort-Object Count -Descending
foreach ($typeStat in $typeStats) {
    Write-Host "  $($typeStat.Name): $($typeStat.Count) unavailable" -ForegroundColor Red
    Write-LogEntry "URL Type - $($typeStat.Name): $($typeStat.Count) unavailable" $LogFile
}

if ($stats.Unavailable -eq 0) {
    Write-Host "`nAll URLs are accessible! 🎉" -ForegroundColor Green
}
