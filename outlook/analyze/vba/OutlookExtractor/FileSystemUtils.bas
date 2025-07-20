Option Explicit

' File System Utilities Module
' Contains file system operations and path manipulation functions

' Helper function to create directory path recursively
Public Sub CreateDirectoryPath(fullPath As String)
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

' Helper function to clean filename
Public Function CleanFileName(fileName As String) As String
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

' Format bytes to human readable
Public Function FormatBytes(bytes As Long) As String
    If bytes < 1024 Then
        FormatBytes = bytes & " B"
    ElseIf bytes < 1048576 Then
        FormatBytes = Round(bytes / 1024, 1) & " KB"
    Else
        FormatBytes = Round(bytes / 1048576, 1) & " MB"
    End If
End Function

' Check if file exists and has content
Public Function FileExistsAndHasContent(filePath As String) As Boolean
    FileExistsAndHasContent = (Dir(filePath) <> "" And FileLen(filePath) > 0)
End Function 