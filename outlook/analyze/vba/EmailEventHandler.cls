Option Explicit

' Email Event Handler Class
' This class handles WithEvents for Outlook email monitoring

' Event-driven variables
Private WithEvents olApp As Outlook.Application
Private WithEvents olInboxItems As Outlook.Items
Private targetInboxFolder As Outlook.Folder
Private isActive As Boolean

' Constants from main module
Private Const TARGET_ACCOUNT As String = "IRM-Standardisation-Office"

' Initialize the event handler
Public Function StartMonitoring() As Boolean
    On Error GoTo ErrorHandler
    
    WriteLog "Initializing email event handler..."
    
    ' Initialize Outlook Application
    Set olApp = Application
    
    ' Find target account and inbox
    Dim olNamespace As Outlook.NameSpace
    Set olNamespace = olApp.GetNamespace("MAPI")
    
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
        StartMonitoring = False
        Exit Function
    End If
    
    ' Get inbox folder
    Dim rootFolder As Outlook.Folder
    Set rootFolder = targetStore.GetRootFolder
    Set targetInboxFolder = FindFolderByName(rootFolder, "Inbox")
    
    If targetInboxFolder Is Nothing Then
        WriteLog "ERROR: Inbox folder not found"
        StartMonitoring = False
        Exit Function
    End If
    
    ' Set up event monitoring for the inbox
    Set olInboxItems = targetInboxFolder.Items
    isActive = True
    
    WriteLog "Event handler initialized successfully!"
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
        Set olApp = Nothing
        Set targetInboxFolder = Nothing
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