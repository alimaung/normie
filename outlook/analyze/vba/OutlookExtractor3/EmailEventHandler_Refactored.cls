Option Explicit

' Email Event Handler Class (Refactored)
' This class handles WithEvents for Outlook email monitoring using the new modular structure

' Event-driven variables
Private WithEvents olApp As Outlook.Application
Private WithEvents olInboxItems As Outlook.Items
Private targetInboxFolder As Outlook.Folder
Private isActive As Boolean

' Initialize the event handler
Public Function StartMonitoring() As Boolean
    On Error GoTo ErrorHandler
    
    WriteLog "Initializing email event handler..."
    
    ' Initialize Outlook Application
    Set olApp = Application
    
    ' Get target inbox folder using the new utility functions
    Set targetInboxFolder = GetTargetInboxFolder()
    
    If targetInboxFolder Is Nothing Then
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
    LogError "EmailEventHandler.StartMonitoring", Err.Description, Err.Number
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
        
        ' Process this single new email using the new modular processor
        ProcessSingleNewEmail mailItem, targetInboxFolder
    End If
    
    Exit Sub
    
ErrorHandler:
    LogError "EmailEventHandler.olInboxItems_ItemAdd", Err.Description, Err.Number
End Sub 