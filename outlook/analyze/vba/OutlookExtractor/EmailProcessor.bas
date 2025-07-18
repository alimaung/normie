Option Explicit

' Email Processor Module
' Handles individual email processing and attachment management

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
    
    ' Create email folder structure and save files
    Dim emailJsonEntry As String
    emailJsonEntry = ProcessEmailFiles(mailItem, emailHash, existingEmails.Count + 1)
    
    ' Add this email to the existing emails dictionary
    existingEmails(emailHash) = emailJsonEntry
    
    ' Rebuild and save the complete JSON file
    SaveCompleteJsonFile existingEmails, targetFolder
    
    WriteLog "  New email processed and JSON updated!"
    
    Exit Sub
    
ErrorHandler:
    LogError "ProcessSingleNewEmail", Err.Description, Err.Number
End Sub

' Process email files and create JSON entry
Private Function ProcessEmailFiles(mailItem As Outlook.MailItem, emailHash As String, emailIndex As Long) As String
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
    ProcessEmailFiles = BuildEmailJsonEntry(mailItem, emailHash, emailIndex, subjectFolderName, msgFileName)
    
    Exit Function
    
ErrorHandler:
    LogError "ProcessEmailFiles", Err.Description, Err.Number
    ProcessEmailFiles = ""
End Function

' Build JSON entry for an email
Private Function BuildEmailJsonEntry(mailItem As Outlook.MailItem, emailHash As String, emailIndex As Long, folderName As String, msgFileName As String) As String
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
    emailJsonEntry = emailJsonEntry & BuildBodyContent(mailItem)
    
    ' Add recipients
    emailJsonEntry = emailJsonEntry & BuildRecipientsJson(mailItem)
    
    ' Add attachments
    emailJsonEntry = emailJsonEntry & BuildAttachmentsJson(mailItem, folderName)
    
    emailJsonEntry = emailJsonEntry & vbCrLf & "    }"
    
    BuildEmailJsonEntry = emailJsonEntry
    
    Exit Function
    
ErrorHandler:
    LogError "BuildEmailJsonEntry", Err.Description, Err.Number
    BuildEmailJsonEntry = ""
End Function

' Build body content JSON
Private Function BuildBodyContent(mailItem As Outlook.MailItem) As String
    Dim bodyText As String
    Dim htmlBody As String
    Dim result As String
    
    ' Extract full body content (no truncation)
    bodyText = mailItem.Body
    result = "      ""body"": """ & EscapeJson(bodyText) & """," & vbCrLf
    
    ' Extract full HTML body content (no truncation)
    htmlBody = mailItem.HTMLBody
    result = result & "      ""html_body"": """ & EscapeJson(htmlBody) & """," & vbCrLf
    
    BuildBodyContent = result
End Function

' Build recipients JSON
Private Function BuildRecipientsJson(mailItem As Outlook.MailItem) As String
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
    BuildRecipientsJson = result
End Function

' Build attachments JSON
Private Function BuildAttachmentsJson(mailItem As Outlook.MailItem, folderName As String) As String
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
            
            WriteLog "  Downloading attachment: " & attachment.fileName
            
            ' Save attachment with error handling
            SaveAttachmentSafely attachment, attachmentPath
            
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
    BuildAttachmentsJson = result
End Function

' Safely save attachment with error handling
Private Sub SaveAttachmentSafely(attachment As Outlook.Attachment, attachmentPath As String)
    On Error Resume Next
    
    ' Ensure directory exists before saving
    Dim folderPath As String
    folderPath = Left(attachmentPath, InStrRev(attachmentPath, "\"))
    CreateDirectoryPath folderPath
    
    ' Try to save the attachment
    attachment.SaveAsFile attachmentPath
    
    If Err.Number = 0 Then
        ' Verify file was actually created and has content
        If FileExistsAndHasContent(attachmentPath) Then
            WriteLog "  Downloaded successfully: " & attachment.fileName
        Else
            WriteLog "  WARNING: Save appeared successful but file not found: " & attachment.fileName
        End If
    Else
        WriteLog "  Failed to download: " & attachment.fileName & " (Error: " & Err.Description & ")"
        
        ' Try alternative save method for common file types
        TryAlternativeSave attachment, attachmentPath
    End If
    
    Err.Clear
    On Error GoTo 0
End Sub

' Try alternative save method for problematic attachments
Private Sub TryAlternativeSave(attachment As Outlook.Attachment, originalPath As String)
    On Error Resume Next
    
    Dim fileExt As String
    fileExt = UCase(Right(attachment.fileName, 4))
    
    If fileExt = ".PDF" Or fileExt = ".DOC" Or fileExt = ".XLS" Then
        WriteLog "  Attempting alternative save method for " & fileExt & " file..."
        
        ' Try with a simplified filename
        Dim folderPath As String
        Dim simplifiedPath As String
        folderPath = Left(originalPath, InStrRev(originalPath, "\"))
        simplifiedPath = folderPath & "attachment_alt" & fileExt
        
        attachment.SaveAsFile simplifiedPath
        
        If Err.Number = 0 And FileExistsAndHasContent(simplifiedPath) Then
            WriteLog "  Alternative save successful: attachment_alt" & fileExt
        Else
            WriteLog "  Alternative save also failed: " & Err.Description
        End If
    End If
    
    On Error GoTo 0
End Sub 