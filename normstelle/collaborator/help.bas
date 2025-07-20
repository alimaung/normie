Sub ShowHelp()
    ' Determine which sheet the user is currently on
    Dim currentSheet As String
    Dim helpContent As String
    
    currentSheet = ActiveSheet.Name
    
    ' Show appropriate help based on current sheet
    Select Case LCase(currentSheet)
        Case "conflicts"
            Call ShowConflictsHelp
        Case "staging"
            Call ShowStagingHelp
        Case "control"
            Call ShowControlHelp
        Case Else
            Call ShowGeneralHelp
    End Select
End Sub

Sub ShowConflictsHelp()
    ' Load the help form with conflicts-specific content
    Load HelpForm
    With HelpForm
        .Caption = "Conflicts Resolution Help"
        .lblTitle.Caption = "How to Resolve Conflicts"
        .txtContent.Text = GetConflictsHelpText()
        .Tag = "conflicts" ' Store context for More Help button
        .Show vbModal
    End With
    Unload HelpForm
End Sub

Sub ShowStagingHelp()
    ' Load the help form with staging-specific content
    Load HelpForm
    With HelpForm
        .Caption = "Staging Area Help"
        .lblTitle.Caption = "Understanding the Staging Area"
        .txtContent.Text = GetStagingHelpText()
        .Tag = "staging" ' Store context for More Help button
        .Show vbModal
    End With
    Unload HelpForm
End Sub

Sub ShowControlHelp()
    ' Load the help form with control-specific content
    Load HelpForm
    With HelpForm
        .Caption = "Control Panel Help"
        .lblTitle.Caption = "Using the Control Panel"
        .txtContent.Text = GetControlHelpText()
        .Tag = "control" ' Store context for More Help button
        .Show vbModal
    End With
    Unload HelpForm
End Sub

Sub ShowGeneralHelp()
    ' Load the help form with general content
    Load HelpForm
    With HelpForm
        .Caption = "Collaborative Editing Help"
        .lblTitle.Caption = "Collaborative Workbook System"
        .txtContent.Text = GetGeneralHelpText()
        .Tag = "general" ' Store context for More Help button
        .Show vbModal
    End With
    Unload HelpForm
End Sub

