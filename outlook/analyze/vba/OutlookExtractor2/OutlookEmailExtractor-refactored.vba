Option Explicit

' Outlook Email Extractor - Refactored Version
' Focused on two main functions for the production IRM account:
' 1. Download all emails & attachments from all available IRM folders
' 2. Event monitoring to detect new emails

' ===== CONFIGURATION =====
Public Const TARGET_ACCOUNT As String = "IRM-Standardisation-Office"

' ===== MODULE-LEVEL VARIABLES =====
Private emailEventHandler As EmailEventHandler

' ===== UTILITY FUNCTIONS =====

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

' Find target IRM store
Private Function FindIRMStore() As Outlook.Store
    On Error GoTo ErrorHandler
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.NameSpace
    Dim store As Outlook.Store
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    
    WriteLog "Searching for IRM account: " & TARGET_ACCOUNT
    
    For Each store In olNamespace.Stores
        If InStr(UCase(store.DisplayName), UCase(TARGET_ACCOUNT)) > 0 Then
            Set FindIRMStore = store
            WriteLog "Found IRM store: " & store.DisplayName
            Exit Function
        End If
    Next store
    
    ' If we get here, IRM account was not found
    WriteLog "ERROR: IRM account not found. Available stores:"
    For Each store In olNamespace.Stores
        WriteLog "  - " & store.DisplayName
    Next store
    
    Set FindIRMStore = Nothing
    Exit Function
    
ErrorHandler:
    WriteLog "ERROR in FindIRMStore: " & Err.Description
    Set FindIRMStore = Nothing
End Function

' Helper function to find folder by name (improved for Gmail)
Private Function FindFolderByName(parentFolder As Outlook.Folder, folderName As String) As Outlook.Folder
    On Error GoTo ErrorHandler
    
    ' First try direct match
    Dim folder As Outlook.Folder
    For Each folder In parentFolder.Folders
        If LCase(folder.Name) = LCase(folderName) Then
            Set FindFolderByName = folder
            Exit Function
        End If
    Next folder
    
    ' If not found, try searching in subfolders (Gmail often has nested structure)
    For Each folder In parentFolder.Folders
        If folder.Folders.Count > 0 Then
            Dim subfolder As Outlook.Folder
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

' Get all available IRM folders
Private Function GetAllIRMFolders() As Collection
    On Error GoTo ErrorHandler
    
    Dim allFolders As New Collection
    Dim irmStore As Outlook.Store
    Dim rootFolder As Outlook.Folder
    
    ' Get IRM store
    Set irmStore = FindIRMStore()
    If irmStore Is Nothing Then
        WriteLog "ERROR: No IRM store found for folder discovery"
        Set GetAllIRMFolders = allFolders
        Exit Function
    End If
    
    Set rootFolder = irmStore.GetRootFolder()
    
    ' Add standard folders if they exist
    AddFolderIfExists allFolders, rootFolder, "Inbox"
    AddFolderIfExists allFolders, rootFolder, "Sent Items"
    AddFolderIfExists allFolders, rootFolder, "Sent Mail"
    AddFolderIfExists allFolders, rootFolder, "Deleted Items"
    AddFolderIfExists allFolders, rootFolder, "Trash"
    AddFolderIfExists allFolders, rootFolder, "Drafts"
    AddFolderIfExists allFolders, rootFolder, "Outbox"
    
    ' For Gmail accounts, check [Gmail] subfolder
    Dim gmailFolder As Outlook.Folder
    Set gmailFolder = FindFolderByName(rootFolder, "[Gmail]")
    If Not gmailFolder Is Nothing Then
        WriteLog "Found [Gmail] parent folder, checking subfolders..."
        AddFolderIfExists allFolders, gmailFolder, "Trash"
        AddFolderIfExists allFolders, gmailFolder, "Sent Mail"
        AddFolderIfExists allFolders, gmailFolder, "Drafts"
        AddFolderIfExists allFolders, gmailFolder, "Important"
        AddFolderIfExists allFolders, gmailFolder, "Starred"
    End If
    
    Set GetAllIRMFolders = allFolders
    WriteLog "Total IRM folders found: " & allFolders.Count
    Exit Function
    
ErrorHandler:
    WriteLog "ERROR in GetAllIRMFolders: " & Err.Description
    Set GetAllIRMFolders = allFolders
