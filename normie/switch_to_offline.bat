@echo off
echo Switching to offline mode...

REM Check if base_offline.html exists
if not exist "normieapp\templates\normieapp\base_offline.html" (
    echo Error: base_offline.html not found!
    echo Please run download_external_assets.py first.
    pause
    exit /b 1
)

REM Backup current base.html to base_online.html
if exist "normieapp\templates\normieapp\base.html" (
    move "normieapp\templates\normieapp\base.html" "normieapp\templates\normieapp\base_online.html"
    echo ✓ Backed up current base.html to base_online.html
)

REM Switch to offline template
move "normieapp\templates\normieapp\base_offline.html" "normieapp\templates\normieapp\base.html"
echo ✓ Switched to offline mode

echo.
echo Your application is now in offline mode!
echo To switch back to online mode, run switch_to_online.bat
pause 