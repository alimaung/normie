Option Explicit

' JSON Utilities Module
' Handles JSON formatting, escaping, and text processing

' Helper function to escape JSON strings
Public Function EscapeJson(text As String) As String
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

' Helper function to detect embedded/filler images
Public Function IsEmbeddedImage(fileName As String) As Boolean
    Dim upperFileName As String
    upperFileName = UCase(fileName)
    
    ' Specific embedded image GUIDs/hashes
    If upperFileName = "9B295F2F83534DC99F68C53110554C14.GIF" Or _
       upperFileName = "72BCF599BF8B42FCA47C22168A12B83C.GIF" Or _
       upperFileName = "AC023DD01F024F33B4EECFFDE3D5D52A.GIF" Or _
       upperFileName = "BA0B320E1A97421AA114D0901B89EB04.JPG" Or _
       upperFileName = "CD4ED6C73D8641B9B269ABC4C9553D69.JPG" Or _
       upperFileName = "D72078099DD54DE490A7A035558F217F.GIF" Then
        IsEmbeddedImage = True
        Exit Function
    End If
    
    ' Generic imageXXX patterns (like image001.png, image002.jpg, etc.)
    If Left(upperFileName, 5) = "IMAGE" And Len(upperFileName) >= 9 Then
        Dim numberPart As String
        Dim extensionPart As String
        
        ' Extract the number part (should be 3 digits)
        numberPart = Mid(upperFileName, 6, 3)
        
        ' Check if it's all digits
        If IsNumeric(numberPart) Then
            ' Extract extension part
            extensionPart = Right(upperFileName, 4) ' .jpg, .png, .gif
            
            If extensionPart = ".JPG" Or extensionPart = ".PNG" Or extensionPart = ".GIF" Then
                IsEmbeddedImage = True
                Exit Function
            End If
        End If
    End If
    
    IsEmbeddedImage = False
End Function

' Extract received time from JSON email entry
Public Function ExtractReceivedTimeFromJson(emailJson As String) As Date
    On Error GoTo ErrorHandler
    
    Dim startPos As Long
    Dim endPos As Long
    Dim timeString As String
    
    ' Find "received_time": "2024-01-01 12:34:56"
    startPos = InStr(emailJson, """received_time"": """) + 19
    endPos = InStr(startPos, emailJson, """") - 1
    
    If startPos > 19 And endPos > startPos Then
        timeString = Mid(emailJson, startPos, endPos - startPos + 1)
        ExtractReceivedTimeFromJson = CDate(timeString)
    Else
        ' Default to current time if parsing fails
        ExtractReceivedTimeFromJson = Now
    End If
    
    Exit Function
    
ErrorHandler:
    ExtractReceivedTimeFromJson = Now
End Function

' Count emails in a JSON file
Public Function CountEmailsInJsonFile(filePath As String) As Long
    On Error GoTo ErrorHandler
    
    Dim fileContent As String
    Dim fileNum As Integer
    Dim line As String
    
    fileNum = FreeFile
    Open filePath For Input As #fileNum
    
    Do While Not EOF(fileNum)
        Line Input #fileNum, line
        fileContent = fileContent & line
    Loop
    
    Close #fileNum
    
    ' Look for "extracted_count": number
    Dim startPos As Long
    Dim endPos As Long
    
    startPos = InStr(fileContent, """extracted_count"": ") + 19
    endPos = InStr(startPos, fileContent, vbCrLf) - 1
    
    If startPos > 19 And endPos > startPos Then
        CountEmailsInJsonFile = CLng(Mid(fileContent, startPos, endPos - startPos + 1))
    Else
        CountEmailsInJsonFile = 0
    End If
    
    Exit Function
    
ErrorHandler:
    CountEmailsInJsonFile = 0
End Function 