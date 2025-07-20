Option Explicit

' Constants and Configuration Module
' Contains all global constants and configuration settings

' Target account configuration
Public Const TARGET_ACCOUNT As String = "IRM-Standardisation-Office"

' JSON Management Configuration
Public Const MAX_EMAILS_PER_FILE As Integer = 500   ' Split JSON when it reaches this size
Public Const ARCHIVE_AFTER_DAYS As Integer = 90     ' Archive emails older than this
Public Const ENABLE_JSON_ROTATION As Boolean = True ' Enable automatic file rotation

' Path Configuration
Public Function GetOutputFolder() As String
    GetOutputFolder = "C:\Users\" & Environ("USERNAME") & "\Desktop\normie\outlook\analyze\mail\"
End Function

Public Function GetAttachmentsFolder() As String
    GetAttachmentsFolder = "C:\Users\" & Environ("USERNAME") & "\Desktop\normie\outlook\analyze\mail\data\"
End Function

Public Function GetLogFile() As String
    GetLogFile = GetOutputFolder() & "extractor_log.txt"
End Function 