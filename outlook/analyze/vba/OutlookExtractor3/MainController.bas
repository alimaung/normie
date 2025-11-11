Option Explicit

' Main Controller Module
' Coordinates all email extraction functionality and provides public interfaces

' Global event handler instance
Private emailEventHandler As EmailEventHandler

' Main entry point - call this to start event-driven monitoring
Public Sub StartEventMonitoring()
    On Error GoTo ErrorHandler
    
    WriteLog "Starting event-driven email monitoring..."
    WriteLog "Output folder: " & GetOutputFolder()
    WriteLog "Data folder: " & GetAttachmentsFolder()
    WriteLog "Target account: " & TARGET_ACCOUNT
    
    ' Create directories if they don't exist
    CreateDirectoryPath GetOutputFolder()
    CreateDirectoryPath GetAttachmentsFolder()
    
    ' Create and start the event handler
    Set emailEventHandler = New EmailEventHandler
    
    If emailEventHandler.StartMonitoring() Then
        WriteLog "Event monitoring started successfully!"
        WriteLog "New emails will be automatically processed as they arrive"
        WriteLog "To stop monitoring, run StopEventMonitoring"
        CreateStatusFile True
    Else
        WriteLog "Failed to start event monitoring"
        Set emailEventHandler = Nothing
    End If

    Exit Sub
    
ErrorHandler:
    LogError "StartEventMonitoring", Err.Description, Err.Number
End Sub

' Stop event monitoring
Public Sub StopEventMonitoring()
    If Not emailEventHandler Is Nothing Then
        If emailEventHandler.IsMonitoringActive() Then
            emailEventHandler.StopMonitoring
            Set emailEventHandler = Nothing
            WriteLog "Event monitoring stopped."
            CreateStatusFile False
        Else
            WriteLog "Event monitoring was not active."
        End If
    Else
        WriteLog "Event monitoring was not active."
    End If
End Sub

' Simple test function to verify macro is working
Public Sub TestMacro()
    Debug.Print "=== MACRO TEST STARTED ==="
    WriteLog "Testing macro functionality..."
    
    ' Test path resolution
    Debug.Print "Output folder: " & GetOutputFolder()
    Debug.Print "Attachments folder: " & GetAttachmentsFolder()
    Debug.Print "Target account: " & TARGET_ACCOUNT
    
    ' Test Outlook connection
    On Error GoTo ErrorHandler
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.NameSpace
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    
    Debug.Print "Outlook connection: OK"
    Debug.Print "Number of stores: " & olNamespace.Stores.Count
    
    ' List all stores
    Dim store As Outlook.Store
    Dim storeIndex As Integer
    storeIndex = 1
    
    For Each store In olNamespace.Stores
        Debug.Print "Store " & storeIndex & ": " & store.DisplayName
        If InStr(UCase(store.DisplayName), UCase(TARGET_ACCOUNT)) > 0 Then
            Debug.Print "  --> TARGET ACCOUNT FOUND!"
        End If
        storeIndex = storeIndex + 1
    Next store
    
    WriteLog "Test completed successfully"
    Debug.Print "=== MACRO TEST COMPLETED ==="
    Exit Sub
    
ErrorHandler:
    Debug.Print "ERROR in TestMacro: " & Err.Description
    LogError "TestMacro", Err.Description, Err.Number
End Sub

' Manual JSON management functions
Public Sub CleanupOldArchives()
    On Error GoTo ErrorHandler
    
    WriteLog "=== Starting manual archive cleanup ==="
    
    Dim archiveFile As String
    Dim fileDate As Date
    Dim deleteCount As Integer
    Dim keepAfterDate As Date
    
    ' Only delete archives older than 6 months
    keepAfterDate = DateAdd("m", -6, Now)
    
    archiveFile = Dir(GetOutputFolder() & "emails_archive_*.json")
    Do While archiveFile <> ""
        ' Extract date from filename (emails_archive_yyyymmdd_hhnnss.json)
        If Len(archiveFile) >= 30 Then
            Dim dateStr As String
            dateStr = Mid(archiveFile, 16, 8) ' Extract yyyymmdd
            
            If IsNumeric(dateStr) And Len(dateStr) = 8 Then
                fileDate = DateSerial(Left(dateStr, 4), Mid(dateStr, 5, 2), Right(dateStr, 2))
                
                If fileDate < keepAfterDate Then
                    WriteLog "Deleting old archive: " & archiveFile & " (Date: " & Format(fileDate, "yyyy-mm-dd") & ")"
                    Kill GetOutputFolder() & archiveFile
                    deleteCount = deleteCount + 1
                Else
                    WriteLog "Keeping archive: " & archiveFile & " (Date: " & Format(fileDate, "yyyy-mm-dd") & ")"
                End If
            End If
        End If
        
        archiveFile = Dir
    Loop
    
    WriteLog "Cleanup completed. Deleted " & deleteCount & " old archive files"
    CreateJsonIndexFile ' Update index
    
    Exit Sub
    