End Function

' Helper to add folder if it exists
Private Sub AddFolderIfExists(folderCollection As Collection, parentFolder As Outlook.Folder, folderName As String)
    On Error Resume Next
    
    Dim folder As Outlook.Folder
    Set folder = FindFolderByName(parentFolder, folderName)
    If Not folder Is Nothing Then
        folderCollection.Add folder, folder.Name & "_" & folder.FolderPath ' Use unique key
        WriteLog "Added folder to processing list: " & folder.Name & " (Items: " & folder.Items.Count & ")"
    End If
    
    On Error GoTo 0
End Sub

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
    
    ' Final fallback: Create hash from essential properties
    Dim hashInput As String
    hashInput = ""
    
    ' Include subject, sender, received time, and size
    On Error Resume Next
    hashInput = hashInput & mailItem.Subject & "|"
    hashInput = hashInput & mailItem.SenderEmailAddress & "|"
    hashInput = hashInput & CStr(mailItem.ReceivedTime) & "|"
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

' ===== MAIN FUNCTION 1: DOWNLOAD ALL EMAILS & ATTACHMENTS =====

' Main function to download all emails and attachments from all IRM folders
Public Sub DownloadAllIRMEmails()
    On Error GoTo ErrorHandler
    
    WriteLog "=== Starting IRM Email Download ==="
    WriteLog "Target account: " & TARGET_ACCOUNT
    WriteLog "Output folder: " & GetOutputFolder()
    WriteLog "Attachments folder: " & GetAttachmentsFolder()
    
    ' Create directories if they don't exist
    CreateDirectoryPath GetOutputFolder()
    CreateDirectoryPath GetAttachmentsFolder()
    
    ' Get all IRM folders
    Dim irmFolders As Collection
    Set irmFolders = GetAllIRMFolders()
    
    If irmFolders.Count = 0 Then
        WriteLog "ERROR: No IRM folders found for processing"
        Exit Sub
    End If
    
    WriteLog "Found " & irmFolders.Count & " IRM folders to process"
    
    ' Process emails from each folder
    Dim folder As Outlook.Folder
    Dim i As Integer
    
    For i = 1 To irmFolders.Count
        Set folder = irmFolders(i)
        WriteLog "Processing folder: " & folder.Name & " (Path: " & folder.FolderPath & ", Items: " & folder.Items.Count & ")"
        
        If folder.Items.Count > 0 Then
            ' Process up to 100 emails per folder to avoid overwhelming the system
            ProcessFolderEmails folder, 100
        Else
            WriteLog "  Skipping empty folder: " & folder.Name
            ' Still create empty JSON file for consistency
            CreateEmptyFolderJson folder.Name
        End If
        
        WriteLog "Completed processing folder: " & folder.Name
    Next i
    
    WriteLog "=== IRM Email Download Completed ==="
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in DownloadAllIRMEmails: " & Err.Description
End Sub

' Process emails from a specific folder
Private Sub ProcessFolderEmails(folder As Outlook.Folder, maxEmails As Long)
    On Error GoTo ErrorHandler
    
    WriteLog "Processing up to " & maxEmails & " emails from " & folder.Name
    
    ' Sort items by received time (most recent first)
    Dim items As Outlook.Items
    Set items = folder.Items
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
    jsonContent = jsonContent & "  ""total_items"": " & folder.Items.Count & "," & vbCrLf
    jsonContent = jsonContent & "  ""emails"": [" & vbCrLf
    
    emailCount = 0
    processedCount = 0
    
    Dim item As Object
    For Each item In items
        If processedCount >= maxEmails Then Exit For
        processedCount = processedCount + 1
        
        If TypeOf item Is Outlook.MailItem Then
            Dim mailItem As Outlook.MailItem
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
            
            ' Create folder structure for this email
            Dim subjectFolderName As String
            Dim subjectAttachmentFolder As String
            Dim msgFileName As String
            Dim msgFilePath As String
            
            ' Use hash-only folder names for simplicity and path length safety
            subjectFolderName = emailHash
            subjectAttachmentFolder = GetAttachmentsFolder() & subjectFolderName & "\"
            msgFileName = emailHash & ".msg"
            msgFilePath = subjectAttachmentFolder & msgFileName
            
            ' Create folder and save .msg file
            WriteLog "    Creating folder and saving .msg file..."
            CreateDirectoryPath subjectAttachmentFolder
            
            On Error Resume Next
            Err.Clear
            mailItem.SaveAs msgFilePath, olMSG
            If Err.Number = 0 Then
                WriteLog "    Saved .msg file: " & msgFileName
            Else
                WriteLog "    WARNING: Failed to save .msg file: " & Err.Description & " (Error: " & Err.Number & ")"
                WriteLog "    Continuing with JSON processing despite MSG save failure"
            End If
            Err.Clear
            On Error GoTo ErrorHandler
            
            ' Build JSON entry for this email
            If emailCount > 0 Then jsonContent = jsonContent & "," & vbCrLf
            
            jsonContent = jsonContent & BuildEmailJsonEntry(mailItem, folder, emailHash, subjectFolderName, msgFileName, emailCount + 1)
            
            emailCount = emailCount + 1
        End If
        
