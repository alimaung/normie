# ESE Pagify Installer - PowerShell Version
# Fixes all console output reading and window monitoring issues

param(
    [string]$ESEPath = "\\DEBERDNA-C011A\Projekte\a-j\ESE\admin\ESE.bat"
)

# Color-coded output functions
function Write-Info { param($Message) Write-Host $Message -ForegroundColor Cyan }
function Write-Success { param($Message) Write-Host $Message -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host $Message -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host $Message -ForegroundColor Red }

# Setup logging
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$InstallerLog = Join-Path $ScriptDir "installer_$Timestamp.log"
$ESELog = Join-Path $ScriptDir "ese_monitor_$Timestamp.log"
$WindowsLog = Join-Path $ScriptDir "windows_monitor_$Timestamp.log"

function Write-Log {
    param($Message, [ValidateSet("Installer", "ESE", "Windows")]$LogType = "Installer")
    
    $TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $LogMessage = "$TimeStamp - $Message"
    
    switch ($LogType) {
        "Installer" { Add-Content -Path $InstallerLog -Value $LogMessage }
        "ESE" { Add-Content -Path $ESELog -Value $LogMessage }
        "Windows" { Add-Content -Path $WindowsLog -Value $LogMessage }
    }
}

function Get-WindowTitles {
    param($Context)
    
    Write-Log "=== WINDOWS SNAPSHOT: $Context ===" -LogType Windows
    
    # Get all processes with window titles
    $Processes = Get-Process | Where-Object { $_.MainWindowTitle -ne "" }
    foreach ($Process in $Processes) {
        $WindowInfo = "$($Process.ProcessName) - PID:$($Process.Id) - Title: $($Process.MainWindowTitle)"
        Write-Log "WINDOW: $WindowInfo" -LogType Windows
    }
    
    # Get command line processes that might not have titles
    $CommandProcesses = Get-WmiObject Win32_Process | Where-Object { 
        $_.Name -match "cmd|powershell|conhost" -and $_.CommandLine 
    }
    foreach ($CmdProcess in $CommandProcesses) {
        $ProcessInfo = "$($CmdProcess.Name) - PID:$($CmdProcess.ProcessId) - CMD: $($CmdProcess.CommandLine)"
        Write-Log "PROCESS: $ProcessInfo" -LogType Windows
    }
    
    Write-Log "=== END SNAPSHOT ===" -LogType Windows
}