ErrorHandler:
    LogError "CleanupOldArchives", Err.Description, Err.Number
End Sub

' Force JSON rotation manually
Public Sub ForceJsonRotation()
    On Error GoTo ErrorHandler
    
    WriteLog "=== Manual JSON rotation started ==="
    
    ' Load existing emails
    Dim existingEmails As Object
    Set existingEmails = CreateObject("Scripting.Dictionary")
    
    Dim existingJsonPath As String
    existingJsonPath = GetOutputFolder() & "emails.json"
    
    If Dir(existingJsonPath) <> "" Then
        LoadExistingEmailsFromJson existingJsonPath, existingEmails
        
        If existingEmails.Count > 0 Then
            WriteLog "Forcing rotation of " & existingEmails.Count & " emails"
            
            ' Get target folder for rotation
            Dim targetFolder As Outlook.Folder
            Set targetFolder = GetTargetInboxFolder()
            
            If Not targetFolder Is Nothing Then
                RotateJsonFiles existingEmails, targetFolder
            Else
                WriteLog "ERROR: Could not access target folder for rotation"
            End If
        Else
            WriteLog "No emails found to rotate"
        End If
    Else
        WriteLog "No main JSON file found"
    End If
    
    Exit Sub
    
ErrorHandler:
    LogError "ForceJsonRotation", Err.Description, Err.Number
End Sub

' Get statistics about JSON files
Public Sub GetJsonStatistics()
    On Error GoTo ErrorHandler
    
    WriteLog "=== JSON FILES STATISTICS ==="
    
    Dim currentFile As String
    Dim archiveFile As String
    Dim totalEmails As Long
    Dim currentEmails As Long
    Dim archiveEmails As Long
    Dim fileCount As Long
    Dim totalSize As Long
    
    ' Check main file
    currentFile = GetOutputFolder() & "emails.json"
    If Dir(currentFile) <> "" Then
        currentEmails = CountEmailsInJsonFile(currentFile)
        totalSize = totalSize + FileLen(currentFile)
        fileCount = fileCount + 1
        WriteLog "Current file (emails.json): " & currentEmails & " emails, " & FormatBytes(FileLen(currentFile))
    End If
    
    ' Check archive files
    archiveFile = Dir(GetOutputFolder() & "emails_archive_*.json")
    Do While archiveFile <> ""
        Dim archiveCount As Long
        Dim archiveSize As Long
        
        archiveCount = CountEmailsInJsonFile(GetOutputFolder() & archiveFile)
        archiveSize = FileLen(GetOutputFolder() & archiveFile)
        
        archiveEmails = archiveEmails + archiveCount
        totalSize = totalSize + archiveSize
        fileCount = fileCount + 1
        
        WriteLog "Archive (" & archiveFile & "): " & archiveCount & " emails, " & FormatBytes(archiveSize)
        
        archiveFile = Dir
    Loop
    
    totalEmails = currentEmails + archiveEmails
    
    WriteLog "--- SUMMARY ---"
    WriteLog "Total files: " & fileCount
    WriteLog "Total emails: " & totalEmails & " (Current: " & currentEmails & ", Archived: " & archiveEmails & ")"
    WriteLog "Total disk space: " & FormatBytes(totalSize)
    WriteLog "Average emails per file: " & IIf(fileCount > 0, Round(totalEmails / fileCount, 0), 0)
    
    Exit Sub
    
ErrorHandler:
    LogError "GetJsonStatistics", Err.Description, Err.Number
End Sub 