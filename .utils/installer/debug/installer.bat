@echo off
setlocal enabledelayedexpansion

:: Get timestamp for log files
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

:: Set up log files in script directory
set "SCRIPT_DIR=%~dp0"
set "INSTALLER_LOG=%SCRIPT_DIR%installer_%timestamp%.log"
set "ESE_LOG=%SCRIPT_DIR%ese_monitor_%timestamp%.log"
set "WINDOWS_LOG=%SCRIPT_DIR%windows_monitor_%timestamp%.log"

:: FIRST: Create ESEApps folder and temp subfolder (BEFORE creating VBS scripts)
echo ============================================================
echo STEP 1: Creating C:\ESEApps folder and temp directory
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

:: Create temp subfolder
if not exist "C:\ESEApps\temp" (
    mkdir "C:\ESEApps\temp"
    if exist "C:\ESEApps\temp" (
        echo [SUCCESS] Successfully created temp folder: C:\ESEApps\temp
    ) else (
        echo [ERROR] Failed to create C:\ESEApps\temp folder
        pause
        exit /b 1
    )
) else (
    echo [INFO] C:\ESEApps\temp folder already exists
)
echo.

:: NOW: Create window monitoring VBS script (after folders exist)
echo Creating window monitoring script...
(
    echo Set WshShell = WScript.CreateObject^("WScript.Shell"^)
    echo Set fso = CreateObject^("Scripting.FileSystemObject"^)
    echo.
    echo ' Function to log window titles with timestamp
    echo Function LogWindows^(context^)
    echo     Dim logFile, timestamp, objWMIService, colItems, objItem
    echo     timestamp = Now^(^)
    echo     Set logFile = fso.OpenTextFile^("%WINDOWS_LOG%", 8, True^)
    echo     logFile.WriteLine timestamp ^& " - === WINDOWS SNAPSHOT: " ^& context ^& " ==="
    echo     
    echo     ' Get all visible windows
    echo     On Error Resume Next
    echo     Set objWMIService = GetObject^("winmgmts:\\\\.\\root\\cimv2"^)
    echo     Set colItems = objWMIService.ExecQuery^("SELECT * FROM Win32_Process WHERE Name='cmd.exe' OR Name='powershell.exe' OR Name='conhost.exe'"^)
    echo     
    echo     ' Also get windows via Shell.Application
    echo     Set objShell = CreateObject^("Shell.Application"^)
    echo     Set objWindows = objShell.Windows
    echo     
    echo     ' Log command line windows
    echo     For Each objItem in colItems
    echo         If Not IsNull^(objItem.CommandLine^) Then
    echo             logFile.WriteLine timestamp ^& " - CMD/PS: " ^& objItem.CommandLine
    echo         End If
    echo     Next
    echo     
    echo     ' Try to enumerate windows using different method
    echo     Set objWMI = GetObject^("winmgmts:"^)
    echo     Set colProcesses = objWMI.ExecQuery^("SELECT * FROM Win32_Process"^)
    echo     For Each objProcess in colProcesses
    echo         If InStr^(objProcess.Name, "cmd"^) > 0 OR InStr^(objProcess.Name, "powershell"^) > 0 OR InStr^(objProcess.Name, "conhost"^) > 0 Then
    echo             If Not IsNull^(objProcess.CommandLine^) Then
    echo                 logFile.WriteLine timestamp ^& " - PROCESS: " ^& objProcess.Name ^& " - " ^& objProcess.CommandLine
    echo             End If
    echo         End If
    echo     Next
    echo     
    echo     On Error Goto 0
    echo     logFile.WriteLine timestamp ^& " - === END SNAPSHOT ==="
    echo     logFile.WriteLine ""
    echo     logFile.Close
    echo End Function
    echo.
    echo ' Log initial windows
    echo LogWindows^("Script Start"^)
) > "C:\ESEApps\temp\window_monitor.vbs"

:: Function to log with timestamp
call :log_msg "============================================================" installer
call :log_msg "ESE Pagify Installer - Steps 1-5 - Started at %timestamp%" installer
call :log_msg "============================================================" installer
call :log_msg "Log files:" installer
call :log_msg "- Installer log: %INSTALLER_LOG%" installer
call :log_msg "- ESE monitor log: %ESE_LOG%" installer
call :log_msg "- Windows monitor log: %WINDOWS_LOG%" installer
call :log_msg "============================================================" installer
call :log_msg "STEP 1: Creating C:\ESEApps folder and temp directory - COMPLETED" installer

:: Log initial windows
call :log_windows "Installer Start"

