Option Explicit

' Outlook Email Extractor VBA Macro
' This macro uses event-driven processing to automatically handle new emails
' Place this in Outlook VBA (Alt+F11 -> Insert -> Module)

' ===== MODULE-LEVEL CONSTANTS =====
' Account configuration with fallback support
' Will try TARGET_ACCOUNT first, then DEBUG_ACCOUNT if not found
Public Const TARGET_ACCOUNT As String = "IRM-Standardisation-Office"
Public Const DEBUG_ACCOUNT As String = "microfilm.development@gmail.com"

' JSON Management Configuration
Public Const MAX_EMAILS_PER_FILE As Integer = 500  ' Split JSON when it reaches this size
Public Const ARCHIVE_AFTER_DAYS As Integer = 90    ' Archive emails older than this
Public Const ENABLE_JSON_ROTATION As Boolean = True ' Enable automatic file rotation

' ===== MODULE-LEVEL VARIABLES =====

' Event handler instance
Private emailEventHandler As EmailEventHandler

' Folder tracking configuration
Public Const TRACK_INBOX As Boolean = True
Public Const TRACK_DELETED_ITEMS As Boolean = True
Public Const TRACK_SENT_ITEMS As Boolean = True
Public Const TRACK_DRAFTS As Boolean = True
Public Const TRACK_OUTBOX As Boolean = True

' ===== HELPER FUNCTIONS =====

' Account priority list - will try in order
Public Function GetAccountPriorityList() As String()
    Dim accounts(1) As String
    accounts(0) = TARGET_ACCOUNT
    accounts(1) = DEBUG_ACCOUNT
    GetAccountPriorityList = accounts
End Function

' Helper function to find target store with fallback accounts
Private Function FindTargetStoreWithFallback() As Outlook.store
    On Error GoTo ErrorHandler
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.NameSpace
    Dim store As Outlook.store
    Dim accounts() As String
    Dim i As Integer
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    accounts = GetAccountPriorityList()
    
    ' Try each account in priority order
    For i = 0 To UBound(accounts)
        WriteLog "Searching for account: " & accounts(i)
        
        For Each store In olNamespace.Stores
            If InStr(UCase(store.DisplayName), UCase(accounts(i))) > 0 Then
                Set FindTargetStoreWithFallback = store
                WriteLog "Found target store: " & store.DisplayName & " (Account: " & accounts(i) & ")"
                Exit Function
            End If
        Next store
        
        WriteLog "Account '" & accounts(i) & "' not found, trying next..."
    Next i
    
    ' If we get here, no accounts were found
    WriteLog "ERROR: No target accounts found. Available stores:"
    For Each store In olNamespace.Stores
        WriteLog "  - " & store.DisplayName
    Next store
    
    Set FindTargetStoreWithFallback = Nothing
    Exit Function
    
ErrorHandler:
    WriteLog "ERROR in FindTargetStoreWithFallback: " & Err.Description
    Set FindTargetStoreWithFallback = Nothing
End Function

' Dynamic paths
Private Function GetOutputFolder() As String
    GetOutputFolder = "C:\Users\" & Environ("USERNAME") & "\Desktop\normie\outlook\analyze\mail\"
End Function

Private Function GetAttachmentsFolder() As String
    GetAttachmentsFolder = "C:\Users\" & Environ("USERNAME") & "\Desktop\normie\outlook\analyze\mail\data\"
End Function

' Get list of folders to track based on configuration
Public Function GetTrackedFolders() As Collection
    On Error GoTo ErrorHandler
    
    Dim trackedFolders As New Collection
    Dim targetStore As Outlook.Store
    Dim rootFolder As Outlook.Folder
    Dim folder As Outlook.Folder
    
    ' Get target store with fallback
    Set targetStore = FindTargetStoreWithFallback()
    If targetStore Is Nothing Then
        WriteLog "ERROR: No target store found for folder tracking"
        Set GetTrackedFolders = trackedFolders
        Exit Function
    End If
    
    Set rootFolder = targetStore.GetRootFolder()
    
    ' Add folders based on configuration
    If TRACK_INBOX Then
        Set folder = FindFolderByName(rootFolder, "Inbox")
        If Not folder Is Nothing Then
            trackedFolders.Add folder, "Inbox"
            WriteLog "Added Inbox folder to tracking"
        End If
    End If
    
    If TRACK_DELETED_ITEMS Then
        Set folder = FindFolderByName(rootFolder, "Deleted Items")
        If folder Is Nothing Then
            Set folder = FindFolderByName(rootFolder, "Trash")
        End If
        If Not folder Is Nothing Then
            trackedFolders.Add folder, folder.Name
            WriteLog "Added " & folder.Name & " folder to tracking"
        End If
    End If
    
    If TRACK_SENT_ITEMS Then
        Set folder = FindFolderByName(rootFolder, "Sent Items")
        If folder Is Nothing Then
            Set folder = FindFolderByName(rootFolder, "Sent Mail")
        End If
        If Not folder Is Nothing Then
            trackedFolders.Add folder, folder.Name
            WriteLog "Added " & folder.Name & " folder to tracking"
        End If
    End If
    
    If TRACK_DRAFTS Then
        Set folder = FindFolderByName(rootFolder, "Drafts")
        If Not folder Is Nothing Then
            trackedFolders.Add folder, "Drafts"
            WriteLog "Added Drafts folder to tracking"
        End If
    End If
    
    If TRACK_OUTBOX Then
        Set folder = FindFolderByName(rootFolder, "Outbox")
        If Not folder Is Nothing Then
            trackedFolders.Add folder, "Outbox"
            WriteLog "Added Outbox folder to tracking"
        End If
    End If
    
    Set GetTrackedFolders = trackedFolders
    WriteLog "Total folders being tracked: " & trackedFolders.Count
    Exit Function
    
ErrorHandler:
    WriteLog "ERROR in GetTrackedFolders: " & Err.Description
    Set GetTrackedFolders = trackedFolders
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
    
    WriteLog "Starting enhanced event-driven email monitoring..."
    WriteLog "Output folder: " & GetOutputFolder()
    WriteLog "Data folder: " & GetAttachmentsFolder()
    WriteLog "Primary account: " & TARGET_ACCOUNT
    WriteLog "Debug account: " & DEBUG_ACCOUNT
    
    ' Create directories if they don't exist
    CreateDirectoryPath GetOutputFolder()
    CreateDirectoryPath GetAttachmentsFolder()
    
    ' Create and start the event handler with multi-folder support
    Set emailEventHandler = New EmailEventHandler
    
    If emailEventHandler.StartMonitoring() Then
        WriteLog "Enhanced event monitoring started successfully!"
        WriteLog "Monitoring multiple folders for new emails, moves, and deletions"
        WriteLog "Creating multi-file JSON structure (emails_inbox.json, emails_sent_items.json, etc.)"
        WriteLog "To stop monitoring, run StopEventMonitoring"
    Else
        WriteLog "Failed to start enhanced event monitoring"
        Set emailEventHandler = Nothing
    End If

    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR starting enhanced event monitoring: " & Err.Description
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

