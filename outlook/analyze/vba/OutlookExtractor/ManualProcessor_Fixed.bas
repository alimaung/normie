Option Explicit

' Manual Email Processor Module - FIXED VERSION
' Handles manual email processing and bulk operations with corrected JSON logic

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

' FIXED: Process emails with correct JSON logic
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
    
    ' Build new email collection (start with existing emails)
    Dim allEmails As Object
    Set allEmails = CreateObject("Scripting.Dictionary")
    
    ' Copy existing emails to the new collection
    Dim existingHash As Variant
    For Each existingHash In existingEmails.Keys
        allEmails(existingHash) = existingEmails(existingHash)
    Next existingHash
    
    Dim processedCount As Long
    Dim newEmailsCount As Long
    Dim skippedCount As Long
    processedCount = 0
    newEmailsCount = 0
    skippedCount = 0
    
    Dim item As Object
    For Each item In items
        If processedCount >= maxEmails Then Exit For
        processedCount = processedCount + 1
        
        If TypeOf item Is Outlook.MailItem Then
            Dim mailItem As Outlook.MailItem
            Set mailItem = item
            
            Dim emailHash As String
            emailHash = GenerateEmailHash(mailItem)
            
            WriteLog "  Processing email " & processedCount & ": " & Left(mailItem.Subject, 50) & "... (Hash: " & emailHash & ")"
            
            ' Check if this email already exists in JSON
            If existingEmails.Exists(emailHash) Then
                WriteLog "    SKIP: Email already in JSON"
                skippedCount = skippedCount + 1
            Else
                WriteLog "    NEW: Adding to JSON"
                
                ' Process this new email and create JSON entry
                Dim emailJsonEntry As String
                emailJsonEntry = ProcessEmailForManual(mailItem, emailHash, allEmails.Count + 1)
                
                If emailJsonEntry <> "" Then
                    allEmails(emailHash) = emailJsonEntry
                    newEmailsCount = newEmailsCount + 1
                    WriteLog "    SUCCESS: Email added to collection"
                Else
                    WriteLog "    ERROR: Failed to process email"
                End If
            End If
        End If
    Next item
    
    ' Save the complete JSON file with all emails
    WriteLog "Saving JSON with " & allEmails.Count & " total emails..."
    SaveJsonWithAllEmails allEmails, folder
    
    WriteLog "Manual processing complete:"
    WriteLog "  - Processed: " & processedCount & " emails"
    WriteLog "  - New emails added: " & newEmailsCount
    WriteLog "  - Skipped (existing): " & skippedCount
    WriteLog "  - Total in JSON: " & allEmails.Count
    
    Exit Sub
    
ErrorHandler:
    LogError "ManualProcessEmails", Err.Description, Err.Number
End Sub

' Process a single email for manual collection (FIXED)
Private Function ProcessEmailForManual(mailItem As Outlook.MailItem, emailHash As String, emailIndex As Long) As String
    On Error GoTo ErrorHandler
    
    ' Create folder structure for this email
    Dim subjectFolderName As String
    Dim subjectAttachmentFolder As String
    Dim msgFileName As String
    Dim msgFilePath As String
    
    subjectFolderName = emailHash
    subjectAttachmentFolder = GetAttachmentsFolder() & subjectFolderName & "\"
    msgFileName = emailHash & ".msg"
    msgFilePath = subjectAttachmentFolder & msgFileName
    
    ' FIXED: Always create folder structure, only skip MSG file if it exists
    WriteLog "    Creating folder structure..."
    CreateDirectoryPath subjectAttachmentFolder
    
    ' Save MSG file if it doesn't exist
    If Dir(msgFilePath) = "" Then
        WriteLog "    Saving .msg file..."
        On Error Resume Next
        mailItem.SaveAs msgFilePath, olMSG
        If Err.Number = 0 Then
            WriteLog "    MSG file saved successfully"
        Else
            WriteLog "    WARNING: Failed to save MSG file: " & Err.Description
        End If
        Err.Clear
        On Error GoTo ErrorHandler
    Else
        WriteLog "    MSG file already exists, skipping save"
    End If
    
    ' FIXED: Always build JSON entry regardless of MSG file existence
    WriteLog "    Building JSON entry..."
    ProcessEmailForManual = BuildCompleteEmailJsonEntry(mailItem, emailHash, emailIndex, subjectFolderName, msgFileName)
    
    Exit Function
    
ErrorHandler:
    LogError "ProcessEmailForManual", Err.Description, Err.Number
    ProcessEmailForManual = ""
End Function

