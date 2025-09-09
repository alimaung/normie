@echo off
echo Starting Excel Data Updater (Single Run)...
echo.

py run_updater.py --once

echo.
echo Update completed. Press any key to exit.
pause > nul
