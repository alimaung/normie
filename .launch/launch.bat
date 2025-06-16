@echo off
REM Startup script for Normie Django Application (Windows)
REM This batch file runs the Python startup script

echo Starting Normie Django Application...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if the specific Python installation exists, then try it
if exist "C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\python.exe" (
    echo Using Miniconda Python...
    "C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\python.exe" launch.py
) else (
    echo Miniconda Python not found, using system Python...
    python launch.py
)

REM Check if there was an error and pause if so
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)