Public Sub OpenMoreHelp(context As String)
    ' Open comprehensive HTML help with context-specific page
    Dim htmlFile As String
    Dim workbookPath As String
    Dim fullUrl As String
    
    ' Get the directory where the workbook is located
    workbookPath = ThisWorkbook.Path
    
    ' Use separate redirect files for each context (avoids file:// URL fragment issues)
    Select Case LCase(context)
        Case "conflicts"
            htmlFile = workbookPath & "\help_conflicts.html"
        Case "staging"
            htmlFile = workbookPath & "\help_staging.html"
        Case "control"
            htmlFile = workbookPath & "\help_control.html"
        Case Else
            htmlFile = workbookPath & "\help_general.html"
    End Select
    
    ' Build full URL with file:/// protocol
    ' Convert backslashes to forward slashes for proper URL format
    Dim urlPath As String
    urlPath = Replace(htmlFile, "\", "/")
    fullUrl = "file:///" & urlPath
    
    ' Debug output to see what URL we're trying to open
    Debug.Print "Opening URL: " & fullUrl
    
    ' Open the HTML file in default browser
    On Error GoTo ErrorHandler
    
    ' Use Shell with cmd /c start to open the redirect file
    ' Need empty title parameter so URL isn't treated as window title
    Shell "cmd /c start """" """ & fullUrl & """", vbHide
    Exit Sub
    
ErrorHandler:
    ' If file doesn't exist or Shell fails, show error message
    MsgBox "Could not open help file: " & fullUrl & vbCrLf & vbCrLf & _
           "Please ensure the help files are in the same directory as the Excel file." & vbCrLf & _
           "Error: " & Err.Description, vbExclamation, "Help File Error"
End Sub



Function GetConflictsHelpText() As String
    Dim helpText As String
    helpText = "CONFLICTS RESOLUTION GUIDE" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    helpText = helpText & "What you see here:" & Chr(13) & Chr(10)
    helpText = helpText & "- Each conflict group shows ORIGINAL data at the top" & Chr(13) & Chr(10)
    helpText = helpText & "- User modifications are listed below with their names and timestamps" & Chr(13) & Chr(10)
    helpText = helpText & "- Red highlighted cells show what was actually changed" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "How to resolve conflicts:" & Chr(13) & Chr(10)
    helpText = helpText & "1. Review the ORIGINAL data and user changes" & Chr(13) & Chr(10)
    helpText = helpText & "2. In the 'Select' column (D), choose which version to keep:" & Chr(13) & Chr(10)
    helpText = helpText & "   - Select '1' to ACCEPT that user's changes" & Chr(13) & Chr(10)
    helpText = helpText & "   - Select '0' to REJECT that user's changes" & Chr(13) & Chr(10)
    helpText = helpText & "   - Leave empty to make no decision yet" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "Visual indicators:" & Chr(13) & Chr(10)
    helpText = helpText & "- Green background = Selected for merge (1)" & Chr(13) & Chr(10)
    helpText = helpText & "- Light red background = Rejected (0)" & Chr(13) & Chr(10)
    helpText = helpText & "- Red highlighted cells = Changed data" & Chr(13) & Chr(10)
    helpText = helpText & "- Original background colors = Unchanged data" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "Tips:" & Chr(13) & Chr(10)
    helpText = helpText & "- Only ONE version per conflict can be selected" & Chr(13) & Chr(10)
    helpText = helpText & "- Selecting one automatically rejects others" & Chr(13) & Chr(10)
    helpText = helpText & "- You can change your mind - just select a different option" & Chr(13) & Chr(10)
    helpText = helpText & "- Clear selection by deleting the value in column D"
    
    GetConflictsHelpText = helpText
End Function

Function GetStagingHelpText() As String
    Dim helpText As String
    helpText = "STAGING AREA GUIDE" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    helpText = helpText & "What you see here:" & Chr(13) & Chr(10)
    helpText = helpText & "- All user edits marked as 'ready' (AB=1) from user workbooks" & Chr(13) & Chr(10)
    helpText = helpText & "- Each row shows: Conflict flag, ID, User name, Timestamp, and data" & Chr(13) & Chr(10)
    helpText = helpText & "- Red highlighted cells show changes compared to main sheet" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "Column meanings:" & Chr(13) & Chr(10)
    helpText = helpText & "- Column A: Conflict indicator (0=conflict, 1=unique)" & Chr(13) & Chr(10)
    helpText = helpText & "- Column B: Unique ID for this edit" & Chr(13) & Chr(10)
    helpText = helpText & "- Column C: User who made the change" & Chr(13) & Chr(10)
    helpText = helpText & "- Column D: When the change was made" & Chr(13) & Chr(10)
    helpText = helpText & "- Column E onward: The actual data from user workbooks" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "Understanding conflicts:" & Chr(13) & Chr(10)
    helpText = helpText & "- Rows with '0' in column A have conflicts" & Chr(13) & Chr(10)
    helpText = helpText & "- Multiple users edited the same Antrag-nummer" & Chr(13) & Chr(10)
    helpText = helpText & "- These need manual resolution in the Conflicts sheet" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "Next steps:" & Chr(13) & Chr(10)
    helpText = helpText & "- Review all staged changes" & Chr(13) & Chr(10)
    helpText = helpText & "- Resolve any conflicts (rows with A=0)" & Chr(13) & Chr(10)
    helpText = helpText & "- Use Control panel to merge approved changes"
    
    GetStagingHelpText = helpText
End Function

Function GetControlHelpText() As String
    Dim helpText As String
    helpText = "CONTROL PANEL GUIDE" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    helpText = helpText & "Available functions:" & Chr(13) & Chr(10)
    helpText = helpText & "- Fetch User Edits: Collect ready changes from user workbooks" & Chr(13) & Chr(10)
    helpText = helpText & "- Build Conflicts List: Organize conflicts for resolution" & Chr(13) & Chr(10)
    helpText = helpText & "- Merge Changes: Apply approved changes to main sheet" & Chr(13) & Chr(10)
    helpText = helpText & "- Clear Areas: Reset staging or conflicts areas" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "Typical workflow:" & Chr(13) & Chr(10)
    helpText = helpText & "1. Click 'Fetch User Edits' to collect all ready changes" & Chr(13) & Chr(10)
    helpText = helpText & "2. Review the Staging sheet for overview" & Chr(13) & Chr(10)
    helpText = helpText & "3. If conflicts exist, go to Conflicts sheet" & Chr(13) & Chr(10)
    helpText = helpText & "4. Resolve all conflicts by selecting preferred versions" & Chr(13) & Chr(10)
    helpText = helpText & "5. Return to Control and click 'Merge Changes'" & Chr(13) & Chr(10)
    helpText = helpText & "6. Merged changes are applied and user workbooks are updated" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "Status indicators:" & Chr(13) & Chr(10)
    helpText = helpText & "- Summary shows counts of changes and conflicts" & Chr(13) & Chr(10)
    helpText = helpText & "- Links to problem areas for quick navigation" & Chr(13) & Chr(10)
    helpText = helpText & "- Merge status shows what was processed" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "Safety features:" & Chr(13) & Chr(10)
    helpText = helpText & "- All operations can be undone" & Chr(13) & Chr(10)
    helpText = helpText & "- Clear functions ask for confirmation" & Chr(13) & Chr(10)
    helpText = helpText & "- Original data is preserved until merge"
    
    GetControlHelpText = helpText
End Function

Function GetGeneralHelpText() As String
    Dim helpText As String
    helpText = "COLLABORATIVE WORKBOOK SYSTEM" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    helpText = helpText & "System Overview:" & Chr(13) & Chr(10)
    helpText = helpText & "This system allows multiple users to edit the same workbook safely" & Chr(13) & Chr(10)
    helpText = helpText & "by using separate user workbooks and a controlled merge process." & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "How it works:" & Chr(13) & Chr(10)
    helpText = helpText & "1. Users copy rows from main workbook to their personal .xlsm files" & Chr(13) & Chr(10)
    helpText = helpText & "2. Users edit their copies and mark them ready (column AB = 1)" & Chr(13) & Chr(10)
    helpText = helpText & "3. At end of day, changes are collected and reviewed" & Chr(13) & Chr(10)
    helpText = helpText & "4. Conflicts are resolved manually" & Chr(13) & Chr(10)
    helpText = helpText & "5. Approved changes are merged back to main workbook" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "Key sheets:" & Chr(13) & Chr(10)
    helpText = helpText & "- Control: Main dashboard for managing the process" & Chr(13) & Chr(10)
    helpText = helpText & "- Staging: Shows all collected user changes" & Chr(13) & Chr(10)
    helpText = helpText & "- Conflicts: Interface for resolving conflicting edits" & Chr(13) & Chr(10)
    helpText = helpText & "- Teile und Stoffe: The main data sheet" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "User workbooks:" & Chr(13) & Chr(10)
    helpText = helpText & "- Verzeichnis_Ali.xlsm" & Chr(13) & Chr(10)
    helpText = helpText & "- Verzeichnis_Andre.xlsm" & Chr(13) & Chr(10)
    helpText = helpText & "- Verzeichnis_Jean-Michel.xlsm" & Chr(13) & Chr(10) & Chr(13) & Chr(10)
    
    helpText = helpText & "For detailed help, navigate to the specific sheet and click Help again."
    
    GetGeneralHelpText = helpText
End Function