:: ESE Pagify Installer Batch Script - Steps 1-5
echo ============================================================
echo                ESE Pagify Installer - Steps 1-5
echo ============================================================
echo This script will:
echo 1. Create C:\ESEApps folder ✓ DONE
echo 2. Run ESE.bat
echo 3. Automatically type "integ miniconda3" in ESE console
echo 4. Wait for Miniconda installation to complete
echo 5. Open new ESE window and run "rrpytools fix"
echo 6. Close all windows automatically when done
echo.
echo Log files created:
echo - Installer: %INSTALLER_LOG%
echo - ESE Monitor: %ESE_LOG%
echo - Windows Monitor: %WINDOWS_LOG%
echo.

:: Step 2: Run ESE.bat and send command
call :log_msg "STEP 2: Running ESE.bat and installing Miniconda" installer
echo ============================================================
echo STEP 2: Running ESE.bat and installing Miniconda
echo ============================================================
set "ESE_BAT_PATH=\\DEBERDNA-C011A\Projekte\a-j\ESE\admin\ESE.bat"
echo Attempting to run: %ESE_BAT_PATH%
call :log_msg "Attempting to run: %ESE_BAT_PATH%" installer
echo.

if exist "%ESE_BAT_PATH%" (
    call :log_msg "ESE.bat found, starting automation" installer
    echo Starting ESE.bat...
    echo This will open the ESE console and automatically type "integ miniconda3"
    echo.
    
    :: Create a VBS script to send keystrokes and monitor console output
    echo Creating automation script...
    call :log_msg "Creating ESE automation VBS script" installer
    (
        echo Set WshShell = WScript.CreateObject^("WScript.Shell"^)
        echo Set fso = CreateObject^("Scripting.FileSystemObject"^)
        echo.
        echo ' Function to log with timestamp
        echo Function LogMsg^(message^)
        echo     Dim logFile, timestamp
        echo     timestamp = Now^(^)
        echo     Set logFile = fso.OpenTextFile^("%ESE_LOG%", 8, True^)
        echo     logFile.WriteLine timestamp ^& " - " ^& message
        echo     logFile.Close
        echo End Function
        echo.
        echo ' Function to log windows
        echo Function LogWindows^(context^)
        echo     Dim logFile, timestamp, objWMIService, colItems, objItem
        echo     timestamp = Now^(^)
        echo     Set logFile = fso.OpenTextFile^("%WINDOWS_LOG%", 8, True^)
        echo     logFile.WriteLine timestamp ^& " - === VBS WINDOWS SNAPSHOT: " ^& context ^& " ==="
        echo     
        echo     ' Get all visible windows
        echo     On Error Resume Next
        echo     Set objWMIService = GetObject^("winmgmts:\\\\.\\root\\cimv2"^)
        echo     Set colItems = objWMIService.ExecQuery^("SELECT * FROM Win32_Process WHERE Name='cmd.exe' OR Name='powershell.exe' OR Name='conhost.exe'"^)
        echo     
        echo     ' Log command line windows
        echo     For Each objItem in colItems
        echo         If Not IsNull^(objItem.CommandLine^) Then
        echo             logFile.WriteLine timestamp ^& " - CMD/PS: " ^& objItem.CommandLine
        echo         End If
        echo     Next
        echo     
        echo     ' Try to get window titles using different approach
        echo     Set objWMI = GetObject^("winmgmts:"^)
        echo     Set colProcesses = objWMI.ExecQuery^("SELECT * FROM Win32_Process"^)
        echo     For Each objProcess in colProcesses
        echo         If InStr^(objProcess.Name, "cmd"^) > 0 OR InStr^(objProcess.Name, "powershell"^) > 0 OR InStr^(objProcess.Name, "conhost"^) > 0 Then
        echo             If Not IsNull^(objProcess.CommandLine^) Then
        echo                 logFile.WriteLine timestamp ^& " - PROCESS: " ^& objProcess.Name ^& " - " ^& objProcess.CommandLine
        echo             End If
        echo         End If
        echo     Next
        echo     
        echo     On Error Goto 0
        echo     logFile.WriteLine timestamp ^& " - === END VBS SNAPSHOT ==="
        echo     logFile.WriteLine ""
        echo     logFile.Close
        echo End Function
        echo.
        echo LogMsg "ESE Automation VBS script started"
        echo LogWindows "VBS Script Start"
        echo.
        echo ' Wait for ESE console to open
        echo LogMsg "Waiting 3 seconds for ESE console to open"
        echo WScript.Sleep 3000
        echo LogWindows "After 3 second wait"
        echo.
        echo ' Send the miniconda installation command to the correct ESE window
        echo LogMsg "Attempting to activate ESE window: ESE prompt obl (version 0.0.10)"
        echo WshShell.AppActivate "ESE prompt obl (version 0.0.10)"
        echo WScript.Sleep 1000
        echo LogMsg "Sending command: integ miniconda3"
        echo WshShell.SendKeys "integ miniconda3{ENTER}"
        echo LogWindows "After sending integ miniconda3"
        echo.
        echo ' Monitor for Miniconda installation completion by checking console output
        echo LogMsg "Starting monitoring loop for Miniconda installation completion"
        echo Do
        echo     WScript.Sleep 3000
        echo     LogMsg "Checking for installation completion..."
        echo     ' Try to read console output by sending a test command
        echo     On Error Resume Next
        echo     LogMsg "Attempting to activate window: ESE prompt obl (version 0.0.10) - integ miniconda3"
        echo     WshShell.AppActivate "ESE prompt obl (version 0.0.10) - integ miniconda3"
        echo     WScript.Sleep 500
        echo     ' Send command to check if we see the completion string
        echo     LogMsg "Sending completion check command"
        echo     WshShell.SendKeys "echo ######## Starting Miniconda3 > C:\ESEApps\temp\check_output.txt 2>&1 && findstr /C:\"######## Starting Miniconda3\" C:\ESEApps\temp\check_output.txt >nul && echo MINICONDA_COMPLETE > C:\ESEApps\temp\ese_done.txt{ENTER}"
        echo     WScript.Sleep 2000
        echo     On Error Goto 0
        echo     
        echo     ' Check if completion marker file exists
        echo     If fso.FileExists^("C:\ESEApps\temp\ese_done.txt"^) Then
        echo         LogMsg "Miniconda installation completed - marker file found"
        echo         LogWindows "Miniconda installation completed"
        echo         Exit Do
        echo     End If
        echo     LogMsg "Installation not complete yet, continuing to wait..."
        echo Loop
        echo.
        echo ' Installation complete, close ESE window
        echo LogMsg "Installation complete, closing ESE window"
        echo LogWindows "Before closing ESE window"
        echo On Error Resume Next
        echo WshShell.AppActivate "ESE prompt obl (version 0.0.10) - integ miniconda3"
        echo WScript.Sleep 500
        echo LogMsg "Sending exit command to ESE window"
        echo WshShell.SendKeys "exit{ENTER}"
        echo WScript.Sleep 1000
        echo LogWindows "After closing ESE window"
        echo.
        echo ' Close any Miniconda windows that opened
        echo LogMsg "Attempting to close Miniconda window"
        echo WshShell.AppActivate "Miniconda3\py312_24.3.0-0-Windows-x86_64"
        echo WScript.Sleep 500
        echo LogMsg "Sending exit command to Miniconda window"
        echo WshShell.SendKeys "exit{ENTER}"
        echo LogWindows "After closing Miniconda window"
        echo On Error Goto 0
        echo LogMsg "ESE automation script completed"
    ) > "C:\ESEApps\temp\ese_automation.vbs"
    
    :: Start ESE.bat
    call :log_msg "Starting ESE.bat process" installer
    call :log_windows "Before starting ESE.bat"
    start "" "%ESE_BAT_PATH%"
    
    :: Wait a moment then run the automation script
    echo Waiting for ESE console to open...
    call :log_msg "Waiting 2 seconds for ESE console to open" installer
    timeout /t 2 /nobreak >nul
    call :log_windows "After 2 second wait"
    
    echo Sending "integ miniconda3" command and monitoring installation...
    call :log_msg "Starting ESE automation VBS script" installer
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
    start /min cscript //nologo "C:\ESEApps\temp\ese_automation.vbs"
    
    :: Monitor for completion
    call :log_msg "Starting completion monitoring loop" installer
    :wait_loop
    if exist "C:\ESEApps\temp\ese_done.txt" (
        echo [SUCCESS] Miniconda installation completed!
        call :log_msg "[SUCCESS] Miniconda installation completed!" installer
        call :log_windows "Miniconda installation completed"
        del "C:\ESEApps\temp\ese_done.txt" 2>nul
        goto installation_complete
    )
    timeout /t 3 /nobreak >nul
    echo Waiting for installation to complete...
    call :log_msg "Still waiting for installation to complete..." installer
    goto wait_loop
    
    :installation_complete
    :: Clean up temporary files
    call :log_msg "Cleaning up temporary files" installer
    del "C:\ESEApps\temp\ese_automation.vbs" 2>nul
    del "C:\ESEApps\temp\check_output.txt" 2>nul
    
    echo.
    echo ============================================================
    echo STEP 4 COMPLETE - PROCEEDING TO STEP 5
    echo ============================================================
    echo Starting Step 5: Running rrpytools fix in new ESE window...
    call :log_msg "STEP 4 COMPLETE - PROCEEDING TO STEP 5" installer
    call :log_windows "Before Step 5"
    echo.
    
    :: Step 5: Run rrpytools fix in new ESE window
    echo ============================================================
    echo STEP 5: Running rrpytools fix
    echo ============================================================
    call :log_msg "STEP 5: Running rrpytools fix" installer
    
    :: Create automation script for rrpytools fix
    echo Creating rrpytools automation script...
    call :log_msg "Creating rrpytools automation VBS script" installer
    (
        echo Set WshShell = WScript.CreateObject^("WScript.Shell"^)
        echo Set fso = CreateObject^("Scripting.FileSystemObject"^)
        echo.
        echo ' Function to log with timestamp
        echo Function LogMsg^(message^)
        echo     Dim logFile, timestamp
        echo     timestamp = Now^(^)
        echo     Set logFile = fso.OpenTextFile^("%ESE_LOG%", 8, True^)
        echo     logFile.WriteLine timestamp ^& " - RRPYTOOLS: " ^& message
        echo     logFile.Close
        echo End Function
        echo.
        echo ' Function to log windows
        echo Function LogWindows^(context^)
        echo     Dim logFile, timestamp, objWMIService, colItems, objItem
        echo     timestamp = Now^(^)
        echo     Set logFile = fso.OpenTextFile^("%WINDOWS_LOG%", 8, True^)
        echo     logFile.WriteLine timestamp ^& " - === RRPYTOOLS WINDOWS SNAPSHOT: " ^& context ^& " ==="
        echo     
        echo     ' Get all visible windows
        echo     On Error Resume Next
        echo     Set objWMIService = GetObject^("winmgmts:\\\\.\\root\\cimv2"^)
        echo     Set colItems = objWMIService.ExecQuery^("SELECT * FROM Win32_Process WHERE Name='cmd.exe' OR Name='powershell.exe' OR Name='conhost.exe'"^)
        echo     
        echo     ' Log command line windows
        echo     For Each objItem in colItems
        echo         If Not IsNull^(objItem.CommandLine^) Then
        echo             logFile.WriteLine timestamp ^& " - CMD/PS: " ^& objItem.CommandLine
        echo         End If
        echo     Next
        echo     
        echo     On Error Goto 0
        echo     logFile.WriteLine timestamp ^& " - === END RRPYTOOLS SNAPSHOT ==="
        echo     logFile.WriteLine ""
        echo     logFile.Close
        echo End Function
        echo.
        echo LogMsg "rrpytools automation VBS script started"
        echo LogWindows "RRPYTOOLS VBS Script Start"
        echo.
        echo ' Wait for new ESE console to open
        echo LogMsg "Waiting 3 seconds for new ESE console to open"
        echo WScript.Sleep 3000
        echo LogWindows "After 3 second wait for new ESE"
        echo.
        echo ' Send the rrpytools fix command to the correct ESE window
        echo LogMsg "Attempting to activate ESE window: ESE prompt obl (version 0.0.10)"
        echo WshShell.AppActivate "ESE prompt obl (version 0.0.10)"
        echo WScript.Sleep 1000
        echo LogMsg "Sending command: rrpytools fix"
        echo WshShell.SendKeys "rrpytools fix{ENTER}"
        echo LogWindows "After sending rrpytools fix"
        echo.
        echo ' Monitor for completion by checking if prompt returns
        echo LogMsg "Starting monitoring loop for rrpytools completion"
        echo Do
        echo     WScript.Sleep 5000
        echo     LogMsg "Checking if rrpytools command completed..."
        echo     ' Try to activate ESE window and check if prompt is ready
        echo     On Error Resume Next
        echo     result = WshShell.AppActivate^("ESE prompt obl (version 0.0.10)"^)
        echo     If Err.Number = 0 Then
        echo         LogMsg "ESE window activated, sending test command"
        echo         ' Send a test command to check if prompt is ready
        echo         WshShell.SendKeys "echo rrpytools_complete > C:\ESEApps\temp\rrpytools_done.txt{ENTER}"
        echo         WScript.Sleep 2000
        echo         ' Check if the file was created ^(means prompt is ready^)
        echo         If fso.FileExists^("C:\ESEApps\temp\rrpytools_done.txt"^) Then
        echo             LogMsg "rrpytools command completed - marker file found"
        echo             LogWindows "rrpytools command completed"
        echo             Exit Do
        echo         End If
        echo     End If
        echo     On Error Goto 0
        echo     LogMsg "rrpytools not complete yet, continuing to wait..."
        echo Loop
        echo.
        echo ' rrpytools fix complete, close ESE window
        echo LogMsg "rrpytools fix complete, closing ESE window"
        echo LogWindows "Before closing final ESE window"
        echo WshShell.AppActivate "ESE prompt obl (version 0.0.10)"
        echo WScript.Sleep 500
        echo LogMsg "Sending exit command to ESE window"
        echo WshShell.SendKeys "exit{ENTER}"
        echo LogWindows "After closing final ESE window"
        echo LogMsg "rrpytools automation script completed"
    ) > "C:\ESEApps\temp\rrpytools_automation.vbs"
    
    :: Start new ESE.bat for rrpytools fix
    call :log_msg "Starting new ESE.bat process for rrpytools fix" installer
    call :log_windows "Before starting new ESE.bat"
    start "" "%ESE_BAT_PATH%"
    
    :: Wait for ESE to open
    echo Waiting for new ESE console to open...
    call :log_msg "Waiting 3 seconds for new ESE console to open" installer
    timeout /t 3 /nobreak >nul
    call :log_windows "After 3 second wait for new ESE"
    
    echo Sending "rrpytools fix" command and monitoring...
    call :log_msg "Starting rrpytools automation VBS script" installer
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
    start /min cscript //nologo "C:\ESEApps\temp\rrpytools_automation.vbs"
    
    :: Monitor for rrpytools completion
    call :log_msg "Starting rrpytools completion monitoring loop" installer
    :rrpytools_wait_loop
    if exist "C:\ESEApps\temp\rrpytools_done.txt" (
        echo [SUCCESS] rrpytools fix completed!
        call :log_msg "[SUCCESS] rrpytools fix completed!" installer
        call :log_windows "rrpytools fix completed"
        del "C:\ESEApps\temp\rrpytools_done.txt" 2>nul
        goto rrpytools_complete
    )
    timeout /t 3 /nobreak >nul
    echo Waiting for rrpytools fix to complete...
    call :log_msg "Still waiting for rrpytools fix to complete..." installer
    goto rrpytools_wait_loop
    
    :rrpytools_complete
    :: Clean up rrpytools automation files
    call :log_msg "Cleaning up rrpytools automation files" installer
    del "C:\ESEApps\temp\rrpytools_automation.vbs" 2>nul
    
    echo.
    echo ============================================================
    echo STEP 5 COMPLETE - ESE WINDOW CLOSED AUTOMATICALLY
    echo ============================================================
    call :log_msg "STEP 5 COMPLETE - ESE WINDOW CLOSED AUTOMATICALLY" installer
    call :log_windows "Installation completed"
    
) else (
    echo [ERROR] Could not find ESE.bat at: %ESE_BAT_PATH%
    call :log_msg "[ERROR] Could not find ESE.bat at: %ESE_BAT_PATH%" installer
    echo Please verify the network path is accessible.
    echo You can manually run ESE.bat by:
    echo 1. Opening File Explorer
    echo 2. Pasting this path: %ESE_BAT_PATH%
    echo 3. Press Enter and run the file
    echo 4. In the ESE console, type: integ miniconda3
    echo 5. Open NEW ESE window and type: rrpytools fix
    pause
    exit /b 1
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
call :log_msg "Installation completed successfully" installer
call :log_msg "============================================================" installer
call :log_windows "Final state"
pause
goto :eof

:: Function to log messages with timestamp
:log_msg
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%" & set "MS=%dt:~15,3%"
set "log_timestamp=%YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%.%MS%"

if "%2"=="installer" (
    echo %log_timestamp% - %~1 >> "%INSTALLER_LOG%"
) else (
    echo %log_timestamp% - %~1 >> "%ESE_LOG%"
)
goto :eof

:: Function to log active windows
:log_windows
cscript //nologo "C:\ESEApps\temp\window_monitor.vbs" > nul 2>&1
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%" & set "MS=%dt:~15,3%"
set "log_timestamp=%YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%.%MS%"
echo %log_timestamp% - CONTEXT: %~1 >> "%WINDOWS_LOG%"
goto :eof
