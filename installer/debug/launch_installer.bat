@echo off
setlocal enabledelayedexpansion

:: ESE Pagify Installer Launcher
echo ============================================================
echo                ESE Pagify Installer Launcher
echo ============================================================
echo Starting pagify installation process...
echo.

:: Check if installer.bat exists in same directory
set "INSTALLER_PATH=%~dp0installer.bat"
if not exist "%INSTALLER_PATH%" (
    echo [ERROR] installer.bat not found in the same directory!
    echo Expected location: %INSTALLER_PATH%
    echo.
    echo Please ensure both files are in the same folder:
    echo - launch_installer.bat ^(this file^)
    echo - installer.bat ^(main installer^)
    echo.
    pause
    exit /b 1
)

echo Found installer at: %INSTALLER_PATH%
echo.

:: Run the installer and capture exit code
echo ============================================================
echo RUNNING INSTALLER
echo ============================================================
call "%INSTALLER_PATH%"
set "INSTALL_RESULT=%errorlevel%"

echo.
echo ============================================================
echo INSTALLATION RESULT
echo ============================================================

:: Check result and provide appropriate message
if %INSTALL_RESULT% equ 0 (
    echo [SUCCESS] Installation completed successfully!
    echo.
    echo Next steps:
    echo 1. Install pip and conda dependencies ^(see instructions^)
    echo 2. Use the PowerShell alias script if needed
    echo.
    echo Installation is ready!
) else (
    echo [ERROR] Installation failed with error code: %INSTALL_RESULT%
    echo.
    echo Possible issues:
    echo - Network connection problems
    echo - ESE.bat path not accessible
    echo - Insufficient permissions
    echo - Miniconda installation failed
    echo.
    echo Please check the error messages above and try again.
    echo If the problem persists, run the installation steps manually.
)

echo.
echo Press any key to exit...
pause >nul 