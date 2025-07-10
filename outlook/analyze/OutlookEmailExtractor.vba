Option Explicit

' Outlook Email Extractor VBA Macro
' This macro runs continuously and extracts emails to JSON files every X minutes
' Place this in Outlook VBA (Alt+F11 -> Insert -> Module)

' Windows API declarations (must be at module level)
Private Declare PtrSafe Function SetTimer Lib "user32" ( _
    ByVal hwnd As LongPtr, _
    ByVal nIDEvent As LongPtr, _
    ByVal uElapse As Long, _
    ByVal lpTimerFunc As LongPtr) As LongPtr

Private Declare PtrSafe Function KillTimer Lib "user32" ( _
    ByVal hwnd As LongPtr, _
    ByVal nIDEvent As LongPtr) As Long

' Global variables for polling
Private Const POLL_INTERVAL_MINUTES As Integer = 1
Private Const MAX_EMAILS_PER_ACCOUNT As Integer = 50
Private Const TARGET_ACCOUNT As String = "IRM-Standardisation-Office"

' Change tracking
Private LastEmailCount As Integer
Private LastModifiedTime As Date

' Timer variables
Private PollTimerID As Long
Private IsPolling As Boolean

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
    Dim i As Integer
    
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

' Main entry point - call this to start polling
Public Sub StartEmailPolling()
    Debug.Print "Starting email polling every " & POLL_INTERVAL_MINUTES & " minutes..."
    Debug.Print "Output folder: " & GetOutputFolder()
    Debug.Print "Data folder: " & GetAttachmentsFolder()
    Debug.Print "Target account: " & TARGET_ACCOUNT
    
    ' Create main output folder if it doesn't exist
    CreateDirectoryPath GetOutputFolder()
    Debug.Print "Created/verified main folder: " & GetOutputFolder()
    
    ' Create data subfolder for emails and attachments
    CreateDirectoryPath GetAttachmentsFolder()
    Debug.Print "Created/verified data folder: " & GetAttachmentsFolder()
    
    ' Run extraction immediately
    ExtractAllEmails
    
    ' Start timer for recurring extractions (interval in milliseconds)
    Dim intervalMS As Long
    intervalMS = POLL_INTERVAL_MINUTES * 60 * 1000
    
    PollTimerID = SetTimer(0, 0, intervalMS, AddressOf TimerCallback)
    IsPolling = True
    
    Debug.Print "Polling started with timer ID: " & PollTimerID
    Debug.Print "To stop, run StopEmailPolling"
End Sub

' Stop the polling
Public Sub StopEmailPolling()
    If IsPolling And PollTimerID <> 0 Then
        KillTimer 0, PollTimerID
        PollTimerID = 0
        IsPolling = False
        Debug.Print "Polling stopped."
    Else
        Debug.Print "Polling was not active."
    End If
End Sub

' Timer callback function
Private Sub TimerCallback()
    On Error Resume Next
    ExtractAllEmails
End Sub

' Main extraction routine
Public Sub ExtractAllEmails()
    On Error GoTo ErrorHandler
    
    Debug.Print "=== Email Extraction Started: " & Now & " ==="
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.Namespace
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    
    ' Extract from target account only
    Dim store As Outlook.Store
    Dim hasChanges As Boolean
    hasChanges = False
    
    For Each store In olNamespace.Stores
        If InStr(UCase(store.DisplayName), UCase(TARGET_ACCOUNT)) > 0 Then
            Debug.Print "Processing target store: " & store.DisplayName
            hasChanges = ExtractEmailsFromStore(store)
            Exit For ' Only process the first matching store
        End If
    Next store
    
    ' Only create status file if there were changes
    If hasChanges Then
        CreateStatusFile
        Debug.Print "Changes detected - files updated"
    Else
        Debug.Print "No changes detected - skipping file writes"
    End If
    
    Debug.Print "=== Email Extraction Completed: " & Now & " ==="
    
    Exit Sub
    
ErrorHandler:
    Debug.Print "Error in ExtractAllEmails: " & Err.Description
