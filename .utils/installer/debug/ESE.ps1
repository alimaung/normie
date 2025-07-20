# Mock ESE (Engineering Software Environment) Simulator
# Simulates ESE.bat behavior for testing purposes

param(
    [string]$Command = ""
)

# Set console title
$Host.UI.RawUI.WindowTitle = "ESE prompt obl (version 0.0.10)"

# Initial ESE startup message
Write-Host "Starting Engineering Software Environment (ESE) version 0.0.10"
Write-Host "located at \\DEBERDNA-C011A\Projekte\a-j\ESE"
Write-Host "######## Site specific environment configuration available"
Write-Host "         for RRCONFIG_SITE=obl in ESE."
Write-Host "Use command setA1156 to change A1156 server."
Write-Host "################################################################################"
Write-Host "# ESE commands to get started:                                                 #"
Write-Host "#  helpese    - Display help for ESE commands or the given arguments           #"
Write-Host "#  index   - Display list of available commands in ESE prompt                  #"
Write-Host "#  version - Display versions of software in ESE or the given arguments        #"
Write-Host "################################################################################"
Write-Host ""

# Main command loop
while ($true) {
    # Show prompt
    Write-Host "C:\Users\u8064927\Desktop\normie\installer ESE>" -NoNewline
    
    # Read command from user
    $input = Read-Host
    
    switch ($input.Trim()) {
        "integ miniconda3" {
            # Update window title to show command is running
            $Host.UI.RawUI.WindowTitle = "ESE prompt obl (version 0.0.10) - integ miniconda3"
            
            # Simulate miniconda installation output
            Write-Host "Init cots\Miniconda3 version py312_24.3.0-0-Windows-x86_64 in integration"
            Write-Host ""
            Write-Host "For help:              Miniconda3 -h"
            Write-Host "To force installation: Miniconda3 -i"
            Write-Host "To uninstall:          Miniconda3 -u"
            Write-Host ""
            Write-Host "Operating System is 64 bit and current process is 64 bit"
            Write-Host "Operating System is 64 bit and current process is 64 bit"
            Write-Host "#### Copying Miniconda3 installer and config files..."
            Write-Host "     Note: in case of network error, simply run this command again to resume the transfer."
            Write-Host ""
            
            # Simulate robocopy operations
            Start-Sleep 1
            Write-Host "-------------------------------------------------------------------------------"
            Write-Host "   ROBOCOPY     ::     Robust File Copy for Windows"
            Write-Host "-------------------------------------------------------------------------------"
            Write-Host ""
            Write-Host "  Started : $(Get-Date -Format 'dddd, d. MMMM yyyy HH:mm:ss')"
            Write-Host "   Source : \\DEBERDNA-C011A\Projekte\a-j\ESE\cots\Miniconda3\py312_24.3.0-0-Windows-x86_64\"
            Write-Host "     Dest : C:\Users\u8064927\AppData\Local\Temp\"
            Write-Host ""
            Write-Host "    Files : Miniconda3-py312_24.3.0-0-Windows-x86_64.exe"
            Write-Host ""
            Write-Host "  Options : /FFT /DST /DCOPY:DA /COPY:DAT /Z /R:0 /W:30"
            Write-Host ""
            Write-Host "------------------------------------------------------------------------------"
            Write-Host "                           1    \\DEBERDNA-C011A\Projekte\a-j\ESE\cots\Miniconda3\py312_24.3.0-0-Windows-x86_64\"
            Write-Host "------------------------------------------------------------------------------"
            Write-Host ""
            Write-Host "               Total    Copied   Skipped  Mismatch    FAILED    Extras"
            Write-Host "    Dirs :         1         0         1         0         0         0"
            Write-Host "   Files :         1         0         1         0         0         0"
            Write-Host "   Bytes :   77.50 m         0   77.50 m         0         0         0"
            Write-Host "   Times :   0:00:00   0:00:00                       0:00:00   0:00:00"
            Write-Host "   Ended : $(Get-Date -Format 'dddd, d. MMMM yyyy HH:mm:ss')"
            Write-Host ""
            
            Start-Sleep 1
            Write-Host "######## Verifying checksum for Miniconda3 installer... OK"
            Write-Host "######## Installing Miniconda3 version py312_24.3.0-0-Windows-x86_64..."
            Write-Host "OK"
            Write-Host ""
            
            Start-Sleep 1
            Write-Host "no change     D:\ESEapps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Scripts\conda.exe"
            Write-Host "no change     D:\ESEapps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Scripts\conda-env.exe"
            Write-Host "no change     D:\ESEapps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Scripts\conda-script.py"
            Write-Host "modified      D:\ESEapps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Scripts\activate"
            Write-Host "modified      D:\ESEapps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Scripts\deactivate"
            Write-Host "modified      C:\Users\u8064927\Documents\WindowsPowerShell\profile.ps1"
            Write-Host "modified      HKEY_CURRENT_USER\Software\Microsoft\Command Processor\AutoRun"
            Write-Host ""
            Write-Host "==> For changes to take effect, close and re-open your current shell. <=="
            Write-Host ""
            Write-Host "#### Adding Miniconda3 py312_24.3.0-0-Windows-x86_64 shortcut to your Programs... OK"
            
            # Create mock conda.bat directory structure
            $condaDir = Join-Path $PSScriptRoot "Miniconda3\py312_24.3.0-0-Windows-x86_64\condabin"
            New-Item -Path $condaDir -ItemType Directory -Force | Out-Null
            
            # Create mock conda.bat file
            $condaBat = Join-Path $condaDir "conda.bat"
            @"
@echo off
title $condaDir
echo Mock conda environment activated
python
"@ | Out-File -FilePath $condaBat -Encoding ASCII
            
            Write-Host "######## Starting Miniconda3 py312_24.3.0-0-Windows-x86_64 from D:\ESEapps\Miniconda3\py312_24.3.0-0-Windows-x86_64\condabin\conda.bat"
            Write-Host ""
            
            # Start conda.bat in a new process
            Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$condaBat`""
            
            # Reset window title
            $Host.UI.RawUI.WindowTitle = "ESE prompt obl (version 0.0.10)"
        }
        
        "rrpytools fix" {
            # Update window title
            $Host.UI.RawUI.WindowTitle = "ESE prompt obl (version 0.0.10) - rrpytools fix"
            
            # Simulate rrpytools fix output
            Write-Host "Found conda on system PATH"
            Write-Host ""
            Write-Host "-------------------------------------------------------------------------------"
            Write-Host "   ROBOCOPY     ::     Robust File Copy for Windows"
            Write-Host "-------------------------------------------------------------------------------"
            Write-Host ""
            Write-Host "  Started : $(Get-Date -Format 'dddd, d. MMMM yyyy HH:mm:ss')"
            Write-Host "   Source : \\DEBERDNA-C011A\Projekte\a-j\ESE\davinci\rrpytools\0.10.1\"
            Write-Host "     Dest : C:\Users\u8064927\AppData\Local\EseCache\davinci\rrpytools\0.10.1\"
            Write-Host ""
            Write-Host "    Files : *.*"
            Write-Host ""
            Write-Host "  Options : *.* /S /E /DCOPY:DA /COPY:DAT /R:1000000 /W:30"
            Write-Host ""
            Write-Host "------------------------------------------------------------------------------"
            Write-Host ""
            Start-Sleep 1
            Write-Host "          New Dir          6    \\DEBERDNA-C011A\Projekte\a-j\ESE\davinci\rrpytools\0.10.1\"
            Write-Host "100%        New File                5018        call-rrpytools-activate.bat"
            Write-Host "100%        New File                4451        call-rrpytools.bat"
            Write-Host "100%        New File                8622        CHANGELOG.md"
            Write-Host "100%        New File                5910        COMMON_README.md"
            Write-Host "100%        New File               10781        README.md"
            Write-Host "100%        New File                4070        REQUIREMENTS.md"
            Start-Sleep 1
            Write-Host "          New Dir          2    \\DEBERDNA-C011A\Projekte\a-j\ESE\davinci\rrpytools\0.10.1\environments\"
            Write-Host "100%        New File                1364        SE_win64_py35.yml"
            Write-Host "100%        New File                 164        test_py35_clean.yml"
            Write-Host "          New Dir          7    \\DEBERDNA-C011A\Projekte\a-j\ESE\davinci\rrpytools\0.10.1\rrpytools\"
            Write-Host "100%        New File               12325        cli.py"
            Write-Host "100%        New File                4749        create_env.py"
            Write-Host "100%        New File               23444        ese_env.py"
            Write-Host "100%        New File               10826        fixconfig.py"
            Write-Host "100%        New File                7032        fixenv.py"
            Write-Host "100%        New File                 259        _compat.py"
            Write-Host "100%        New File                 164        __init__.py"
            Start-Sleep 1
            Write-Host ""
            Write-Host "------------------------------------------------------------------------------"
            Write-Host ""
            Write-Host "               Total    Copied   Skipped  Mismatch    FAILED    Extras"
            Write-Host "    Dirs :         5         5         0         0         0         0"
            Write-Host "   Files :        18        18         0         0         0         0"
            Write-Host "   Bytes :   104.0 k   104.0 k         0         0         0         0"
            Write-Host "   Times :   0:00:03   0:00:02                       0:00:00   0:00:01"
            Write-Host ""
            Write-Host ""
            Write-Host "   Speed :               41686 Bytes/sec."
            Write-Host "   Speed :               2.385 MegaBytes/min."
            Write-Host "   Ended : $(Get-Date -Format 'dddd, d. MMMM yyyy HH:mm:ss')"
            Write-Host ""
            Start-Sleep 1
            Write-Host "Applying fix: condarc"
            Write-Host "Backing up existing config: C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\.condarc -> .condarc.2.bat"
            Write-Host "Writing default config to file: C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\.condarc"
            Write-Host "Applying fix: noproxy"
            Write-Host ""
            Write-Host "SUCCESS: Specified value was saved."
            Write-Host "Skipping fix: update-conda"
            Write-Host "Applying fix: conda-init"
            Start-Sleep 1
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Scripts\conda.exe"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Scripts\conda-env.exe"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Scripts\conda-script.py"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Scripts\conda-env-script.py"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\condabin\conda.bat"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Library\bin\conda.bat"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\condabin\_conda_activate.bat"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\condabin\rename_tmp.bat"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\condabin\conda_auto_activate.bat"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\condabin\conda_hook.bat"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Scripts\activate.bat"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\condabin\activate.bat"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\condabin\deactivate.bat"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Scripts\activate"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Scripts\deactivate"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\etc\profile.d\conda.sh"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\etc\fish\conf.d\conda.fish"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\shell\condabin\Conda.psm1"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\shell\condabin\conda-hook.ps1"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\Lib\site-packages\xontrib\conda.xsh"
            Write-Host "no change     C:\ESEApps\Miniconda3\py312_24.3.0-0-Windows-x86_64\etc\profile.d\conda.csh"
            Write-Host "no change     C:\Users\u8064927\Documents\WindowsPowerShell\profile.ps1"
            Write-Host "no change     HKEY_CURRENT_USER\Software\Microsoft\Command Processor\AutoRun"
            Write-Host "No action taken."
            Write-Host "Applying fix: pip-config"
            Write-Host "processed file: C:\ProgramData\pip\pip.ini"
            Write-Host "Successfully processed 1 files; Failed processing 0 files"
            Write-Host ""
            
            # Reset window title
            $Host.UI.RawUI.WindowTitle = "ESE prompt obl (version 0.0.10)"
        }
        
        "exit" {
            Write-Host "Exiting ESE..."
            break
        }
        
        "helpese" {
            Write-Host "Available ESE commands:"
            Write-Host "  integ miniconda3 - Install Miniconda3"
            Write-Host "  rrpytools fix    - Fix rrpytools configuration"
            Write-Host "  exit             - Exit ESE"
            Write-Host "  helpese          - Show this help"
            Write-Host "  index            - Show command index"
            Write-Host "  version          - Show version information"
        }
        
        "index" {
            Write-Host "ESE Command Index:"
            Write-Host "  integ miniconda3"
            Write-Host "  rrpytools fix"
            Write-Host "  helpese"
            Write-Host "  version"
            Write-Host "  exit"
        }
        
        "version" {
            Write-Host "ESE version 0.0.10"
            Write-Host "Mock implementation for testing"
        }
        
        "" {
            # Empty input, just continue
        }
        
        default {
            Write-Host "Unknown command: $input"
            Write-Host "Type 'helpese' for available commands"
        }
    }
}
