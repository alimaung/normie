Option Explicit

' Outlook VBA Script for Auto-Reply with IP Address
' This script monitors incoming emails for #IRMNORMIE and sends automatic replies

Private WithEvents olInbox As Outlook.Items

Private Sub Application_Startup()
    ' Initialize the inbox monitoring when Outlook starts
    Set olInbox = Application.Session.GetDefaultFolder(olFolderInbox).Items
End Sub

Private Sub olInbox_ItemAdd(ByVal Item As Object)
    ' This event fires when a new item is added to the inbox
    If TypeOf Item Is Outlook.MailItem Then
        Call ProcessIncomingEmail(Item)
    End If
End Sub

Private Sub ProcessIncomingEmail(ByVal mailItem As Outlook.MailItem)
    Dim subject As String
    Dim body As String
    Dim containsTrigger As Boolean
    
    ' Get email content
    subject = LCase(mailItem.Subject)
    body = LCase(mailItem.Body)
    
    ' Check if email contains the trigger text
    containsTrigger = (InStr(subject, "#irmnormie") > 0) Or (InStr(body, "#irmnormie") > 0)
    
    If containsTrigger Then
        ' Send automatic reply
        Call SendAutoReply(mailItem)
    End If
End Sub

Private Sub SendAutoReply(ByVal originalMail As Outlook.MailItem)
    Dim replyMail As Outlook.MailItem
    Dim ipAddress As String
    Dim htmlTemplate As String
    Dim finalHtml As String
    Dim errorMsg As String
    
    On Error GoTo ErrorHandler
    
    ' Get the IPv4 address
    ipAddress = GetIPv4Address()
    
    ' Load and modify the HTML template
    htmlTemplate = LoadHtmlTemplate()
    finalHtml = ReplaceHtmlTemplate(htmlTemplate, ipAddress)
    
    ' Create reply
    Set replyMail = originalMail.Reply
    
    ' Set reply properties
    With replyMail
        .Subject = "Re: " & originalMail.Subject
        .HTMLBody = finalHtml
        .BodyFormat = olFormatHTML
        
        ' Ensure recipient is set
        If .To = "" And originalMail.SenderEmailAddress <> "" Then
            .To = originalMail.SenderEmailAddress
        End If
        
        ' Try to send with error handling
        .Send
    End With
    
    ' Log success
    Debug.Print "Auto-reply sent successfully to: " & originalMail.SenderEmailAddress
    
    ' Clean up
    Set replyMail = Nothing
    Exit Sub
    
ErrorHandler:
    errorMsg = "Error sending auto-reply: " & Err.Description & " (Error " & Err.Number & ")"
    Debug.Print errorMsg
    
    ' Try alternative sending method
    Call SendAutoReplyAlternative(originalMail, finalHtml, ipAddress)
    
    ' Clean up
    If Not replyMail Is Nothing Then
        Set replyMail = Nothing
    End If
End Sub

