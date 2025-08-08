# Outlook Email Extractor - Refactored Version

This is a streamlined version of the Outlook Email Extractor that focuses specifically on two core functions for the **production IRM account only**.

## Key Features

### 🎯 **Focused Functionality**
- **Function 1**: Download all emails & attachments from all available IRM folders
- **Function 2**: Event monitoring to detect and process new emails in real-time

### 🏢 **IRM Account Only**
- Designed specifically for the `IRM-Standardisation-Office` account
- No fallback accounts - simplified and focused
- Automatic discovery of all available IRM folders

### 📁 **Multi-Folder Support**
- Automatically finds and processes all available folders:
  - Inbox
  - Sent Items / Sent Mail (Gmail)
  - Deleted Items / Trash (Gmail)
  - Drafts
  - Outbox
  - Gmail special folders (Important, Starred)

### 🔄 **Real-Time Event Monitoring**
- Monitors all IRM folders for new emails
- Automatic processing when emails arrive
- Duplicate detection to avoid reprocessing

## Files

### `OutlookEmailExtractor-refactored.vba`
Main module containing:
- **DownloadAllIRMEmails()** - Downloads all emails from all IRM folders
- **StartEventMonitoring()** - Starts real-time email monitoring
- **StopEventMonitoring()** - Stops event monitoring
- **TestMacro()** - Tests functionality and IRM connection
- **GetStatus()** - Shows current status

### `EmailEventHandler.cls`
Event handler class for real-time monitoring:
- Monitors multiple folders simultaneously
- Handles new email events across all IRM folders
- Automatic email processing and JSON generation

## Usage

### 1. Setup
1. Open Outlook VBA Editor (Alt+F11)
2. Import both files:
   - Add `OutlookEmailExtractor-refactored.vba` as a Module
   - Add `EmailEventHandler.cls` as a Class Module

### 2. Test Connection
```vba
' Test if everything is working
Call TestMacro
```

### 3. Download All Emails (One-time)
```vba
' Download all emails and attachments from all IRM folders
Call DownloadAllIRMEmails
```

### 4. Start Real-time Monitoring
```vba
' Start monitoring for new emails
Call StartEventMonitoring

' Check status
Call GetStatus

' Stop monitoring when needed
Call StopEventMonitoring
```

## Output Structure

### JSON Files
- `emails_inbox.json` - Inbox emails
- `emails_sent_items.json` - Sent emails
- `emails_deleted_items.json` - Deleted emails
- `emails_drafts.json` - Draft emails
- `emails_outbox.json` - Outbox emails

### Attachments
- `data/{hash}/` - Folder for each email (named by hash)
- `data/{hash}/{hash}.msg` - Original .msg file
- `data/{hash}/attachment.pdf` - Email attachments

### Logs
- `extractor_log.txt` - Detailed operation logs

## Key Improvements

### ✅ **Simplified**
- Removed fallback account logic
- Focused on IRM account only
- Cleaner, more maintainable code

### ✅ **Reliable**
- Robust error handling
- Duplicate detection
- Safe file operations

### ✅ **Comprehensive**
- Processes all available IRM folders
- Full email content extraction
- Complete attachment handling

### ✅ **Real-time**
- Event-driven monitoring
- Automatic processing
- Multi-folder event handling

## Configuration

The script is pre-configured for the IRM account:
```vba
Public Const TARGET_ACCOUNT As String = "IRM-Standardisation-Office"
```

Output paths are automatically determined:
- Output: `C:\Users\{username}\Desktop\normie\outlook\analyze\mail\`
- Data: `C:\Users\{username}\Desktop\normie\outlook\analyze\mail\data\`

## Error Handling

- Comprehensive error logging
- Graceful failure handling
- Continues processing even if individual emails fail
- Detailed debug information in logs

## Performance

- Processes up to 100 emails per folder (configurable)
- Efficient duplicate detection
- Minimal memory usage
- Safe string handling to avoid VBA limitations

## Compatibility

- Works with both Outlook and Gmail accounts
- Handles Gmail's nested folder structure
- Compatible with standard Outlook folder names
- Automatic folder discovery and adaptation

---

**Note**: This refactored version maintains all the core functionality of the original while being significantly cleaner, more focused, and easier to maintain.