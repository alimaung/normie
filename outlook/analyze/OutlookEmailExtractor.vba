Option Explicit

' Outlook Email Extractor VBA Macro
' This macro runs continuously and extracts emails to JSON files every X minutes
' Place this in Outlook VBA (Alt+F11 -> Insert -> Module)

' Global variables for polling
Private WithEvents pollTimer As Outlook.Application
Private Const POLL_INTERVAL_MINUTES As Integer = 5
Private Const OUTPUT_FOLDER As String = "C:\temp\outlook_extract\"
Private Const MAX_EMAILS_PER_ACCOUNT As Integer = 50

' Main entry point - call this to start polling
Public Sub StartEmailPolling()
    Debug.Print "Starting email polling every " & POLL_INTERVAL_MINUTES & " minutes..."
    Debug.Print "Output folder: " & OUTPUT_FOLDER
    
    ' Create output folder if it doesn't exist
    If Dir(OUTPUT_FOLDER, vbDirectory) = "" Then
        MkDir OUTPUT_FOLDER
    End If
    
    ' Run extraction immediately
    ExtractAllEmails
    
    ' Schedule next run
    Application.OnTime Now + TimeValue("00:" & Format(POLL_INTERVAL_MINUTES, "00") & ":00"), "ExtractAllEmails"
    
    Debug.Print "Polling started. To stop, run StopEmailPolling"
End Sub

' Stop the polling
Public Sub StopEmailPolling()
    On Error Resume Next
    Application.OnTime Now + TimeValue("00:" & Format(POLL_INTERVAL_MINUTES, "00") & ":00"), "ExtractAllEmails", , False
    Debug.Print "Polling stopped."
End Sub

' Main extraction routine
Public Sub ExtractAllEmails()
    On Error GoTo ErrorHandler
    
    Debug.Print "=== Email Extraction Started: " & Now & " ==="
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.Namespace
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    
    ' Extract from all stores (accounts)
    Dim store As Outlook.Store
    For Each store In olNamespace.Stores
        Debug.Print "Processing store: " & store.DisplayName
        ExtractEmailsFromStore store
    Next store
    
    ' Create status file with timestamp
    CreateStatusFile
    
    Debug.Print "=== Email Extraction Completed: " & Now & " ==="
    
    ' Schedule next run
    Application.OnTime Now + TimeValue("00:" & Format(POLL_INTERVAL_MINUTES, "00") & ":00"), "ExtractAllEmails"
    
    Exit Sub
    
ErrorHandler:
    Debug.Print "Error in ExtractAllEmails: " & Err.Description
    ' Continue polling even if there's an error
    Application.OnTime Now + TimeValue("00:" & Format(POLL_INTERVAL_MINUTES, "00") & ":00"), "ExtractAllEmails"
End Sub

' Extract emails from a specific store
Private Sub ExtractEmailsFromStore(store As Outlook.Store)
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
        ExtractEmailsFromFolder inboxFolder, storeName & "_inbox"
    End If
    
    ' Extract from Sent Items
    Dim sentFolder As Outlook.Folder
    Set sentFolder = FindFolderByName(rootFolder, "Sent Items")
    
    If Not sentFolder Is Nothing Then
        Debug.Print "  Extracting from Sent Items: " & sentFolder.Items.Count & " items"
        ExtractEmailsFromFolder sentFolder, storeName & "_sent"
    End If
    
    Exit Sub
    
ErrorHandler:
    Debug.Print "Error extracting from store " & store.DisplayName & ": " & Err.Description
End Sub

' Extract emails from a specific folder
Private Sub ExtractEmailsFromFolder(folder As Outlook.Folder, filePrefix As String)
    On Error GoTo ErrorHandler
    
    Dim jsonContent As String
    Dim emailCount As Integer
    Dim timestamp As String
    
    timestamp = Format(Now, "yyyy-mm-dd_hh-nn-ss")
    
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
            attachmentIndex = 0
            
            Dim attachment As Outlook.attachment
            For Each attachment In mailItem.Attachments
                If attachmentIndex > 0 Then jsonContent = jsonContent & "," & vbCrLf
                jsonContent = jsonContent & "        {" & vbCrLf
                jsonContent = jsonContent & "          ""filename"": """ & EscapeJson(attachment.FileName) & """," & vbCrLf
                jsonContent = jsonContent & "          ""size"": " & attachment.Size & "," & vbCrLf
                jsonContent = jsonContent & "          ""type"": " & attachment.Type & vbCrLf
                jsonContent = jsonContent & "        }"
                attachmentIndex = attachmentIndex + 1
                If attachmentIndex >= 10 Then Exit For ' Limit attachments
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
    
    ' Write to file
    Dim fileName As String
    fileName = OUTPUT_FOLDER & filePrefix & "_" & timestamp & ".json"
    
    Dim fileNum As Integer
    fileNum = FreeFile
    Open fileName For Output As #fileNum
    Print #fileNum, jsonContent
    Close #fileNum
    
    Debug.Print "    Exported " & emailCount & " emails to: " & fileName
    
    Exit Sub
    
ErrorHandler:
    Debug.Print "Error extracting emails from folder: " & Err.Description
End Sub

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

' Create status file with current timestamp
Private Sub CreateStatusFile()
    Dim statusFile As String
    statusFile = OUTPUT_FOLDER & "last_extraction.txt"
    
    Dim fileNum As Integer
    fileNum = FreeFile
    Open statusFile For Output As #fileNum
    Print #fileNum, "Last extraction: " & Format(Now, "yyyy-mm-dd hh:nn:ss")
    Print #fileNum, "Next extraction: " & Format(Now + TimeValue("00:" & Format(POLL_INTERVAL_MINUTES, "00") & ":00"), "yyyy-mm-dd hh:nn:ss")
    Close #fileNum
End Sub

' Manual extraction function for testing
Public Sub ExtractEmailsOnce()
    Debug.Print "Starting one-time email extraction..."
    ExtractAllEmails
    Debug.Print "One-time extraction completed."
End Sub 