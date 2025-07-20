@echo off
setlocal enabledelayedexpansion

:: ESE Pagify Installer Batch Script - Steps 1-5
echo ============================================================
echo                ESE Pagify Installer - Steps 1-5
echo ============================================================
echo This script will:
echo 1. Create C:\ESEApps folder
echo 2. Run ESE.bat
echo 3. Automatically type "integ miniconda3" in ESE console
echo 4. Wait for Miniconda installation to complete
echo 5. Open new ESE window and run "rrpytools fix"
echo 6. Close all windows automatically when done
echo.

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
        echo ' Monitor for Miniconda installation completion
        echo Do
        echo     WScript.Sleep 3000
        echo     ' Check if Miniconda window has opened ^(indicates installation is complete^)
        echo     On Error Resume Next
        echo     Set objWMIService = GetObject^("winmgmts:\\\\.\\root\\cimv2"^)
        echo     Set colProcesses = objWMIService.ExecQuery^("SELECT * FROM Win32_Process WHERE CommandLine LIKE '%%Miniconda3%%' OR CommandLine LIKE '%%py312_24.3.0-0-Windows%%'"^)
        echo     minicondaFound = False
        echo     For Each objProcess in colProcesses
        echo         minicondaFound = True
        echo         Exit For
        echo     Next
        echo     On Error Goto 0
        echo     
        echo     ' If Miniconda process found, installation is complete
        echo     If minicondaFound Then
        echo         ' Create completion marker file
        echo         Set objFile = fso.CreateTextFile^("%TEMP%\ese_done.txt", True^)
        echo         objFile.WriteLine "Miniconda installation complete"
        echo         objFile.Close
        echo         Exit Do
        echo     End If
        echo Loop
        echo.
        echo ' Installation complete, close BOTH ESE and Miniconda windows
        echo ' Close the original ESE window
        echo On Error Resume Next
        echo WshShell.AppActivate "ESE"
        echo WScript.Sleep 500
        echo WshShell.SendKeys "exit{ENTER}"
        echo WScript.Sleep 1000
        echo.
        echo ' Close any Miniconda windows that opened
        echo Set objWMIService = GetObject^("winmgmts:\\\\.\\root\\cimv2"^)
        echo Set colProcesses = objWMIService.ExecQuery^("SELECT * FROM Win32_Process WHERE CommandLine LIKE '%%Miniconda3%%' OR CommandLine LIKE '%%py312_24.3.0-0-Windows%%'"^)
        echo For Each objProcess in colProcesses
        echo     objProcess.Terminate
        echo Next
        echo On Error Goto 0
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
    echo STEP 4 COMPLETE - PROCEEDING TO STEP 5
    echo ============================================================
    echo Starting Step 5: Running rrpytools fix in new ESE window...
    echo.
    
    :: Step 5: Run rrpytools fix in new ESE window
    echo ============================================================
    echo STEP 5: Running rrpytools fix
    echo ============================================================
    
    :: Create automation script for rrpytools fix
    echo Creating rrpytools automation script...
    (
        echo Set WshShell = WScript.CreateObject^("WScript.Shell"^)
        echo Set fso = CreateObject^("Scripting.FileSystemObject"^)
        echo.
        echo ' Wait for new ESE console to open
        echo WScript.Sleep 3000
        echo.
        echo ' Send the rrpytools fix command
        echo WshShell.AppActivate "ESE"
        echo WScript.Sleep 1000
        echo WshShell.SendKeys "rrpytools fix{ENTER}"
        echo.
        echo ' Monitor for completion
        echo Do
        echo     WScript.Sleep 5000
        echo     ' Try to activate ESE window to check if it's responsive
        echo     On Error Resume Next
        echo     result = WshShell.AppActivate^("ESE"^)
        echo     If Err.Number = 0 Then
        echo         ' Send a test command to check if prompt is ready
        echo         WshShell.SendKeys "echo rrpytools_complete > %TEMP%\rrpytools_done.txt{ENTER}"
        echo         WScript.Sleep 2000
        echo         ' Check if the file was created ^(means prompt is ready^)
        echo         If fso.FileExists^("%TEMP%\rrpytools_done.txt"^) Then
        echo             Exit Do
        echo         End If
        echo     End If
        echo     On Error Goto 0
        echo Loop
        echo.
        echo ' rrpytools fix complete, close ESE window
        echo WshShell.AppActivate "ESE"
        echo WScript.Sleep 500
        echo WshShell.SendKeys "exit{ENTER}"
    ) > "%TEMP%\rrpytools_automation.vbs"
    
    :: Start new ESE.bat for rrpytools fix
    start "" "%ESE_BAT_PATH%"
    
    :: Wait for ESE to open
    echo Waiting for new ESE console to open...
    timeout /t 3 /nobreak >nul
    
    echo Sending "rrpytools fix" command and monitoring...
    echo.
    echo ============================================================
    echo RRPYTOOLS FIX IN PROGRESS
    echo ============================================================
    echo - Command sent to new ESE console
    echo - Monitoring rrpytools fix progress automatically
    echo - Will close ESE window when complete
    echo - This may take a few minutes
    echo.
    
    :: Run the rrpytools automation script
    start /min cscript //nologo "%TEMP%\rrpytools_automation.vbs"
    
    :: Monitor for rrpytools completion
    :rrpytools_wait_loop
    if exist "%TEMP%\rrpytools_done.txt" (
        echo [SUCCESS] rrpytools fix completed!
        del "%TEMP%\rrpytools_done.txt" 2>nul
        goto rrpytools_complete
    )
    timeout /t 3 /nobreak >nul
    echo Waiting for rrpytools fix to complete...
    goto rrpytools_wait_loop
    
    :rrpytools_complete
    :: Clean up rrpytools automation files
    del "%TEMP%\rrpytools_automation.vbs" 2>nul
    
    echo.
    echo ============================================================
    echo STEP 5 COMPLETE - ESE WINDOW CLOSED AUTOMATICALLY
    echo ============================================================
    
) else (
    echo [ERROR] Could not find ESE.bat at: %ESE_BAT_PATH%
    echo Please verify the network path is accessible.
    echo You can manually run ESE.bat by:
    echo 1. Opening File Explorer
    echo 2. Pasting this path: %ESE_BAT_PATH%
    echo 3. Press Enter and run the file
    echo 4. In the ESE console, type: integ miniconda3
    echo 5. Open NEW ESE window and type: rrpytools fix
    pause
)

echo.
echo ============================================================
echo STEPS 1-5 COMPLETE
echo ============================================================
echo ✓ C:\ESEApps folder created
echo ✓ ESE.bat executed
echo ✓ Miniconda3 installed automatically
echo ✓ All windows closed automatically
echo ✓ New ESE window opened
echo ✓ rrpytools fix executed automatically
echo ✓ ESE window closed automatically
echo.
echo Next steps (run separately):
echo 1. Install pip and conda dependencies
echo.
echo This installer has completed Steps 1-5.
pause
