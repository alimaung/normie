@echo off
echo Switching to online mode...

REM Check if base_online.html exists
if not exist "normieapp\templates\normieapp\base_online.html" (
    echo Error: base_online.html not found!
    echo Cannot switch to online mode without backup.
    pause
    exit /b 1
)

REM Backup current base.html to base_offline.html
if exist "normieapp\templates\normieapp\base.html" (
    move "normieapp\templates\normieapp\base.html" "normieapp\templates\normieapp\base_offline.html"
    echo ✓ Backed up current base.html to base_offline.html
)

REM Switch to online template
move "normieapp\templates\normieapp\base_online.html" "normieapp\templates\normieapp\base.html"
echo ✓ Switched to online mode

echo.
echo Your application is now in online mode!
echo To switch back to offline mode, run switch_to_offline.bat
pause 