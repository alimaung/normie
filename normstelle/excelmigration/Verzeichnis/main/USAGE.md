# Data Updater Usage Guide

## Overview

The `data_updater.py` script consolidates the functionality of all three original scripts into a single continuous data pipeline for your Django app.

## Features

✅ **Fetches latest Excel** from network paths (live/test fallback)  
✅ **Converts xlsb → xlsx** in temp directory  
✅ **Extracts structured data** with hyperlinks and approval statuses  
✅ **Applies URL cleanup** rules from replace file  
✅ **Saves to Django data directory** as JSON  
✅ **Continuous updates** with configurable intervals  
✅ **Comprehensive logging** and error handling  

## Quick Start

### 1. Single Update (Test Run)
```bash
cd normstelle/excelmigration/Verzeichnis/main/
python data_updater.py --once
```

### 2. Continuous Updates (Production)
```bash
# Update every 30 minutes (default)
python data_updater.py

# Custom interval (e.g., every 15 minutes)
python data_updater.py --interval 15
```

### 3. Background Service (Windows)
```bash
# Run in background and log to file
python data_updater.py > data_updater_output.log 2>&1 &
```

## Configuration

### Default Paths
- **Temp Directory**: `C:\Users\RAVEN\Desktop\normie\normie\normieapp\static\normieapp\temp`
- **Data File**: `C:\Users\RAVEN\Desktop\normie\normie\normieapp\static\normieapp\data\Verzeichnis.json`
- **Log File**: `data_updater.log` (in script directory)

### Custom Paths
```bash
python data_updater.py --temp-dir "C:\custom\temp" --data-file "C:\custom\data.json"
```

### URL Cleanup Rules

Edit the `replace` file to configure URL transformations:

```
replace:
../docs
..\docs

with:
\\NetworkServer\path\to\documents

ignore:
http://
https://
#N/A
```

## Django Integration

The script automatically saves data to your Django static directory:
```
normie/
├── normieapp/
│   ├── static/
│   │   ├── normieapp/
│   │   │   ├── temp/           # Temporary Excel files
│   │   │   └── data/
│   │   │       └── Verzeichnis.json  # Final JSON data
```

In your Django views, load the data:
```python
import json
from django.conf import settings
from pathlib import Path

def load_verzeichnis_data():
    data_file = Path(settings.STATIC_ROOT) / 'normieapp' / 'data' / 'Verzeichnis.json'
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)
```

## Monitoring

### Check Logs
```bash
tail -f data_updater.log
```

### Statistics
The script tracks:
- Total updates completed
- Last update timestamp
- Total errors
- URL changes applied

### Health Check
Create a simple health check endpoint in Django:
```python
def data_health_check(request):
    data_file = Path(settings.STATIC_ROOT) / 'normieapp' / 'data' / 'Verzeichnis.json'
    if data_file.exists():
        stat = data_file.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        return JsonResponse({
            'status': 'ok',
            'last_update': last_modified.isoformat(),
            'file_size': stat.st_size
        })
    return JsonResponse({'status': 'error', 'message': 'Data file not found'})
```

## Troubleshooting

### Common Issues

1. **COM Error**: Install pywin32
   ```bash
   pip install pywin32
   ```

2. **Permission Error**: Run as administrator or check file permissions

3. **Network Path Access**: Ensure network drives are accessible

4. **Missing Replace File**: Create `replace` file with URL rules

### Debug Mode
Add more verbose logging:
```python
logging.getLogger().setLevel(logging.DEBUG)
```

## Production Deployment

### Windows Service
Use `nssm` or Task Scheduler to run as a Windows service:

```bash
# Install NSSM
nssm install DataUpdater "C:\path\to\python.exe" "C:\path\to\data_updater.py"
nssm set DataUpdater AppDirectory "C:\path\to\script\directory"
nssm start DataUpdater
```

### Task Scheduler
Create a scheduled task that runs the script continuously with restart on failure.

## Security Notes

- Script runs with read-only access to source Excel files
- Temporary files are automatically cleaned up
- Network paths should use service accounts with minimal required permissions
- Consider running the update service with a dedicated service account
