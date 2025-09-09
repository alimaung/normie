@echo off
echo URL Availability Checker
echo =======================
echo.
echo This will check all URLs in urls_cleaned.txt for availability
echo and create a list of unavailable URLs.
echo.
echo Press any key to start...
pause >nul

powershell.exe -ExecutionPolicy Bypass -File "check_url_availability.ps1"

echo.
echo Check complete! Results saved to:
echo - urls_unavailable.txt (unavailable URLs)
echo - url_check_log.txt (detailed log)
echo.
pause
