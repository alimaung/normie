Option Explicit

' Simple Outlook VBA Script for Email Detection
' This script monitors incoming emails for #IRMNORMIE and shows a message box

Private WithEvents olInbox As Outlook.Items

Private Sub Application_Startup()
    ' Initialize the inbox monitoring when Outlook starts
    Set olInbox = Application.Session.GetDefaultFolder(olFolderInbox).Items
    MsgBox "Email monitoring started! Looking for emails with #IRMNORMIE", vbInformation, "Auto-Reply Monitor"
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
        ' Show message box with email details
        Call ShowEmailDetected(mailItem)
    End If
End Sub

Private Sub ShowEmailDetected(ByVal mailItem As Outlook.MailItem)
    Dim senderName As String
    Dim senderEmail As String
    Dim emailSubject As String
    Dim ipAddress As String
    Dim replyMail As Outlook.MailItem
    Dim htmlTemplate As String
    Dim finalHtml As String
    
    ' Get email information
    senderName = mailItem.SenderName
    senderEmail = mailItem.SenderEmailAddress
    emailSubject = mailItem.Subject
    
    ' Get IP address
    ipAddress = GetIPv4Address()
    
    ' Load and modify the HTML template
    htmlTemplate = LoadHtmlTemplate()
    finalHtml = ReplaceHtmlTemplate(htmlTemplate, ipAddress)
    
    ' Create and send reply email
    Set replyMail = Application.CreateItem(olMailItem)
    With replyMail
        .To = senderEmail
        .Subject = "Re: " & emailSubject
        .HTMLBody = finalHtml
        .BodyFormat = olFormatHTML
        .Send
    End With
    
    ' Clean up
    Set replyMail = Nothing
End Sub

' Manual test function
Public Sub TestEmailDetection()
    Dim testMail As Outlook.MailItem
    Set testMail = Application.CreateItem(olMailItem)
    
    With testMail
        .Subject = "Test Directory Access #IRMNORMIE"
        .Body = "This is a test email with #IRMNORMIE trigger for directory access"
        .To = "test@example.com"
        .Save
    End With
    
    Call ProcessIncomingEmail(testMail)
    
    Set testMail = Nothing
End Sub

' Function to manually start monitoring (if needed)
Public Sub StartMonitoring()
    Set olInbox = Application.Session.GetDefaultFolder(olFolderInbox).Items
    MsgBox "Email monitoring started manually!", vbInformation, "Monitor Started"
End Sub

' Function to stop monitoring
Public Sub StopMonitoring()
    Set olInbox = Nothing
    MsgBox "Email monitoring stopped!", vbInformation, "Monitor Stopped"
End Sub

' Get IPv4 address from system
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
    
    ' Parse the output to find IPv4 address - prioritize Ethernet, then WiFi
    lines = Split(output, vbCrLf)
    Dim foundEthernet As Boolean
    Dim foundWiFi As Boolean
    foundEthernet = False
    foundWiFi = False
    
    For i = 0 To UBound(lines)
        line = Trim(lines(i))
        
        ' Look for Ethernet adapter first (for testing)
        If InStr(LCase(line), "ethernet adapter") > 0 And InStr(LCase(line), "media disconnected") = 0 Then
            foundEthernet = True
        ElseIf foundEthernet And InStr(LCase(line), "ipv4 address") > 0 Then
            ' Extract IP address from Ethernet
            Dim parts As Variant
            parts = Split(line, ":")
            If UBound(parts) >= 1 Then
                ipAddress = Trim(parts(1))
                ipAddress = Replace(ipAddress, vbCr, "")
                ipAddress = Replace(ipAddress, vbLf, "")
                ipAddress = Replace(ipAddress, vbTab, "")
                Exit For
            End If
        ElseIf foundEthernet And (InStr(LCase(line), "ethernet adapter") > 0 Or InStr(LCase(line), "wireless lan adapter") > 0) Then
            ' Stop looking if we hit another adapter
            foundEthernet = False
        End If
    Next i
    
    ' If no Ethernet IP found, try WiFi (for production)
    If ipAddress = "" Then
        For i = 0 To UBound(lines)
            line = Trim(lines(i))
            
            ' Look for WiFi adapter section (try multiple variations)
            If InStr(LCase(line), "wireless lan adapter wifi") > 0 Or _
               InStr(LCase(line), "wireless lan adapter wi-fi") > 0 Or _
               InStr(LCase(line), "wi-fi") > 0 Or _
               InStr(LCase(line), "wifi") > 0 Then
                foundWiFi = True
            ElseIf foundWiFi And InStr(LCase(line), "ipv4 address") > 0 Then
                ' Extract IP address from WiFi
                Dim parts2 As Variant
                parts2 = Split(line, ":")
                If UBound(parts2) >= 1 Then
                    ipAddress = Trim(parts2(1))
                    ipAddress = Replace(ipAddress, vbCr, "")
                    ipAddress = Replace(ipAddress, vbLf, "")
                    ipAddress = Replace(ipAddress, vbTab, "")
                    Exit For
                End If
            ElseIf foundWiFi And (InStr(LCase(line), "ethernet adapter") > 0 Or InStr(LCase(line), "wireless lan adapter") > 0) Then
                ' Stop looking if we hit another adapter
                foundWiFi = False
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
    GetIPv4Address = "IP_ERROR"
    If Not exec Is Nothing Then Set exec = Nothing
    If Not shell Is Nothing Then Set shell = Nothing
End Function

' Load HTML template from file
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
    Else
        ' Fallback to embedded template if file not found
        LoadHtmlTemplate = GetDefaultTemplate()
    End If
    
    Set file = Nothing
    Set fso = Nothing
End Function

' Replace template with IP address
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

' Fallback template if HTML file is not found
Private Function GetDefaultTemplate() As String
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