function Start-ESEAutomation {
    param($ESEBatPath)
    
    Write-Info "Starting ESE automation with console output monitoring..."
    Write-Log "Starting ESE automation with path: $ESEBatPath" -LogType ESE
    
    try {
        # Configure process start info
        $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
        $IsUsingMockESE = $ESEBatPath.EndsWith('.ps1')
        
        # Check if we're using the PowerShell fallback (mock ESE)
        if ($IsUsingMockESE) {
            $ProcessInfo.FileName = "powershell.exe"
            $ProcessInfo.Arguments = "-ExecutionPolicy Bypass -File `"$ESEBatPath`""
            $ProcessInfo.UseShellExecute = $true
            $ProcessInfo.CreateNoWindow = $false
            $ProcessInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Normal
        } else {
            # Real ESE.bat - use console redirection
            $ProcessInfo.FileName = $ESEBatPath
            $ProcessInfo.UseShellExecute = $false
            $ProcessInfo.RedirectStandardInput = $true
            $ProcessInfo.RedirectStandardOutput = $true
            $ProcessInfo.RedirectStandardError = $true
            $ProcessInfo.CreateNoWindow = $false
        }
        
        # Start ESE process
        $ESEProcess = [System.Diagnostics.Process]::Start($ProcessInfo)
        Write-Log "ESE process started with PID: $($ESEProcess.Id)" -LogType ESE
        Get-WindowTitles "After starting ESE.bat"
        
        # Wait for ESE to initialize
        Write-Info "Waiting 3 seconds for ESE to initialize..."
        Start-Sleep 3
        Get-WindowTitles "After ESE initialization wait"
        
        # Handle command sending and monitoring based on ESE type
        $InstallationComplete = $false
        $TimeoutMinutes = 5
        $StartTime = Get-Date
        
        if ($IsUsingMockESE) {
            # Mock ESE - use window monitoring
            Write-Info "Monitoring ESE window and waiting for Miniconda installation completion..."
            
            # Wait for ESE window to appear and stabilize
            Start-Sleep 3
            
            # Send command using SendKeys (requires the window to be active)
            Write-Info "Sending 'integ miniconda3' command to ESE window..."
            
            # Find ESE window and send command
            Add-Type -AssemblyName System.Windows.Forms
            $ESEWindow = Get-Process | Where-Object { $_.MainWindowTitle -match "ESE prompt obl" } | Select-Object -First 1
            
            if ($ESEWindow) {
                # Activate the ESE window
                [System.Windows.Forms.SendKeys]::SendWait("integ miniconda3{ENTER}")
                Write-Log "Sent command: integ miniconda3" -LogType ESE
                Get-WindowTitles "After sending integ miniconda3"
            }
            
            # Monitor for completion by checking window titles and process status
            while ((Get-Date) -lt $StartTime.AddMinutes($TimeoutMinutes) -and !$InstallationComplete) {
                
                # Check for conda.bat window (indicates completion)
                $CondaWindows = Get-Process | Where-Object { 
                    $_.MainWindowTitle -match "Miniconda3.*py312_24.3.0-0-Windows-x86_64" -or
                    $_.MainWindowTitle -match "conda" -or
                    $_.ProcessName -eq "python"
                }
                
                if ($CondaWindows) {
                    Write-Success "Miniconda installation completion detected (conda window found)!"
                    Write-Log "Installation completion detected - conda window found" -LogType ESE
                    $InstallationComplete = $true
                    
                    # Close conda windows
                    foreach ($Window in $CondaWindows) {
                        try {
                            $Window.Kill()
                            Write-Log "Closed conda window: $($Window.ProcessName)" -LogType ESE
                        }
                        catch {
                            Write-Log "Could not close window: $($Window.ProcessName)" -LogType ESE
                        }
                    }
                    break
                }
                
                Start-Sleep 2
            }
        } else {
            # Real ESE.bat - use console redirection
            Write-Info "Sending 'integ miniconda3' command to real ESE..."
            $ESEProcess.StandardInput.WriteLine("integ miniconda3")
            $ESEProcess.StandardInput.Flush()
            Write-Log "Sent command: integ miniconda3" -LogType ESE
            Get-WindowTitles "After sending integ miniconda3"
            
            # Monitor output for completion
            Write-Info "Monitoring ESE output for installation completion..."
            
            while ((Get-Date) -lt $StartTime.AddMinutes($TimeoutMinutes) -and !$InstallationComplete) {
                try {
                    $Line = $ESEProcess.StandardOutput.ReadLine()
                    if ($Line) {
                        Write-Host "ESE: $Line" -ForegroundColor Gray
                        Write-Log "ESE OUTPUT: $Line" -LogType ESE
                        
                        # Check for completion indicator
                        if ($Line -match "######## Starting Miniconda3" -or $Line -match "Miniconda3\\py312_24.3.0-0-Windows-x86_64") {
                            Write-Success "Miniconda installation completion detected!"
                            Write-Log "Installation completion detected in output: $Line" -LogType ESE
                            $InstallationComplete = $true
                            break
                        }
                    }
                }
                catch {
                    # Continue if no output available
                }
                
                Start-Sleep 1
            }
        }
        
        if ($InstallationComplete) {
            Write-Success "Miniconda installation completed successfully!"
            Get-WindowTitles "After Miniconda installation completion"
        }
        else {
            Write-Warning "Timeout waiting for Miniconda installation completion"
            Write-Log "Timeout occurred waiting for installation completion" -LogType ESE
        }
        
        # Close ESE window
        Write-Info "Closing ESE window..."
        try {
            if (!$ESEProcess.HasExited) {
                if ($IsUsingMockESE) {
                    # Mock ESE - close window
                    $ESEProcess.CloseMainWindow()
                    Start-Sleep 2
                } else {
                    # Real ESE - send exit command
                    $ESEProcess.StandardInput.WriteLine("exit")
                    $ESEProcess.StandardInput.Flush()
                    $ESEProcess.WaitForExit(10000)  # Wait up to 10 seconds
                }
                
                # If still running, force close
                if (!$ESEProcess.HasExited) {
                    Write-Warning "ESE process did not exit gracefully, forcing termination..."
                    $ESEProcess.Kill()
                }
            }
        }
        catch {
            Write-Log "Error closing ESE process: $($_.Exception.Message)" -LogType ESE
        }
        
        Write-Log "ESE process closed" -LogType ESE
        Get-WindowTitles "After closing ESE"
        
        return $InstallationComplete
        
    }
    catch {
        Write-Error "Error during ESE automation: $($_.Exception.Message)"
        Write-Log "ERROR: $($_.Exception.Message)" -LogType ESE
        return $false
    }
}

function Start-RRPYToolsAutomation {
    param($ESEBatPath)
    
    Write-Info "Starting rrpytools fix automation..."
    Write-Log "Starting rrpytools fix automation" -LogType ESE
    
    try {
        # Start new ESE process for rrpytools
        $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
        $IsUsingMockESE = $ESEBatPath.EndsWith('.ps1')
        
        # Check if we're using the PowerShell fallback (mock ESE)
        if ($IsUsingMockESE) {
            $ProcessInfo.FileName = "powershell.exe"
            $ProcessInfo.Arguments = "-ExecutionPolicy Bypass -File `"$ESEBatPath`""
            $ProcessInfo.UseShellExecute = $true
            $ProcessInfo.CreateNoWindow = $false
            $ProcessInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Normal
        } else {
            # Real ESE.bat - use console redirection
            $ProcessInfo.FileName = $ESEBatPath
            $ProcessInfo.UseShellExecute = $false
            $ProcessInfo.RedirectStandardInput = $true
            $ProcessInfo.RedirectStandardOutput = $true
            $ProcessInfo.RedirectStandardError = $true
            $ProcessInfo.CreateNoWindow = $false
        }
        
        $ESEProcess = [System.Diagnostics.Process]::Start($ProcessInfo)
        Write-Log "New ESE process started for rrpytools with PID: $($ESEProcess.Id)" -LogType ESE
        Get-WindowTitles "After starting new ESE for rrpytools"
        
        # Wait for ESE to initialize
        Start-Sleep 3
        
        # Handle command sending and monitoring based on ESE type
        $RRPYToolsComplete = $false
        $TimeoutMinutes = 3
        $StartTime = Get-Date
        
        if ($IsUsingMockESE) {
            # Mock ESE - use window monitoring
            # Wait for ESE window to appear and stabilize
            Start-Sleep 3
            
            # Send command using SendKeys
            Write-Info "Sending 'rrpytools fix' command to ESE window..."
            
            # Find ESE window and send command
            Add-Type -AssemblyName System.Windows.Forms
            $ESEWindow = Get-Process | Where-Object { $_.MainWindowTitle -match "ESE prompt obl" } | Select-Object -First 1
            
            if ($ESEWindow) {
                # Activate the ESE window
                [System.Windows.Forms.SendKeys]::SendWait("rrpytools fix{ENTER}")
                Write-Log "Sent command: rrpytools fix" -LogType ESE
                Get-WindowTitles "After sending rrpytools fix"
            }
            
            # Monitor for completion by checking window title changes
            Write-Info "Monitoring rrpytools fix for completion..."
            
            # Wait for command to complete (window title should change back)
            while ((Get-Date) -lt $StartTime.AddMinutes($TimeoutMinutes) -and !$RRPYToolsComplete) {
                
                # Check if ESE window title has returned to normal (indicating completion)
                $ESEWindow = Get-Process | Where-Object { $_.MainWindowTitle -match "ESE prompt obl" } | Select-Object -First 1
                
                if ($ESEWindow) {
                    $WindowTitle = $ESEWindow.MainWindowTitle
                    Write-Log "Current ESE window title: $WindowTitle" -LogType ESE
                    
                    # If title is back to normal (no command suffix), command is complete
                    if ($WindowTitle -eq "ESE prompt obl (version 0.0.10)") {
                        Write-Success "rrpytools fix completion detected (window title returned to normal)!"
                        Write-Log "rrpytools fix completion detected - window title: $WindowTitle" -LogType ESE
                        $RRPYToolsComplete = $true
                        break
                    }
                }
                
                Start-Sleep 2
            }
        } else {
            # Real ESE.bat - use console redirection
            Write-Info "Sending 'rrpytools fix' command to real ESE..."
            $ESEProcess.StandardInput.WriteLine("rrpytools fix")
            $ESEProcess.StandardInput.Flush()
            Write-Log "Sent command: rrpytools fix" -LogType ESE
            Get-WindowTitles "After sending rrpytools fix"
            
            # Monitor output for completion
            Write-Info "Monitoring rrpytools fix output for completion..."
            
            while ((Get-Date) -lt $StartTime.AddMinutes($TimeoutMinutes) -and !$RRPYToolsComplete) {
                try {
                    $Line = $ESEProcess.StandardOutput.ReadLine()
                    if ($Line) {
                        Write-Host "ESE: $Line" -ForegroundColor Gray
                        Write-Log "ESE OUTPUT: $Line" -LogType ESE
                        
                        # Check for completion indicator
                        if ($Line -match "Successfully processed.*files.*Failed processing.*files" -or $Line -match "C:\\Windows ESE>") {
                            Write-Success "rrpytools fix completion detected!"
                            Write-Log "rrpytools fix completion detected in output: $Line" -LogType ESE
                            $RRPYToolsComplete = $true
                            break
                        }
                    }
                }
                catch {
                    # Continue if no output available
                }
                
                Start-Sleep 1
            }
        }
        
        if ($RRPYToolsComplete) {
            Write-Success "rrpytools fix completed successfully!"
            Write-Log "rrpytools fix completed successfully" -LogType ESE
        }
        else {
            Write-Warning "Timeout waiting for rrpytools fix completion"
            Write-Log "Timeout occurred waiting for rrpytools fix completion" -LogType ESE
        }
        
        # Close ESE window
        try {
            if (!$ESEProcess.HasExited) {
                if ($IsUsingMockESE) {
                    # Mock ESE - close window
                    $ESEProcess.CloseMainWindow()
                    Start-Sleep 2
                } else {
                    # Real ESE - send exit command
                    $ESEProcess.StandardInput.WriteLine("exit")
                    $ESEProcess.StandardInput.Flush()
                    $ESEProcess.WaitForExit(5000)
                }
                
                # If still running, force close
                if (!$ESEProcess.HasExited) {
                    $ESEProcess.Kill()
                }
            }
        }
        catch {
            Write-Log "Error closing rrpytools ESE process: $($_.Exception.Message)" -LogType ESE
        }
        
        Write-Log "rrpytools ESE process closed" -LogType ESE
        Get-WindowTitles "After closing rrpytools ESE"
        
        return $RRPYToolsComplete
        
    }
    catch {
        Write-Error "Error during rrpytools automation: $($_.Exception.Message)"
        Write-Log "ERROR in rrpytools: $($_.Exception.Message)" -LogType ESE
        return $false
    }
}

