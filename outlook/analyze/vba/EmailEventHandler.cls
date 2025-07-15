Option Explicit

' Email Event Handler Class
' This class handles WithEvents for Outlook email monitoring

' Event-driven variables
Private WithEvents olApp As Outlook.Application
Private WithEvents olInboxItems As Outlook.Items
Private WithEvents olDeletedItems As Outlook.Items
Private WithEvents olSentItems As Outlook.Items
Private WithEvents olDrafts As Outlook.Items
Private WithEvents olOutbox As Outlook.Items
Private targetInboxFolder As Outlook.Folder
Private targetDeletedFolder As Outlook.Folder
Private targetSentFolder As Outlook.Folder
Private targetDraftsFolder As Outlook.Folder
Private targetOutboxFolder As Outlook.Folder
Private isActive As Boolean

' Constants from main module
Private Const TARGET_ACCOUNT As String = "IRM-Standardisation-Office"
Private Const DEBUG_ACCOUNT As String = "microfilm.development@gmail.com"

' Account priority list - will try in order
Private Function GetAccountPriorityList() As String()
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

' Initialize the event handler
Public Function StartMonitoring() As Boolean
    On Error GoTo ErrorHandler
    
    WriteLog "Initializing email event handler..."
    
    ' Initialize Outlook Application
    Set olApp = Application
    
    ' Find target account and inbox
    Dim targetStore As Outlook.store
    Set targetStore = FindTargetStoreWithFallback()
    
    If targetStore Is Nothing Then
        WriteLog "ERROR: No target accounts found"
        StartMonitoring = False
        Exit Function
    End If
    
    ' Get root folder for all folder access
    Dim rootFolder As Outlook.Folder
    Set rootFolder = targetStore.GetRootFolder
    
    ' Set up tracking for all configured folders
    Dim foldersSetup As Integer
    foldersSetup = 0
    
    ' Inbox folder
    Set targetInboxFolder = FindFolderByName(rootFolder, "Inbox")
    If Not targetInboxFolder Is Nothing Then
        Set olInboxItems = targetInboxFolder.Items
        foldersSetup = foldersSetup + 1
        WriteLog "Event handler: Inbox folder tracking enabled"
    End If
    
    ' Deleted Items folder (try both standard Outlook and Gmail names)
    Set targetDeletedFolder = FindFolderByName(rootFolder, "Deleted Items")
    If targetDeletedFolder Is Nothing Then
        Set targetDeletedFolder = FindFolderByName(rootFolder, "Trash")
    End If
    If Not targetDeletedFolder Is Nothing Then
        Set olDeletedItems = targetDeletedFolder.Items
        foldersSetup = foldersSetup + 1
        WriteLog "Event handler: " & targetDeletedFolder.Name & " folder tracking enabled"
    End If
    
    ' Sent Items folder (try both standard Outlook and Gmail names)
    Set targetSentFolder = FindFolderByName(rootFolder, "Sent Items")
    If targetSentFolder Is Nothing Then
        Set targetSentFolder = FindFolderByName(rootFolder, "Sent Mail")
    End If
    If Not targetSentFolder Is Nothing Then
        Set olSentItems = targetSentFolder.Items
        foldersSetup = foldersSetup + 1
        WriteLog "Event handler: " & targetSentFolder.Name & " folder tracking enabled"
    End If
    
    ' Drafts folder
    Set targetDraftsFolder = FindFolderByName(rootFolder, "Drafts")
    If Not targetDraftsFolder Is Nothing Then
        Set olDrafts = targetDraftsFolder.Items
        foldersSetup = foldersSetup + 1
        WriteLog "Event handler: Drafts folder tracking enabled"
    End If
    
    ' Outbox folder
    Set targetOutboxFolder = FindFolderByName(rootFolder, "Outbox")
    If Not targetOutboxFolder Is Nothing Then
        Set olOutbox = targetOutboxFolder.Items
        foldersSetup = foldersSetup + 1
        WriteLog "Event handler: Outbox folder tracking enabled"
    End If
    
    If foldersSetup = 0 Then
        WriteLog "ERROR: No folders found for tracking"
        StartMonitoring = False
        Exit Function
    End If
    
    isActive = True
    WriteLog "Event handler initialized successfully! Tracking " & foldersSetup & " folders."
    StartMonitoring = True
    
    Exit Function
    
ErrorHandler:
    WriteLog "ERROR starting event handler: " & Err.Description
    StartMonitoring = False
End Function

