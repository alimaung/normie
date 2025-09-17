# Troubleshooting "Could Not Send Message" Error

## Common Causes & Solutions

### 1. **Outlook Security Settings** (Most Common)
**Problem**: Outlook blocks VBA from sending emails automatically
**Solution**:
1. Go to **File** → **Options** → **Trust Center** → **Trust Center Settings**
2. Click **Macro Settings**
3. Select **"Enable all macros"** or **"Enable all macros with notification"**
4. Click **Programmatic Access** tab
5. Select **"Never warn me about suspicious activity"** or **"Warn me about suspicious activity when my antivirus software is inactive or out of date"**
6. **Restart Outlook**

### 2. **Antivirus Software Blocking**
**Problem**: Antivirus software blocks VBA email sending
**Solution**:
- Add Outlook to antivirus exclusions
- Temporarily disable real-time protection to test
- Check antivirus logs for blocked activities

### 3. **Exchange/Server Permissions**
**Problem**: Server doesn't allow programmatic sending
**Solution**:
- Contact IT administrator
- Check if "Send As" permissions are required
- Verify Exchange security policies

### 4. **Outlook Profile Issues**
**Problem**: Corrupted Outlook profile
**Solution**:
- Create new Outlook profile
- Repair Office installation
- Check if manual sending works

## Testing Steps

### Step 1: Test Basic Email Sending
Run this in VBA editor:
```vba
Public Sub TestEmailSending()
    ' This function is now included in the script
End Sub
```

### Step 2: Check Security Settings
Run this in VBA editor:
```vba
Public Sub CheckOutlookSecurity()
    ' This function is now included in the script
End Sub
```

### Step 3: Test Auto-Reply
Run this in VBA editor:
```vba
Public Sub TestAutoReply()
    ' This function is now included in the script
End Sub
```

## Enhanced Error Handling

The updated script now includes:

### **3-Tier Fallback System**:
1. **Primary**: Standard reply method
2. **Secondary**: Create new email instead of reply
3. **Tertiary**: Save to drafts folder

### **Debug Information**:
- All errors are logged to the Immediate window
- Success messages show recipient email
- Detailed error descriptions with error codes

### **How to View Debug Messages**:
1. In VBA editor, go to **View** → **Immediate Window**
2. Run your test functions
3. Check the window for error messages

## Alternative Solutions

### Option 1: Manual Send from Drafts
If automatic sending fails, the script saves to drafts:
1. Check your **Drafts** folder
2. Find emails with "[DRAFT - Auto-reply failed to send]"
3. Send manually

### Option 2: PowerShell Alternative
If VBA continues to fail, consider a PowerShell script:
```powershell
# PowerShell script that monitors Outlook and sends emails
# This bypasses VBA security restrictions
```

### Option 3: Outlook Rules + Templates
1. Create Outlook rule for emails containing "#IRMNORMIE"
2. Use rule to apply HTML template
3. Still requires manual sending but automates template application

## Quick Fix Checklist

- [ ] Enable all macros in Outlook
- [ ] Check Programmatic Access settings
- [ ] Restart Outlook after changes
- [ ] Run `TestEmailSending()` function
- [ ] Check antivirus exclusions
- [ ] Verify manual email sending works
- [ ] Check Immediate window for error details

## Still Having Issues?

1. **Check the Immediate Window** in VBA editor for specific error messages
2. **Run the test functions** to isolate the problem
3. **Try sending a manual email** to verify Outlook works
4. **Contact IT support** if it's a server/permissions issue

The enhanced script will now provide much better error information to help diagnose the exact cause of the sending failure.
