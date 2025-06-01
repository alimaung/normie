@echo off
REM Startup script for Normie Django Application (Windows)
REM This batch file runs the Python startup script

echo Starting Normie Django Application...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Try the specific Python installation first, then fall back to system Python
try (
    "C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\python.exe" launch.py
) || (
    python launch.py
)

REM Pause to see any error messages
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)