NextItem:
    Next item
    
    ' Close JSON structure
    jsonContent = jsonContent & vbCrLf & "  ]," & vbCrLf
    jsonContent = jsonContent & "  ""extracted_count"": " & emailCount & vbCrLf
    jsonContent = jsonContent & "}" & vbCrLf
    
    ' Write JSON file with folder-specific name
    WriteLog "Writing JSON file to: " & existingJsonPath
    
    Dim fileNum As Integer
    fileNum = FreeFile
    
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
    
    WriteLog "Processing complete. Processed " & emailCount & " emails total (from " & processedCount & " checked)"
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in ProcessFolderEmails: " & Err.Description & " (Error Number: " & Err.Number & ")"
End Sub

' Build JSON entry for an email
Private Function BuildEmailJsonEntry(mailItem As Outlook.MailItem, folder As Outlook.Folder, emailHash As String, subjectFolderName As String, msgFileName As String, emailIndex As Long) As String
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
    emailJsonEntry = emailJsonEntry & "      ""folder"": """ & EscapeJson(folder.Name) & """," & vbCrLf
    emailJsonEntry = emailJsonEntry & "      ""folder_path"": """ & EscapeJson(folder.FolderPath) & """," & vbCrLf
    
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
            
            WriteLog "    Downloading attachment: " & attachment.fileName
            
            ' Ensure directory exists before saving
            CreateDirectoryPath GetAttachmentsFolder() & subjectFolderName & "\"
            
            On Error Resume Next
            attachment.SaveAsFile attachmentPath
            If Err.Number = 0 Then
                WriteLog "    Downloaded successfully: " & attachment.fileName
            Else
                WriteLog "    Failed to download: " & attachment.fileName & " (Error: " & Err.Description & ")"
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

' Create empty JSON file for missing folder
Private Sub CreateEmptyFolderJson(folderName As String)
    On Error GoTo ErrorHandler
    
    WriteLog "Creating empty JSON file for: " & folderName
    
    Dim folderJsonName As String
    folderJsonName = GetFolderJsonName(folderName)
    
    Dim jsonPath As String
    jsonPath = GetOutputFolder() & folderJsonName
    
    ' Build empty JSON structure
    Dim jsonContent As String
    jsonContent = "{" & vbCrLf
    jsonContent = jsonContent & "  ""timestamp"": """ & Format(Now, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_name"": """ & folderName & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_path"": ""/" & folderName & """," & vbCrLf
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

' ===== MAIN FUNCTION 2: EVENT MONITORING =====

' Start event monitoring for new emails
Public Sub StartEventMonitoring()
    On Error GoTo ErrorHandler
    
    WriteLog "=== Starting IRM Event Monitoring ==="
    WriteLog "Target account: " & TARGET_ACCOUNT
    WriteLog "Output folder: " & GetOutputFolder()
    WriteLog "Data folder: " & GetAttachmentsFolder()
    
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
    
    WriteLog "=== EVENT: Processing new email in folder: " & targetFolder.Name & " ==="
    
    ' Create folder-specific JSON filename
    Dim folderJsonName As String
    Dim existingJsonPath As String
    Dim existingEmails As Object
    Set existingEmails = CreateObject("Scripting.Dictionary")
    
    folderJsonName = GetFolderJsonName(targetFolder.Name)
    existingJsonPath = GetOutputFolder() & folderJsonName
    
    WriteLog "Event processing - JSON file: " & folderJsonName
    
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
    emailJsonEntry = BuildEmailJsonEntry(mailItem, targetFolder, emailHash, subjectFolderName, msgFileName, existingEmails.Count + 1)
    
    ' Add this email to the existing emails dictionary
    existingEmails(emailHash) = emailJsonEntry
    
    ' Save the updated folder-specific JSON file
    SaveFolderSpecificJsonFile existingEmails, targetFolder, folderJsonName
    
    WriteLog "  Event: New email processed and JSON updated!"
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in ProcessSingleNewEmail: " & Err.Description
End Sub

' Save folder-specific JSON file
Private Sub SaveFolderSpecificJsonFile(emailDict As Object, folder As Outlook.Folder, folderJsonName As String)
    On Error GoTo ErrorHandler
    
    Dim jsonContent As String
    Dim emailCount As Long
    
    ' Build complete JSON structure for this specific folder
    jsonContent = "{" & vbCrLf
    jsonContent = jsonContent & "  ""timestamp"": """ & Format(Now, "yyyy-mm-dd hh:nn:ss") & """," & vbCrLf
    jsonContent = jsonContent & "  ""folder_name"": """ & folder.Name & """," & vbCrLf
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

' ===== TEST AND UTILITY FUNCTIONS =====

' Simple test function to verify macro is working
Public Sub TestMacro()
    Debug.Print "=== IRM MACRO TEST STARTED ==="
    WriteLog "Testing IRM-focused macro functionality..."
    
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
    
    ' List all stores and check for IRM account
    Dim store As Outlook.Store
    Dim storeIndex As Integer
    Dim foundIRM As Boolean
    
    storeIndex = 1
    foundIRM = False
    
    For Each store In olNamespace.Stores
        Debug.Print "Store " & storeIndex & ": " & store.DisplayName
        
        ' Check if this store matches IRM account
        If InStr(UCase(store.DisplayName), UCase(TARGET_ACCOUNT)) > 0 Then
            Debug.Print "  --> IRM ACCOUNT FOUND!"
            foundIRM = True
        End If
        
        storeIndex = storeIndex + 1
    Next store
    
    If foundIRM Then
        Debug.Print "IRM account test: SUCCESS"
        
        ' Test the IRM store finder
        Dim testStore As Outlook.Store
        Set testStore = FindIRMStore()
        If Not testStore Is Nothing Then
            Debug.Print "FindIRMStore test: SUCCESS - Found " & testStore.DisplayName
            
            ' Test folder discovery
            Dim testFolders As Collection
            Set testFolders = GetAllIRMFolders()
            Debug.Print "Folder discovery test: Found " & testFolders.Count & " folders"
        Else
            Debug.Print "FindIRMStore test: FAILED"
        End If
    Else
        Debug.Print "IRM account test: FAILED - Account not found"
    End If
    
    WriteLog "Test completed successfully"
    Debug.Print "=== IRM MACRO TEST COMPLETED ==="
    Exit Sub
    
ErrorHandler:
    Debug.Print "ERROR in TestMacro: " & Err.Description
    WriteLog "ERROR in TestMacro: " & Err.Description
End Sub

' Get status of current operations
Public Sub GetStatus()
    WriteLog "=== IRM EMAIL EXTRACTOR STATUS ==="
    WriteLog "Target account: " & TARGET_ACCOUNT
    WriteLog "Output folder: " & GetOutputFolder()
    WriteLog "Attachments folder: " & GetAttachmentsFolder()
    
    ' Check if event monitoring is active
    If Not emailEventHandler Is Nothing Then
        If emailEventHandler.IsMonitoringActive() Then
            WriteLog "Event monitoring: ACTIVE"
        Else
            WriteLog "Event monitoring: INACTIVE"
        End If
    Else
        WriteLog "Event monitoring: INACTIVE"
    End If
    
    ' Check IRM connection
    Dim irmStore As Outlook.Store
    Set irmStore = FindIRMStore()
    If Not irmStore Is Nothing Then
        WriteLog "IRM connection: OK - " & irmStore.DisplayName
        
        ' Get folder count
        Dim folders As Collection
        Set folders = GetAllIRMFolders()
        WriteLog "Available IRM folders: " & folders.Count
    Else
        WriteLog "IRM connection: FAILED"
    End If
    
    WriteLog "=== STATUS CHECK COMPLETED ==="
End Sub
