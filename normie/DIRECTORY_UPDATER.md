# Django Directory Service

The directory updater runs automatically with the Django server and optimizes JSON file size.

## Service Location

**`normie/normieapp/services/directory_service.py`**

Contains:
- `DirectoryUpdaterService` - Background updater
- `JSONOptimizer` - File compression
- Global service instance

## How It Works

1. **Background Service**: Starts automatically when Django starts (`python manage.py runserver`)
2. **JSON Optimization**: Creates compressed version (~70% smaller) for faster loading
3. **Atomic Updates**: No interference with web access during updates
4. **Smart Loading**: Frontend tries compressed version first, falls back to full version

## Setup

Everything is already configured! Just start Django normally:

```bash
python manage.py runserver
```

The background service will:
- Start automatically with the server **in a separate PowerShell window**
- Run every 5 minutes (checks for Excel changes)
- Create both `Verzeichnis.json` (full) and `Verzeichnis_compressed.json` (optimized)
- Only update if source Excel file has actually changed
- Use unique temporary filenames to avoid COM conflicts
- **Non-blocking**: Django server stays responsive during Excel processing
- Log updates in the PowerShell window

## External PowerShell Window

When you start Django, it automatically opens a **separate PowerShell window** titled "Directory Updater Service" that:

- ✅ **Runs independently** from Django server
- ✅ **Never blocks** web requests during Excel processing
- ✅ **Shows real-time logs** of update progress
- ✅ **Handles COM operations** safely in isolated process
- ✅ **Auto-restarts** if it crashes
- ✅ **Closes automatically** when Django server stops

You can **close this window** if you don't want background updates, and the web interface will still work with existing data.

## Manual Operations

Management commands available:

```bash
# Single update with optimization
python manage.py update_directory --once

# Continuous mode (for testing)
python manage.py update_directory --continuous --interval 15

# Just optimize existing JSON
python manage.py optimize_json
python manage.py optimize_json --input custom.json --output compressed.json

# Start external updater manually
powershell -ExecutionPolicy Bypass -File start_directory_updater.ps1 -IntervalMinutes 5
```

## Service Integration

The service integrates cleanly with Django:

- **Apps**: Auto-starts in `normieapp/apps.py`
- **Services**: Located in `normieapp/services/directory_service.py`
- **Commands**: Available via `python manage.py update_directory`
- **Logging**: Uses Django's logging system

## File Sizes

- **Original**: ~10MB (full JSON with all data)
- **Compressed**: ~2-3MB (shortened keys, compressed URLs, no null values)
- **Network Transfer**: Compressed version loads 70% faster

## No Changes Needed

- Web interface works exactly the same
- All data remains accessible 
- Document previews work normally
- Background updates don't interfere with users

The system automatically handles everything - just run `python manage.py runserver` and you're done!