Private Function GetIPv4Address() As String
    Dim shell As Object
    Dim exec As Object
    Dim output As String
    Dim lines As Variant
    Dim i As Integer
    Dim line As String
    Dim ipAddress As String
    
    On Error GoTo IPErrorHandler
    
    ' Initialize shell object
    Set shell = CreateObject("WScript.Shell")
    
    ' Execute ipconfig command
    Set exec = shell.Exec("ipconfig")
    
    ' Read the output
    Do While Not exec.StdOut.AtEndOfStream
        output = output & exec.StdOut.ReadLine & vbCrLf
    Loop
    
    Debug.Print "ipconfig output: " & output
    
    ' Parse the output to find IPv4 address - prioritize Ethernet, then WiFi
    lines = Split(output, vbCrLf)
    Dim foundEthernet As Boolean
    Dim foundWiFi As Boolean
    foundEthernet = False
    foundWiFi = False
    
    For i = 0 To UBound(lines)
        line = Trim(lines(i))
        Debug.Print "Processing line: " & line
        
        ' Look for Ethernet adapter first (for testing)
        If InStr(LCase(line), "ethernet adapter") > 0 And InStr(LCase(line), "media disconnected") = 0 Then
            foundEthernet = True
            Debug.Print "Found active Ethernet adapter: " & line
        ElseIf foundEthernet And InStr(LCase(line), "ipv4 address") > 0 Then
            ' Extract IP address from Ethernet
            Dim parts As Variant
            parts = Split(line, ":")
            If UBound(parts) >= 1 Then
                ipAddress = Trim(parts(1))
                ipAddress = Replace(ipAddress, vbCr, "")
                ipAddress = Replace(ipAddress, vbLf, "")
                ipAddress = Replace(ipAddress, vbTab, "")
                Debug.Print "Found Ethernet IP address: " & ipAddress
                Exit For
            End If
        ElseIf foundEthernet And (InStr(LCase(line), "ethernet adapter") > 0 Or InStr(LCase(line), "wireless lan adapter") > 0) Then
            ' Stop looking if we hit another adapter
            foundEthernet = False
        End If
    Next i
    
    ' If no Ethernet IP found, try WiFi (for production)
    If ipAddress = "" Then
        Debug.Print "No Ethernet IP found, looking for WiFi adapter"
        For i = 0 To UBound(lines)
            line = Trim(lines(i))
            
            ' Look for WiFi adapter section (try multiple variations)
            If InStr(LCase(line), "wireless lan adapter wifi") > 0 Or _
               InStr(LCase(line), "wireless lan adapter wi-fi") > 0 Or _
               InStr(LCase(line), "wi-fi") > 0 Or _
               InStr(LCase(line), "wifi") > 0 Then
                foundWiFi = True
                Debug.Print "Found WiFi adapter: " & line
            ElseIf foundWiFi And InStr(LCase(line), "ipv4 address") > 0 Then
                ' Extract IP address from WiFi
                Dim parts2 As Variant
                parts2 = Split(line, ":")
                If UBound(parts2) >= 1 Then
                    ipAddress = Trim(parts2(1))
                    ipAddress = Replace(ipAddress, vbCr, "")
                    ipAddress = Replace(ipAddress, vbLf, "")
                    ipAddress = Replace(ipAddress, vbTab, "")
                    Debug.Print "Found WiFi IP address: " & ipAddress
                    Exit For
                End If
            ElseIf foundWiFi And (InStr(LCase(line), "ethernet adapter") > 0 Or InStr(LCase(line), "wireless lan adapter") > 0) Then
                ' Stop looking if we hit another adapter
                foundWiFi = False
            End If
        Next i
    End If
    
    ' If WiFi not found, try to find any IPv4 address
    If ipAddress = "" Then
        Debug.Print "WiFi adapter not found, looking for any IPv4 address"
        For i = 0 To UBound(lines)
            line = Trim(lines(i))
            If InStr(LCase(line), "ipv4 address") > 0 Then
                Dim parts3 As Variant
                parts3 = Split(line, ":")
                If UBound(parts3) >= 1 Then
                    ipAddress = Trim(parts3(1))
                    ipAddress = Replace(ipAddress, vbCr, "")
                    ipAddress = Replace(ipAddress, vbLf, "")
                    ipAddress = Replace(ipAddress, vbTab, "")
                    ' Skip localhost addresses
                    If InStr(ipAddress, "127.0.0.1") = 0 And InStr(ipAddress, "169.254") = 0 Then
                        Debug.Print "Found alternative IP address: " & ipAddress
                        Exit For
                    End If
                End If
            End If
        Next i
    End If
    
    ' Clean up
    Set exec = Nothing
    Set shell = Nothing
    
    ' Return the IP address or default message
    If ipAddress <> "" Then
        GetIPv4Address = ipAddress
    Else
        GetIPv4Address = "IP_NOT_FOUND"
    End If
    Exit Function
    
