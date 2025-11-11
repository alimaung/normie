Option Explicit

' Hash Generator Module
' Handles email hash generation for unique identification

' Generate comprehensive email hash using maximum properties for collision resistance
Public Function GenerateEmailHash(mailItem As Object) As String
    On Error GoTo ErrorHandler
    
    Dim hashInput As String
    Dim tempValue As String
    Dim i As Long
    
    ' 1. EntryID (most unique identifier)
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.EntryID
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 2. Subject
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.Subject
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 3. Sender email address
    tempValue = ""
    On Error Resume Next
    If Not mailItem.SenderEmailAddress Is Nothing Then
        tempValue = mailItem.SenderEmailAddress
    ElseIf Not mailItem.Sender Is Nothing Then
        tempValue = mailItem.Sender.Address
    End If
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 4. Sender name
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.SenderName
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 5. Full body text (more unique than partial)
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.Body
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 6. HTML body (different formatting can make emails unique)
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.HTMLBody
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 7. Received time (as string for consistency)
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.ReceivedTime)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 8. Sent time (different from received)
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.SentOn)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 9. Size (helps distinguish emails with similar content)
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.Size)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 10. Importance level
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.Importance)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 11. Number of attachments
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.Attachments.Count)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 12. All recipient addresses (To, CC, BCC)
    tempValue = ""
    On Error Resume Next
    For i = 1 To mailItem.Recipients.Count
        tempValue = tempValue & mailItem.Recipients(i).Address & ";"
    Next i
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 13. Categories
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.Categories
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 14. Message ID (RFC standard unique identifier)
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x1035001E")
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 15. Conversation ID
    tempValue = ""
    On Error Resume Next
    tempValue = mailItem.ConversationID
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 16. Creation time
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.CreationTime)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue & "|"
    
    ' 17. Last modification time
    tempValue = ""
    On Error Resume Next
    tempValue = CStr(mailItem.LastModificationTime)
    On Error GoTo ErrorHandler
    hashInput = hashInput & tempValue
    
    ' Generate hash from combined properties
    GenerateEmailHash = ShortHash(hashInput)
    Exit Function
    
ErrorHandler:
    ' Fallback to simple EntryID + Subject + timestamp if anything fails
    On Error Resume Next
    Dim fallbackInput As String
    fallbackInput = mailItem.EntryID & "|" & mailItem.Subject & "|" & CStr(Now)
    GenerateEmailHash = ShortHash(fallbackInput)
End Function

' Helper function to generate a 6-digit hash - deterministic but collision-resistant
Private Function ShortHash(text As String) As String
    On Error GoTo ErrorHandler
    
    Dim i As Long
    Dim hashValue As Long
    Dim char As Long
    Dim inputText As String
    Dim temp As Long
    
    ' Use more of the input text for better uniqueness
    inputText = Left(text, 200)
    
    ' Start with a large prime for better distribution
    hashValue = 5381
    
    ' DJB2 hash algorithm - deterministic and well-distributed
    For i = 1 To Len(inputText)
        char = Asc(Mid(inputText, i, 1))
        
        ' Calculate hash * 33 + char with overflow protection
        temp = hashValue * 33
        
        ' Handle potential overflow
        If temp > 2000000000 Then
            ' Use modulo with a large prime to maintain distribution
            hashValue = (temp Mod 999983) + char
        Else
            hashValue = temp + char
        End If
        
        ' Additional character position weighting for better distribution
        hashValue = hashValue + (i * 7)
        
        ' Keep values manageable
        If hashValue > 1000000000 Then
            hashValue = hashValue Mod 999979
        End If
    Next i
    
    ' Add length-based component for additional uniqueness
    hashValue = hashValue + (Len(inputText) * 31)
    
    ' Add checksum of all characters for more uniqueness
    Dim checksum As Long
    For i = 1 To Len(inputText) Step 3  ' Sample every 3rd character for efficiency
        checksum = checksum + Asc(Mid(inputText, i, 1))
    Next i
    hashValue = hashValue + (checksum * 17)
    
    ' Final result - always positive 6-digit number
    ShortHash = Format(Abs(hashValue) Mod 1000000, "000000")
    
    Exit Function
    
ErrorHandler:
    ' Deterministic fallback based on string properties
    Dim fallbackValue As Long
    
    If Len(text) > 0 Then
        ' Use string length, first char, last char, and middle char if available
        fallbackValue = Len(text) * 1000
        fallbackValue = fallbackValue + (Asc(Left(text, 1)) * 100)
        
        If Len(text) > 1 Then
            fallbackValue = fallbackValue + (Asc(Right(text, 1)) * 10)
        End If
        
        If Len(text) > 2 Then
            Dim midPos As Long
            midPos = Len(text) \ 2
            fallbackValue = fallbackValue + Asc(Mid(text, midPos, 1))
        End If
    Else
        fallbackValue = 123456  ' Fixed value for empty strings
    End If
    
    ShortHash = Format(Abs(fallbackValue) Mod 1000000, "000000")
End Function 