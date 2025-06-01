@echo off
REM Directory Analyzer Runner
REM Runs the Python directory analyzer with error handling and logging

echo ================================================================================
echo Directory Analyzer Runner
echo ================================================================================
echo Starting at: %date% %time%
echo.

REM Set the specific Python path
set "PYTHON_PATH=C:\ESEApps\miniconda\python\python.exe"

REM Check if Python is available at the specified path
if not exist "%PYTHON_PATH%" (
    echo ERROR: Python not found at: %PYTHON_PATH%
    echo Please verify the Python installation path
    pause
    exit /b 1
)

REM Display Python version
echo Python path: %PYTHON_PATH%
echo Python version:
"%PYTHON_PATH%" --version
echo.

REM Change to the script directory
cd /d "%~dp0"
echo Current directory: %cd%
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Set log file with timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"
set "logfile=logs\analysis_%timestamp%.log"

echo Log file: %logfile%
echo.

REM Run the Python script with live output and log capture
echo Starting directory analysis with live output...
echo ================================================================================

REM Log the start info
echo Analysis started at: %date% %time% > "%logfile%"
echo Python path: %PYTHON_PATH% >> "%logfile%"
echo ================================================================================ >> "%logfile%"

REM Run Python script - this will show live output and we'll capture it separately
echo Running Python analysis script...
echo.

REM Use a simple approach: run with live output, then append to log
"%PYTHON_PATH%" dir_analysis.py 2>&1 | "%PYTHON_PATH%" -c "import sys; [print(line.rstrip(), file=sys.stdout, flush=True) or open(r'%logfile%', 'a', encoding='utf-8').write(line) for line in sys.stdin]"

set "exit_code=%errorlevel%"

echo.
echo ================================================================================
echo Analysis completed at: %date% %time%
echo Exit code: %exit_code%

REM Log the completion
echo. >> "%logfile%"
echo Analysis completed at: %date% %time% >> "%logfile%"
echo Exit code: %exit_code% >> "%logfile%"

REM Check exit code and provide feedback
if %exit_code% equ 0 (
    echo.
    echo SUCCESS: Directory analysis completed successfully!
    echo.
    echo Generated files:
    if exist "analysis_report.txt" (
        echo   - analysis_report.txt ^(summary report^)
        for %%A in ("analysis_report.txt") do echo     Size: %%~zA bytes
    )
    if exist "directory_index.txt" (
        echo   - directory_index.txt ^(detailed file listing^)
        for %%A in ("directory_index.txt") do echo     Size: %%~zA bytes
    )
    echo   - %logfile% ^(execution log^)
    echo.
    echo You can now review the generated reports.
) else (
    echo.
    echo ERROR: Directory analysis failed with exit code %exit_code%
    echo.
    echo Please check the log file for details: %logfile%
    echo.
    echo Common issues:
    echo   - Network path not accessible
    echo   - Insufficient permissions
    echo   - Python dependencies missing
    echo   - Network connectivity issues
)

echo.
echo Press any key to open the results folder...
pause >nul

REM Open the current directory in Windows Explorer
start "" "%cd%"

REM Keep window open for review
echo.
echo Press any key to exit...
pause >nul

exit /b %exit_code% 