' Build complete JSON entry for an email
Private Function BuildCompleteEmailJsonEntry(mailItem As Outlook.MailItem, emailHash As String, emailIndex As Long, folderName As String, msgFileName As String) As String
    On Error GoTo ErrorHandler
    
    Dim emailJsonEntry As String
    emailJsonEntry = "    {" & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""index"": " & emailIndex & "," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""hash"": """ & emailHash & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""subject"": """ & EscapeJson(mailItem.Subject) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""sender_name"": """ & EscapeJson(mailItem.SenderName) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""sender_email"": """ & EscapeJson(mailItem.SenderEmailAddress) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""received_time"": """ & Format(mailItem.ReceivedTime, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""sent_on"": """ & Format(mailItem.SentOn, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""size"": " & mailItem.Size & "," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""importance"": " & mailItem.Importance & "," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""unread"": " & LCase(CStr(mailItem.UnRead)) & "," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""categories"": """ & EscapeJson(mailItem.Categories) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""msg_file"": """ & EscapeJson("data/" & folderName & "/" & msgFileName) & """," & vbCrLf
    
    ' Add body content
    Dim bodyText As String
    bodyText = Left(mailItem.Body, 2000)
    If Len(mailItem.Body) > 2000 Then bodyText = bodyText & "... [TRUNCATED]"
    emailJsonEntry = emailJsonEntry & "      ""body"": """ & EscapeJson(bodyText) & """," & vbCrLf
    
    ' Add HTML body
    Dim htmlBody As String
    htmlBody = Left(mailItem.HTMLBody, 3000)
    If Len(mailItem.HTMLBody) > 3000 Then htmlBody = htmlBody & "... [TRUNCATED]"
    emailJsonEntry = emailJsonEntry & "      ""html_body"": """ & EscapeJson(htmlBody) & """," & vbCrLf
    
    ' Add recipients
    emailJsonEntry = emailJsonEntry & BuildRecipientsJsonFixed(mailItem)
    
    ' Add attachments
    emailJsonEntry = emailJsonEntry & BuildAttachmentsJsonFixed(mailItem, folderName)
    
    emailJsonEntry = emailJsonEntry & vbCrLf & "    }"
    
    BuildCompleteEmailJsonEntry = emailJsonEntry
    
    Exit Function
    
ErrorHandler:
    LogError "BuildCompleteEmailJsonEntry", Err.Description, Err.Number
    BuildCompleteEmailJsonEntry = ""
End Function

' Build recipients JSON (FIXED)
Private Function BuildRecipientsJsonFixed(mailItem As Outlook.MailItem) As String
    Dim result As String
    Dim recipientIndex As Long
    Dim recipient As Outlook.Recipient
    
    result = "      ""recipients"": [" & vbCrLf
    recipientIndex = 0
    
    For Each recipient In mailItem.Recipients
        If recipientIndex > 0 Then result = result & "," & vbCrLf
        result = result & "        {" & vbCrLf
        result = result & "          ""name"": """ & EscapeJson(recipient.Name) & """," & vbCrLf
        result = result & "          ""address"": """ & EscapeJson(recipient.Address) & """," & vbCrLf
        result = result & "          ""type"": " & recipient.Type & vbCrLf
        result = result & "        }"
        recipientIndex = recipientIndex + 1
        If recipientIndex >= 10 Then Exit For
    Next recipient
    
    result = result & vbCrLf & "      ]," & vbCrLf
    BuildRecipientsJsonFixed = result
End Function

' Build attachments JSON (FIXED)
Private Function BuildAttachmentsJsonFixed(mailItem As Outlook.MailItem, folderName As String) As String
    Dim result As String
    Dim attachmentIndex As Long
    Dim attachment As Outlook.Attachment
    
    result = "      ""attachments"": [" & vbCrLf
    attachmentIndex = 0
    
    For Each attachment In mailItem.Attachments
        ' Skip embedded images
        If Not IsEmbeddedImage(attachment.fileName) Then
            If attachmentIndex > 0 Then result = result & "," & vbCrLf
            
            Dim attachmentPath As String
            Dim relativeAttachmentPath As String
            
            relativeAttachmentPath = "data/" & folderName & "/" & attachment.fileName
            attachmentPath = GetAttachmentsFolder() & folderName & "\" & attachment.fileName
            
            ' Save attachment if it doesn't exist
            If Dir(attachmentPath) = "" Then
                WriteLog "      Downloading attachment: " & attachment.fileName
                SaveAttachmentSafely attachment, attachmentPath
            Else
                WriteLog "      Attachment already exists: " & attachment.fileName
            End If
            
            result = result & "        {" & vbCrLf
            result = result & "          ""filename"": """ & EscapeJson(attachment.fileName) & """," & vbCrLf
            result = result & "          ""size"": " & attachment.Size & "," & vbCrLf
            result = result & "          ""type"": " & attachment.Type & "," & vbCrLf
            result = result & "          ""filepath"": """ & EscapeJson(relativeAttachmentPath) & """" & vbCrLf
            result = result & "        }"
            attachmentIndex = attachmentIndex + 1
            If attachmentIndex >= 10 Then Exit For
        End If
    Next attachment
    
    result = result & vbCrLf & "      ]" & vbCrLf
    BuildAttachmentsJsonFixed = result
End Function

' Save JSON file with all emails (FIXED)
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
    
    Open existingJsonPath For Output As #fileNum
    Print #fileNum, jsonContent
    Close #fileNum
    
    WriteLog "JSON file saved successfully with " & emailCount & " total emails"
    
    Exit Sub
    
ErrorHandler:
    LogError "SaveJsonWithAllEmails", Err.Description, Err.Number
End Sub 