End Sub

' Extract emails from a specific store
Private Function ExtractEmailsFromStore(store As Outlook.Store) As Boolean
    On Error GoTo ErrorHandler
    
    Dim rootFolder As Outlook.Folder
    Set rootFolder = store.GetRootFolder
    
    ' Clean store name for filename
    Dim storeName As String
    storeName = CleanFileName(store.DisplayName)
    
    ' Extract from Inbox
    Dim inboxFolder As Outlook.Folder
    Set inboxFolder = FindFolderByName(rootFolder, "Inbox")
    
    If Not inboxFolder Is Nothing Then
        Debug.Print "  Extracting from Inbox: " & inboxFolder.Items.Count & " items"
        ExtractEmailsFromStore = ExtractEmailsFromFolder(inboxFolder, "emails")
    Else
        ExtractEmailsFromStore = False
    End If
    
    Exit Function
    
ErrorHandler:
    Debug.Print "Error extracting from store " & store.DisplayName & ": " & Err.Description
    ExtractEmailsFromStore = False
End Function

' Extract emails from a specific folder
Private Function ExtractEmailsFromFolder(folder As Outlook.Folder, filePrefix As String) As Boolean
    On Error GoTo ErrorHandler
    
    Dim jsonContent As String
    Dim emailCount As Integer
    
    ' Start JSON structure
    jsonContent = "{" & vbCrLf
    jsonContent = jsonContent & "  ""timestamp"": """ & Format(Now, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_name"": """ & folder.Name & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_path"": """ & EscapeJson(folder.FolderPath) & """," & vbCrLf
    jsonContent = jsonContent & "  ""total_items"": " & folder.Items.Count & "," & vbCrLf
    jsonContent = jsonContent & "  ""emails"": [" & vbCrLf
    
    ' Sort items by received time (most recent first)
    Dim items As Outlook.items
    Set items = folder.items
    items.Sort "[ReceivedTime]", True
    
    ' Check if folder has changed since last run
    Dim currentCount As Integer
    Dim latestEmailTime As Date
    currentCount = items.Count
    
    If currentCount > 0 Then
        Dim firstItem As Object
        Set firstItem = items.Item(1)
        If TypeOf firstItem Is Outlook.MailItem Then
            latestEmailTime = firstItem.ReceivedTime
        End If
    End If
    
    ' Compare with last run
    If currentCount = LastEmailCount And latestEmailTime <= LastModifiedTime Then
        Debug.Print "    No changes detected (Count: " & currentCount & ", Latest: " & latestEmailTime & ")"
        ExtractEmailsFromFolder = False
        Exit Function
    End If
    
    Debug.Print "    Changes detected - updating files"
    LastEmailCount = currentCount
    LastModifiedTime = latestEmailTime
    
    emailCount = 0
    
    ' Extract emails
    Dim item As Object
    For Each item In items
        If emailCount >= MAX_EMAILS_PER_ACCOUNT Then Exit For
        
        If TypeOf item Is Outlook.MailItem Then
            Dim mailItem As Outlook.MailItem
            Set mailItem = item
            
            If emailCount > 0 Then jsonContent = jsonContent & "," & vbCrLf
            
            jsonContent = jsonContent & "    {" & vbCrLf
            jsonContent = jsonContent & "      ""index"": " & (emailCount + 1) & "," & vbCrLf
            jsonContent = jsonContent & "      ""subject"": """ & EscapeJson(mailItem.Subject) & """," & vbCrLf
            jsonContent = jsonContent & "      ""sender_name"": """ & EscapeJson(mailItem.SenderName) & """," & vbCrLf
            jsonContent = jsonContent & "      ""sender_email"": """ & EscapeJson(mailItem.SenderEmailAddress) & """," & vbCrLf
            jsonContent = jsonContent & "      ""received_time"": """ & Format(mailItem.ReceivedTime, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
            jsonContent = jsonContent & "      ""sent_on"": """ & Format(mailItem.SentOn, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
            jsonContent = jsonContent & "      ""size"": " & mailItem.Size & "," & vbCrLf
            jsonContent = jsonContent & "      ""importance"": " & mailItem.Importance & "," & vbCrLf
            jsonContent = jsonContent & "      ""unread"": " & LCase(CStr(mailItem.UnRead)) & "," & vbCrLf
            jsonContent = jsonContent & "      ""categories"": """ & EscapeJson(mailItem.Categories) & """," & vbCrLf
            jsonContent = jsonContent & "      ""msg_file"": ""data\" & subjectFolderName & "\" & CleanFileName(mailItem.Subject) & ".msg""," & vbCrLf
            
            ' Extract body (truncate if too long)
            Dim bodyText As String
            bodyText = Left(mailItem.Body, 2000)
            If Len(mailItem.Body) > 2000 Then bodyText = bodyText & "... [TRUNCATED]"
            jsonContent = jsonContent & "      ""body"": """ & EscapeJson(bodyText) & """," & vbCrLf
            
            ' Extract HTML body (truncate if too long)
            Dim htmlBody As String
            htmlBody = Left(mailItem.HTMLBody, 3000)
            If Len(mailItem.HTMLBody) > 3000 Then htmlBody = htmlBody & "... [TRUNCATED]"
            jsonContent = jsonContent & "      ""html_body"": """ & EscapeJson(htmlBody) & """," & vbCrLf
            
            ' Extract recipients
            jsonContent = jsonContent & "      ""recipients"": [" & vbCrLf
            Dim recipientIndex As Integer
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
                If recipientIndex >= 10 Then Exit For ' Limit recipients
            Next recipient
            
            jsonContent = jsonContent & vbCrLf & "      ]," & vbCrLf
            
            ' Extract attachments
            jsonContent = jsonContent & "      ""attachments"": [" & vbCrLf
            Dim attachmentIndex As Integer
            Dim subjectFolderName As String
            Dim subjectAttachmentFolder As String
            Dim attachmentPath As String
            Dim relativeAttachmentPath As String
            Dim hasRealAttachments As Boolean
            Dim folderCreated As Boolean
            Dim msgFileName As String
            Dim msgFilePath As String
            
            attachmentIndex = 0
            hasRealAttachments = False
            folderCreated = False
            
            ' Pre-check if there are any real attachments (not embedded images)
            Dim attachment As Outlook.attachment
            For Each attachment In mailItem.Attachments
                If Not IsEmbeddedImage(attachment.FileName) Then
                    hasRealAttachments = True
                    Exit For
                End If
            Next attachment
            
            ' Always create folder for emails (for .msg file and attachments)
            subjectFolderName = CleanFileName(mailItem.Subject)
            subjectAttachmentFolder = GetAttachmentsFolder() & subjectFolderName & "\"
            
            Debug.Print "      Creating folder for email: " & subjectAttachmentFolder
            CreateDirectoryPath subjectAttachmentFolder
            folderCreated = True
            
            ' Save the actual .msg email file
            msgFileName = CleanFileName(mailItem.Subject) & ".msg"
            msgFilePath = subjectAttachmentFolder & "\" & msgFileName
            
            On Error Resume Next
            mailItem.SaveAs msgFilePath, olMSG
            If Err.Number = 0 Then
                Debug.Print "      Saved .msg email: " & msgFileName
            Else
                Debug.Print "      Failed to save .msg email: " & Err.Description
            End If
            On Error GoTo ErrorHandler
            
            ' Process attachments
            For Each attachment In mailItem.Attachments
                ' Skip embedded/filler images
                If Not IsEmbeddedImage(attachment.FileName) Then
                    If attachmentIndex > 0 Then jsonContent = jsonContent & "," & vbCrLf
                    
                    ' Download attachment (keep original filename) - only if folder was created
                    If folderCreated Then
                        relativeAttachmentPath = "data\" & subjectFolderName & "\" & attachment.FileName
                        attachmentPath = subjectAttachmentFolder & "\" & attachment.FileName
                        
                        Debug.Print "      Attachment path: " & attachmentPath
                        Debug.Print "      Relative path: " & relativeAttachmentPath
                    End If
                    
                    ' Save attachment to disk (only if folder was created and it doesn't exist)
                    If folderCreated Then
                        On Error Resume Next
                        If Dir(attachmentPath) = "" Then
                            Debug.Print "      Saving attachment: " & attachment.FileName & " to " & attachmentPath
                            attachment.SaveAsFile attachmentPath
                            If Err.Number = 0 Then
                                Debug.Print "      Downloaded successfully: " & attachment.FileName
                                attachmentPath = relativeAttachmentPath
                            Else
                                Debug.Print "      Failed to download: " & attachment.FileName & " (Error: " & Err.Description & ")"
                                attachmentPath = "" ' Failed to save
                            End If
                        Else
                            Debug.Print "      Already exists: " & attachment.FileName
                            attachmentPath = relativeAttachmentPath
                        End If
                        On Error GoTo ErrorHandler
                    Else
                        ' No folder created, just record the filename
                        attachmentPath = attachment.FileName
                    End If
                    
                    jsonContent = jsonContent & "        {" & vbCrLf
                    jsonContent = jsonContent & "          ""filename"": """ & EscapeJson(attachment.FileName) & """," & vbCrLf
                    jsonContent = jsonContent & "          ""size"": " & attachment.Size & "," & vbCrLf
                    jsonContent = jsonContent & "          ""type"": " & attachment.Type & "," & vbCrLf
                    jsonContent = jsonContent & "          ""filepath"": """ & EscapeJson(attachmentPath) & """" & vbCrLf
                    jsonContent = jsonContent & "        }"
                    attachmentIndex = attachmentIndex + 1
                    If attachmentIndex >= 10 Then Exit For ' Limit attachments
                End If
            Next attachment
            
            jsonContent = jsonContent & vbCrLf & "      ]" & vbCrLf
            jsonContent = jsonContent & "    }"
            
            emailCount = emailCount + 1
        End If
    Next item
    
    ' Close JSON structure
    jsonContent = jsonContent & vbCrLf & "  ]," & vbCrLf
    jsonContent = jsonContent & "  ""extracted_count"": " & emailCount & vbCrLf
    jsonContent = jsonContent & "}" & vbCrLf
    
    ' Write to file (overwrite same file)
    Dim fileName As String
    fileName = GetOutputFolder() & filePrefix & ".json"
    
    Dim fileNum As Integer
    fileNum = FreeFile
    Open fileName For Output As #fileNum
    Print #fileNum, jsonContent
    Close #fileNum
    
    Debug.Print "    Exported " & emailCount & " emails to: " & fileName
    ExtractEmailsFromFolder = True
    
    Exit Function
    
ErrorHandler:
    Debug.Print "Error extracting emails from folder: " & Err.Description
    ExtractEmailsFromFolder = False
End Function

' Helper function to find folder by name
Private Function FindFolderByName(parentFolder As Outlook.Folder, folderName As String) As Outlook.Folder
    On Error GoTo ErrorHandler
    
    Dim folder As Outlook.Folder
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
    statusFile = GetOutputFolder() & "last_extraction.txt"
    
    Dim fileNum As Integer
    fileNum = FreeFile
    Open statusFile For Output As #fileNum
    Print #fileNum, "Last extraction: " & Format(Now, "yyyy-mm-dd hh:nn:ss")
    Print #fileNum, "Next extraction: " & Format(Now + TimeValue("00:0" & Format(POLL_INTERVAL_MINUTES, "0") & ":00"), "yyyy-mm-dd hh:nn:ss")
    Print #fileNum, "Target account: " & TARGET_ACCOUNT
    Close #fileNum
End Sub

' Manual extraction function for testing
Public Sub ExtractEmailsOnce()
    Debug.Print "Starting one-time email extraction..."
    ExtractAllEmails
    Debug.Print "One-time extraction completed."
End Sub 