' Process a single new email (called by event handler) - UPDATED FOR MULTI-FILE STRUCTURE
Public Sub ProcessSingleNewEmail(mailItem As Outlook.MailItem, targetFolder As Outlook.Folder)
    On Error GoTo ErrorHandler
    
    WriteLog "=== EVENT: Processing new email in folder: " & targetFolder.Name & " ==="
    
    ' Use multi-file structure: create folder-specific JSON
    Dim folderJsonName As String
    Dim existingJsonPath As String
    Dim existingEmails As Object
    Set existingEmails = CreateObject("Scripting.Dictionary")
    
    ' Get standardized folder name and JSON filename
    Dim standardFolderName As String
    standardFolderName = GetStandardFolderName(targetFolder.Name)
    folderJsonName = GetFolderJsonName(standardFolderName)
    existingJsonPath = GetOutputFolder() & folderJsonName
    
    WriteLog "Event processing - JSON file: " & folderJsonName
    WriteLog "Event processing - Standard folder: " & standardFolderName
    
    ' Load existing emails from folder-specific JSON if it exists
    If Dir(existingJsonPath) <> "" Then
        WriteLog "Loading existing emails from: " & folderJsonName
        LoadExistingEmailsFromJson existingJsonPath, existingEmails
    End If
    
    ' Generate email hash for unique identification
    Dim emailHash As String
    emailHash = GenerateEmailHash(mailItem)
    
    ' Check if this email already exists
    If existingEmails.Exists(emailHash) Then
        WriteLog "  Event: Email already exists in JSON - skipping (Hash: " & emailHash & ")"
        Exit Sub
    End If
    
    WriteLog "  Event: Processing new email (Hash: " & emailHash & ")"
    
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
    Err.Clear
    mailItem.SaveAs msgFilePath, olMSG
    If Err.Number = 0 Then
        WriteLog "  Saved .msg file: " & msgFileName
    Else
        WriteLog "  WARNING: Failed to save .msg file: " & Err.Description & " (Error: " & Err.Number & ")"
        WriteLog "  Continuing with JSON processing despite MSG save failure"
    End If
    Err.Clear
    On Error GoTo ErrorHandler
    
    ' Build JSON entry for this email
    Dim emailJsonEntry As String
    emailJsonEntry = BuildEmailJsonEntry(mailItem, targetFolder, standardFolderName, emailHash, subjectFolderName, msgFileName, existingEmails.Count + 1)
    
    ' Add this email to the existing emails dictionary
    existingEmails(emailHash) = emailJsonEntry
    
    ' Save the updated folder-specific JSON file
    SaveFolderSpecificJsonFile existingEmails, targetFolder, standardFolderName, folderJsonName
    
    WriteLog "  Event: New email processed and JSON updated!"
    
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



' Helper function to find folder by name (improved for Gmail)
Private Function FindFolderByName(parentFolder As Outlook.folder, folderName As String) As Outlook.folder
    On Error GoTo ErrorHandler
    
    ' First try direct match
    Dim folder As Outlook.folder
    For Each folder In parentFolder.Folders
        If LCase(folder.Name) = LCase(folderName) Then
            Set FindFolderByName = folder
            Exit Function
        End If
    Next folder
    
    ' If not found, try searching in subfolders (Gmail often has nested structure)
    For Each folder In parentFolder.Folders
        If folder.Folders.Count > 0 Then
            Dim subfolder As Outlook.folder
            For Each subfolder In folder.Folders
                If LCase(subfolder.Name) = LCase(folderName) Then
                    Set FindFolderByName = subfolder
                    Exit Function
                End If
            Next subfolder
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
    
    ' Primary: Use EntryID directly (Outlook's built-in unique identifier)
    Dim entryId As String
    entryId = ""
    On Error Resume Next
    entryId = mailItem.EntryID
    On Error GoTo ErrorHandler
    
    If Len(entryId) > 0 Then
        ' EntryID is available - use a 16-digit hash for file paths
        GenerateEmailHash = LongHash(entryId)
        WriteLog "    Using EntryID as identifier: " & GenerateEmailHash & " (from " & Left(entryId, 30) & "...)"
        Exit Function
    End If
    
    ' Fallback 1: Use Message ID (RFC standard unique identifier)
    Dim messageId As String
    messageId = ""
    On Error Resume Next
    messageId = mailItem.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x1035001E")
    On Error GoTo ErrorHandler
    
    If Len(messageId) > 0 Then
        ' Use a 16-digit hash of Message ID for consistent length
        GenerateEmailHash = LongHash(messageId)
        WriteLog "    Using MessageID as identifier: " & GenerateEmailHash & " (from " & Left(messageId, 30) & "...)"
        Exit Function
    End If
    
    ' Fallback 2: Use ConversationID
    Dim conversationId As String
    conversationId = ""
    On Error Resume Next
    conversationId = mailItem.ConversationID
    On Error GoTo ErrorHandler
    
    If Len(conversationId) > 0 Then
        GenerateEmailHash = LongHash(conversationId)
        WriteLog "    Using ConversationID as identifier: " & GenerateEmailHash & " (from " & Left(conversationId, 30) & "...)"
        Exit Function
    End If
    
    ' Final fallback: Create hash from essential properties (old method)
    Dim hashInput As String
    hashInput = ""
    
    ' Include subject
    On Error Resume Next
    hashInput = hashInput & mailItem.Subject & "|"
    On Error GoTo ErrorHandler
    
    ' Include sender
    On Error Resume Next
    hashInput = hashInput & mailItem.SenderEmailAddress & "|"
    On Error GoTo ErrorHandler
    
    ' Include received time
    On Error Resume Next
    hashInput = hashInput & CStr(mailItem.ReceivedTime) & "|"
    On Error GoTo ErrorHandler
    
    ' Include size
    On Error Resume Next
    hashInput = hashInput & CStr(mailItem.Size)
    On Error GoTo ErrorHandler
    
    GenerateEmailHash = LongHash(hashInput)
    WriteLog "    Using fallback hash as identifier: " & GenerateEmailHash
    Exit Function
    
ErrorHandler:
    ' Emergency fallback
    On Error Resume Next
    Dim emergencyInput As String
    emergencyInput = mailItem.Subject & "|" & CStr(Now)
    GenerateEmailHash = LongHash(emergencyInput)
    WriteLog "    Using emergency hash as identifier: " & GenerateEmailHash
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

' Helper function to generate a 16-digit hash - deterministic but collision-resistant
Private Function LongHash(text As String) As String
    On Error GoTo ErrorHandler
    
    Dim i As Long
    Dim hashValue1 As Long, hashValue2 As Long
    Dim char As Long
    Dim inputText As String
    
    ' Use more of the input text for better uniqueness
    inputText = Left(text, 200)  ' Reduced to avoid overflow
    
    ' Generate two 8-digit hashes with safer arithmetic
    hashValue1 = 1001  ' Smaller starting values
    hashValue2 = 2003
    
    ' Safer hash algorithm to avoid overflow
    For i = 1 To Len(inputText)
        char = Asc(Mid(inputText, i, 1))
        
        ' First hash - safer multiplication
        hashValue1 = (hashValue1 * 7 + char) Mod 99999999
        
        ' Second hash - different approach
        hashValue2 = (hashValue2 * 11 + char + i) Mod 99999999
        
        ' Keep values in safe range
        If hashValue1 < 0 Then hashValue1 = Abs(hashValue1)
        If hashValue2 < 0 Then hashValue2 = Abs(hashValue2)
    Next i
    
    ' Add length-based components safely
    hashValue1 = (hashValue1 + Len(inputText) * 13) Mod 99999999
    hashValue2 = (hashValue2 + Len(inputText) * 17) Mod 99999999
    
    ' Combine into 16-digit result
    Dim part1 As String, part2 As String
    part1 = Format(hashValue1 Mod 100000000, "00000000")
    part2 = Format(hashValue2 Mod 100000000, "00000000")
    
    LongHash = part1 & part2
    Exit Function
    