IPErrorHandler:
    Debug.Print "Error getting IP address: " & Err.Description
    GetIPv4Address = "IP_ERROR"
    If Not exec Is Nothing Then Set exec = Nothing
    If Not shell Is Nothing Then Set shell = Nothing
End Function

Private Function LoadHtmlTemplate() As String
    Dim fso As Object
    Dim file As Object
    Dim templatePath As String
    
    ' Use the specific absolute path provided
    templatePath = "C:\Users\user1\Desktop\normie\outlook\riply\cerberus-fluid.html"
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    If fso.FileExists(templatePath) Then
        Set file = fso.OpenTextFile(templatePath, 1) ' 1 = ForReading
        LoadHtmlTemplate = file.ReadAll
        file.Close
        Debug.Print "HTML template loaded successfully from: " & templatePath
    Else
        ' Fallback to embedded template if file not found
        Debug.Print "HTML template file not found at: " & templatePath
        LoadHtmlTemplate = GetDefaultTemplate()
    End If
    
    Set file = Nothing
    Set fso = Nothing
End Function

Private Function ReplaceHtmlTemplate(ByVal template As String, ByVal ipAddress As String) As String
    Dim modifiedTemplate As String
    Dim buttonLink As String
    
    ' Create the button link with IP address
    buttonLink = "http://" & ipAddress & "/directory"
    
    ' Replace the placeholder button link in the template
    modifiedTemplate = Replace(template, "https://google.com/", buttonLink)
    
    ' Update button text to be more relevant
    modifiedTemplate = Replace(modifiedTemplate, "Primary Button", "Access Directory")
    
    ' Update the main heading
    modifiedTemplate = Replace(modifiedTemplate, "Praesent laoreet malesuada&nbsp;cursus.", "Directory Access Available")
    
    ' Update the description text
    modifiedTemplate = Replace(modifiedTemplate, "Maecenas sed ante pellentesque, posuere leo id, eleifend dolor. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Praesent laoreet malesuada cursus. Maecenas scelerisque congue eros eu posuere. Praesent in felis ut velit pretium lobortis rhoncus ut&nbsp;erat.", "Your directory access request has been processed. Click the button below to access the directory using your current IP address: " & ipAddress)
    
    ReplaceHtmlTemplate = modifiedTemplate
End Function

Private Function GetDefaultTemplate() As String
    ' Fallback template if the HTML file is not found
    GetDefaultTemplate = "<!DOCTYPE html>" & vbCrLf & _
        "<html><head><title>Directory Access</title></head>" & vbCrLf & _
        "<body style=""font-family: Arial, sans-serif; padding: 20px;"">" & vbCrLf & _
        "<h1>Directory Access Available</h1>" & vbCrLf & _
        "<p>Your directory access request has been processed.</p>" & vbCrLf & _
        "<p>Click the button below to access the directory:</p>" & vbCrLf & _
        "<a href=""http://IP_PLACEHOLDER/directory"" style=""background-color: #222222; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;"">Access Directory</a>" & vbCrLf & _
        "<p>IP Address: IP_PLACEHOLDER</p>" & vbCrLf & _
        "</body></html>"
End Function

