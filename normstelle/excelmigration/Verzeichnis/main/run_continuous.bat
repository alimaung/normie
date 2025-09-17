@echo off
echo Starting Excel Data Updater (Continuous Mode)...
echo This will run every 30 minutes. Press Ctrl+C to stop.
echo.

py run_updater.py --continuous

echo.
echo Continuous updates stopped. Press any key to exit.
pause > nul
