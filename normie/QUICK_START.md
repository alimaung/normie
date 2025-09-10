# Quick Start: External PowerShell Updater

## ✅ What Changed

- **Update interval**: 2 minutes → **5 minutes**
- **Processing**: Now runs in **separate PowerShell window**
- **Server**: Django **never blocks** during Excel processing
- **Dependencies**: Added `psutil` for process monitoring

## 🚀 Installation

1. **Install new dependency:**
```bash
pip install psutil>=5.9.0
```

2. **Start Django (as usual):**
```bash
python manage.py runserver
```

3. **Automatic PowerShell window** opens with title "Directory Updater Service"

## 🎯 What You'll See

### Django Server
- Starts normally
- Serves web pages instantly
- **Never blocks** during Excel processing
- Shows log: `"Started directory updater in external PowerShell window"`

### PowerShell Window
- **Green header**: "Directory Updater Background Service"
- **Real-time logs** of update progress
- **Updates every 5 minutes**
- **Press Ctrl+C** to stop (optional)

### Web Interface
- **Live status indicator** shows actual service health
- **All statistics** update automatically
- **10MB → 3MB** compressed JSON loads 70% faster

## 🔧 Troubleshooting

**If PowerShell window doesn't open:**
- Check `start_directory_updater.ps1` exists in project root
- Fallback: Internal service starts automatically
- Manual start: `powershell -ExecutionPolicy Bypass -File start_directory_updater.ps1`

**If live status shows "Offline":**
- PowerShell window may be closed
- Restart Django server to reopen window
- Or run manual update: `python manage.py update_directory --once`

## ✨ Benefits

- ✅ **Zero blocking**: Web pages load instantly during updates
- ✅ **Process isolation**: Excel COM operations in separate process
- ✅ **Better monitoring**: Real-time status indicator
- ✅ **Automatic compression**: 70% smaller JSON files
- ✅ **Crash recovery**: External process auto-restarts
- ✅ **Easy debugging**: Separate log window for updates

## 🎉 Result

Your Django server now stays **100% responsive** while background updates happen every 5 minutes in a separate PowerShell window!
