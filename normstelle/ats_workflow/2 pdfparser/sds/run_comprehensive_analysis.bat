@echo off
echo ============================================
echo   Comprehensive SDS Analysis Script
echo ============================================
echo.
echo This script will analyze all PDFs in the 'sds' folder for:
echo   - SDS detection (is it a valid Safety Data Sheet?)
echo   - Date validation (is it within 2-year validity?)
echo   - Critical issues (expired SDS files)
echo   - Action items (expiring soon)
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

echo Starting comprehensive analysis...
echo.

REM Run the comprehensive analysis script
python batch_detect_with_dates.py

echo.
echo ============================================
echo     Analysis Complete!
echo ============================================
echo.
echo Generated reports include:
echo   📊 HTML Report - Interactive web-based analysis
echo   📄 JSON Data - Machine-readable results
echo   📋 CSV Summary - Spreadsheet-compatible data
echo.
echo The HTML report includes:
echo   🚨 Critical Issues - Expired SDS files
echo   ⚠️  Action Needed - Files expiring soon
echo   📈 Overview - Summary of all findings
echo   📋 All Files - Complete file listing
echo.

REM Open the results folder in Windows Explorer
for /d %%i in (comprehensive_sds_analysis_*) do (
    echo Opening results folder: %%i
    start "" "%%i"
    goto :found
)

:found
echo.
echo TIP: Open the HTML report in your web browser for the best experience!
echo.
pause 