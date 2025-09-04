# Outlook VBA Auto-Reply Setup Guide

## Overview
This VBA script automatically monitors incoming emails for the trigger text "#IRMNORMIE" and sends an HTML-formatted reply with a dynamic link to your directory using the current IPv4 address.

## Files Included
- `riply.vba` - Main VBA script
- `cerberus-fluid.html` - HTML email template
- `SETUP_GUIDE.md` - This setup guide

## Setup Instructions

### 1. Enable VBA in Outlook
1. Open Outlook
2. Go to **File** → **Options** → **Trust Center** → **Trust Center Settings**
3. Click **Macro Settings**
4. Select **Enable all macros** (or **Enable all macros with notification** for security)
5. Click **OK** and restart Outlook

### 2. Access VBA Editor
1. In Outlook, press **Alt + F11** to open the VBA editor
2. In the Project Explorer (left panel), expand **VbaProject.OTM**
3. Right-click on **ThisOutlookSession** and select **View Code**

### 3. Import the VBA Code
1. Copy the entire contents of `riply.vba`
2. Paste it into the VBA editor window
3. Save the project (**Ctrl + S**)

### 4. Set Up HTML Template
1. Ensure `cerberus-fluid.html` is in the same directory as your VBA project
2. The script will automatically look for the template in:
   - Same directory as the VBA project
   - `C:\Users\[USERNAME]\Desktop\normie\outlook\riply\cerberus-fluid.html`

### 5. Test the Script
1. In the VBA editor, press **F5** or go to **Run** → **Run Sub/UserForm**
2. Select `TestAutoReply` from the list
3. This will create a test email and process it

## How It Works

### Email Monitoring
- The script uses Outlook's `ItemAdd` event to monitor the inbox
- When a new email arrives, it checks both the subject and body for "#IRMNORMIE"
- The check is case-insensitive

### IP Address Detection
- Runs `ipconfig` command via Windows shell
- Parses output to find IPv4 address for "Wireless LAN adapter WiFi"
- Falls back to "IP_NOT_FOUND" if WiFi adapter not found

### HTML Template Processing
- Loads the HTML template from file
- Replaces placeholder link with actual IP address
- Updates button text and content to be relevant

### Auto-Reply Generation
- Creates a reply to the original email
- Sets HTML body with processed template
- Automatically sends the reply

## Customization Options

### Change Trigger Text
Modify this line in the `ProcessIncomingEmail` function:
```vba
containsTrigger = (InStr(subject, "#irmnormie") > 0) Or (InStr(body, "#irmnormie") > 0)
```

### Change Directory Path
Modify this line in the `ReplaceHtmlTemplate` function:
```vba
buttonLink = "http://" & ipAddress & "/directory"
```

### Modify Email Content
Edit the `ReplaceHtmlTemplate` function to change:
- Button text
- Email headings
- Description text
- Footer content

## Troubleshooting

### Script Not Running
1. Check that macros are enabled in Outlook
2. Verify the VBA code is saved in `ThisOutlookSession`
3. Restart Outlook after making changes

### IP Address Not Found
1. Check that you're connected to WiFi
2. Verify the adapter name matches "Wireless LAN adapter WiFi"
3. Run `ipconfig` manually to see your adapter names

### HTML Template Not Loading
1. Check file path in `LoadHtmlTemplate` function
2. Ensure `cerberus-fluid.html` exists in the expected location
3. The script includes a fallback template if file not found

### Email Not Sending
1. Check Outlook's security settings
2. Verify you have permission to send emails
3. Check if antivirus is blocking the script

## Security Considerations
- The script runs with full Outlook permissions
- It can send emails automatically
- Consider using "Enable all macros with notification" for better security
- The script accesses system commands (ipconfig)

## Testing
Use the `TestAutoReply` function to test without waiting for real emails:
1. Open VBA editor
2. Run `TestAutoReply` sub
3. Check if a test email is created and processed

## Support
If you encounter issues:
1. Check the VBA editor's Immediate window for error messages
2. Verify all file paths are correct
3. Test with the built-in test function first
