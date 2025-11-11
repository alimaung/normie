Option Explicit

' Logging Module
' Handles all logging operations

' Main logging function
Public Sub WriteLog(message As String)
    On Error Resume Next
    
    ' Always output to Immediate window for debugging
    Debug.Print Format(Now, "yyyy-mm-dd hh:nn:ss") & " - " & message
    
    Dim logFile As String
    Dim fileNum As Integer
    Dim timestamp As String
    
    logFile = GetLogFile()
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

' Log error with additional context
Public Sub LogError(context As String, errorDescription As String, errorNumber As Long)
    WriteLog "ERROR in " & context & ": " & errorDescription & " (Error Number: " & errorNumber & ")"
End Sub

' Log debug information
Public Sub LogDebug(context As String, message As String)
    WriteLog "DEBUG [" & context & "]: " & message
End Sub

' Create status file with current timestamp
Public Sub CreateStatusFile(isEventMonitoringActive As Boolean)
    On Error Resume Next
    
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
    
    On Error GoTo 0
End Sub 