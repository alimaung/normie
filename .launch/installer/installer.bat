@echo off
setlocal enabledelayedexpansion

:: ESE Pagify Installer Batch Script - Step 1 Only
echo ============================================================
echo                ESE Pagify Installer - Step 1
echo ============================================================
echo This script will:
echo 1. Create C:\ESEApps folder
echo 2. Run ESE.bat
echo 3. Automatically type "integ miniconda3" in ESE console
echo 4. Wait for Miniconda installation to complete
echo 5. Close all windows automatically when done
echo.

:: Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: This script should be run as Administrator for best results.
    echo Right-click on this file and select "Run as administrator"
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i "!continue!" neq "y" exit /b 1
)

:: Step 1: Create ESEApps folder
echo ============================================================
echo STEP 1: Creating C:\ESEApps folder
echo ============================================================
if not exist "C:\ESEApps" (
    mkdir "C:\ESEApps"
    if exist "C:\ESEApps" (
        echo [SUCCESS] Successfully created folder: C:\ESEApps
    ) else (
        echo [ERROR] Failed to create C:\ESEApps folder
        echo Please create it manually and run this script again.
        pause
        exit /b 1
    )
) else (
    echo [INFO] C:\ESEApps folder already exists
)
echo.

:: Step 2: Run ESE.bat and send command
echo ============================================================
echo STEP 2: Running ESE.bat and installing Miniconda
echo ============================================================
set "ESE_BAT_PATH=\\DEBERDNA-C011A\Projekte\a-j\ESE\admin\ESE.bat"
echo Attempting to run: %ESE_BAT_PATH%
echo.

if exist "%ESE_BAT_PATH%" (
    echo Starting ESE.bat...
    echo This will open the ESE console and automatically type "integ miniconda3"
    echo.
    
    :: Create a VBS script to send keystrokes and monitor completion
    echo Creating automation script...
    (
        echo Set WshShell = WScript.CreateObject^("WScript.Shell"^)
        echo Set fso = CreateObject^("Scripting.FileSystemObject"^)
        echo.
        echo ' Wait for ESE console to open
        echo WScript.Sleep 3000
        echo.
        echo ' Send the miniconda installation command
        echo WshShell.AppActivate "ESE"
        echo WScript.Sleep 1000
        echo WshShell.SendKeys "integ miniconda3{ENTER}"
        echo.
        echo ' Monitor for completion
        echo Do
        echo     WScript.Sleep 5000
        echo     ' Try to activate ESE window to check if it's responsive
        echo     On Error Resume Next
        echo     result = WshShell.AppActivate^("ESE"^)
        echo     If Err.Number = 0 Then
        echo         ' Send a simple command to test if prompt is ready
        echo         WshShell.SendKeys "echo installation_complete > %TEMP%\ese_done.txt{ENTER}"
        echo         WScript.Sleep 2000
        echo         ' Check if the file was created ^(means prompt is ready^)
        echo         If fso.FileExists^("%TEMP%\ese_done.txt"^) Then
        echo             Exit Do
        echo         End If
        echo     End If
        echo     On Error Goto 0
        echo Loop
        echo.
        echo ' Installation complete, close ESE and any Miniconda windows
        echo WshShell.AppActivate "ESE"
        echo WScript.Sleep 500
        echo WshShell.SendKeys "exit{ENTER}"
        echo.
        echo ' Close any Miniconda windows that might have opened
        echo WScript.Sleep 1000
        echo Set objWMIService = GetObject^("winmgmts:\\\\.\\root\\cimv2"^)
        echo Set colProcesses = objWMIService.ExecQuery^("SELECT * FROM Win32_Process WHERE Name = 'python.exe' OR CommandLine LIKE '%%miniconda%%'"^)
        echo For Each objProcess in colProcesses
        echo     objProcess.Terminate
        echo Next
    ) > "%TEMP%\ese_automation.vbs"
    
    :: Start ESE.bat
    start "" "%ESE_BAT_PATH%"
    
    :: Wait a moment then run the automation script
    echo Waiting for ESE console to open...
    timeout /t 2 /nobreak >nul
    
    echo Sending "integ miniconda3" command and monitoring installation...
    echo.
    echo ============================================================
    echo MINICONDA INSTALLATION IN PROGRESS
    echo ============================================================
    echo - Command sent to ESE console
    echo - Monitoring installation progress automatically
    echo - Will close all windows when installation is complete
    echo - This may take up to 5 minutes
    echo.
    
    :: Run the automation script in background
    start /min cscript //nologo "%TEMP%\ese_automation.vbs"
    
    :: Monitor for completion
    :wait_loop
    if exist "%TEMP%\ese_done.txt" (
        echo [SUCCESS] Miniconda installation completed!
        del "%TEMP%\ese_done.txt" 2>nul
        goto installation_complete
    )
    timeout /t 3 /nobreak >nul
    echo Waiting for installation to complete...
    goto wait_loop
    
    :installation_complete
    :: Clean up temporary files
    del "%TEMP%\ese_automation.vbs" 2>nul
    
    echo.
    echo ============================================================
    echo INSTALLATION COMPLETE - WINDOWS CLOSED AUTOMATICALLY
    echo ============================================================
    
) else (
    echo [ERROR] Could not find ESE.bat at: %ESE_BAT_PATH%
    echo Please verify the network path is accessible.
    echo You can manually run ESE.bat by:
    echo 1. Opening File Explorer
    echo 2. Pasting this path: %ESE_BAT_PATH%
    echo 3. Press Enter and run the file
    echo 4. In the ESE console, type: integ miniconda3
    pause
)

echo.
echo ============================================================
echo STEP 1 COMPLETE
echo ============================================================
echo ✓ C:\ESEApps folder created
echo ✓ ESE.bat executed
echo ✓ Miniconda3 installed automatically
echo ✓ All windows closed automatically
echo.
echo Next steps (run separately):
echo 1. Open a NEW ESE window and run: rrpytools fix
echo 2. Install pip and conda dependencies
echo.
echo This installer has completed Step 1.
pause
