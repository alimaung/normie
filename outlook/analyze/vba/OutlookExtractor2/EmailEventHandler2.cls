VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "EmailEventHandler"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False
Option Explicit

' Email Event Handler Class - Refactored for IRM Account Only
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

' Constants
Private Const TARGET_ACCOUNT As String = "IRM-Standardisation-Office"

' Helper function to find target IRM store
Private Function FindIRMStore() As Outlook.Store
    On Error GoTo ErrorHandler
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.NameSpace
    Dim store As Outlook.Store
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    
    WriteLog "Event Handler: Searching for IRM account: " & TARGET_ACCOUNT
    
    For Each store In olNamespace.Stores
        If InStr(UCase(store.DisplayName), UCase(TARGET_ACCOUNT)) > 0 Then
            Set FindIRMStore = store
            WriteLog "Event Handler: Found IRM store: " & store.DisplayName
            Exit Function
        End If
    Next store
    
    WriteLog "ERROR: IRM account not found in event handler"
    Set FindIRMStore = Nothing
    Exit Function
    
ErrorHandler:
    WriteLog "ERROR in FindIRMStore (EventHandler): " & Err.Description
    Set FindIRMStore = Nothing
End Function

' Helper function to find folder by name
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

' Initialize the event handler
Public Function StartMonitoring() As Boolean
    On Error GoTo ErrorHandler
    
    WriteLog "Initializing IRM email event handler..."
    
    ' Initialize Outlook Application
    Set olApp = Application
    
    ' Find IRM account and folders
    Dim irmStore As Outlook.Store
    Set irmStore = FindIRMStore()
    
    If irmStore Is Nothing Then
        WriteLog "ERROR: No IRM account found"
        StartMonitoring = False
        Exit Function
    End If
    
    ' Get root folder for all folder access
    Dim rootFolder As Outlook.Folder
    Set rootFolder = irmStore.GetRootFolder
    
    ' Set up tracking for all available folders
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
        ' For Gmail, also try in [Gmail] subfolder
        If targetDeletedFolder Is Nothing Then
            Dim gmailFolder As Outlook.Folder
            Set gmailFolder = FindFolderByName(rootFolder, "[Gmail]")
            If Not gmailFolder Is Nothing Then
                Set targetDeletedFolder = FindFolderByName(gmailFolder, "Trash")
            End If
        End If
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
        ' For Gmail, also try in [Gmail] subfolder
        If targetSentFolder Is Nothing Then
            Set gmailFolder = FindFolderByName(rootFolder, "[Gmail]")
            If Not gmailFolder Is Nothing Then
                Set targetSentFolder = FindFolderByName(gmailFolder, "Sent Mail")
            End If
        End If
    End If
    If Not targetSentFolder Is Nothing Then
        Set olSentItems = targetSentFolder.Items
        foldersSetup = foldersSetup + 1
        WriteLog "Event handler: " & targetSentFolder.Name & " folder tracking enabled"
    End If
    
    ' Drafts folder
    Set targetDraftsFolder = FindFolderByName(rootFolder, "Drafts")
    If targetDraftsFolder Is Nothing Then
        ' For Gmail, also try in [Gmail] subfolder
        Set gmailFolder = FindFolderByName(rootFolder, "[Gmail]")
        If Not gmailFolder Is Nothing Then
            Set targetDraftsFolder = FindFolderByName(gmailFolder, "Drafts")
        End If
    End If
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
        WriteLog "ERROR: No folders found for event monitoring"
        StartMonitoring = False
        Exit Function
    End If
    
    isActive = True
    WriteLog "IRM event handler initialized successfully! Monitoring " & foldersSetup & " folders."
    StartMonitoring = True
    
    Exit Function
    
ErrorHandler:
    WriteLog "ERROR in StartMonitoring (EventHandler): " & Err.Description
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
        WriteLog "IRM event handler stopped."
    End If
End Sub

' Check if monitoring is active
Public Function IsMonitoringActive() As Boolean
    IsMonitoringActive = isActive
End Function

' Event handlers - automatically triggered when new emails arrive

' Inbox events
Private Sub olInboxItems_ItemAdd(ByVal Item As Object)
    On Error GoTo ErrorHandler
    
    If TypeOf Item Is Outlook.MailItem Then
        Dim mailItem As Outlook.MailItem
        Set mailItem = Item
        WriteLog "EVENT: New email in Inbox - " & Left(mailItem.Subject, 50)
        ProcessSingleNewEmail mailItem, targetInboxFolder
    End If
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in olInboxItems_ItemAdd: " & Err.Description
End Sub

' Deleted Items events
Private Sub olDeletedItems_ItemAdd(ByVal Item As Object)
    On Error GoTo ErrorHandler
    
    If TypeOf Item Is Outlook.MailItem Then
        Dim mailItem As Outlook.MailItem
        Set mailItem = Item
        WriteLog "EVENT: New email in " & targetDeletedFolder.Name & " - " & Left(mailItem.Subject, 50)
        ProcessSingleNewEmail mailItem, targetDeletedFolder
    End If
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in olDeletedItems_ItemAdd: " & Err.Description
End Sub

' Sent Items events
Private Sub olSentItems_ItemAdd(ByVal Item As Object)
    On Error GoTo ErrorHandler
    
    If TypeOf Item Is Outlook.MailItem Then
        Dim mailItem As Outlook.MailItem
        Set mailItem = Item
        WriteLog "EVENT: New email in " & targetSentFolder.Name & " - " & Left(mailItem.Subject, 50)
        ProcessSingleNewEmail mailItem, targetSentFolder
    End If
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in olSentItems_ItemAdd: " & Err.Description
End Sub

' Drafts events
Private Sub olDrafts_ItemAdd(ByVal Item As Object)
    On Error GoTo ErrorHandler
    
    If TypeOf Item Is Outlook.MailItem Then
        Dim mailItem As Outlook.MailItem
        Set mailItem = Item
        WriteLog "EVENT: New email in Drafts - " & Left(mailItem.Subject, 50)
        ProcessSingleNewEmail mailItem, targetDraftsFolder
    End If
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in olDrafts_ItemAdd: " & Err.Description
End Sub

' Outbox events
Private Sub olOutbox_ItemAdd(ByVal Item As Object)
    On Error GoTo ErrorHandler
    
    If TypeOf Item Is Outlook.MailItem Then
        Dim mailItem As Outlook.MailItem
        Set mailItem = Item
        WriteLog "EVENT: New email in Outbox - " & Left(mailItem.Subject, 50)
        ProcessSingleNewEmail mailItem, targetOutboxFolder
    End If
    
    Exit Sub
    
ErrorHandler:
    WriteLog "ERROR in olOutbox_ItemAdd: " & Err.Description
End Sub