' Alternative sending method for when primary method fails
Private Sub SendAutoReplyAlternative(ByVal originalMail As Outlook.MailItem, ByVal htmlContent As String, ByVal ipAddress As String)
    Dim newMail As Outlook.MailItem
    Dim errorMsg As String
    
    On Error GoTo AltErrorHandler
    
    ' Create new email instead of reply
    Set newMail = Application.CreateItem(olMailItem)
    
    With newMail
        ' Debug sender information
        Debug.Print "SenderEmailAddress: [" & originalMail.SenderEmailAddress & "]"
        Debug.Print "SenderName: [" & originalMail.SenderName & "]"
        
        ' Ensure we have a valid recipient - use email address only
        If originalMail.SenderEmailAddress <> "" Then
            .To = originalMail.SenderEmailAddress
            Debug.Print "Using SenderEmailAddress: " & originalMail.SenderEmailAddress
        Else
            ' If no email address, try to extract from sender name
            Dim senderInfo As String
            senderInfo = originalMail.SenderName
            Debug.Print "Trying to extract from SenderName: " & senderInfo
            
            If InStr(senderInfo, "<") > 0 And InStr(senderInfo, ">") > 0 Then
                ' Extract email from "Name <email@domain.com>" format
                Dim startPos As Integer, endPos As Integer
                startPos = InStr(senderInfo, "<") + 1
                endPos = InStr(senderInfo, ">")
                .To = Mid(senderInfo, startPos, endPos - startPos)
                Debug.Print "Extracted email from SenderName: " & .To
            Else
                ' For test emails, use a test recipient
                If InStr(LCase(originalMail.Subject), "test") > 0 Then
                    .To = Application.Session.CurrentUser.Address
                    Debug.Print "Using current user for test email: " & .To
                Else
                    ' Use current user as fallback
                    .To = Application.Session.CurrentUser.Address
                    Debug.Print "Using current user as fallback: " & .To
                End If
            End If
        End If
        
        .Subject = "Re: " & originalMail.Subject
        .HTMLBody = htmlContent
        .BodyFormat = olFormatHTML
        
        ' Try to send
        .Send
    End With
    
    Debug.Print "Alternative auto-reply sent successfully to: " & originalMail.SenderEmailAddress
    Set newMail = Nothing
    Exit Sub
    
AltErrorHandler:
    errorMsg = "Alternative send also failed: " & Err.Description & " (Error " & Err.Number & ")"
    Debug.Print errorMsg
    
    ' Try saving to drafts as last resort
    Call SaveToDrafts(originalMail, htmlContent, ipAddress)
    
    If Not newMail Is Nothing Then
        Set newMail = Nothing
    End If
End Sub

' Save to drafts if sending fails
Private Sub SaveToDrafts(ByVal originalMail As Outlook.MailItem, ByVal htmlContent As String, ByVal ipAddress As String)
    Dim draftMail As Outlook.MailItem
    
    On Error GoTo DraftErrorHandler
    
    Set draftMail = Application.CreateItem(olMailItem)
    
    With draftMail
        ' Ensure we have a valid recipient
        If originalMail.SenderEmailAddress <> "" Then
            .To = originalMail.SenderEmailAddress
        ElseIf originalMail.SenderName <> "" Then
            .To = originalMail.SenderName
        Else
            .To = "Unknown Sender"
        End If
        
        .Subject = "Re: " & originalMail.Subject & " [DRAFT - Auto-reply failed to send]"
        .HTMLBody = htmlContent & "<br><br><p style='color: red; font-size: 12px;'>Note: This auto-reply failed to send automatically. Please send manually.</p>"
        .BodyFormat = olFormatHTML
        .Save
    End With
    
    Debug.Print "Auto-reply saved to drafts for: " & originalMail.SenderEmailAddress
    Set draftMail = Nothing
    Exit Sub
    
DraftErrorHandler:
    Debug.Print "Failed to save to drafts: " & Err.Description
    If Not draftMail Is Nothing Then
        Set draftMail = Nothing
    End If
End Sub

' Function to check Outlook security settings
Public Sub CheckOutlookSecurity()
    Dim msg As String
    msg = "Outlook Security Check:" & vbCrLf & vbCrLf
    msg = msg & "1. Go to File → Options → Trust Center → Trust Center Settings" & vbCrLf
    msg = msg & "2. Click 'Macro Settings'" & vbCrLf
    msg = msg & "3. Select 'Enable all macros' or 'Enable all macros with notification'" & vbCrLf & vbCrLf
    msg = msg & "4. Click 'Programmatic Access' tab" & vbCrLf
    msg = msg & "5. Select 'Never warn me about suspicious activity'" & vbCrLf & vbCrLf
    msg = msg & "6. Click 'Email Security' tab" & vbCrLf
    msg = msg & "7. UNCHECK 'Warn me about suspicious activity when my antivirus software is inactive or out of date'" & vbCrLf & vbCrLf
    msg = msg & "8. Restart Outlook after making changes"
    
    MsgBox msg, vbInformation, "Outlook Security Settings"