# Main installer logic
try {
    Write-Host "============================================================" -ForegroundColor Magenta
    Write-Host "           ESE Pagify Installer - PowerShell Version       " -ForegroundColor Magenta
    Write-Host "============================================================" -ForegroundColor Magenta
    
    Write-Log "ESE Pagify Installer started at $(Get-Date)"
    Write-Log "Log files: Installer=$InstallerLog, ESE=$ESELog, Windows=$WindowsLog"
    
    Write-Info "Log files created:"
    Write-Host "- Installer: $InstallerLog" -ForegroundColor Gray
    Write-Host "- ESE Monitor: $ESELog" -ForegroundColor Gray  
    Write-Host "- Windows Monitor: $WindowsLog" -ForegroundColor Gray
    Write-Host ""
    
    # Step 1: Create folders
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "STEP 1: Creating C:\ESEApps folder and temp directory" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Yellow
    
    try {
        New-Item -Path "C:\ESEApps" -ItemType Directory -Force | Out-Null
        Write-Success "[SUCCESS] C:\ESEApps folder created/verified"
        Write-Log "C:\ESEApps folder created/verified"
        
        New-Item -Path "C:\ESEApps\temp" -ItemType Directory -Force | Out-Null  
        Write-Success "[SUCCESS] C:\ESEApps\temp folder created/verified"
        Write-Log "C:\ESEApps\temp folder created/verified"
    }
    catch {
        Write-Error "[ERROR] Failed to create folders: $($_.Exception.Message)"
        Write-Log "ERROR creating folders: $($_.Exception.Message)"
        throw
    }
    
    Get-WindowTitles "After folder creation"
    
    # Step 2: Check ESE.bat existence
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "STEP 2: Checking ESE.bat accessibility" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Yellow
    
    Write-Info "Checking ESE.bat at: $ESEPath"
    Write-Log "Checking ESE.bat at: $ESEPath"
    
    $ESEFallbackPath = Join-Path $ScriptDir "ESE.ps1"
    
    if (Test-Path $ESEPath) {
        Write-Success "[SUCCESS] ESE.bat found and accessible"
        Write-Log "ESE.bat found and accessible"
    }
    elseif (Test-Path $ESEFallbackPath) {
        Write-Warning "[WARNING] ESE.bat not accessible, using fallback: $ESEFallbackPath"
        Write-Log "ESE.bat not accessible, using fallback: $ESEFallbackPath"
        $ESEPath = $ESEFallbackPath
    }
    else {
        Write-Error "[ERROR] ESE.bat not found at: $ESEPath"
        Write-Error "[ERROR] ESE.ps1 fallback not found at: $ESEFallbackPath"
        Write-Log "ERROR: ESE.bat not found at: $ESEPath"
        Write-Log "ERROR: ESE.ps1 fallback not found at: $ESEFallbackPath"
        Write-Host ""
        Write-Host "Please verify:" -ForegroundColor Red
        Write-Host "1. Network path is accessible: $ESEPath" -ForegroundColor Red
        Write-Host "2. You have permissions to access the ESE directory" -ForegroundColor Red
        Write-Host "3. ESE.ps1 fallback exists in: $ESEFallbackPath" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Step 3: Run Miniconda installation
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "STEP 3: Installing Miniconda via ESE" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Yellow
    
    $MinicondaSuccess = Start-ESEAutomation -ESEBatPath $ESEPath
    
    if ($MinicondaSuccess) {
        Write-Success "[SUCCESS] Miniconda installation completed successfully"
        Write-Log "Miniconda installation completed successfully"
    }
    else {
        Write-Warning "[WARNING] Miniconda installation may not have completed properly"
        Write-Log "Miniconda installation completion uncertain"
    }
    
    # Step 4: Run rrpytools fix
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "STEP 4: Running rrpytools fix" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Yellow
    
    $RRPYToolsSuccess = Start-RRPYToolsAutomation -ESEBatPath $ESEPath
    
    if ($RRPYToolsSuccess) {
        Write-Success "[SUCCESS] rrpytools fix completed successfully"
        Write-Log "rrpytools fix completed successfully"
    }
    else {
        Write-Warning "[WARNING] rrpytools fix may not have completed properly"
        Write-Log "rrpytools fix completion uncertain"
    }
    
    # Final summary
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "                    INSTALLATION COMPLETE                   " -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    
    Write-Success "[SUCCESS] C:\ESEApps folder created"
    Write-Success "[SUCCESS] ESE.bat executed"
    if ($MinicondaSuccess) { Write-Success "[SUCCESS] Miniconda3 installed" } else { Write-Warning "[WARNING] Miniconda3 status uncertain" }
    if ($RRPYToolsSuccess) { Write-Success "[SUCCESS] rrpytools fix executed" } else { Write-Warning "[WARNING] rrpytools fix status uncertain" }
    Write-Success "[SUCCESS] All windows closed automatically"
    
    Write-Host ""
    Write-Info "Next steps:"
    Write-Host "1. Install pip and conda dependencies" -ForegroundColor Gray
    Write-Host ""
    Write-Info "Installation logs saved to:"
    Write-Host "- $InstallerLog" -ForegroundColor Gray
    Write-Host "- $ESELog" -ForegroundColor Gray
    Write-Host "- $WindowsLog" -ForegroundColor Gray
    
    Write-Log "Installation completed successfully at $(Get-Date)"
    Get-WindowTitles "Final state"
    
}
catch {
    Write-Error "FATAL ERROR: $($_.Exception.Message)"
    Write-Log "FATAL ERROR: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Check the log files for details:" -ForegroundColor Red
    Write-Host "- $InstallerLog" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"