ErrorHandler:
    ' Deterministic fallback based on string properties - safer arithmetic
    Dim fallbackValue1 As Long, fallbackValue2 As Long
    
    If Len(text) > 0 Then
        ' Generate two fallback values with safer math
        fallbackValue1 = (Len(text) * 1000) Mod 50000000
        fallbackValue2 = (Len(text) * 2000) Mod 50000000
        
        fallbackValue1 = (fallbackValue1 + Asc(Left(text, 1)) * 100) Mod 50000000
        fallbackValue2 = (fallbackValue2 + Asc(Left(text, 1)) * 200) Mod 50000000
        
        If Len(text) > 1 Then
            fallbackValue1 = (fallbackValue1 + Asc(Right(text, 1)) * 10) Mod 50000000
            fallbackValue2 = (fallbackValue2 + Asc(Right(text, 1)) * 20) Mod 50000000
        End If
        
        If Len(text) > 2 Then
            Dim midPos As Long
            midPos = Len(text) \ 2
            fallbackValue1 = (fallbackValue1 + Asc(Mid(text, midPos, 1))) Mod 50000000
            fallbackValue2 = (fallbackValue2 + Asc(Mid(text, midPos, 1)) * 2) Mod 50000000
        End If
    Else
        fallbackValue1 = 12345678
        fallbackValue2 = 87654321
    End If
    
    ' Ensure positive values
    If fallbackValue1 < 0 Then fallbackValue1 = Abs(fallbackValue1)
    If fallbackValue2 < 0 Then fallbackValue2 = Abs(fallbackValue2)
    
    Dim fbPart1 As String, fbPart2 As String
    fbPart1 = Format(fallbackValue1 Mod 100000000, "00000000")
    fbPart2 = Format(fallbackValue2 Mod 100000000, "00000000")
    
    LongHash = fbPart1 & fbPart2
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
    
    ' Find target account using fallback logic
    Dim targetStore As Outlook.store
    Set targetStore = FindTargetStoreWithFallback()
    
    If targetStore Is Nothing Then
        WriteLog "ERROR: No target accounts found"
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

' Manual download from ALL folders (Gmail-compatible)
Public Sub ManualDownloadAllFolders()
    On Error GoTo ErrorHandler
    
    WriteLog "=== Manual Download from ALL Folders Started ==="
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.NameSpace
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    
    ' Find target account using fallback logic
    Dim targetStore As Outlook.store
    Set targetStore = FindTargetStoreWithFallback()
    
    If targetStore Is Nothing Then
        WriteLog "ERROR: No target accounts found"
        Exit Sub
    End If
    
    ' Get root folder for all folder access
    Dim rootFolder As Outlook.folder
    Set rootFolder = targetStore.GetRootFolder
    
    ' Create directories if they don't exist
    CreateDirectoryPath GetOutputFolder()
    CreateDirectoryPath GetAttachmentsFolder()
    
    ' Get all tracked folders
    Dim trackedFolders As Collection
    Set trackedFolders = GetTrackedFolders()
    
    If trackedFolders.Count = 0 Then
        WriteLog "ERROR: No folders found for tracking"
        Exit Sub
    End If
    
    ' Process emails from each folder
    Dim folder As Outlook.folder
    Dim i As Integer
    
    For i = 1 To trackedFolders.Count
        Set folder = trackedFolders(i)
        WriteLog "Processing folder: " & folder.Name & " (Path: " & folder.FolderPath & ")"
        
        ' Process up to 50 emails per folder to avoid overwhelming the system
        ManualProcessEmails folder, 50
        
        WriteLog "Completed processing folder: " & folder.Name
    Next i
    
    WriteLog "=== Manual Download from ALL Folders Completed ==="
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in ManualDownloadAllFolders: " & Err.Description
End Sub

