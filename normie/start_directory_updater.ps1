# Directory Updater Background Service
# Runs in separate PowerShell window to avoid blocking Django

param(
    [int]$IntervalMinutes = 5
)

# Set window title
$Host.UI.RawUI.WindowTitle = "Directory Updater Service"

Write-Host "============================================" -ForegroundColor Green
Write-Host "  Directory Updater Background Service" -ForegroundColor Green  
Write-Host "============================================" -ForegroundColor Green
Write-Host "Interval: $IntervalMinutes minutes" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Get script directory and navigate to project
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = $ScriptDir

# Navigate to continuous updater directory
$UpdaterDir = Join-Path $ProjectDir "..\normstelle\excelmigration\Verzeichnis\cu"

if (!(Test-Path $UpdaterDir)) {
    Write-Host "ERROR: Updater directory not found: $UpdaterDir" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

Set-Location $UpdaterDir

# Check if continuous_updater.py exists
if (!(Test-Path "continuous_updater.py")) {
    Write-Host "ERROR: continuous_updater.py not found in $UpdaterDir" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host "Starting continuous updates..." -ForegroundColor Green
Write-Host "Working directory: $UpdaterDir" -ForegroundColor Cyan

try {
    # Run the continuous updater
    py continuous_updater.py --continuous $IntervalMinutes
}
catch {
    Write-Host "ERROR: Failed to start updater: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host "Directory updater stopped." -ForegroundColor Yellow
Read-Host "Press Enter to close"
