Option Explicit

' JSON Manager Module - FIXED VERSION
' Handles JSON file creation, rotation, and management with improved parsing

' FIXED: Load existing emails from JSON file into dictionary for comparison
Public Sub LoadExistingEmailsFromJson(jsonPath As String, emailDict As Object)
    On Error GoTo ErrorHandler
    
    WriteLog "DEBUG: Starting to load existing emails from: " & jsonPath
    
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
    
    WriteLog "DEBUG: Loaded file content, length: " & Len(fileContent) & " characters"
    
    ' Simple extraction of email entries based on "hash" field
    Dim startPos As Long
    Dim hashStart As Long
    Dim hashEnd As Long
    Dim emailHash As String
    Dim emailEntry As String
    Dim emailsProcessed As Long
    
    startPos = 1
    emailsProcessed = 0
    
    Do
        ' Find start of email object by looking for "hash": pattern
        startPos = InStr(startPos, fileContent, """hash"":")
        If startPos = 0 Then 
            WriteLog "DEBUG: No more hash fields found"
            Exit Do
        End If
        
        WriteLog "DEBUG: Found hash field at position: " & startPos
        
        ' Extract hash value
        hashStart = InStr(startPos, fileContent, """") + 1
        hashStart = InStr(hashStart, fileContent, """") + 1
        hashEnd = InStr(hashStart, fileContent, """") - 1
        
        If hashEnd > hashStart Then
            emailHash = Mid(fileContent, hashStart, hashEnd - hashStart + 1)
            WriteLog "DEBUG: Extracted hash: [" & emailHash & "]"
            
            ' Validate that we have a proper hash (should be 6 digits)
            If Len(emailHash) = 6 And IsNumeric(emailHash) Then
                ' Find the start of this email object (go backwards to find opening brace)
                Dim objStart As Long
                objStart = startPos
                
                ' Look for the opening brace that starts this email object
                Do While objStart > 1
                    objStart = objStart - 1
                    If Mid(fileContent, objStart, 1) = "{" Then
                        ' Check if this is the start of an email object (not nested)
                        Dim prevChar As String
                        If objStart > 1 Then
                            prevChar = Mid(fileContent, objStart - 1, 1)
                        Else
                            prevChar = ""
                        End If
                        
                        If prevChar = vbLf Or prevChar = " " Or objStart = 1 Then
                            Exit Do
                        End If
                    End If
                Loop
                
                ' Find the end of this email object (find matching closing brace)
                Dim objEnd As Long
                Dim braceCount As Long
                Dim currentChar As String
                objEnd = objStart
                braceCount = 0
                
                Do While objEnd <= Len(fileContent)
                    currentChar = Mid(fileContent, objEnd, 1)
                    If currentChar = "{" Then
                        braceCount = braceCount + 1
                    ElseIf currentChar = "}" Then
                        braceCount = braceCount - 1
                        If braceCount = 0 Then Exit Do
                    End If
                    objEnd = objEnd + 1
                Loop
                
                If braceCount = 0 And objEnd <= Len(fileContent) Then
                    ' Extract the full email entry
                    emailEntry = Mid(fileContent, objStart, objEnd - objStart + 1)
                    
                    ' Store in dictionary
                    emailDict(emailHash) = emailEntry
                    emailsProcessed = emailsProcessed + 1
                    
                    WriteLog "DEBUG: Successfully loaded email with hash: " & emailHash & " (Entry length: " & Len(emailEntry) & ")"
                Else
                    WriteLog "DEBUG: Failed to find matching closing brace for hash: " & emailHash
                End If
            Else
                WriteLog "DEBUG: Invalid hash format: [" & emailHash & "] (length: " & Len(emailHash) & ")"
            End If
        Else
            WriteLog "DEBUG: Failed to extract hash value at position: " & startPos
        End If
        
        startPos = startPos + 1
        
        ' Safety check to prevent infinite loops
        If emailsProcessed > 1000 Then
            WriteLog "WARNING: Processed 1000 emails, stopping to prevent infinite loop"
            Exit Do
        End If
        
    Loop
    
    WriteLog "Successfully loaded " & emailDict.Count & " existing emails from JSON"
    WriteLog "DEBUG: Emails processed in loop: " & emailsProcessed
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR loading existing JSON: " & Err.Description & " (Line: " & Erl & ")"
    WriteLog "DEBUG: Error occurred while processing. Emails loaded so far: " & emailDict.Count
End Sub

' Save complete JSON file with all emails (existing + new) - with rotation management
Public Sub SaveCompleteJsonFile(emailDict As Object, folder As Outlook.Folder)
    On Error GoTo ErrorHandler
    
    ' Check if we need to rotate files before saving
    If ENABLE_JSON_ROTATION And emailDict.Count >= MAX_EMAILS_PER_FILE Then
        WriteLog "JSON file size limit reached (" & emailDict.Count & " emails). Performing rotation..."
        RotateJsonFiles emailDict, folder
        Exit Sub
    End If
    
    SaveJsonToFile emailDict, folder, "emails.json", "current"
    
    Exit Sub
    
ErrorHandler:
    LogError "SaveCompleteJsonFile", Err.Description, Err.Number
End Sub

' Save JSON to a specific file
Public Sub SaveJsonToFile(emailDict As Object, folder As Outlook.Folder, fileName As String, fileType As String)
    On Error GoTo ErrorHandler
    
    WriteLog "DEBUG: Saving JSON file: " & fileName & " with " & emailDict.Count & " emails"
    
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
        
        ' Progress logging for large files
        If emailCount Mod 10 = 0 Then
            WriteLog "DEBUG: Added " & emailCount & " emails to JSON content"
        End If
    Next emailHash
    
    ' Close JSON structure
    jsonContent = jsonContent & vbCrLf & "  ]," & vbCrLf
    jsonContent = jsonContent & "  ""extracted_count"": " & emailCount & vbCrLf
    jsonContent = jsonContent & "}" & vbCrLf
    
    WriteLog "DEBUG: Built JSON content, total length: " & Len(jsonContent) & " characters"
    
    ' Write to file
    Dim fullPath As String
    Dim fileNum As Integer
    
    fullPath = GetOutputFolder() & fileName
    fileNum = FreeFile
    
    WriteLog "DEBUG: Writing to file: " & fullPath
    
    Open fullPath For Output As #fileNum
    Print #fileNum, jsonContent
    Close #fileNum
    
    WriteLog "JSON file '" & fileName & "' updated with " & emailCount & " emails"
    WriteLog "DEBUG: File written successfully, size: " & FileLen(fullPath) & " bytes"
    
    Exit Sub
    
ErrorHandler:
    LogError "SaveJsonToFile", Err.Description, Err.Number
End Sub

' Rotate JSON files when they get too large
Public Sub RotateJsonFiles(emailDict As Object, folder As Outlook.Folder)
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
    LogError "RotateJsonFiles", Err.Description, Err.Number
End Sub

' Create an index file that lists all JSON files for easy navigation
Public Sub CreateJsonIndexFile()
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
    LogError "CreateJsonIndexFile", Err.Description, Err.Number
End Sub 