' Process emails with intelligent skipping for manual download
Private Sub ManualProcessEmails(folder As Outlook.folder, maxEmails As Long)
    On Error GoTo ErrorHandler
    
    WriteLog "Processing up to " & maxEmails & " emails from " & folder.Name
    
    ' Sort items by received time (most recent first)
    Dim items As Outlook.items
    Set items = folder.items
    items.Sort "[ReceivedTime]", True
    
    ' Create folder-specific JSON filename
    Dim folderJsonName As String
    folderJsonName = GetFolderJsonName(folder.Name)
    
    ' Load existing JSON if it exists
    Dim existingJsonPath As String
    Dim existingEmails As Object
    Set existingEmails = CreateObject("Scripting.Dictionary")
    
    existingJsonPath = GetOutputFolder() & folderJsonName
    
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
            If Dir(msgFilePath) = "" Then
                ' Ensure directory exists before saving
                WriteLog "    DEBUG: Ensuring directory exists: " & subjectAttachmentFolder
                CreateDirectoryPath subjectAttachmentFolder
                
                ' Save MSG file if it doesn't exist with proper error handling
                WriteLog "    DEBUG: Saving MSG file to: " & msgFilePath
                WriteLog "    DEBUG: Folder exists after creation: " & (Dir(subjectAttachmentFolder, vbDirectory) <> "")
                
                On Error Resume Next
                Err.Clear
                mailItem.SaveAs msgFilePath, olMSG
                If Err.Number = 0 Then
                    WriteLog "    DEBUG: MSG file saved successfully"
                    ' Verify file was actually created
                    If Dir(msgFilePath) <> "" Then
                        WriteLog "    DEBUG: MSG file verified on disk"
                    Else
                        WriteLog "    WARNING: MSG save reported success but file not found on disk"
                    End If
                Else
                    WriteLog "    WARNING: Failed to save MSG file: " & Err.Description & " (Error: " & Err.Number & ")"
                    
                    ' Handle specific common errors
                    Select Case Err.Number
                        Case -2147287037  ' The operation failed
                            WriteLog "    DEBUG: Common Outlook COM error - might be due to permissions or file locking"
                            WriteLog "    DEBUG: Trying alternative save approach..."
                            ' Try saving with a different filename
                            Dim altPath As String
                            altPath = subjectAttachmentFolder & "email_" & emailHash & "_alt.msg"
                            Err.Clear
                            mailItem.SaveAs altPath, olMSG
                            If Err.Number = 0 Then
                                WriteLog "    DEBUG: Alternative save successful: " & altPath
                            Else
                                WriteLog "    DEBUG: Alternative save also failed: " & Err.Description
                            End If
                        Case Else
                            WriteLog "    DEBUG: Unhandled error type, skipping MSG save"
                    End Select
                    
                    WriteLog "    DEBUG: Continuing with JSON processing despite MSG save failure"
                End If
                Err.Clear
                On Error GoTo ErrorHandler
            Else
                WriteLog "    DEBUG: MSG file already exists, skipping save"
            End If
            ' ALWAYS process email for JSON (outside the IF block)
            
            ' Build JSON entry for this email
            WriteLog "    DEBUG: MSG file processing complete, starting JSON build..."
            WriteLog "    Building JSON entry, current length: " & Len(jsonContent)
            
            ' Check for potential string length issues
            If Len(jsonContent) > 500000 Then  ' Approaching VBA string limits
                WriteLog "    WARNING: JSON content getting very large (" & Len(jsonContent) & " chars), consider file rotation"
            End If
            
            If emailCount > 0 Then 
                On Error Resume Next
                jsonContent = jsonContent & "," & vbCrLf
                If Err.Number <> 0 Then
                    WriteLog "    ERROR concatenating JSON: " & Err.Description & " (Error: " & Err.Number & ")"
                    WriteLog "    DEBUG: Current JSON length: " & Len(jsonContent) & ", Email count: " & emailCount
                    Err.Clear
                    GoTo NextItem
                End If
                Err.Clear
                On Error GoTo ErrorHandler
            End If
            
            jsonContent = jsonContent & "    {" & vbCrLf
            jsonContent = jsonContent & "      ""index"": " & (emailCount + 1) & "," & vbCrLf
            jsonContent = jsonContent & "      ""hash"": """ & emailHash & """," & vbCrLf
            
            ' Add Outlook identifiers for Python service
            Dim rawEntryId As String, rawMessageId As String, rawConversationId As String
            On Error Resume Next
            rawEntryId = mailItem.EntryID
            rawMessageId = mailItem.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x1035001E")
            rawConversationId = mailItem.ConversationID
            On Error GoTo ErrorHandler
            
            jsonContent = jsonContent & "      ""entry_id"": """ & EscapeJson(rawEntryId) & """," & vbCrLf
            jsonContent = jsonContent & "      ""message_id"": """ & EscapeJson(rawMessageId) & """," & vbCrLf
            jsonContent = jsonContent & "      ""conversation_id"": """ & EscapeJson(rawConversationId) & """," & vbCrLf
            jsonContent = jsonContent & "      ""folder"": """ & EscapeJson(folder.Name) & """," & vbCrLf
            jsonContent = jsonContent & "      ""folder_path"": """ & EscapeJson(folder.FolderPath) & """," & vbCrLf
            
            jsonContent = jsonContent & "      ""subject"": """ & EscapeJson(mailItem.Subject) & """," & vbCrLf
            jsonContent = jsonContent & "      ""sender_name"": """ & EscapeJson(mailItem.SenderName) & """," & vbCrLf
            jsonContent = jsonContent & "      ""sender_email"": """ & EscapeJson(mailItem.SenderEmailAddress) & """," & vbCrLf
            jsonContent = jsonContent & "      ""received_time"": """ & Format(mailItem.ReceivedTime, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
            jsonContent = jsonContent & "      ""sent_on"": """ & Format(mailItem.SentOn, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
            jsonContent = jsonContent & "      ""size"": " & mailItem.Size & "," & vbCrLf
            jsonContent = jsonContent & "      ""importance"": " & mailItem.Importance & "," & vbCrLf
            jsonContent = jsonContent & "      ""unread"": " & LCase(CStr(mailItem.UnRead)) & "," & vbCrLf
            
            ' Extract flag information
            Dim flagged As Boolean
            Dim flagRequest As String
            Dim flagDueBy As String
            Dim flagStatus As Integer
            
            ' Get flag properties with error handling
            On Error Resume Next
            flagRequest = mailItem.FlagRequest
            flagDueBy = Format(mailItem.FlagDueBy, "yyyy-mm-dd hh:nn:ss")
            flagStatus = mailItem.FlagStatus
            
            ' Determine if email is flagged
            flagged = (Len(flagRequest) > 0 And flagRequest <> "") Or (flagStatus = 2)
            
            On Error GoTo ErrorHandler
            
            jsonContent = jsonContent & "      ""flagged"": " & LCase(CStr(flagged)) & "," & vbCrLf
            jsonContent = jsonContent & "      ""flag_request"": """ & EscapeJson(flagRequest) & """," & vbCrLf
            jsonContent = jsonContent & "      ""flag_due_by"": """ & flagDueBy & """," & vbCrLf
            jsonContent = jsonContent & "      ""flag_status"": " & flagStatus & "," & vbCrLf
            
            jsonContent = jsonContent & "      ""categories"": """ & EscapeJson(mailItem.Categories) & """," & vbCrLf
            
            ' Extract full body content (no truncation)
            Dim bodyText As String
            bodyText = mailItem.Body
            jsonContent = jsonContent & "      ""body"": """ & EscapeJson(bodyText) & """," & vbCrLf
            
            ' Extract full HTML body content (no truncation)
            Dim htmlBody As String
            htmlBody = mailItem.htmlBody
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
    
    ' Write JSON file with folder-specific name
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

' Helper function to get folder-specific JSON filename
Private Function GetFolderJsonName(folderName As String) As String
    Dim cleanName As String
    cleanName = folderName
    
    ' Clean folder name for filename
    cleanName = Replace(cleanName, " ", "_")
    cleanName = Replace(cleanName, "[", "")
    cleanName = Replace(cleanName, "]", "")
    cleanName = Replace(cleanName, "/", "_")
    cleanName = Replace(cleanName, "\", "_")
    cleanName = Replace(cleanName, ":", "_")
    cleanName = Replace(cleanName, "*", "_")
    cleanName = Replace(cleanName, "?", "_")
    cleanName = Replace(cleanName, """", "_")
    cleanName = Replace(cleanName, "<", "_")
    cleanName = Replace(cleanName, ">", "_")
    cleanName = Replace(cleanName, "|", "_")
    
    GetFolderJsonName = "emails_" & LCase(cleanName) & ".json"
End Function



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
    Debug.Print "Primary account: " & TARGET_ACCOUNT
    Debug.Print "Debug account: " & DEBUG_ACCOUNT
    
    ' Test Outlook connection
    On Error GoTo ErrorHandler
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.NameSpace
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    
    Debug.Print "Outlook connection: OK"
    Debug.Print "Number of stores: " & olNamespace.Stores.Count
    
    ' List all stores and check for target accounts
    Dim store As Outlook.store
    Dim storeIndex As Integer
    Dim accounts() As String
    Dim i As Integer
    
    storeIndex = 1
    accounts = GetAccountPriorityList()
    
    For Each store In olNamespace.Stores
        Debug.Print "Store " & storeIndex & ": " & store.DisplayName
        
        ' Check if this store matches any of our target accounts
        For i = 0 To UBound(accounts)
            If InStr(UCase(store.DisplayName), UCase(accounts(i))) > 0 Then
                Debug.Print "  --> TARGET ACCOUNT FOUND: " & accounts(i)
            End If
        Next i
        
        storeIndex = storeIndex + 1
    Next store
    
    ' Test the fallback logic
    Dim testStore As Outlook.store
    Set testStore = FindTargetStoreWithFallback()
    If Not testStore Is Nothing Then
        Debug.Print "Fallback logic test: SUCCESS - Found " & testStore.DisplayName
    Else
        Debug.Print "Fallback logic test: FAILED - No accounts found"
    End If
    
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

' Debug function to list all available folders
Public Sub DebugListAllFolders()
    On Error GoTo ErrorHandler
    
    WriteLog "=== DEBUG: Listing All Available Folders ==="
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.NameSpace
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    
    ' Find target account using fallback logic
    Dim targetStore As Outlook.store
    Set targetStore = FindTargetStoreWithFallback()
    
    If targetStore Is Nothing Then
        WriteLog "ERROR: No target accounts found"
        Exit Sub
    End If
    
    WriteLog "Found target store: " & targetStore.DisplayName
    
    ' Get root folder for all folder access
    Dim rootFolder As Outlook.folder
    Set rootFolder = targetStore.GetRootFolder
    
    WriteLog "Root folder: " & rootFolder.Name & " (Path: " & rootFolder.FolderPath & ")"
    WriteLog "Root folder has " & rootFolder.Folders.Count & " subfolders"
    
    ' List all subfolders
    Dim folder As Outlook.folder
    Dim i As Integer
    i = 1
    
    For Each folder In rootFolder.Folders
        WriteLog "Folder " & i & ": '" & folder.Name & "' (Path: " & folder.FolderPath & ", Items: " & folder.Items.Count & ")"
        
        ' Also check if this folder has subfolders
        If folder.Folders.Count > 0 Then
            WriteLog "  └─ Has " & folder.Folders.Count & " subfolders:"
            Dim subfolder As Outlook.folder
            Dim j As Integer
            j = 1
            For Each subfolder In folder.Folders
                WriteLog "     " & j & ". '" & subfolder.Name & "' (Items: " & subfolder.Items.Count & ")"
                j = j + 1
                If j > 10 Then
                    WriteLog "     ... (showing first 10 subfolders only)"
                    Exit For
                End If
            Next subfolder
        End If
        
        i = i + 1
        If i > 20 Then
            WriteLog "... (showing first 20 folders only)"
            Exit For
        End If
    Next folder
    
    ' Test specific folder lookups
    WriteLog ""
    WriteLog "=== Testing Specific Folder Lookups ==="
    
    Dim testFolders() As String
    ReDim testFolders(9)
    testFolders(0) = "Inbox"
    testFolders(1) = "Sent Items"
    testFolders(2) = "Sent Mail"
    testFolders(3) = "Deleted Items"
    testFolders(4) = "Trash"
    testFolders(5) = "Drafts"
    testFolders(6) = "Outbox"
    testFolders(7) = "Sent"
    testFolders(8) = "[Gmail]"
    testFolders(9) = "INBOX"
    
    Dim testFolder As Outlook.folder
    Dim k As Integer
    
    For k = 0 To UBound(testFolders)
        Set testFolder = FindFolderByName(rootFolder, testFolders(k))
        If Not testFolder Is Nothing Then
            WriteLog "✓ FOUND: '" & testFolders(k) & "' -> '" & testFolder.Name & "' (Items: " & testFolder.Items.Count & ")"
        Else
            WriteLog "✗ NOT FOUND: '" & testFolders(k) & "'"
        End If
    Next k
    
    WriteLog "=== Debug folder listing completed ==="
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in DebugListAllFolders: " & Err.Description
End Sub

' Extract emails from ALL Gmail folders (including nested ones)
Public Sub ExtractFromAllGmailFolders()
    On Error GoTo ErrorHandler
    
    WriteLog "=== Extracting from ALL Gmail Folders ==="
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.NameSpace
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    
    ' Find target account using fallback logic
    Dim targetStore As Outlook.store
    Set targetStore = FindTargetStoreWithFallback()
    
    If targetStore Is Nothing Then
        WriteLog "ERROR: No target accounts found"
        Exit Sub
    End If
    
    ' Get root folder for all folder access
    Dim rootFolder As Outlook.folder
    Set rootFolder = targetStore.GetRootFolder
    
    ' Create directories if they don't exist
    CreateDirectoryPath GetOutputFolder()
    CreateDirectoryPath GetAttachmentsFolder()
    
    ' Define the folders we want to extract from
    Dim foldersToProcess As Collection
    Set foldersToProcess = New Collection
    
    ' Add Inbox (direct child of root)
    Dim inboxFolder As Outlook.folder
    Set inboxFolder = FindFolderByName(rootFolder, "Inbox")
    If Not inboxFolder Is Nothing Then
        foldersToProcess.Add inboxFolder
        WriteLog "Added Inbox folder for processing (" & inboxFolder.Items.Count & " items)"
    End If
    
    ' Add Outbox (direct child of root)
    Dim outboxFolder As Outlook.folder
    Set outboxFolder = FindFolderByName(rootFolder, "Outbox")
    If Not outboxFolder Is Nothing Then
        foldersToProcess.Add outboxFolder
        WriteLog "Added Outbox folder for processing (" & outboxFolder.Items.Count & " items)"
    End If
    
    ' Add Gmail nested folders
    Dim gmailFolder As Outlook.folder
    Set gmailFolder = FindFolderByName(rootFolder, "[Gmail]")
    If Not gmailFolder Is Nothing Then
        WriteLog "Found [Gmail] parent folder with " & gmailFolder.Folders.Count & " subfolders"
        
        ' Add Trash
        Dim trashFolder As Outlook.folder
        Set trashFolder = FindFolderByName(gmailFolder, "Trash")
        If Not trashFolder Is Nothing Then
            foldersToProcess.Add trashFolder
            WriteLog "Added Trash folder for processing (" & trashFolder.Items.Count & " items)"
        End If
        
        ' Add Sent Mail
        Dim sentFolder As Outlook.folder
        Set sentFolder = FindFolderByName(gmailFolder, "Sent Mail")
        If Not sentFolder Is Nothing Then
            foldersToProcess.Add sentFolder
            WriteLog "Added Sent Mail folder for processing (" & sentFolder.Items.Count & " items)"
        End If
        
        ' Add Drafts
        Dim draftsFolder As Outlook.folder
        Set draftsFolder = FindFolderByName(gmailFolder, "Drafts")
        If Not draftsFolder Is Nothing Then
            foldersToProcess.Add draftsFolder
            WriteLog "Added Drafts folder for processing (" & draftsFolder.Items.Count & " items)"
        End If
        
        ' Add Important
        Dim importantFolder As Outlook.folder
        Set importantFolder = FindFolderByName(gmailFolder, "Important")
        If Not importantFolder Is Nothing Then
            foldersToProcess.Add importantFolder
            WriteLog "Added Important folder for processing (" & importantFolder.Items.Count & " items)"
        End If
        
        ' Add Starred
        Dim starredFolder As Outlook.folder
        Set starredFolder = FindFolderByName(gmailFolder, "Starred")
        If Not starredFolder Is Nothing Then
            foldersToProcess.Add starredFolder
            WriteLog "Added Starred folder for processing (" & starredFolder.Items.Count & " items)"
        End If
    Else
        WriteLog "WARNING: [Gmail] parent folder not found"
    End If
    
    If foldersToProcess.Count = 0 Then
        WriteLog "ERROR: No folders found for processing"
        Exit Sub
    End If
    
    WriteLog "Will process " & foldersToProcess.Count & " folders total"
    
    ' Process each folder
    Dim folder As Outlook.folder
    Dim folderIndex As Integer
    
    For folderIndex = 1 To foldersToProcess.Count
        Set folder = foldersToProcess(folderIndex)
        WriteLog "Processing folder " & folderIndex & "/" & foldersToProcess.Count & ": " & folder.Name & " (" & folder.Items.Count & " items)"
        
        If folder.Items.Count > 0 Then
            ' Process up to 50 emails per folder to avoid overwhelming
            ManualProcessEmails folder, 50
        Else
            WriteLog "  Skipping empty folder: " & folder.Name
        End If
        
        WriteLog "Completed processing folder: " & folder.Name
    Next folderIndex
    
    WriteLog "=== Extraction from ALL Gmail Folders Completed ==="
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in ExtractFromAllGmailFolders: " & Err.Description
End Sub

' Universal extraction function - works with both Outlook and Gmail automatically
Public Sub ExtractFromAllFoldersUniversal()
    On Error GoTo ErrorHandler
    
    WriteLog "=== Universal Email Extraction Started ==="
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.NameSpace
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    
    ' Find target account using fallback logic
    Dim targetStore As Outlook.store
    Set targetStore = FindTargetStoreWithFallback()
    
    If targetStore Is Nothing Then
        WriteLog "ERROR: No target accounts found"
        Exit Sub
    End If
    
    WriteLog "Processing account: " & targetStore.DisplayName
    
    ' Detect if this is Gmail or standard Outlook
    Dim isGmail As Boolean
    isGmail = (InStr(LCase(targetStore.DisplayName), "gmail") > 0)
    
    If isGmail Then
        WriteLog "Detected Gmail account - using Gmail folder structure"
    Else
        WriteLog "Detected standard Outlook account - using Outlook folder structure"
    End If
    
    ' Get root folder for all folder access
    Dim rootFolder As Outlook.folder
    Set rootFolder = targetStore.GetRootFolder
    
    ' Create directories if they don't exist
    CreateDirectoryPath GetOutputFolder()
    CreateDirectoryPath GetAttachmentsFolder()
    
    ' Collection to hold all folders we want to process
    Dim foldersToProcess As Collection
    Set foldersToProcess = New Collection
    
    ' === INBOX (same for both Gmail and Outlook) ===
    Dim inboxFolder As Outlook.folder
    Set inboxFolder = FindFolderByName(rootFolder, "Inbox")
    If Not inboxFolder Is Nothing Then
        foldersToProcess.Add inboxFolder
        WriteLog "Added Inbox folder (" & inboxFolder.Items.Count & " items)"
    End If
    
    If isGmail Then
        ' === GMAIL STRUCTURE: Look in [Gmail] subfolder ===
        Dim gmailFolder As Outlook.folder
        Set gmailFolder = FindFolderByName(rootFolder, "[Gmail]")
        If Not gmailFolder Is Nothing Then
            WriteLog "Found [Gmail] parent folder with " & gmailFolder.Folders.Count & " subfolders"
            
            ' Gmail Trash -> Standardized as "Deleted Items"
            Dim trashFolder As Outlook.folder
            Set trashFolder = FindFolderByName(gmailFolder, "Trash")
            If Not trashFolder Is Nothing Then
                foldersToProcess.Add trashFolder
                WriteLog "Added Gmail Trash folder (" & trashFolder.Items.Count & " items)"
            End If
            
            ' Gmail Sent Mail -> Standardized as "Sent Items"
            Dim sentMailFolder As Outlook.folder
            Set sentMailFolder = FindFolderByName(gmailFolder, "Sent Mail")
            If Not sentMailFolder Is Nothing Then
                foldersToProcess.Add sentMailFolder
                WriteLog "Added Gmail Sent Mail folder (" & sentMailFolder.Items.Count & " items)"
            End If
            
            ' Gmail Drafts -> Standardized as "Drafts"
            Dim gmailDraftsFolder As Outlook.folder
            Set gmailDraftsFolder = FindFolderByName(gmailFolder, "Drafts")
            If Not gmailDraftsFolder Is Nothing Then
                foldersToProcess.Add gmailDraftsFolder
                WriteLog "Added Gmail Drafts folder (" & gmailDraftsFolder.Items.Count & " items)"
            End If
        Else
            WriteLog "WARNING: [Gmail] parent folder not found"
        End If
        
    Else
        ' === OUTLOOK STRUCTURE: Look at root level ===
        
        ' Outlook Deleted Items
        Dim deletedItemsFolder As Outlook.folder
        Set deletedItemsFolder = FindFolderByName(rootFolder, "Deleted Items")
        If Not deletedItemsFolder Is Nothing Then
            foldersToProcess.Add deletedItemsFolder
            WriteLog "Added Outlook Deleted Items folder (" & deletedItemsFolder.Items.Count & " items)"
        End If
        
        ' Outlook Sent Items
        Dim sentItemsFolder As Outlook.folder
        Set sentItemsFolder = FindFolderByName(rootFolder, "Sent Items")
        If Not sentItemsFolder Is Nothing Then
            foldersToProcess.Add sentItemsFolder
            WriteLog "Added Outlook Sent Items folder (" & sentItemsFolder.Items.Count & " items)"
        End If
        
        ' Outlook Drafts (check root level for Outlook)
        Dim outlookDraftsFolder As Outlook.folder
        Set outlookDraftsFolder = FindFolderByName(rootFolder, "Drafts")
        If Not outlookDraftsFolder Is Nothing Then
            foldersToProcess.Add outlookDraftsFolder
            WriteLog "Added Outlook Drafts folder (" & outlookDraftsFolder.Items.Count & " items)"
        End If
    End If
    
    ' Process standard folders (create JSON files even if empty)
    ProcessStandardFolders targetStore, isGmail
    
    WriteLog "=== Universal Email Extraction Completed ==="
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in ExtractFromAllFoldersUniversal: " & Err.Description
End Sub

' Process standard folders with consistent naming
Private Sub ProcessStandardFolders(targetStore As Outlook.Store, isGmail As Boolean)
    On Error GoTo ErrorHandler
    
    WriteLog "Processing standard folders with consistent naming..."
    
    Dim rootFolder As Outlook.folder
    Set rootFolder = targetStore.GetRootFolder
    
    ' Define standard folder structure
    Dim standardFolders(3) As String
    standardFolders(0) = "Inbox"
    standardFolders(1) = "Drafts"
    standardFolders(2) = "Sent Items"
    standardFolders(3) = "Deleted Items"
    
    Dim i As Integer
    For i = 0 To UBound(standardFolders)
        Dim standardName As String
        standardName = standardFolders(i)
        
        WriteLog "Processing standard folder: " & standardName
        
        ' Find the actual folder based on platform
        Dim actualFolder As Outlook.folder
        Set actualFolder = FindStandardFolder(rootFolder, standardName, isGmail)
        
        If Not actualFolder Is Nothing Then
            WriteLog "  Found folder: " & actualFolder.Name & " (" & actualFolder.Items.Count & " items)"
            ' Process emails and create JSON with standardized name
            ProcessFolderWithStandardName actualFolder, standardName, 50
        Else
            WriteLog "  Folder not found: " & standardName
            ' Create empty JSON file for missing folder
            CreateEmptyFolderJson standardName
        End If
    Next i
    
    WriteLog "Standard folder processing completed"
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in ProcessStandardFolders: " & Err.Description
End Sub

' Find standard folder based on platform
Private Function FindStandardFolder(rootFolder As Outlook.folder, standardName As String, isGmail As Boolean) As Outlook.folder
    On Error GoTo ErrorHandler
    
    Select Case standardName
        Case "Inbox"
            ' Same for both platforms
            Set FindStandardFolder = FindFolderByName(rootFolder, "Inbox")
            
        Case "Drafts"
            ' Same for both platforms
            Set FindStandardFolder = FindFolderByName(rootFolder, "Drafts")
            If FindStandardFolder Is Nothing And isGmail Then
                ' Try Gmail nested structure
                Dim gmailFolder As Outlook.folder
                Set gmailFolder = FindFolderByName(rootFolder, "[Gmail]")
                If Not gmailFolder Is Nothing Then
                    Set FindStandardFolder = FindFolderByName(gmailFolder, "Drafts")
                End If
            End If
            
        Case "Sent Items"
            If isGmail Then
                ' Gmail: Look for "Sent Mail" in [Gmail] folder
                Set gmailFolder = FindFolderByName(rootFolder, "[Gmail]")
                If Not gmailFolder Is Nothing Then
                    Set FindStandardFolder = FindFolderByName(gmailFolder, "Sent Mail")
                End If
            Else
                ' Outlook: Look for "Sent Items" at root level
                Set FindStandardFolder = FindFolderByName(rootFolder, "Sent Items")
            End If
            
        Case "Deleted Items"
            If isGmail Then
                ' Gmail: Look for "Trash" in [Gmail] folder
                Set gmailFolder = FindFolderByName(rootFolder, "[Gmail]")
                If Not gmailFolder Is Nothing Then
                    Set FindStandardFolder = FindFolderByName(gmailFolder, "Trash")
                End If
            Else
                ' Outlook: Look for "Deleted Items" at root level
                Set FindStandardFolder = FindFolderByName(rootFolder, "Deleted Items")
            End If
            
        Case Else
            Set FindStandardFolder = Nothing
    End Select
    
    Exit Function
    
ErrorHandler:
    WriteLog "ERROR in FindStandardFolder: " & Err.Description
    Set FindStandardFolder = Nothing
End Function

' Process folder with standardized name for JSON file
Private Sub ProcessFolderWithStandardName(folder As Outlook.folder, standardName As String, maxEmails As Long)
    On Error GoTo ErrorHandler
    
    WriteLog "Processing folder '" & folder.Name & "' as '" & standardName & "'"
    
    ' Sort items by received time (most recent first)
    Dim items As Outlook.items
    Set items = folder.items
    items.Sort "[ReceivedTime]", True
    
    ' Create folder-specific JSON filename using standard name
    Dim folderJsonName As String
    folderJsonName = GetFolderJsonName(standardName)
    
    ' Load existing JSON if it exists
    Dim existingJsonPath As String
    Dim existingEmails As Object
    Set existingEmails = CreateObject("Scripting.Dictionary")
    
    existingJsonPath = GetOutputFolder() & folderJsonName
    
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
    jsonContent = jsonContent & "  ""folder_name"": """ & standardName & """," & vbCrLf
    jsonContent = jsonContent & "  ""actual_folder_name"": """ & folder.Name & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_path"": """ & EscapeJson(folder.FolderPath) & """," & vbCrLf
    jsonContent = jsonContent & "  ""total_items"": " & folder.items.Count & "," & vbCrLf
    jsonContent = jsonContent & "  ""emails"": [" & vbCrLf
    
    emailCount = 0
    processedCount = 0
    
    ' Process emails if any exist
    If folder.items.Count > 0 Then
        Dim item As Object
        For Each item In items
            If processedCount >= maxEmails Then Exit For
            processedCount = processedCount + 1
            
            If TypeOf item Is Outlook.mailItem Then
                Dim mailItem As Outlook.mailItem
                Set mailItem = item
                
                ' Generate email hash for unique identification
                Dim emailHash As String
                
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
                
                ' Build JSON entry for this email (simplified version)
                If emailCount > 0 Then jsonContent = jsonContent & "," & vbCrLf
                
                jsonContent = jsonContent & "    {" & vbCrLf
                jsonContent = jsonContent & "      ""index"": " & (emailCount + 1) & "," & vbCrLf
                jsonContent = jsonContent & "      ""hash"": """ & emailHash & """," & vbCrLf
                jsonContent = jsonContent & "      ""folder"": """ & standardName & """," & vbCrLf
                jsonContent = jsonContent & "      ""subject"": """ & EscapeJson(mailItem.Subject) & """," & vbCrLf
                jsonContent = jsonContent & "      ""sender_email"": """ & EscapeJson(mailItem.SenderEmailAddress) & """," & vbCrLf
                jsonContent = jsonContent & "      ""received_time"": """ & Format(mailItem.ReceivedTime, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
                jsonContent = jsonContent & "      ""unread"": " & LCase(CStr(mailItem.UnRead)) & "," & vbCrLf
                jsonContent = jsonContent & "      ""importance"": " & mailItem.Importance & "," & vbCrLf
                jsonContent = jsonContent & "      ""flagged"": " & LCase(CStr(mailItem.FlagStatus = 2)) & "," & vbCrLf
                jsonContent = jsonContent & "      ""flag_request"": """ & EscapeJson(mailItem.FlagRequest) & """," & vbCrLf
                jsonContent = jsonContent & "      ""flag_due_by"": """ & Format(mailItem.FlagDueBy, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
                jsonContent = jsonContent & "      ""flag_status"": " & mailItem.FlagStatus & "," & vbCrLf
                jsonContent = jsonContent & "      ""categories"": """ & EscapeJson(mailItem.Categories) & """," & vbCrLf
                
                ' Extract full body content (no truncation)
                Dim bodyText As String
                bodyText = mailItem.Body
                jsonContent = jsonContent & "      ""body"": """ & EscapeJson(bodyText) & """," & vbCrLf
                
                ' Extract full HTML body content (no truncation)
                Dim htmlBody As String
                htmlBody = mailItem.htmlBody
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
                    ' Skip embedded images
                    If Not IsEmbeddedImage(attachment.fileName) Then
                        If attachmentIndex > 0 Then jsonContent = jsonContent & "," & vbCrLf
                        
                        Dim attachmentPath As String
                        Dim relativeAttachmentPath As String
                        Dim subjectFolderName As String
                        
                        relativeAttachmentPath = "data/" & subjectFolderName & "/" & attachment.fileName
                        attachmentPath = GetAttachmentsFolder() & subjectFolderName & "\" & attachment.fileName
                        
                        WriteLog "  Downloading attachment: " & attachment.fileName
                        
                        ' Ensure directory exists before saving
                        CreateDirectoryPath GetAttachmentsFolder() & subjectFolderName & "\"
                        
                        On Error Resume Next
                        attachment.SaveAsFile attachmentPath
                        If Err.Number = 0 Then
                            WriteLog "  Downloaded successfully: " & attachment.fileName
                        Else
                            WriteLog "  Failed to download: " & attachment.fileName & " (Error: " & Err.Description & ")"
                        End If
                        Err.Clear
                        On Error GoTo ErrorHandler
                        
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
    End If
    
    ' Close JSON structure
    jsonContent = jsonContent & vbCrLf & "  ]," & vbCrLf
    jsonContent = jsonContent & "  ""extracted_count"": " & emailCount & vbCrLf
    jsonContent = jsonContent & "}" & vbCrLf
    
    ' Write JSON file
    WriteLog "Writing JSON file: " & existingJsonPath
    
    Dim fileNum As Integer
    fileNum = FreeFile
    
    Open existingJsonPath For Output As #fileNum
    Print #fileNum, jsonContent
    Close #fileNum
    
    WriteLog "Processed " & emailCount & " emails for " & standardName
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in ProcessFolderWithStandardName: " & Err.Description
End Sub

' Create empty JSON file for missing folder
Private Sub CreateEmptyFolderJson(standardName As String)
    On Error GoTo ErrorHandler
    
    WriteLog "Creating empty JSON file for: " & standardName
    
    Dim folderJsonName As String
    folderJsonName = GetFolderJsonName(standardName)
    
    Dim jsonPath As String
    jsonPath = GetOutputFolder() & folderJsonName
    
    ' Build empty JSON structure
    Dim jsonContent As String
    jsonContent = "{" & vbCrLf
    jsonContent = jsonContent & "  ""timestamp"": """ & Format(Now, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_name"": """ & standardName & """," & vbCrLf
    jsonContent = jsonContent & "  ""actual_folder_name"": ""(not found)""," & vbCrLf
    jsonContent = jsonContent & "  ""folder_path"": ""/" & standardName & """," & vbCrLf
    jsonContent = jsonContent & "  ""total_items"": 0," & vbCrLf
    jsonContent = jsonContent & "  ""emails"": []," & vbCrLf
    jsonContent = jsonContent & "  ""extracted_count"": 0" & vbCrLf
    jsonContent = jsonContent & "}" & vbCrLf
    
    ' Write empty JSON file
    Dim fileNum As Integer
    fileNum = FreeFile
    
    Open jsonPath For Output As #fileNum
    Print #fileNum, jsonContent
    Close #fileNum
    
    WriteLog "Created empty JSON file: " & folderJsonName
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in CreateEmptyFolderJson: " & Err.Description
End Sub

' Get standardized folder name for consistent JSON files
Private Function GetStandardFolderName(actualFolderName As String) As String
    Dim folderName As String
    folderName = LCase(actualFolderName)
    
    ' Standardize folder names across Gmail and Outlook
    If folderName = "inbox" Then
        GetStandardFolderName = "Inbox"
    ElseIf folderName = "sent items" Or folderName = "sent mail" Then
        GetStandardFolderName = "Sent Items"
    ElseIf folderName = "deleted items" Or folderName = "trash" Then
        GetStandardFolderName = "Deleted Items"
    ElseIf folderName = "drafts" Then
        GetStandardFolderName = "Drafts"
    ElseIf folderName = "outbox" Then
        GetStandardFolderName = "Outbox"
    Else
        ' For other folders, use title case
        GetStandardFolderName = StrConv(actualFolderName, vbProperCase)
    End If
End Function

' Build JSON entry for an email
Private Function BuildEmailJsonEntry(mailItem As Outlook.MailItem, targetFolder As Outlook.Folder, standardFolderName As String, emailHash As String, subjectFolderName As String, msgFileName As String, emailIndex As Long) As String
    On Error GoTo ErrorHandler
    
    Dim emailJsonEntry As String
    emailJsonEntry = "    {" & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""index"": " & emailIndex & "," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""hash"": """ & emailHash & """," & vbCrLf
    
    ' Add Outlook identifiers for Python service
    Dim rawEntryId As String, rawMessageId As String, rawConversationId As String
    On Error Resume Next
    rawEntryId = mailItem.EntryID
    rawMessageId = mailItem.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x1035001E")
    rawConversationId = mailItem.ConversationID
    On Error GoTo ErrorHandler
    
    emailJsonEntry = emailJsonEntry & "      ""entry_id"": """ & EscapeJson(rawEntryId) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""message_id"": """ & EscapeJson(rawMessageId) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""conversation_id"": """ & EscapeJson(rawConversationId) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""folder"": """ & EscapeJson(standardFolderName) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""folder_path"": """ & EscapeJson(targetFolder.FolderPath) & """," & vbCrLf
    
    emailJsonEntry = emailJsonEntry & "      ""subject"": """ & EscapeJson(mailItem.Subject) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""sender_name"": """ & EscapeJson(mailItem.SenderName) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""sender_email"": """ & EscapeJson(mailItem.SenderEmailAddress) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""received_time"": """ & Format(mailItem.ReceivedTime, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""sent_on"": """ & Format(mailItem.SentOn, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""size"": " & mailItem.Size & "," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""importance"": " & mailItem.Importance & "," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""unread"": " & LCase(CStr(mailItem.UnRead)) & "," & vbCrLf
    
    ' Extract flag information
    Dim flagged As Boolean
    Dim flagRequest As String
    Dim flagDueBy As String
    Dim flagStatus As Integer
    
    ' Get flag properties with error handling
    On Error Resume Next
    flagRequest = mailItem.FlagRequest
    flagDueBy = Format(mailItem.FlagDueBy, "yyyy-mm-dd hh:nn:ss")
    flagStatus = mailItem.FlagStatus
    
    ' Determine if email is flagged (FlagStatus = 2 means flagged)
    flagged = (Len(flagRequest) > 0 And flagRequest <> "") Or (flagStatus = 2)
    
    On Error GoTo ErrorHandler
    
    emailJsonEntry = emailJsonEntry & "      ""flagged"": " & LCase(CStr(flagged)) & "," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""flag_request"": """ & EscapeJson(flagRequest) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""flag_due_by"": """ & flagDueBy & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""flag_status"": " & flagStatus & "," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""categories"": """ & EscapeJson(mailItem.Categories) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""msg_file"": """ & EscapeJson("data/" & subjectFolderName & "/" & msgFileName) & """," & vbCrLf
            
    ' Extract full body content (no truncation)
    Dim bodyText As String
    bodyText = mailItem.Body
    emailJsonEntry = emailJsonEntry & "      ""body"": """ & EscapeJson(bodyText) & """," & vbCrLf
            
    ' Extract full HTML body content (no truncation)
    Dim htmlBody As String
    htmlBody = mailItem.htmlBody
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
            attachmentPath = GetAttachmentsFolder() & subjectFolderName & "\" & attachment.fileName
            
            WriteLog "  Downloading attachment: " & attachment.fileName
            
            ' Ensure directory exists before saving
            CreateDirectoryPath GetAttachmentsFolder() & subjectFolderName & "\"
            
            On Error Resume Next
            attachment.SaveAsFile attachmentPath
            If Err.Number = 0 Then
                WriteLog "  Downloaded successfully: " & attachment.fileName
            Else
                WriteLog "  Failed to download: " & attachment.fileName & " (Error: " & Err.Description & ")"
            End If
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
    
    BuildEmailJsonEntry = emailJsonEntry
    Exit Function
    
ErrorHandler:
    WriteLog "ERROR in BuildEmailJsonEntry: " & Err.Description
    BuildEmailJsonEntry = ""
End Function

' Save folder-specific JSON file (replaces SaveCompleteJsonFile for multi-file structure)
Private Sub SaveFolderSpecificJsonFile(emailDict As Object, folder As Outlook.Folder, standardFolderName As String, folderJsonName As String)
    On Error GoTo ErrorHandler
    
    Dim jsonContent As String
    Dim emailCount As Long
    
    ' Build complete JSON structure for this specific folder
    jsonContent = "{" & vbCrLf
    jsonContent = jsonContent & "  ""timestamp"": """ & Format(Now, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_name"": """ & standardFolderName & """," & vbCrLf
    jsonContent = jsonContent & "  ""actual_folder_name"": """ & folder.Name & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_path"": """ & EscapeJson(folder.FolderPath) & """," & vbCrLf
    jsonContent = jsonContent & "  ""total_items"": " & folder.Items.Count & "," & vbCrLf
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
    
    ' Write to folder-specific file
    Dim fileName As String
    Dim fileNum As Integer
    
    fileName = GetOutputFolder() & folderJsonName
    fileNum = FreeFile
    Open fileName For Output As #fileNum
    Print #fileNum, jsonContent
    Close #fileNum
    
    WriteLog "Folder-specific JSON updated: " & folderJsonName & " with " & emailCount & " total emails"
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in SaveFolderSpecificJsonFile: " & Err.Description
End Sub