' Stop event monitoring
Public Sub StopMonitoring()
    If isActive Then
        Set olInboxItems = Nothing
        Set olDeletedItems = Nothing
        Set olSentItems = Nothing
        Set olDrafts = Nothing
        Set olOutbox = Nothing
        Set olApp = Nothing
        Set targetInboxFolder = Nothing
        Set targetDeletedFolder = Nothing
        Set targetSentFolder = Nothing
        Set targetDraftsFolder = Nothing
        Set targetOutboxFolder = Nothing
        isActive = False
        WriteLog "Event handler stopped."
    End If
End Sub

' Check if monitoring is active
Public Function IsMonitoringActive() As Boolean
    IsMonitoringActive = isActive
End Function

' Event handler - automatically triggered when new email arrives
Private Sub olInboxItems_ItemAdd(ByVal Item As Object)
    On Error GoTo ErrorHandler
    
    ' Only process mail items
    If TypeOf Item Is Outlook.MailItem Then
        Dim mailItem As Outlook.MailItem
        Set mailItem = Item
        
        WriteLog "=== NEW EMAIL DETECTED ==="
        WriteLog "Subject: " & mailItem.Subject
        WriteLog "From: " & mailItem.SenderName & " (" & mailItem.SenderEmailAddress & ")"
        WriteLog "Received: " & Format(mailItem.ReceivedTime, "yyyy-mm-dd hh:nn:ss")
        
        ' Process this single new email (call function from main module)
        ProcessSingleNewEmail mailItem, targetInboxFolder
    End If
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in olInboxItems_ItemAdd: " & Err.Description
End Sub

' Helper function to find folder by name (copied from main module)
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

' Helper logging function (calls main module function)
Private Sub WriteLog(message As String)
    ' Call the WriteLog function from the main module directly
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

' Helper functions copied from main module
Private Function GetOutputFolder() As String
    GetOutputFolder = "C:\Users\" & Environ("USERNAME") & "\Desktop\normie\outlook\analyze\mail\"
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

' Event handler for Deleted Items folder
Private Sub olDeletedItems_ItemAdd(ByVal Item As Object)
    On Error GoTo ErrorHandler
    
    If TypeOf Item Is Outlook.MailItem Then
        Dim mailItem As Outlook.MailItem
        Set mailItem = Item
        
        WriteLog "=== EMAIL MOVED TO " & UCase(targetDeletedFolder.Name) & " ==="
        WriteLog "Subject: " & mailItem.Subject
        WriteLog "From: " & mailItem.SenderName & " (" & mailItem.SenderEmailAddress & ")"
        
        ' Process email in Deleted Items folder
        ProcessSingleNewEmail mailItem, targetDeletedFolder
    End If
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in olDeletedItems_ItemAdd: " & Err.Description
End Sub

' Event handler for Sent Items folder
Private Sub olSentItems_ItemAdd(ByVal Item As Object)
    On Error GoTo ErrorHandler
    
    If TypeOf Item Is Outlook.MailItem Then
        Dim mailItem As Outlook.MailItem
        Set mailItem = Item
        
        WriteLog "=== EMAIL SENT ==="
        WriteLog "Subject: " & mailItem.Subject
        WriteLog "To: " & mailItem.To
        
        ' Process email in Sent Items folder
        ProcessSingleNewEmail mailItem, targetSentFolder
    End If
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in olSentItems_ItemAdd: " & Err.Description
End Sub

' Event handler for Drafts folder
Private Sub olDrafts_ItemAdd(ByVal Item As Object)
    On Error GoTo ErrorHandler
    
    If TypeOf Item Is Outlook.MailItem Then
        Dim mailItem As Outlook.MailItem
        Set mailItem = Item
        
        WriteLog "=== EMAIL SAVED TO DRAFTS ==="
        WriteLog "Subject: " & mailItem.Subject
        
        ' Process email in Drafts folder
        ProcessSingleNewEmail mailItem, targetDraftsFolder
    End If
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in olDrafts_ItemAdd: " & Err.Description
End Sub

' Event handler for Outbox folder
Private Sub olOutbox_ItemAdd(ByVal Item As Object)
    On Error GoTo ErrorHandler
    
    If TypeOf Item Is Outlook.MailItem Then
        Dim mailItem As Outlook.MailItem
        Set mailItem = Item
        
        WriteLog "=== EMAIL IN OUTBOX ==="
        WriteLog "Subject: " & mailItem.Subject
        WriteLog "To: " & mailItem.To
        
        ' Process email in Outbox folder
        ProcessSingleNewEmail mailItem, targetOutboxFolder
    End If
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in olOutbox_ItemAdd: " & Err.Description
End Sub