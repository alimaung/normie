@echo off
echo ====================================
echo     SDS Detection Batch Script
echo ====================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo Running SDS detection on all PDFs in the 'sds' folder...
echo.

REM Run the Python script
python batch_detect_sds.py

echo.
echo ====================================
echo     Detection Complete!
echo ====================================
echo.
echo Check the generated results folder for:
echo - HTML report (open in browser)
echo - CSV summary (open in Excel)
echo - JSON details (for further processing)
echo.

REM Open the results folder in Windows Explorer
for /d %%i in (sds_detection_results_*) do (
    echo Opening results folder: %%i
    start "" "%%i"
    goto :found
)

:found
echo.
pause 