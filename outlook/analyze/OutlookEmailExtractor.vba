Option Explicit

' Outlook Email Extractor VBA Macro
' This macro uses event-driven processing to automatically handle new emails
' Place this in Outlook VBA (Alt+F11 -> Insert -> Module)

' Global variables
Public Const TARGET_ACCOUNT As String = "IRM-Standardisation-Office"

' JSON Management Configuration
Public Const MAX_EMAILS_PER_FILE As Integer = 500  ' Split JSON when it reaches this size
Public Const ARCHIVE_AFTER_DAYS As Integer = 90    ' Archive emails older than this
Public Const ENABLE_JSON_ROTATION As Boolean = True ' Enable automatic file rotation

' Event handler instance
Private emailEventHandler As EmailEventHandler

' Dynamic paths
Private Function GetOutputFolder() As String
    GetOutputFolder = "C:\Users\" & Environ("USERNAME") & "\Desktop\normie\outlook\analyze\mail\"
End Function

Private Function GetAttachmentsFolder() As String
    GetAttachmentsFolder = "C:\Users\" & Environ("USERNAME") & "\Desktop\normie\outlook\analyze\mail\data\"
End Function

' Helper function to create directory path recursively
Private Sub CreateDirectoryPath(fullPath As String)
    On Error Resume Next
    
    Dim pathParts() As String
    Dim currentPath As String
    Dim i As Long
    
    ' Remove trailing backslash if present
    If Right(fullPath, 1) = "\" Then
        fullPath = Left(fullPath, Len(fullPath) - 1)
    End If
    
    pathParts = Split(fullPath, "\")
    
    ' Start with the drive letter
    currentPath = pathParts(0) & "\"
    
    ' Create each directory level
    For i = 1 To UBound(pathParts)
        currentPath = currentPath & pathParts(i) & "\"
        If Dir(currentPath, vbDirectory) = "" Then
            MkDir currentPath
        End If
    Next i
    
    On Error GoTo 0
End Sub

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
    Else
        WriteLog "Failed to start event monitoring"
        Set emailEventHandler = Nothing
    End If

        Exit Sub
    
ErrorHandler:
    WriteLog "ERROR starting event monitoring: " & Err.Description
End Sub

' Stop event monitoring
Public Sub StopEventMonitoring()
    If Not emailEventHandler Is Nothing Then
        If emailEventHandler.IsMonitoringActive() Then
            emailEventHandler.StopMonitoring
            Set emailEventHandler = Nothing
            WriteLog "Event monitoring stopped."
        Else
            WriteLog "Event monitoring was not active."
    End If
    Else
        WriteLog "Event monitoring was not active."
    End If
End Sub

' Process a single new email (called by event handler)
Public Sub ProcessSingleNewEmail(mailItem As Outlook.MailItem, targetFolder As Outlook.Folder)
    On Error GoTo ErrorHandler
    
    ' Load existing JSON to append to it
    Dim existingJsonPath As String
    Dim existingEmails As Object
    Set existingEmails = CreateObject("Scripting.Dictionary")
    
    existingJsonPath = GetOutputFolder() & "emails.json"
    
    If Dir(existingJsonPath) <> "" Then
        LoadExistingEmailsFromJson existingJsonPath, existingEmails
    End If
    
    ' Generate email hash for unique identification using multiple properties
    Dim emailHash As String
    emailHash = GenerateEmailHash(mailItem)
    
    ' Check if this email already exists (shouldn't happen with events, but safety check)
    If existingEmails.Exists(emailHash) Then
        WriteLog "  Email already exists in JSON - skipping (Hash: " & emailHash & ")"
        Exit Sub
    End If
    
    WriteLog "  Processing new email (Hash: " & emailHash & ")"
    
    ' Create folder structure for this email
            Dim subjectFolderName As String
            Dim subjectAttachmentFolder As String
            Dim msgFileName As String
            Dim msgFilePath As String
            
            subjectFolderName = emailHash
            subjectAttachmentFolder = GetAttachmentsFolder() & subjectFolderName & "\"
            msgFileName = emailHash & ".msg"
    msgFilePath = subjectAttachmentFolder & msgFileName
    
    ' Create folder and save .msg file
    WriteLog "  Creating folder and saving .msg file..."
    CreateDirectoryPath subjectAttachmentFolder
    
    On Error Resume Next
    mailItem.SaveAs msgFilePath, olMSG
    If Err.Number = 0 Then
        WriteLog "  Saved .msg file: " & msgFileName
    Else
        WriteLog "  Failed to save .msg file: " & Err.Description
    End If
    On Error GoTo ErrorHandler
    
    ' Build JSON entry for this email
    Dim emailJsonEntry As String
    emailJsonEntry = "    {" & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""index"": " & (existingEmails.Count + 1) & "," & vbCrLf
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
    emailJsonEntry = emailJsonEntry & "      ""msg_file"": """ & EscapeJson("data/" & subjectFolderName & "/" & msgFileName) & """," & vbCrLf
            
            ' Extract body (truncate if too long)
            Dim bodyText As String
            bodyText = Left(mailItem.Body, 2000)
            If Len(mailItem.Body) > 2000 Then bodyText = bodyText & "... [TRUNCATED]"
    emailJsonEntry = emailJsonEntry & "      ""body"": """ & EscapeJson(bodyText) & """," & vbCrLf
            
            ' Extract HTML body (truncate if too long)
            Dim htmlBody As String
            htmlBody = Left(mailItem.htmlBody, 3000)
            If Len(mailItem.htmlBody) > 3000 Then htmlBody = htmlBody & "... [TRUNCATED]"
    emailJsonEntry = emailJsonEntry & "      ""html_body"": """ & EscapeJson(htmlBody) & """," & vbCrLf
            
            ' Extract recipients
    emailJsonEntry = emailJsonEntry & "      ""recipients"": [" & vbCrLf
    Dim recipientIndex As Long
            recipientIndex = 0
            
            Dim recipient As Outlook.recipient
            For Each recipient In mailItem.Recipients
        If recipientIndex > 0 Then emailJsonEntry = emailJsonEntry & "," & vbCrLf
        emailJsonEntry = emailJsonEntry & "        {" & vbCrLf
        emailJsonEntry = emailJsonEntry & "          ""name"": """ & EscapeJson(recipient.Name) & """," & vbCrLf
        emailJsonEntry = emailJsonEntry & "          ""address"": """ & EscapeJson(recipient.Address) & """," & vbCrLf
        emailJsonEntry = emailJsonEntry & "          ""type"": " & recipient.Type & vbCrLf
        emailJsonEntry = emailJsonEntry & "        }"
                recipientIndex = recipientIndex + 1
        If recipientIndex >= 10 Then Exit For
            Next recipient
            
    emailJsonEntry = emailJsonEntry & vbCrLf & "      ]," & vbCrLf
            
        ' Process attachments
    emailJsonEntry = emailJsonEntry & "      ""attachments"": [" & vbCrLf
    Dim attachmentIndex As Long
            attachmentIndex = 0
            
            Dim attachment As Outlook.attachment
            For Each attachment In mailItem.Attachments
        ' Skip embedded images
                If Not IsEmbeddedImage(attachment.fileName) Then
            If attachmentIndex > 0 Then emailJsonEntry = emailJsonEntry & "," & vbCrLf
            
            Dim attachmentPath As String
            Dim relativeAttachmentPath As String
            
            relativeAttachmentPath = "data/" & subjectFolderName & "/" & attachment.fileName
            attachmentPath = subjectAttachmentFolder & "\" & attachment.fileName
            
            WriteLog "  Downloading attachment: " & attachment.fileName
            WriteLog "  DEBUG: Original attachment.fileName: [" & attachment.fileName & "]"
            WriteLog "  DEBUG: Attachment path: " & attachmentPath
            WriteLog "  DEBUG: Subject folder: " & subjectAttachmentFolder
            WriteLog "  DEBUG: File extension check: " & Right(attachment.fileName, 4)
            
            ' Ensure directory exists before saving
            CreateDirectoryPath subjectAttachmentFolder
            
            On Error Resume Next
            attachment.SaveAsFile attachmentPath
            If Err.Number = 0 Then
                WriteLog "  Downloaded successfully: " & attachment.fileName
            Else
                WriteLog "  Failed to download: " & attachment.fileName & " (Error: " & Err.Description & ")"
            End If
            ' Clear any error before continuing
            Err.Clear
            On Error GoTo ErrorHandler
            
            emailJsonEntry = emailJsonEntry & "        {" & vbCrLf
            emailJsonEntry = emailJsonEntry & "          ""filename"": """ & EscapeJson(attachment.fileName) & """," & vbCrLf
            emailJsonEntry = emailJsonEntry & "          ""size"": " & attachment.Size & "," & vbCrLf
            emailJsonEntry = emailJsonEntry & "          ""type"": " & attachment.Type & "," & vbCrLf
            emailJsonEntry = emailJsonEntry & "          ""filepath"": """ & EscapeJson(relativeAttachmentPath) & """" & vbCrLf
            emailJsonEntry = emailJsonEntry & "        }"
            attachmentIndex = attachmentIndex + 1
            If attachmentIndex >= 10 Then Exit For
        End If
    Next attachment
    
    emailJsonEntry = emailJsonEntry & vbCrLf & "      ]" & vbCrLf
    emailJsonEntry = emailJsonEntry & "    }"
    
    ' Add this email to the existing emails dictionary
    existingEmails(emailHash) = emailJsonEntry
    
    ' Rebuild and save the complete JSON file
    SaveCompleteJsonFile existingEmails, targetFolder
    
    WriteLog "  New email processed and JSON updated!"
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in ProcessSingleNewEmail: " & Err.Description
End Sub

' Save complete JSON file with all emails (existing + new) - with rotation management
Private Sub SaveCompleteJsonFile(emailDict As Object, folder As Outlook.Folder)
    On Error GoTo ErrorHandler
    
    ' Check if we need to rotate files before saving
    If ENABLE_JSON_ROTATION And emailDict.Count >= MAX_EMAILS_PER_FILE Then
        WriteLog "JSON file size limit reached (" & emailDict.Count & " emails). Performing rotation..."
        RotateJsonFiles emailDict, folder
        Exit Sub
                    End If
                    
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
    
    ' Write to file
    Dim fileName As String
    Dim fileNum As Integer
    
    fileName = GetOutputFolder() & "emails.json"
    fileNum = FreeFile
    Open fileName For Output As #fileNum
    Print #fileNum, jsonContent
    Close #fileNum
    
    WriteLog "JSON file updated with " & emailCount & " total emails"
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in SaveCompleteJsonFile: " & Err.Description
End Sub

' Rotate JSON files when they get too large
Private Sub RotateJsonFiles(emailDict As Object, folder As Outlook.Folder)
    On Error GoTo ErrorHandler
    
    WriteLog "Starting JSON file rotation..."
    
    ' Separate emails into current (recent) and archive (old) based on date
    Dim currentEmails As Object
    Dim archiveEmails As Object
    Dim cutoffDate As Date
    
    Set currentEmails = CreateObject("Scripting.Dictionary")
    Set archiveEmails = CreateObject("Scripting.Dictionary")
    
    cutoffDate = DateAdd("d", -ARCHIVE_AFTER_DAYS, Now)
    WriteLog "Cutoff date for archiving: " & Format(cutoffDate, "yyyy-mm-dd")
    
    ' Parse each email to determine if it should be archived
    Dim emailHash As Variant
    Dim emailContent As String
    Dim receivedTime As Date
    
    For Each emailHash In emailDict.Keys
        emailContent = emailDict(emailHash)
        receivedTime = ExtractReceivedTimeFromJson(emailContent)
        
        If receivedTime >= cutoffDate Then
            ' Keep in current file
            currentEmails(emailHash) = emailContent
        Else
            ' Move to archive
            archiveEmails(emailHash) = emailContent
                            End If
    Next emailHash
    
    WriteLog "Separated: " & currentEmails.Count & " current, " & archiveEmails.Count & " to archive"
    
    ' Save archive file if we have old emails
    If archiveEmails.Count > 0 Then
        Dim archiveFileName As String
        archiveFileName = "emails_archive_" & Format(Now, "yyyymmdd_hhnnss") & ".json"
        SaveJsonToFile archiveEmails, folder, archiveFileName, "archive"
        WriteLog "Archived " & archiveEmails.Count & " old emails to: " & archiveFileName
                        End If
    
    ' Save current file with recent emails
    SaveJsonToFile currentEmails, folder, "emails.json", "current"
    WriteLog "Saved " & currentEmails.Count & " current emails to main file"
    
    ' Create index file for easy navigation
    CreateJsonIndexFile
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in RotateJsonFiles: " & Err.Description
End Sub

' Extract received time from JSON email entry
Private Function ExtractReceivedTimeFromJson(emailJson As String) As Date
                        On Error GoTo ErrorHandler
    
    Dim startPos As Long
    Dim endPos As Long
    Dim timeString As String
    
    ' Find "received_time": "2024-01-01 12:34:56"
    startPos = InStr(emailJson, """received_time"": """) + 19
    endPos = InStr(startPos, emailJson, """") - 1
    
    If startPos > 19 And endPos > startPos Then
        timeString = Mid(emailJson, startPos, endPos - startPos + 1)
        ExtractReceivedTimeFromJson = CDate(timeString)
    Else
        ' Default to current time if parsing fails
        ExtractReceivedTimeFromJson = Now
                    End If
                    
    Exit Function
    
