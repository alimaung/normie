from django.apps import AppConfig
import os
import subprocess
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


class NormieappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'normieapp'

    def ready(self):
        import normieapp.signals
        
        # Start background directory updater only in main process
        # (not in management commands or during migrations)
        if os.environ.get('RUN_MAIN', None) != 'true':
            return  # Skip in autoreloader child process
            
        # Check if we're running the main server (not migrations, etc.)
        import sys
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv[0]:
            self.start_external_updater()

    def start_external_updater(self):
        """Start the directory updater in a separate PowerShell window."""
        try:
            # Path to the PowerShell script
            script_path = Path(settings.BASE_DIR) / "start_directory_updater.ps1"
            
            if not script_path.exists():
                logger.warning(f"Directory updater script not found: {script_path}")
                return
            
            # PowerShell command to run in new window
            ps_command = [
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-WindowStyle", "Normal",
                "-File", str(script_path),
                "-IntervalMinutes", "5"
            ]
            
            # Start PowerShell in new window (non-blocking)
            subprocess.Popen(
                ps_command,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=str(settings.BASE_DIR)
            )
            
            logger.info("Started directory updater in external PowerShell window")
            
        except Exception as e:
            logger.error(f"Failed to start external directory updater: {e}")
            # Fallback to internal service if external fails
            try:
                from .services.directory_service import directory_service
                directory_service.start()
                logger.info("Fallback: Started internal directory service")
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")