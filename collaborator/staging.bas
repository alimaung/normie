Sub FetchUserEdits()
    Dim fileList As Variant
    Dim userFile As Variant
    Dim userName As String
    Dim wbUser As Workbook
    Dim wsUser As Worksheet
    Dim wsMain As Worksheet
    Dim wsStaging As Worksheet
    Dim destRow As Long
    Dim r As Long, col As Long
    Dim userPath As String
    Dim antragNum As Variant
    Dim foundCell As Range
    Dim stagingRow As Long
    Dim cellStage As Range, cellMain As Range
    Dim mainRow As Long
    Dim dict As Object
    Dim uniqueID As Long
    Dim linkStage As String, linkMain As String

    Application.ScreenUpdating = False
    Application.EnableEvents = False

    Set dict = CreateObject("Scripting.Dictionary")
    fileList = Array("Verzeichnis_Ali.xlsm", "Verzeichnis_Andre.xlsm", "Verzeichnis_Jean-Michel.xlsm")

    Set wsMain = ThisWorkbook.Sheets("Teile und Stoffe")
    Set wsStaging = ThisWorkbook.Sheets("Staging")

    ' Clear previous staging data but keep headers and formats
    wsStaging.Range("A2:ZZ" & wsStaging.Rows.Count).ClearContents
    wsStaging.Range("E2:ZZ" & wsStaging.Rows.Count).Interior.ColorIndex = xlNone

    destRow = 2
    uniqueID = 1

    For Each userFile In fileList
        userPath = ThisWorkbook.Path & "\" & userFile

        userName = Trim(Mid(userFile, InStrRev(userFile, "_") + 1))
        userName = Replace(userName, ".xlsm", "")

        If Dir(userPath) <> "" Then
            Set wbUser = Workbooks.Open(Filename:=userPath, ReadOnly:=True)
            Set wsUser = wbUser.Sheets(1)

            For r = 2 To 51
                If wsUser.Cells(r, "AB").Value = 1 Then
                    ' Write user and timestamp
                    wsStaging.Cells(destRow, "C").Value = userName
                    wsStaging.Cells(destRow, "D").Value = Now

                    ' Copy columns A:AA from user to staging starting at column E
                    wsUser.Range("A" & r & ":AA" & r).Copy
                    wsStaging.Cells(destRow, "E").PasteSpecial Paste:=xlPasteAllUsingSourceTheme
                    Application.CutCopyMode = False

                    ' Get Antragnummer from col E (was col A)
                    antragNum = wsStaging.Cells(destRow, "E").Value

                    ' Track occurrences to detect conflicts
                    If dict.Exists(antragNum) Then
                        dict(antragNum) = dict(antragNum) + 1
                    Else
                        dict.Add antragNum, 1
                    End If

                    ' Unique ID in col B
                    wsStaging.Cells(destRow, "B").Value = uniqueID
                    uniqueID = uniqueID + 1

                    destRow = destRow + 1
                End If
            Next r

            wbUser.Close SaveChanges:=False
        Else
            MsgBox "File not found: " & userFile, vbExclamation
        End If
    Next userFile

    ' Mark conflicts in col A: 0 if conflict, 1 if unique
    For stagingRow = 2 To destRow - 1
        antragNum = wsStaging.Cells(stagingRow, "E").Value
        If dict(antragNum) > 1 Then
            wsStaging.Cells(stagingRow, "A").Value = 0
        Else
            wsStaging.Cells(stagingRow, "A").Value = 1
        End If
    Next stagingRow

    ' Highlight changes: compare staging (E:AE) with main (A:AA)
    For stagingRow = 2 To destRow - 1
        antragNum = wsStaging.Cells(stagingRow, "E").Value
        If antragNum <> "" Then
            Set foundCell = wsMain.Columns("A").Find(What:=antragNum, LookIn:=xlValues, LookAt:=xlWhole)

            If Not foundCell Is Nothing Then
                mainRow = foundCell.Row

                For col = 1 To 27
                    Set cellStage = wsStaging.Cells(stagingRow, col + 4) ' E=5 is col 1 of main data
                    Set cellMain = wsMain.Cells(mainRow, col)

                    If col >= 13 And col <= 21 Then
                        ' Columns M to U ? compare hyperlink addresses
                        On Error Resume Next
                        linkStage = ""
                        linkMain = ""
                        If cellStage.Hyperlinks.Count > 0 Then
                            linkStage = cellStage.Hyperlinks(1).Address
                        End If
                        If cellMain.Hyperlinks.Count > 0 Then
                            linkMain = cellMain.Hyperlinks(1).Address
                        End If
                        On Error GoTo 0

                        If linkStage <> linkMain Then
                            cellStage.FormatConditions.Delete
                            cellStage.Interior.Color = RGB(255, 50, 50)
                            cellStage.Font.Color = RGB(255, 255, 255)
                        End If
                    Else
                        ' Normal value compare
                        If Trim(CStr(cellStage.Value)) <> Trim(CStr(cellMain.Value)) Then
                            cellStage.FormatConditions.Delete
                            cellStage.Interior.Color = RGB(255, 50, 50)
                            cellStage.Font.Color = RGB(255, 255, 255)
                        End If
                    End If
                Next col
            End If
        End If
    Next stagingRow

    Application.ScreenUpdating = True
    Application.EnableEvents = True

    Conflicts.BuildConflictsList
End Sub


Sub ClearStagingArea()
    Dim ws As Worksheet
    Dim answer As VbMsgBoxResult
    
    answer = MsgBox("Are you sure you want to clear the staging area?", vbYesNo + vbExclamation, "Confirm Clear")
    If answer <> vbYes Then Exit Sub
    
    Set ws = ThisWorkbook.Sheets("Staging")
    
    ' Clear contents only (keep formatting) from columns A to D, starting from row 2
    ws.Range("A2:D" & ws.Rows.Count).ClearContents
    
    ' Clear everything (contents + formatting) from column E onward, starting from row 2
    ws.Range("E2:ZZ" & ws.Rows.Count).Clear
End Sub