ErrorHandler:
    ExtractReceivedTimeFromJson = Now
End Function

' Save JSON to a specific file
Private Sub SaveJsonToFile(emailDict As Object, folder As Outlook.Folder, fileName As String, fileType As String)
    On Error GoTo ErrorHandler
    
    Dim jsonContent As String
    Dim emailCount As Long
    
    ' Build JSON structure
    jsonContent = "{" & vbCrLf
    jsonContent = jsonContent & "  ""timestamp"": """ & Format(Now, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_name"": """ & folder.Name & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_path"": """ & EscapeJson(folder.FolderPath) & """," & vbCrLf
    jsonContent = jsonContent & "  ""total_items"": " & folder.Items.Count & "," & vbCrLf
    jsonContent = jsonContent & "  ""file_info"": {" & vbCrLf
    jsonContent = jsonContent & "    ""type"": """ & fileType & """," & vbCrLf
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
    
    ' Write to file
    Dim fullPath As String
    Dim fileNum As Integer
    
    fullPath = GetOutputFolder() & fileName
    fileNum = FreeFile
    Open fullPath For Output As #fileNum
    Print #fileNum, jsonContent
    Close #fileNum
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in SaveJsonToFile: " & Err.Description
End Sub

' Create an index file that lists all JSON files for easy navigation
Private Sub CreateJsonIndexFile()
    On Error GoTo ErrorHandler
    
    Dim indexFile As String
    Dim fileNum As Integer
    Dim fileName As String
    Dim fileCount As Integer
    
    indexFile = GetOutputFolder() & "json_index.txt"
    fileNum = FreeFile
    Open indexFile For Output As #fileNum
    
    Print #fileNum, "EMAIL JSON FILES INDEX"
    Print #fileNum, "Generated: " & Format(Now, "yyyy-mm-dd hh:nn:ss")
    Print #fileNum, "======================================"
    Print #fileNum, ""
    Print #fileNum, "CURRENT FILES:"
    
    ' List current files
    fileName = Dir(GetOutputFolder() & "emails.json")
    If fileName <> "" Then
        Print #fileNum, "  - emails.json (main current file)"
        fileCount = fileCount + 1
    End If
    
    Print #fileNum, ""
    Print #fileNum, "ARCHIVE FILES:"
    
    ' List archive files
    fileName = Dir(GetOutputFolder() & "emails_archive_*.json")
    Do While fileName <> ""
        Print #fileNum, "  - " & fileName
        fileCount = fileCount + 1
        fileName = Dir
    Loop
    
    Print #fileNum, ""
    Print #fileNum, "CONFIGURATION:"
    Print #fileNum, "  - Max emails per file: " & MAX_EMAILS_PER_FILE
    Print #fileNum, "  - Archive after days: " & ARCHIVE_AFTER_DAYS
    Print #fileNum, "  - Auto-rotation: " & IIf(ENABLE_JSON_ROTATION, "Enabled", "Disabled")
    Print #fileNum, ""
    Print #fileNum, "Total JSON files: " & fileCount
    
    Close #fileNum
    
    WriteLog "Created JSON index file with " & fileCount & " files listed"
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in CreateJsonIndexFile: " & Err.Description
End Sub



' Helper function to find folder by name
Private Function FindFolderByName(parentFolder As Outlook.folder, folderName As String) As Outlook.folder
    On Error GoTo ErrorHandler
    
    Dim folder As Outlook.folder
    For Each folder In parentFolder.Folders
        If LCase(folder.Name) = LCase(folderName) Then
            Set FindFolderByName = folder
            Exit Function
        End If
    Next folder
    
    Set FindFolderByName = Nothing
    Exit Function
    
ErrorHandler:
    Set FindFolderByName = Nothing
End Function

' Helper function to clean filename
Private Function CleanFileName(fileName As String) As String
    Dim result As String
    result = fileName
    
    ' Replace invalid characters
    result = Replace(result, "\", "_")
    result = Replace(result, "/", "_")
    result = Replace(result, ":", "_")
    result = Replace(result, "*", "_")
    result = Replace(result, "?", "_")
    result = Replace(result, """", "_")
    result = Replace(result, "<", "_")
    result = Replace(result, ">", "_")
    result = Replace(result, "|", "_")
    result = Replace(result, "@", "_")
    result = Replace(result, " ", "_")
    
    CleanFileName = result
End Function

' Helper function to escape JSON strings
Private Function EscapeJson(text As String) As String
    Dim result As String
    result = text
    
    ' Escape special characters
    result = Replace(result, "\", "\\")
    result = Replace(result, """", "\""")
    result = Replace(result, vbCrLf, "\n")
    result = Replace(result, vbCr, "\n")
    result = Replace(result, vbLf, "\n")
    result = Replace(result, vbTab, "\t")
    
    EscapeJson = result
End Function

' Generate comprehensive email hash using maximum properties for collision resistance
Private Function GenerateEmailHash(mailItem As Object) As String
    On Error GoTo ErrorHandler
    
    Dim hashInput As String
    Dim tempValue As String
    Dim i As Long
    
    ' 1. EntryID (most unique identifier)
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.EntryID
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 2. Subject
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.Subject
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 3. Sender email address
    tempValue = ""
    On Error Resume Next
    If Not mailItem.SenderEmailAddress Is Nothing Then
        tempValue = mailItem.SenderEmailAddress
    ElseIf Not mailItem.Sender Is Nothing Then
        tempValue = mailItem.Sender.Address
    End If
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 4. Sender name
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.SenderName
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 5. Full body text (more unique than partial)
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.Body
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 6. HTML body (different formatting can make emails unique)
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.HTMLBody
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 7. Received time (as string for consistency)
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.ReceivedTime)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 8. Sent time (different from received)
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.SentOn)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 9. Size (helps distinguish emails with similar content)
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.Size)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 10. Importance level
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.Importance)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 11. Number of attachments
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.Attachments.Count)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 12. All recipient addresses (To, CC, BCC)
    tempValue = ""
    On Error Resume Next
    For i = 1 To mailItem.Recipients.Count
        tempValue = tempValue & mailItem.Recipients(i).Address & ";"
    Next i
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 13. Categories
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.Categories
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 14. Message ID (RFC standard unique identifier)
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x1035001E")
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 15. Conversation ID
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.ConversationID
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 16. Creation time
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.CreationTime)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 17. Last modification time
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.LastModificationTime)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue
    
    ' Generate hash from combined properties
    GenerateEmailHash = ShortHash(hashInput)
    Exit Function
    
ErrorHandler:
    ' Fallback to simple EntryID + Subject + timestamp if anything fails
    On Error Resume Next
    Dim fallbackInput As String
    fallbackInput = mailItem.EntryID & "|" & mailItem.Subject & "|" & CStr(Now)
    GenerateEmailHash = ShortHash(fallbackInput)
End Function

' Helper function to generate a 6-digit hash - deterministic but collision-resistant
Private Function ShortHash(text As String) As String
    On Error GoTo ErrorHandler
    
    Dim i As Long
    Dim hashValue As Long
    Dim char As Long
    Dim inputText As String
    Dim temp As Long
    
    ' Use more of the input text for better uniqueness
    inputText = Left(text, 200)
    
    ' Start with a large prime for better distribution
    hashValue = 5381
    
    ' DJB2 hash algorithm - deterministic and well-distributed
    For i = 1 To Len(inputText)
        char = Asc(Mid(inputText, i, 1))
        
        ' Calculate hash * 33 + char with overflow protection
        temp = hashValue * 33
        
        ' Handle potential overflow
        If temp > 2000000000 Then
            ' Use modulo with a large prime to maintain distribution
            hashValue = (temp Mod 999983) + char
        Else
            hashValue = temp + char
        End If
        
        ' Additional character position weighting for better distribution
        hashValue = hashValue + (i * 7)
        
        ' Keep values manageable
        If hashValue > 1000000000 Then
            hashValue = hashValue Mod 999979
        End If
    Next i
    
    ' Add length-based component for additional uniqueness
    hashValue = hashValue + (Len(inputText) * 31)
    
    ' Add checksum of all characters for more uniqueness
    Dim checksum As Long
    For i = 1 To Len(inputText) Step 3  ' Sample every 3rd character for efficiency
        checksum = checksum + Asc(Mid(inputText, i, 1))
    Next i
    hashValue = hashValue + (checksum * 17)
    
    ' Final result - always positive 6-digit number
    ShortHash = Format(Abs(hashValue) Mod 1000000, "000000")
    
    Exit Function
    
ErrorHandler:
    ' Deterministic fallback based on string properties
    Dim fallbackValue As Long
    
    If Len(text) > 0 Then
        ' Use string length, first char, last char, and middle char if available
        fallbackValue = Len(text) * 1000
        fallbackValue = fallbackValue + (Asc(Left(text, 1)) * 100)
        
        If Len(text) > 1 Then
            fallbackValue = fallbackValue + (Asc(Right(text, 1)) * 10)
        End If
        
        If Len(text) > 2 Then
            Dim midPos As Long
            midPos = Len(text) \ 2
            fallbackValue = fallbackValue + Asc(Mid(text, midPos, 1))
        End If
    Else
        fallbackValue = 123456  ' Fixed value for empty strings
    End If
    
    ShortHash = Format(Abs(fallbackValue) Mod 1000000, "000000")
End Function

' Logging function to replace Debug.Print
Public Sub WriteLog(message As String)
    On Error Resume Next
    
    ' Always output to Immediate window for debugging
    Debug.Print Format(Now, "yyyy-mm-dd hh:nn:ss") & " - " & message
    
    Dim logFile As String
    Dim fileNum As Integer
    Dim timestamp As String
    
    logFile = GetOutputFolder() & "extractor_log.txt"
    timestamp = Format(Now, "yyyy-mm-dd hh:nn:ss")
    
    ' Try to create output directory if it doesn't exist
    CreateDirectoryPath GetOutputFolder()
    
    fileNum = FreeFile
    Open logFile For Append As #fileNum
    Print #fileNum, timestamp & " - " & message
    Close #fileNum
    
    ' If there was an error writing to file, at least we have Debug.Print output
    If Err.Number <> 0 Then
        Debug.Print "ERROR writing to log file: " & Err.Description
    End If
    
    On Error GoTo 0
End Sub

' Helper function to detect embedded/filler images
Private Function IsEmbeddedImage(fileName As String) As Boolean
    Dim upperFileName As String
    upperFileName = UCase(fileName)
    
    ' Specific embedded image GUIDs/hashes
    If upperFileName = "9B295F2F83534DC99F68C53110554C14.GIF" Or _
       upperFileName = "72BCF599BF8B42FCA47C22168A12B83C.GIF" Or _
       upperFileName = "AC023DD01F024F33B4EECFFDE3D5D52A.GIF" Or _
       upperFileName = "BA0B320E1A97421AA114D0901B89EB04.JPG" Or _
       upperFileName = "CD4ED6C73D8641B9B269ABC4C9553D69.JPG" Or _
       upperFileName = "D72078099DD54DE490A7A035558F217F.GIF" Then
        IsEmbeddedImage = True
        Exit Function
    End If
    
    ' Generic imageXXX patterns (like image001.png, image002.jpg, etc.)
    If Left(upperFileName, 5) = "IMAGE" And Len(upperFileName) >= 9 Then
        Dim numberPart As String
        Dim extensionPart As String
        
        ' Extract the number part (should be 3 digits)
        numberPart = Mid(upperFileName, 6, 3)
        
        ' Check if it's all digits
        If IsNumeric(numberPart) Then
            ' Extract extension part
            extensionPart = Right(upperFileName, 4) ' .jpg, .png, .gif
            
            If extensionPart = ".JPG" Or extensionPart = ".PNG" Or extensionPart = ".GIF" Then
                IsEmbeddedImage = True
                Exit Function
            End If
        End If
    End If
    
    IsEmbeddedImage = False
End Function



' Create status file with current timestamp
Private Sub CreateStatusFile()
    Dim statusFile As String
    statusFile = GetOutputFolder() & "monitoring_status.txt"
    
    Dim fileNum As Integer
    fileNum = FreeFile
    Open statusFile For Output As #fileNum
    Print #fileNum, "Last activity: " & Format(Now, "yyyy-mm-dd hh:nn:ss")
    If isEventMonitoringActive Then
        Print #fileNum, "Event monitoring: ACTIVE"
        Print #fileNum, "Mode: Real-time email processing"
    Else
        Print #fileNum, "Event monitoring: INACTIVE"
    End If
    Print #fileNum, "Target account: " & TARGET_ACCOUNT
    Close #fileNum
End Sub

' Manual download of last 100 emails with intelligent skipping
Public Sub ManualDownloadLast100Emails()
    On Error GoTo ErrorHandler
    
    WriteLog "=== Manual Download of Last 100 Emails Started ==="
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.NameSpace
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    
    ' Find target account
    Dim store As Outlook.store
    Dim targetStore As Outlook.store
    Set targetStore = Nothing
    
    For Each store In olNamespace.Stores
        If InStr(UCase(store.DisplayName), UCase(TARGET_ACCOUNT)) > 0 Then
            Set targetStore = store
            WriteLog "Found target store: " & store.DisplayName
            Exit For
        End If
    Next store
    
    If targetStore Is Nothing Then
        WriteLog "ERROR: Target account '" & TARGET_ACCOUNT & "' not found"
        Exit Sub
    End If
    
    ' Get inbox folder
    Dim rootFolder As Outlook.folder
    Set rootFolder = targetStore.GetRootFolder
    
    Dim inboxFolder As Outlook.folder
    Set inboxFolder = FindFolderByName(rootFolder, "Inbox")
    
    If inboxFolder Is Nothing Then
        WriteLog "ERROR: Inbox folder not found"
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
    WriteLog "ERROR in ManualDownloadLast100Emails: " & Err.Description
End Sub

' Process emails with intelligent skipping for manual download
Private Sub ManualProcessEmails(folder As Outlook.folder, maxEmails As Long)
    On Error GoTo ErrorHandler
    
    WriteLog "Processing up to " & maxEmails & " emails from " & folder.Name
    
    ' Sort items by received time (most recent first)
    Dim items As Outlook.items
    Set items = folder.items
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
    Dim jsonContent As String
    Dim emailCount As Long
    Dim processedCount As Long
    
    jsonContent = "{" & vbCrLf
    jsonContent = jsonContent & "  ""timestamp"": """ & Format(Now, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_name"": """ & folder.Name & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_path"": """ & EscapeJson(folder.FolderPath) & """," & vbCrLf
    jsonContent = jsonContent & "  ""total_items"": " & folder.items.Count & "," & vbCrLf
    jsonContent = jsonContent & "  ""emails"": [" & vbCrLf
    
    emailCount = 0
    processedCount = 0
    
    Dim item As Object
    For Each item In items
        If processedCount >= maxEmails Then Exit For
        processedCount = processedCount + 1
        
        If TypeOf item Is Outlook.mailItem Then
            Dim mailItem As Outlook.mailItem
            Set mailItem = item
            
            ' Generate email hash for unique identification
            Dim emailHash As String
            
            WriteLog "    Generating hash for email: " & Left(mailItem.Subject, 30)
            On Error Resume Next
            emailHash = GenerateEmailHash(mailItem)
            If Err.Number <> 0 Then
                WriteLog "    ERROR in GenerateEmailHash: " & Err.Description
                GoTo NextItem
            End If
            On Error GoTo ErrorHandler
            
            ' Check if this email already exists in JSON
            If existingEmails.Exists(emailHash) Then
                WriteLog "  SKIP: Email already in JSON - " & Left(mailItem.Subject, 50) & "... (Hash: " & emailHash & ")"
                
                ' Still add to new JSON content (copy from existing)
                If emailCount > 0 Then jsonContent = jsonContent & "," & vbCrLf
                jsonContent = jsonContent & existingEmails(emailHash)
                emailCount = emailCount + 1
                GoTo NextItem
            End If
            
            WriteLog "  PROCESS: New email - " & Left(mailItem.Subject, 50) & "... (Hash: " & emailHash & ")"
            WriteLog "    DEBUG: Starting folder/file processing..."
            
            ' Create folder structure for this email
            Dim subjectFolderName As String
            Dim subjectAttachmentFolder As String
            Dim msgFileName As String
            Dim msgFilePath As String
            
            WriteLog "    DEBUG: Original subject: " & Left(mailItem.Subject, 100)
            WriteLog "    DEBUG: Email hash: " & emailHash
            
                         ' Use hash-only folder names for simplicity and path length safety
             subjectFolderName = emailHash
             WriteLog "    DEBUG: Folder name (hash only): " & subjectFolderName
             
             Dim basePath As String
             basePath = GetAttachmentsFolder()
             WriteLog "    DEBUG: Base path: [" & basePath & "]"
             WriteLog "    DEBUG: Subject folder name: [" & subjectFolderName & "]"
             subjectAttachmentFolder = basePath & subjectFolderName & "\"
             WriteLog "    DEBUG: Full folder path: [" & subjectAttachmentFolder & "]"
            WriteLog "    DEBUG: Folder path length: " & Len(subjectAttachmentFolder)
            
                         ' Use simple hash-only filename for main MSG file for easy recognition
             msgFileName = emailHash & ".msg"
             WriteLog "    DEBUG: MSG filename: " & msgFileName
            
            msgFilePath = subjectAttachmentFolder & msgFileName
            WriteLog "    DEBUG: Full MSG path: " & msgFilePath
            WriteLog "    DEBUG: Full MSG path length: " & Len(msgFilePath)
            
            ' Check if .msg file already exists (skip if folder/files exist)
            WriteLog "    DEBUG: Checking if MSG file exists..."
            If Dir(msgFilePath) <> "" Then
                WriteLog "    SKIP: .msg file already exists - " & msgFileName
            Else
                WriteLog "    Creating folder and saving .msg file..."
                WriteLog "    DEBUG: About to create directory path: " & subjectAttachmentFolder
                
                On Error Resume Next
                CreateDirectoryPath subjectAttachmentFolder
                If Err.Number <> 0 Then
                    WriteLog "    ERROR: Failed to create directory: " & Err.Description & " (Error " & Err.Number & ")"
                    Err.Clear
                    On Error GoTo ErrorHandler
                    GoTo NextItem
                End If
                On Error GoTo ErrorHandler
                WriteLog "    DEBUG: Directory creation successful"
                
                On Error Resume Next
                mailItem.SaveAs msgFilePath, olMSG
                If Err.Number = 0 Then
                    WriteLog "    Saved .msg file: " & msgFileName
                Else
                    WriteLog "    Failed to save .msg file: " & Err.Description
                End If
                ' Clear any error before continuing
                Err.Clear
                On Error GoTo ErrorHandler
            End If
            
            ' Build JSON entry for this email
            WriteLog "    DEBUG: MSG file processing complete, starting JSON build..."
            WriteLog "    Building JSON entry, current length: " & Len(jsonContent)
            If emailCount > 0 Then 
                On Error Resume Next
                jsonContent = jsonContent & "," & vbCrLf
                If Err.Number <> 0 Then
                    WriteLog "    ERROR concatenating JSON: " & Err.Description
                    Err.Clear
                    GoTo NextItem
                End If
                Err.Clear
                On Error GoTo ErrorHandler
            End If
            
            jsonContent = jsonContent & "    {" & vbCrLf
            jsonContent = jsonContent & "      ""index"": " & (emailCount + 1) & "," & vbCrLf
            jsonContent = jsonContent & "      ""hash"": """ & emailHash & """," & vbCrLf
            jsonContent = jsonContent & "      ""subject"": """ & EscapeJson(mailItem.Subject) & """," & vbCrLf
            jsonContent = jsonContent & "      ""sender_name"": """ & EscapeJson(mailItem.SenderName) & """," & vbCrLf
            jsonContent = jsonContent & "      ""sender_email"": """ & EscapeJson(mailItem.SenderEmailAddress) & """," & vbCrLf
            jsonContent = jsonContent & "      ""received_time"": """ & Format(mailItem.ReceivedTime, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
            jsonContent = jsonContent & "      ""sent_on"": """ & Format(mailItem.SentOn, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
            jsonContent = jsonContent & "      ""size"": " & mailItem.Size & "," & vbCrLf
            jsonContent = jsonContent & "      ""importance"": " & mailItem.Importance & "," & vbCrLf
            jsonContent = jsonContent & "      ""unread"": " & LCase(CStr(mailItem.UnRead)) & "," & vbCrLf
            jsonContent = jsonContent & "      ""categories"": """ & EscapeJson(mailItem.Categories) & """," & vbCrLf
            jsonContent = jsonContent & "      ""msg_file"": """ & EscapeJson("data/" & subjectFolderName & "/" & msgFileName) & """," & vbCrLf
            
            ' Extract body (truncate if too long)
            Dim bodyText As String
            bodyText = Left(mailItem.Body, 2000)
            If Len(mailItem.Body) > 2000 Then bodyText = bodyText & "... [TRUNCATED]"
            jsonContent = jsonContent & "      ""body"": """ & EscapeJson(bodyText) & """," & vbCrLf
            
            ' Extract HTML body (truncate if too long)
            Dim htmlBody As String
            htmlBody = Left(mailItem.htmlBody, 3000)
            If Len(mailItem.htmlBody) > 3000 Then htmlBody = htmlBody & "... [TRUNCATED]"
            jsonContent = jsonContent & "      ""html_body"": """ & EscapeJson(htmlBody) & """," & vbCrLf
            
            ' Extract recipients
            jsonContent = jsonContent & "      ""recipients"": [" & vbCrLf
            Dim recipientIndex As Long
            recipientIndex = 0
            
            Dim recipient As Outlook.recipient
            For Each recipient In mailItem.Recipients
                If recipientIndex > 0 Then jsonContent = jsonContent & "," & vbCrLf
                jsonContent = jsonContent & "        {" & vbCrLf
                jsonContent = jsonContent & "          ""name"": """ & EscapeJson(recipient.Name) & """," & vbCrLf
                jsonContent = jsonContent & "          ""address"": """ & EscapeJson(recipient.Address) & """," & vbCrLf
                jsonContent = jsonContent & "          ""type"": " & recipient.Type & vbCrLf
                jsonContent = jsonContent & "        }"
                recipientIndex = recipientIndex + 1
                If recipientIndex >= 10 Then Exit For
            Next recipient
            
            jsonContent = jsonContent & vbCrLf & "      ]," & vbCrLf
            
            ' Process attachments
            WriteLog "    DEBUG: Starting attachment processing..."
            jsonContent = jsonContent & "      ""attachments"": [" & vbCrLf
            Dim attachmentIndex As Long
            attachmentIndex = 0
            
            Dim attachment As Outlook.attachment
            WriteLog "    DEBUG: Found " & mailItem.Attachments.Count & " attachments to process"
            For Each attachment In mailItem.Attachments
                WriteLog "    DEBUG: Processing attachment: " & attachment.fileName & " (Type: " & attachment.Type & ")"
                WriteLog "    DEBUG: Original attachment.fileName: [" & attachment.fileName & "]"
                WriteLog "    DEBUG: Attachment.DisplayName: [" & attachment.DisplayName & "]"
                ' Skip embedded images
                If Not IsEmbeddedImage(attachment.fileName) Then
                    WriteLog "    DEBUG: Attachment is not embedded image, proceeding..."
                    If attachmentIndex > 0 Then jsonContent = jsonContent & "," & vbCrLf
                    
                    Dim attachmentPath As String
                    Dim relativeAttachmentPath As String
                    
                    relativeAttachmentPath = "data/" & subjectFolderName & "/" & attachment.fileName
                    WriteLog "    DEBUG: subjectAttachmentFolder var: [" & subjectAttachmentFolder & "]"
                    WriteLog "    DEBUG: attachment.fileName: [" & attachment.fileName & "]"
                    attachmentPath = subjectAttachmentFolder & "\" & attachment.fileName
                    
                    ' Check if attachment already exists
                    If Dir(attachmentPath) <> "" Then
                        WriteLog "    SKIP: Attachment already exists - " & attachment.fileName
                    Else
                        WriteLog "                        Downloading attachment: " & attachment.fileName & " (Size: " & attachment.Size & " bytes, Type: " & attachment.Type & ")"
                        WriteLog "    DEBUG: Manual - Attachment path: " & attachmentPath
                        WriteLog "    DEBUG: Manual - Subject folder: " & subjectAttachmentFolder
                        WriteLog "    DEBUG: Manual - Relative path: " & relativeAttachmentPath
                        
                        ' More robust attachment saving with detailed error handling
                        On Error Resume Next
                        Err.Clear  ' Clear any previous errors
                        
                        ' Ensure directory exists before saving
                        CreateDirectoryPath subjectAttachmentFolder
                        
                        ' Try to save the attachment
                        attachment.SaveAsFile attachmentPath
                        
                        Dim saveError As Long
                        Dim saveErrorDesc As String
                        saveError = Err.Number
                        saveErrorDesc = Err.Description
                        
                        If saveError = 0 Then
                            ' Verify file was actually created and has content
                            If Dir(attachmentPath) <> "" Then
                                WriteLog "    Downloaded successfully: " & attachment.fileName
                            Else
                                WriteLog "    WARNING: Save appeared successful but file not found: " & attachment.fileName
                            End If
                        Else
                            WriteLog "    Failed to download: " & attachment.fileName & " (Error " & saveError & ": " & saveErrorDesc & ")"
                            
                            ' For PDFs and other common file types, try alternative approach
                            Dim fileExt As String
                            fileExt = UCase(Right(attachment.fileName, 4))
                            
                            If fileExt = ".PDF" Or fileExt = ".DOC" Or fileExt = ".XLS" Then
                                WriteLog "    Attempting alternative save method for " & fileExt & " file..."
                                Err.Clear
                                
                                ' Try with a simplified filename
                                Dim simplifiedPath As String
                                simplifiedPath = subjectAttachmentFolder & "attachment_" & attachmentIndex & fileExt
                                attachment.SaveAsFile simplifiedPath
                                
                                If Err.Number = 0 And Dir(simplifiedPath) <> "" Then
                                    WriteLog "    Alternative save successful: attachment_" & attachmentIndex & fileExt
                                    ' Update the path reference
                                    attachmentPath = simplifiedPath
                                    relativeAttachmentPath = "data/" & subjectFolderName & "/attachment_" & attachmentIndex & fileExt
                                Else
                                    WriteLog "    Alternative save also failed: " & Err.Description
                                End If
                            End If
                        End If
                        
                        ' Clear any error before continuing
                        Err.Clear
                        On Error GoTo ErrorHandler
                    End If
                    
                    jsonContent = jsonContent & "        {" & vbCrLf
                    jsonContent = jsonContent & "          ""filename"": """ & EscapeJson(attachment.fileName) & """," & vbCrLf
                    jsonContent = jsonContent & "          ""size"": " & attachment.Size & "," & vbCrLf
                    jsonContent = jsonContent & "          ""type"": " & attachment.Type & "," & vbCrLf
                    jsonContent = jsonContent & "          ""filepath"": """ & EscapeJson(relativeAttachmentPath) & """" & vbCrLf
                    jsonContent = jsonContent & "        }"
                    attachmentIndex = attachmentIndex + 1
                    If attachmentIndex >= 10 Then Exit For
                End If
            Next attachment
            
            jsonContent = jsonContent & vbCrLf & "      ]" & vbCrLf
            jsonContent = jsonContent & "    }"
            
            WriteLog "    DEBUG: Email processing complete, incrementing count..."
            emailCount = emailCount + 1
        End If
        
NextItem:
    Next item
    
    ' Close JSON structure
    jsonContent = jsonContent & vbCrLf & "  ]," & vbCrLf
    jsonContent = jsonContent & "  ""extracted_count"": " & emailCount & vbCrLf
    jsonContent = jsonContent & "}" & vbCrLf
    
    ' Write JSON file
    WriteLog "DEBUG: Writing JSON file to: " & existingJsonPath
    WriteLog "DEBUG: JSON content length: " & Len(jsonContent) & " characters"
    
    Dim fileNum As Integer
    fileNum = FreeFile
    WriteLog "DEBUG: Using file number: " & fileNum
    
    On Error Resume Next
    Open existingJsonPath For Output As #fileNum
    If Err.Number <> 0 Then
        WriteLog "ERROR: Failed to open JSON file for writing: " & Err.Description
        Err.Clear
        On Error GoTo ErrorHandler
        Exit Sub
    End If
    
    Print #fileNum, jsonContent
    If Err.Number <> 0 Then
        WriteLog "ERROR: Failed to write JSON content: " & Err.Description
        Close #fileNum
        Err.Clear
        On Error GoTo ErrorHandler
        Exit Sub
    End If
    
    Close #fileNum
    If Err.Number <> 0 Then
        WriteLog "ERROR: Failed to close JSON file: " & Err.Description
        Err.Clear
        On Error GoTo ErrorHandler
        Exit Sub
    End If
    On Error GoTo ErrorHandler
    
    WriteLog "DEBUG: JSON file written successfully"
    
    WriteLog "Manual processing complete. Processed " & emailCount & " emails total (from " & processedCount & " checked)"
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in ManualProcessEmails: " & Err.Description & " (Error Number: " & Err.Number & ")"
    WriteLog "ERROR Context: Processing email " & (processedCount + 1) & " of " & maxEmails
    If Not mailItem Is Nothing Then
        WriteLog "ERROR Email Subject: " & Left(mailItem.Subject, 100)
        WriteLog "ERROR Email Hash: " & emailHash
    End If
    WriteLog "ERROR Source: " & Err.Source
End Sub

' Load existing emails from JSON file into dictionary for comparison
Private Sub LoadExistingEmailsFromJson(jsonPath As String, emailDict As Object)
    On Error GoTo ErrorHandler
    
    ' This is a simplified JSON parser for our specific structure
    ' It extracts email hashes and their full JSON entries
    
    Dim fileNum As Integer
    Dim fileContent As String
    Dim line As String
    
    fileNum = FreeFile
    Open jsonPath For Input As #fileNum
    
    Do While Not EOF(fileNum)
        Line Input #fileNum, line
        fileContent = fileContent & line & vbCrLf
    Loop
    
    Close #fileNum
    
    ' Simple extraction of email entries based on "hash" field
    Dim startPos As Long
    Dim endPos As Long
    Dim hashStart As Long
    Dim hashEnd As Long
    Dim emailHash As String
    Dim emailEntry As String
    
    startPos = 1
    
    Do
        ' Find start of email object
        startPos = InStr(startPos, fileContent, """hash"":")
        If startPos = 0 Then Exit Do
        
        ' Extract hash value
        hashStart = InStr(startPos, fileContent, """") + 1
        hashStart = InStr(hashStart, fileContent, """") + 1
        hashEnd = InStr(hashStart, fileContent, """") - 1
        
        If hashEnd > hashStart Then
            emailHash = Mid(fileContent, hashStart, hashEnd - hashStart + 1)
            
            ' Find the start of this email object (go backwards to find opening brace)
            Dim objStart As Long
            objStart = startPos
            Do While objStart > 1
                objStart = objStart - 1
                If Mid(fileContent, objStart, 1) = "{" And _
                   (objStart = 1 Or Mid(fileContent, objStart - 1, 1) = vbLf Or Mid(fileContent, objStart - 1, 1) = " ") Then
                    Exit Do
                End If
            Loop
            
            ' Find the end of this email object (find matching closing brace)
            Dim objEnd As Long
            Dim braceCount As Long
            objEnd = objStart
            braceCount = 0
            
            Do While objEnd <= Len(fileContent)
                If Mid(fileContent, objEnd, 1) = "{" Then
                    braceCount = braceCount + 1
                ElseIf Mid(fileContent, objEnd, 1) = "}" Then
                    braceCount = braceCount - 1
                    If braceCount = 0 Then Exit Do
                End If
                objEnd = objEnd + 1
            Loop
            
            ' Extract the full email entry
            emailEntry = Mid(fileContent, objStart, objEnd - objStart + 1)
            
            ' Store in dictionary
            emailDict(emailHash) = emailEntry
            
            WriteLog "  Loaded existing email: " & emailHash
        End If
        
        startPos = startPos + 1
        
    Loop
    
    WriteLog "Loaded " & emailDict.Count & " existing emails from JSON"
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR loading existing JSON: " & Err.Description
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
    Dim store As Outlook.store
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
    WriteLog "ERROR in TestMacro: " & Err.Description
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
    WriteLog "ERROR in CleanupOldArchives: " & Err.Description
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
            RotateJsonFiles existingEmails, targetInboxFolder
        Else
            WriteLog "No emails found to rotate"
        End If
    Else
        WriteLog "No main JSON file found"
    End If
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in ForceJsonRotation: " & Err.Description
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
    WriteLog "ERROR in GetJsonStatistics: " & Err.Description
End Sub

' Count emails in a JSON file
Private Function CountEmailsInJsonFile(filePath As String) As Long
    On Error GoTo ErrorHandler
    
    Dim fileContent As String
    Dim fileNum As Integer
    Dim line As String
    
    fileNum = FreeFile
    Open filePath For Input As #fileNum
    
    Do While Not EOF(fileNum)
        Line Input #fileNum, line
        fileContent = fileContent & line
    Loop
    
    Close #fileNum
    
    ' Look for "extracted_count": number
    Dim startPos As Long
    Dim endPos As Long
    
    startPos = InStr(fileContent, """extracted_count"": ") + 19
    endPos = InStr(startPos, fileContent, vbCrLf) - 1
    
    If startPos > 19 And endPos > startPos Then
        CountEmailsInJsonFile = CLng(Mid(fileContent, startPos, endPos - startPos + 1))
    Else
        CountEmailsInJsonFile = 0
    End If
    
    Exit Function
    
ErrorHandler:
    CountEmailsInJsonFile = 0
End Function

' Format bytes to human readable
Private Function FormatBytes(bytes As Long) As String
    If bytes < 1024 Then
        FormatBytes = bytes & " B"
    ElseIf bytes < 1048576 Then
        FormatBytes = Round(bytes / 1024, 1) & " KB"
    Else
        FormatBytes = Round(bytes / 1048576, 1) & " MB"
    End If
End Function

