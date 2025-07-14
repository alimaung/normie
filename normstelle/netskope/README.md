# Netskope Popup Capture Tool

This tool captures the contents of Netskope popup windows that appear when links are blocked.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Monitor for popups (recommended)
```bash
python detect.py
```

This will:
- Start monitoring for Netskope popup windows
- Automatically capture popup content when detected
- Save captured data to JSON files with timestamps
- Continue monitoring until you press Ctrl+C

### Test mode (scan current windows)
```bash
python detect.py --test
```

This will scan for existing popup windows once and exit.

## How it works

The script:
1. Monitors for windows from the Netskope process (`stAgentUI.exe`)
2. Detects popup/dialog windows based on:
   - Process ownership (Netskope process)
   - Window titles/classes containing keywords like 'block', 'security', 'policy'
   - Window styles indicating dialogs/popups
3. Captures all text content from the popup window and its child controls
4. Saves the data to timestamped JSON files in the `netskope/` directory

## Output

Captured popup data includes:
- Window title
- Window class name
- Window position and size
- All text content from child controls
- Timestamp of capture

Files are saved as: `netskope_popup_YYYYMMDD_HHMMSS.json`

## Tips

- Run the script before trying to access blocked links
- The script runs continuously, so you can capture multiple popups
- Each popup is only captured once to avoid duplicates
- Press Ctrl+C to stop monitoring and see a summary 