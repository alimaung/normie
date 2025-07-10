# VBA + Python Email Extraction Setup

This system uses VBA to extract email content (bypassing corporate security) and Python to monitor and process the extracted data.

## 🚀 Quick Start

### 1. Setup VBA Macro in Outlook

1. **Open Outlook VBA Editor:**
   - Press `Alt + F11` in Outlook
   - Go to `Insert > Module`

2. **Add the VBA Code:**
   - Copy all content from `OutlookEmailExtractor.vba`
   - Paste into the new module
   - Save (`Ctrl + S`)

3. **Configure Settings (Optional):**
   ```vba
   Private Const POLL_INTERVAL_MINUTES As Integer = 5     ' Change polling frequency
   Private Const OUTPUT_FOLDER As String = "C:\temp\outlook_extract\"  ' Change output location
   Private Const MAX_EMAILS_PER_ACCOUNT As Integer = 50   ' Change email limit
   ```

### 2. Setup Python Monitor

1. **Install Dependencies:**
   ```bash
   pip install -r requirements_monitor.txt
   ```

2. **Create Output Folder:**
   ```bash
   mkdir C:\temp\outlook_extract
   ```

### 3. Start the System

#### Method A: Automatic Polling (Recommended)

1. **Start VBA Polling:**
   - In Outlook VBA, press `F5` or run: `StartEmailPolling`
   - Check output: `View > Immediate Window` in VBA

2. **Start Python Monitor:**
   ```bash
   python email_monitor.py
   ```

#### Method B: Manual Extraction

1. **One-time VBA extraction:**
   - Run: `ExtractEmailsOnce` in VBA

2. **One-time Python processing:**
   ```bash
   python email_monitor.py --once
   ```

## 📁 File Structure

```
C:\temp\outlook_extract\
├── Ali_Maung_Rolls-Royce_com_inbox_2025-07-10_14-30-00.json
├── Ali_Maung_Rolls-Royce_com_sent_2025-07-10_14-30-00.json
├── IRM-Standardisation-Office_inbox_2025-07-10_14-30-00.json
├── IRM-Standardisation-Office_sent_2025-07-10_14-30-00.json
├── last_extraction.txt
└── email_database.json
```

## 🔧 Troubleshooting

### VBA Issues

**Problem:** "Macro disabled" error
**Solution:** 
1. Go to `File > Options > Trust Center > Trust Center Settings`
2. Select `Macro Settings > Enable all macros`
3. Restart Outlook

**Problem:** "Permission denied" error
**Solution:**
1. Make sure `C:\temp\outlook_extract\` exists
2. Check folder permissions
3. Try different output folder

**Problem:** No emails extracted
**Solution:**
1. Check VBA Immediate Window for errors
2. Verify folders exist (Inbox, Sent Items)
3. Check if emails exist in those folders

### Python Issues

**Problem:** `watchdog` import error
**Solution:** `pip install watchdog`

**Problem:** No files found
**Solution:**
1. Check if VBA is running and creating files
2. Verify folder path matches VBA output folder
3. Check file permissions

## 📊 What Gets Extracted

### ✅ Available (VBA bypasses security):
- **Full email content:** Subject, body, HTML body
- **Sender details:** Name, email address
- **Recipient information:** Names, addresses, types
- **Attachments:** Filenames, sizes, types
- **Metadata:** Timestamps, importance, categories
- **Folder information:** Paths, item counts

### 🔒 Previously Blocked (Now Working):
- Email body content ✅
- Sender email addresses ✅
- Recipient details ✅
- HTML formatting ✅

## ⚙️ Configuration Options

### VBA Settings:
```vba
POLL_INTERVAL_MINUTES = 5        ' How often to extract (minutes)
MAX_EMAILS_PER_ACCOUNT = 50      ' Max emails per extraction
OUTPUT_FOLDER = "C:\temp\..."    ' Where to save JSON files
```

### Python Settings:
```bash
python email_monitor.py --folder "D:\custom\path"  # Custom watch folder
python email_monitor.py --once                     # Run once, don't monitor
```

## 📈 Monitoring Output

The Python monitor will show:
```
📧 Processing file: Ali_Maung_Rolls-Royce_com_inbox_2025-07-10_14-30-00.json
  📁 Folder: Inbox
  📊 Total items: 173, Extracted: 50
    📨 Rolls-Royce Daily Digest
      👤 From: RR Communications (communications@rolls-royce.com)
      🕒 Time: 2025-07-10 09:47:18
      📏 Size: 133397 bytes [UNREAD]
      📎 Attachments: newsletter.pdf
      💬 Preview: Welcome to the daily digest...
```

## 🛑 Stopping the System

1. **Stop VBA Polling:**
   - Run: `StopEmailPolling` in VBA

2. **Stop Python Monitor:**
   - Press `Ctrl + C` in terminal

## 💾 Data Export

All processed emails are saved to:
- **Individual files:** `account_folder_timestamp.json`
- **Combined database:** `email_database.json`

## 🎯 Next Steps

Once this is working, you can:
1. **Analyze email patterns** with the JSON data
2. **Build reports** on email activity
3. **Search email content** across accounts
4. **Export to databases** for long-term storage
5. **Create dashboards** for email insights

The VBA approach should successfully bypass the corporate security restrictions! 🚀 