End Sub

' Function to test with a simple email first
Public Sub TestSimpleEmail()
    Dim testMail As Outlook.MailItem
    
    On Error GoTo TestErrorHandler
    
    Set testMail = Application.CreateItem(olMailItem)
    
    With testMail
        .To = Application.Session.CurrentUser.Address
        .Subject = "Simple VBA Test"
        .Body = "This is a simple test email from VBA."
        .Send
    End With
    
    MsgBox "Simple test email sent successfully!", vbInformation, "Test Complete"
    Set testMail = Nothing
    Exit Sub
    
TestErrorHandler:
    MsgBox "Simple test failed: " & Err.Description & vbCrLf & vbCrLf & "Error Code: " & Err.Number, vbCritical, "Test Failed"
    If Not testMail Is Nothing Then
        Set testMail = Nothing
    End If
End Sub

' Function to test email sending capabilities
Public Sub TestEmailSending()
    Dim testMail As Outlook.MailItem
    Dim ipAddress As String
    
    On Error GoTo TestErrorHandler
    
    ipAddress = GetIPv4Address()
    
    Set testMail = Application.CreateItem(olMailItem)
    
    With testMail
        .To = Application.Session.CurrentUser.Address
        .Subject = "VBA Test Email - IP: " & ipAddress
        .Body = "This is a test email from the VBA script. Your IP address is: " & ipAddress
        .Send
    End With
    
    MsgBox "Test email sent successfully! Check your inbox.", vbInformation, "Test Complete"
    Set testMail = Nothing
    Exit Sub
    
TestErrorHandler:
    MsgBox "Test email failed: " & Err.Description & vbCrLf & vbCrLf & "This indicates the same issue affecting auto-replies.", vbCritical, "Test Failed"
    If Not testMail Is Nothing Then
        Set testMail = Nothing
    End If
End Sub

' Function to test IP detection specifically
Public Sub TestIPDetection()
    Dim ipAddress As String
    ipAddress = GetIPv4Address()
    
    MsgBox "Detected IP Address: " & ipAddress, vbInformation, "IP Detection Test"
    Debug.Print "IP Detection Test Result: " & ipAddress
End Sub

' Function to run ipconfig manually and show output
Public Sub ShowIPConfigOutput()
    Dim shell As Object
    Dim exec As Object
    Dim output As String
    
    Set shell = CreateObject("WScript.Shell")
    Set exec = shell.Exec("ipconfig")
    
    Do While Not exec.StdOut.AtEndOfStream
        output = output & exec.StdOut.ReadLine & vbCrLf
    Loop
    
    MsgBox "ipconfig output:" & vbCrLf & vbCrLf & output, vbInformation, "ipconfig Output"
    Debug.Print "ipconfig output: " & output
    
    Set exec = Nothing
    Set shell = Nothing
End Sub

' Manual trigger function for testing
Public Sub TestAutoReply()
    Dim testMail As Outlook.MailItem
    Set testMail = Application.CreateItem(olMailItem)
    
    With testMail
        .Subject = "Test #IRMNORMIE"
        .Body = "This is a test email with #IRMNORMIE trigger"
        .To = "test@example.com"  ' Set a test recipient
        .Save
    End With
    
    Call ProcessIncomingEmail(testMail)
    
    Set testMail = Nothing
End Sub

' Test with a real email address
Public Sub TestAutoReplyWithRealEmail()
    Dim testMail As Outlook.MailItem
    Set testMail = Application.CreateItem(olMailItem)
    
    With testMail
        .Subject = "Directory Access Request #IRMNORMIE"
        .Body = "Please provide directory access. #IRMNORMIE"
        .To = Application.Session.CurrentUser.Address  ' Send to yourself for testing
        .Save
    End With
    
    Call ProcessIncomingEmail(testMail)
    
    Set testMail = Nothing
End Sub
