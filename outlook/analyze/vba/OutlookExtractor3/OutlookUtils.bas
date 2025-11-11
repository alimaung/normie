Option Explicit

' Outlook Utilities Module
' Contains Outlook-specific helper functions

' Helper function to find folder by name
Public Function FindFolderByName(parentFolder As Outlook.Folder, folderName As String) As Outlook.Folder
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

' Find target Outlook store by account name
Public Function FindTargetStore(accountName As String) As Outlook.Store
    On Error GoTo ErrorHandler
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.NameSpace
    Dim store As Outlook.Store
    
    Set olApp = Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    
    For Each store In olNamespace.Stores
        If InStr(UCase(store.DisplayName), UCase(accountName)) > 0 Then
            Set FindTargetStore = store
            WriteLog "Found target store: " & store.DisplayName
            Exit Function
        End If
    Next store
    
    Set FindTargetStore = Nothing
    WriteLog "ERROR: Target account '" & accountName & "' not found"
    
    Exit Function
    
ErrorHandler:
    Set FindTargetStore = Nothing
    LogError "FindTargetStore", Err.Description, Err.Number
End Function

' Get inbox folder from target store
Public Function GetInboxFolder(targetStore As Outlook.Store) As Outlook.Folder
    On Error GoTo ErrorHandler
    
    If targetStore Is Nothing Then
        Set GetInboxFolder = Nothing
        Exit Function
    End If
    
    Dim rootFolder As Outlook.Folder
    Set rootFolder = targetStore.GetRootFolder
    Set GetInboxFolder = FindFolderByName(rootFolder, "Inbox")
    
    If GetInboxFolder Is Nothing Then
        WriteLog "ERROR: Inbox folder not found"
    End If
    
    Exit Function
    
ErrorHandler:
    Set GetInboxFolder = Nothing
    LogError "GetInboxFolder", Err.Description, Err.Number
End Function

' Get target inbox folder (combines store and folder finding)
Public Function GetTargetInboxFolder() As Outlook.Folder
    Dim targetStore As Outlook.Store
    Set targetStore = FindTargetStore(TARGET_ACCOUNT)
    
    If Not targetStore Is Nothing Then
        Set GetTargetInboxFolder = GetInboxFolder(targetStore)
    Else
        Set GetTargetInboxFolder = Nothing
    End If
End Function 