"""
Directory service status API endpoints.
"""

import time
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from django.conf import settings
import os

from ..services.directory_service import get_directory_service


@require_http_methods(["GET"])
def directory_status(request):
    """
    Return current status of the directory update service.
    Now works with external PowerShell process.
    """
    import psutil
    
    # Get file timestamps
    data_dir = Path(settings.BASE_DIR) / "normieapp" / "static" / "normieapp" / "data"
    verzeichnis_file = data_dir / "Verzeichnis.json"
    compressed_file = data_dir / "Verzeichnis_compressed.json"
    
    last_update = None
    has_compressed = compressed_file.exists()
    
    if verzeichnis_file.exists():
        last_update = verzeichnis_file.stat().st_mtime
    
    # Calculate time since last update
    time_since_update = None
    if last_update:
        time_since_update = int(time.time() - last_update)
    
    # Check if external updater process is running
    is_running = False
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info.get('cmdline', [])
            if (cmdline and 
                'python' in cmdline[0].lower() and 
                'continuous_updater.py' in ' '.join(cmdline)):
                is_running = True
                break
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
    
    # Determine status
    if not is_running:
        status = "offline"
        status_text = "Offline"
        status_class = "offline"
    elif time_since_update is None:
        status = "starting"
        status_text = "Starting"
        status_class = "starting"
    elif time_since_update <= 60:  # Updated within last minute
        status = "updating"
        status_text = "Updating"
        status_class = "updating"
    elif time_since_update <= 300:  # Updated within last 5 minutes
        status = "live"
        status_text = "Live"
        status_class = "live"
    else:  # Haven't updated in a while
        status = "stale"
        status_text = "Stale"
        status_class = "warning"
    
    update_interval = 5 * 60  # 5 minutes in seconds
    
    return JsonResponse({
        "status": status,
        "status_text": status_text,
        "status_class": status_class,
        "is_running": is_running,
        "last_update": last_update,
        "time_since_update": time_since_update,
        "has_compressed": has_compressed,
        "update_interval": update_interval,
        "next_update_in": update_interval - (time_since_update or 0) if time_since_update else None
    })


@require_http_methods(["POST"])
@csrf_exempt
def trigger_update(request):
    """
    Manually trigger a directory update.
    """
    service = get_directory_service()
    
    if service.updater is None:
        return JsonResponse({
            "success": False,
            "error": "Directory updater service not available"
        }, status=503)
    
    try:
        # Run update in background (don't block the request)
        import threading
        def run_update():
            service.run_single_update()
        
        thread = threading.Thread(target=run_update, daemon=True)
        thread.start()
        
        return JsonResponse({
            "success": True,
            "message": "Update triggered successfully"
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

