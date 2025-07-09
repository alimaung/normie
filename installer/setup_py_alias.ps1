# PowerShell Script to Setup 'py' Alias for pagify
# Sets up alias in PowerShell profile (user-level, no admin required)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "            PowerShell 'py' Alias Setup for pagify" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Define the Python executable path
$pythonPath = "C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\python.exe"

# Check if Python exists
if (Test-Path $pythonPath) {
    Write-Host "[SUCCESS] Python found at: $pythonPath" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python not found at: $pythonPath" -ForegroundColor Red
    Write-Host "Please run the main installer first to install Miniconda." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Get PowerShell profile path
$profilePath = $PROFILE.CurrentUserAllHosts
Write-Host "PowerShell profile location: $profilePath" -ForegroundColor Yellow

# Create profile directory if it doesn't exist
$profileDir = Split-Path $profilePath -Parent
if (!(Test-Path $profileDir)) {
    Write-Host "Creating profile directory: $profileDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

# Define the alias command to add
$aliasCommand = "Set-Alias -Name py -Value '$pythonPath'"

# Check if profile exists
if (Test-Path $profilePath) {
    # Check if alias already exists in profile
    $profileContent = Get-Content $profilePath -Raw
    if ($profileContent -match "Set-Alias.*-Name py.*-Value") {
        Write-Host "[INFO] 'py' alias already exists in PowerShell profile" -ForegroundColor Yellow
        Write-Host "Updating existing alias..." -ForegroundColor Yellow
        
        # Remove existing py alias lines and add new one
        $updatedContent = $profileContent -replace "Set-Alias.*-Name py.*-Value.*", ""
        $updatedContent = $updatedContent.Trim() + "`n`n# pagify Python alias`n$aliasCommand"
        Set-Content -Path $profilePath -Value $updatedContent
    } else {
        Write-Host "[INFO] Adding 'py' alias to existing PowerShell profile" -ForegroundColor Yellow
        Add-Content -Path $profilePath -Value "`n`n# pagify Python alias`n$aliasCommand"
    }
} else {
    Write-Host "[INFO] Creating new PowerShell profile with 'py' alias" -ForegroundColor Yellow
    Set-Content -Path $profilePath -Value "# PowerShell Profile`n`n# pagify Python alias`n$aliasCommand"
}

Write-Host ""
Write-Host "[SUCCESS] 'py' alias has been added to PowerShell profile!" -ForegroundColor Green
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "                        USAGE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "1. Close and reopen PowerShell for changes to take effect" -ForegroundColor White
Write-Host "2. You can now use 'py' instead of the full python path:" -ForegroundColor White
Write-Host "   Example: py script.py" -ForegroundColor Green
Write-Host "   Example: py --version" -ForegroundColor Green
Write-Host ""
Write-Host "To test the alias immediately in this session, run:" -ForegroundColor Yellow
Write-Host "   . `$PROFILE" -ForegroundColor Cyan
Write-Host "   py --version" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to reload profile now
$reload = Read-Host "Reload PowerShell profile now to test alias? (y/n)"
if ($reload -eq "y" -or $reload -eq "Y") {
    try {
        . $PROFILE
        Write-Host ""
        Write-Host "[SUCCESS] Profile reloaded! Testing 'py' alias..." -ForegroundColor Green
        py --version
        Write-Host ""
        Write-Host "Alias is working! You can now use 'py' in PowerShell." -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Could not reload profile automatically." -ForegroundColor Yellow
        Write-Host "Please restart PowerShell to use the 'py' alias." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Setup complete! Press Enter to exit..." -ForegroundColor Green
Read-Host 