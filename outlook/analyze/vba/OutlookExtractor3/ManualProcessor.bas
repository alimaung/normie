Option Explicit

' Manual Email Processor Module
' Handles manual email processing and bulk operations

' Manual download of last 100 emails with intelligent skipping
Public Sub ManualDownloadLast100Emails()
    On Error GoTo ErrorHandler
    
    WriteLog "=== Manual Download of Last 100 Emails Started ==="
    
    ' Get target inbox folder
    Dim inboxFolder As Outlook.Folder
    Set inboxFolder = GetTargetInboxFolder()
    
    If inboxFolder Is Nothing Then
        WriteLog "ERROR: Could not access target inbox folder"
        Exit Sub
    End If
    
    ' Create directories if they don't exist
    CreateDirectoryPath GetOutputFolder()
    CreateDirectoryPath GetAttachmentsFolder()
    
    ' Process last 100 emails
    ManualProcessEmails inboxFolder, 100
    
    WriteLog "=== Manual Download Completed ==="
    Exit Sub
    
ErrorHandler:
    LogError "ManualDownloadLast100Emails", Err.Description, Err.Number
End Sub

' Process emails with intelligent skipping for manual download
Public Sub ManualProcessEmails(folder As Outlook.Folder, maxEmails As Long)
    On Error GoTo ErrorHandler
    
    WriteLog "Processing up to " & maxEmails & " emails from " & folder.Name
    
    ' Sort items by received time (most recent first)
    Dim items As Outlook.Items
    Set items = folder.Items
    items.Sort "[ReceivedTime]", True
    
    ' Load existing JSON if it exists
    Dim existingJsonPath As String
    Dim existingEmails As Object
    Set existingEmails = CreateObject("Scripting.Dictionary")
    
    existingJsonPath = GetOutputFolder() & "emails.json"
    
    If Dir(existingJsonPath) <> "" Then
        WriteLog "Loading existing email JSON for comparison..."
        LoadExistingEmailsFromJson existingJsonPath, existingEmails
    Else
        WriteLog "No existing email JSON found - will create new file"
    End If
    
    ' Build new JSON content
    Dim allEmails As Object
    Set allEmails = CreateObject("Scripting.Dictionary")
    
    ' Copy existing emails to the new dictionary
    Dim existingHash As Variant
    For Each existingHash In existingEmails.Keys
        allEmails(existingHash) = existingEmails(existingHash)
    Next existingHash
    
    Dim processedCount As Long
    Dim newEmailsCount As Long
    processedCount = 0
    newEmailsCount = 0
    
    Dim item As Object
    For Each item In items
        If processedCount >= maxEmails Then Exit For
        processedCount = processedCount + 1
        
        If TypeOf item Is Outlook.MailItem Then
            Dim mailItem As Outlook.MailItem
            Set mailItem = item
            
            Dim emailHash As String
            emailHash = GenerateEmailHash(mailItem)
            
            ' Check if this email already exists in JSON
            If existingEmails.Exists(emailHash) Then
                WriteLog "  SKIP: Email already in JSON - " & Left(mailItem.Subject, 50) & "... (Hash: " & emailHash & ")"
            Else
                WriteLog "  PROCESS: New email - " & Left(mailItem.Subject, 50) & "... (Hash: " & emailHash & ")"
                
                ' Process this new email
                Dim emailJsonEntry As String
                emailJsonEntry = ProcessEmailFiles(mailItem, emailHash, allEmails.Count + 1)
                
                If emailJsonEntry <> "" Then
                    allEmails(emailHash) = emailJsonEntry
                    newEmailsCount = newEmailsCount + 1
                End If
            End If
        End If
    Next item
    
    ' Save the complete JSON file with all emails
    If newEmailsCount > 0 Or existingEmails.Count = 0 Then
        SaveJsonWithAllEmails allEmails, folder
        WriteLog "Manual processing complete. Added " & newEmailsCount & " new emails (total: " & allEmails.Count & ")"
    Else
        WriteLog "Manual processing complete. No new emails found."
    End If
    
    Exit Sub
    
ErrorHandler:
    LogError "ManualProcessEmails", Err.Description, Err.Number
End Sub

' Save JSON file with all emails (for manual processing)
Private Sub SaveJsonWithAllEmails(emailDict As Object, folder As Outlook.Folder)
    On Error GoTo ErrorHandler
    
    Dim jsonContent As String
    Dim emailCount As Long
    
    ' Build complete JSON structure
    jsonContent = "{" & vbCrLf
    jsonContent = jsonContent & "  ""timestamp"": """ & Format(Now, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_name"": """ & folder.Name & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_path"": """ & EscapeJson(folder.FolderPath) & """," & vbCrLf
    jsonContent = jsonContent & "  ""total_items"": " & folder.Items.Count & "," & vbCrLf
    jsonContent = jsonContent & "  ""file_info"": {" & vbCrLf
    jsonContent = jsonContent & "    ""type"": ""current""," & vbCrLf
    jsonContent = jsonContent & "    ""max_emails_per_file"": " & MAX_EMAILS_PER_FILE & "," & vbCrLf
    jsonContent = jsonContent & "    ""archive_after_days"": " & ARCHIVE_AFTER_DAYS & vbCrLf
    jsonContent = jsonContent & "  }," & vbCrLf
    jsonContent = jsonContent & "  ""emails"": [" & vbCrLf
    
    emailCount = 0
    
    ' Add all emails from dictionary
    Dim emailHash As Variant
    For Each emailHash In emailDict.Keys
        If emailCount > 0 Then jsonContent = jsonContent & "," & vbCrLf
        jsonContent = jsonContent & emailDict(emailHash)
        emailCount = emailCount + 1
    Next emailHash
    
    ' Close JSON structure
    jsonContent = jsonContent & vbCrLf & "  ]," & vbCrLf
    jsonContent = jsonContent & "  ""extracted_count"": " & emailCount & vbCrLf
    jsonContent = jsonContent & "}" & vbCrLf
    
    ' Write JSON file
    Dim existingJsonPath As String
    Dim fileNum As Integer
    
    existingJsonPath = GetOutputFolder() & "emails.json"
    fileNum = FreeFile
    
    On Error Resume Next
    Open existingJsonPath For Output As #fileNum
    If Err.Number <> 0 Then
        LogError "SaveJsonWithAllEmails", "Failed to open JSON file for writing: " & Err.Description, Err.Number
        Exit Sub
    End If
    
    Print #fileNum, jsonContent
    Close #fileNum
    
    If Err.Number <> 0 Then
        LogError "SaveJsonWithAllEmails", "Failed to write JSON content: " & Err.Description, Err.Number
        Exit Sub
    End If
    
    On Error GoTo ErrorHandler
    WriteLog "JSON file written successfully with " & emailCount & " total emails"
    
    Exit Sub
    
ErrorHandler:
    LogError "SaveJsonWithAllEmails", Err.Description, Err.Number
End Sub 