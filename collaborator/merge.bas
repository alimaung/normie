Sub CommitNonConflictedChanges()
    Dim wsStaging As Worksheet, wsMain As Worksheet, wsArchive As Worksheet
    Dim lastRow As Long, stagingRow As Long, mainRow As Long
    Dim antragNum As Variant
    Dim foundCell As Range
    Dim commitCount As Long
    Dim archiveRow As Long
    
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    
    Set wsStaging = ThisWorkbook.Sheets("Staging")
    Set wsMain = ThisWorkbook.Sheets("Teile und Stoffe")
    
    ' Create Archive sheet if it doesn't exist
    On Error Resume Next
    Set wsArchive = ThisWorkbook.Sheets("Archive")
    If wsArchive Is Nothing Then
        Set wsArchive = ThisWorkbook.Sheets.Add(After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count))
        wsArchive.Name = "Archive"
        Call SetupArchiveHeaders(wsArchive)
    End If
    On Error GoTo 0
    
    lastRow = wsStaging.Cells(wsStaging.Rows.Count, "A").End(xlUp).Row
    commitCount = 0
    
    ' Get next archive row
    archiveRow = wsArchive.Cells(wsArchive.Rows.Count, "A").End(xlUp).Row + 1
    
    ' Process non-conflicted changes (A = 1)
    For stagingRow = 2 To lastRow
        If wsStaging.Cells(stagingRow, "A").Value = 1 Then
            antragNum = wsStaging.Cells(stagingRow, "E").Value
            
            ' Find corresponding row in main sheet
            Set foundCell = wsMain.Columns("A").Find(What:=antragNum, LookIn:=xlValues, LookAt:=xlWhole)
            
            If Not foundCell Is Nothing Then
                mainRow = foundCell.Row
                
                ' Archive the original data before updating
                Call ArchiveOriginalData(wsMain, wsArchive, mainRow, archiveRow, "AUTO_COMMIT", _
                                       wsStaging.Cells(stagingRow, "C").Value, _
                                       wsStaging.Cells(stagingRow, "D").Value)
                archiveRow = archiveRow + 1
                
                ' Update main sheet with staging data (E:AB -> A:AB)
                wsStaging.Range("E" & stagingRow & ":AB" & stagingRow).Copy
                wsMain.Cells(mainRow, "A").PasteSpecial Paste:=xlPasteValues
                Application.CutCopyMode = False
                
                ' Reset red highlights to original colors in main sheet
                Call ResetRedHighlights(wsMain, mainRow)
                
                ' Archive the new data
                Call ArchiveNewData(wsMain, wsArchive, mainRow, archiveRow, "AUTO_COMMIT", _
                                  wsStaging.Cells(stagingRow, "C").Value, _
                                  wsStaging.Cells(stagingRow, "D").Value)
                archiveRow = archiveRow + 1
                
                commitCount = commitCount + 1
            End If
        End If
    Next stagingRow
    
    ' Clean up committed entries from staging
    Call RemoveCommittedFromStaging(wsStaging)
    
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    
    MsgBox "Committed " & commitCount & " non-conflicted changes to main sheet." & vbCrLf & _
           "Original data archived for traceability." & vbCrLf & _
           "Committed entries removed from staging.", vbInformation, "Auto-Commit Complete"
End Sub

Sub MergeResolvedConflicts()
    Dim wsConflicts As Worksheet, wsMain As Worksheet, wsArchive As Worksheet
    Dim lastRow As Long, conflictRow As Long, mainRow As Long
    Dim antragNum As Variant
    Dim foundCell As Range
    Dim mergeCount As Long
    Dim archiveRow As Long
    Dim userName As String, userDate As Variant
    
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    
    Set wsConflicts = ThisWorkbook.Sheets("Conflicts")
    Set wsMain = ThisWorkbook.Sheets("Teile und Stoffe")
    
    ' Create Archive sheet if it doesn't exist
    On Error Resume Next
    Set wsArchive = ThisWorkbook.Sheets("Archive")
    If wsArchive Is Nothing Then
        Set wsArchive = ThisWorkbook.Sheets.Add(After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count))
        wsArchive.Name = "Archive"
        Call SetupArchiveHeaders(wsArchive)
    End If
    On Error GoTo 0
    
    lastRow = wsConflicts.Cells(wsConflicts.Rows.Count, "A").End(xlUp).Row
    mergeCount = 0
    
    ' Get next archive row
    archiveRow = wsArchive.Cells(wsArchive.Rows.Count, "A").End(xlUp).Row + 1
    
    ' Process resolved conflicts (D = 1)
    For conflictRow = 2 To lastRow
        If wsConflicts.Cells(conflictRow, "D").Value = 1 And _
           Not wsConflicts.Cells(conflictRow, "A").MergeCells Then
            
            antragNum = wsConflicts.Cells(conflictRow, "E").Value
            userName = wsConflicts.Cells(conflictRow, "B").Value
            userDate = wsConflicts.Cells(conflictRow, "C").Value
            
            ' Find corresponding row in main sheet
            Set foundCell = wsMain.Columns("A").Find(What:=antragNum, LookIn:=xlValues, LookAt:=xlWhole)
            
            If Not foundCell Is Nothing Then
                mainRow = foundCell.Row
                
                ' Archive the original data before updating
                Call ArchiveOriginalData(wsMain, wsArchive, mainRow, archiveRow, "CONFLICT_RESOLVED", userName, userDate)
                archiveRow = archiveRow + 1
                
                ' Update main sheet with selected conflict resolution (E:AB -> A:AB)
                wsConflicts.Range("E" & conflictRow & ":AB" & conflictRow).Copy
                wsMain.Cells(mainRow, "A").PasteSpecial Paste:=xlPasteValues
                Application.CutCopyMode = False
                
                ' Reset red highlights to original colors in main sheet
                Call ResetRedHighlights(wsMain, mainRow)
                
                ' Archive the new data
                Call ArchiveNewData(wsMain, wsArchive, mainRow, archiveRow, "CONFLICT_RESOLVED", userName, userDate)
                archiveRow = archiveRow + 1
                
                mergeCount = mergeCount + 1
            End If
        End If
    Next conflictRow
    
    ' Clean up resolved conflicts from conflicts sheet
    Call RemoveResolvedFromConflicts(wsConflicts)
    
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    
    MsgBox "Merged " & mergeCount & " resolved conflicts to main sheet." & vbCrLf & _
           "Original data archived for traceability." & vbCrLf & _
           "Resolved conflicts removed from conflicts sheet.", vbInformation, "Conflict Merge Complete"
End Sub

Sub SetupArchiveHeaders(ws As Worksheet)
    ' Setup archive sheet headers
    ws.Cells(1, 1).Value = "Timestamp"
    ws.Cells(1, 2).Value = "Action"
    ws.Cells(1, 3).Value = "User"
    ws.Cells(1, 4).Value = "User_Date"
    ws.Cells(1, 5).Value = "Record_Type"
    ws.Cells(1, 6).Value = "Antragnummer"
    
    ' Copy headers from main sheet (A:AB -> G:AI)
    Dim wsMain As Worksheet
    Set wsMain = ThisWorkbook.Sheets("Teile und Stoffe")
    wsMain.Range("A1:AB1").Copy
    ws.Cells(1, 7).PasteSpecial Paste:=xlPasteValues
    Application.CutCopyMode = False
    
    ' Format headers
    With ws.Range("A1:AI1")
        .Font.Bold = True
        .Interior.Color = RGB(217, 217, 217)
        .Borders.LineStyle = xlContinuous
    End With
    
    ' Auto-fit columns
    ws.Columns("A:AI").AutoFit
End Sub

Sub ArchiveOriginalData(wsMain As Worksheet, wsArchive As Worksheet, mainRow As Long, archiveRow As Long, action As String, userName As String, userDate As Variant)
    ' Archive original data before changes
    wsArchive.Cells(archiveRow, 1).Value = Now ' Timestamp
    wsArchive.Cells(archiveRow, 2).Value = action ' Action
    wsArchive.Cells(archiveRow, 3).Value = userName ' User
    wsArchive.Cells(archiveRow, 4).Value = userDate ' User Date
    wsArchive.Cells(archiveRow, 5).Value = "BEFORE" ' Record Type
    wsArchive.Cells(archiveRow, 6).Value = wsMain.Cells(mainRow, "A").Value ' Antragnummer
    
    ' Copy original data (A:AB -> G:AI)
    wsMain.Range("A" & mainRow & ":AB" & mainRow).Copy
    wsArchive.Cells(archiveRow, 7).PasteSpecial Paste:=xlPasteValues
    wsArchive.Cells(archiveRow, 7).PasteSpecial Paste:=xlPasteFormats
    Application.CutCopyMode = False
End Sub

Sub ArchiveNewData(wsMain As Worksheet, wsArchive As Worksheet, mainRow As Long, archiveRow As Long, action As String, userName As String, userDate As Variant)
    ' Archive new data after changes
    wsArchive.Cells(archiveRow, 1).Value = Now ' Timestamp
    wsArchive.Cells(archiveRow, 2).Value = action ' Action
    wsArchive.Cells(archiveRow, 3).Value = userName ' User
    wsArchive.Cells(archiveRow, 4).Value = userDate ' User Date
    wsArchive.Cells(archiveRow, 5).Value = "AFTER" ' Record Type
    wsArchive.Cells(archiveRow, 6).Value = wsMain.Cells(mainRow, "A").Value ' Antragnummer
    
    ' Copy new data (A:AB -> G:AI)
    wsMain.Range("A" & mainRow & ":AB" & mainRow).Copy
    wsArchive.Cells(archiveRow, 7).PasteSpecial Paste:=xlPasteValues
    wsArchive.Cells(archiveRow, 7).PasteSpecial Paste:=xlPasteFormats
    Application.CutCopyMode = False
End Sub



Sub ViewArchiveHistory()
    Dim wsArchive As Worksheet
    
    ' Check if Archive sheet exists
    On Error Resume Next
    Set wsArchive = ThisWorkbook.Sheets("Archive")
    On Error GoTo 0
    
    If wsArchive Is Nothing Then
        MsgBox "No archive data found. Archive sheet will be created when first changes are committed.", vbInformation
        Exit Sub
    End If
    
    ' Activate archive sheet
    wsArchive.Activate
    
    ' Auto-fit columns for better viewing
    wsArchive.Columns("A:AI").AutoFit
    
    MsgBox "Archive history displayed. Each change shows BEFORE and AFTER records for full traceability.", vbInformation
End Sub

Sub ResetRedHighlights(ws As Worksheet, targetRow As Long)
    ' Reset red highlights (RGB(255, 50, 50)) to original colors
    Dim col As Long
    Dim cell As Range
    
    For col = 1 To 28 ' A to AB
        Set cell = ws.Cells(targetRow, col)
        
        ' Check if cell has red highlighting from staging comparison
        If cell.Interior.Color = RGB(255, 50, 50) Then
            ' Reset to white background and black font
            cell.Interior.Color = RGB(255, 255, 255) ' White
            cell.Font.Color = RGB(0, 0, 0) ' Black
            
            ' Clear any conditional formatting
            cell.FormatConditions.Delete
        End If
    Next col
End Sub

Sub RemoveCommittedFromStaging(ws As Worksheet)
    ' Remove rows where A = 1 (committed changes)
    Dim lastRow As Long, stagingRow As Long
    
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    ' Work backwards to avoid row shifting issues
    For stagingRow = lastRow To 2 Step -1
        If ws.Cells(stagingRow, "A").Value = 1 Then
            ws.Rows(stagingRow).Delete
        End If
    Next stagingRow
End Sub

Sub RemoveResolvedFromConflicts(ws As Worksheet)
    ' Remove conflict groups that have been resolved (D = 1)
    Dim lastRow As Long, conflictRow As Long
    Dim groupsToDelete As Collection
    Dim i As Long
    
    Set groupsToDelete = New Collection
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    ' Identify conflict groups to delete
    For conflictRow = 2 To lastRow
        If ws.Cells(conflictRow, "D").Value = 1 And _
           Not ws.Cells(conflictRow, "A").MergeCells Then
            
            ' Find the start and end of this conflict group
            Dim groupStart As Long, groupEnd As Long
            groupStart = conflictRow
            groupEnd = conflictRow
            
            ' Find group boundaries
            For i = conflictRow - 1 To 2 Step -1
                If ws.Cells(i, "A").MergeCells Then
                    groupStart = i
                    Exit For
                End If
            Next i
            
            For i = conflictRow + 1 To lastRow
                If ws.Cells(i, "A").Value = "" And ws.Cells(i, "B").Value = "" Then
                    groupEnd = i - 1
                    Exit For
                ElseIf i = lastRow Then
                    groupEnd = i
                End If
            Next i
            
            ' Add to deletion list if not already added
            Dim found As Boolean
            found = False
            On Error Resume Next
            For i = 1 To groupsToDelete.Count
                If groupsToDelete(i) = groupStart Then
                    found = True
                    Exit For
                End If
            Next i
            On Error GoTo 0
            
            If Not found Then
                groupsToDelete.Add groupStart & ":" & groupEnd
            End If
        End If
    Next conflictRow
    
    ' Delete groups from bottom to top to avoid row shifting
    Dim deleteList As New Collection
    For i = 1 To groupsToDelete.Count
        deleteList.Add groupsToDelete(i)
    Next i
    
    ' Sort by start row (descending)
    Dim j As Long
    For i = 1 To deleteList.Count - 1
        For j = i + 1 To deleteList.Count
            Dim range1Start As Long, range2Start As Long
            range1Start = CLng(Split(deleteList(i), ":")(0))
            range2Start = CLng(Split(deleteList(j), ":")(0))
            If range1Start < range2Start Then
                Dim temp As String
                temp = deleteList(i)
                deleteList.Remove i
                deleteList.Add temp, , j
            End If
        Next j
    Next i
    
    ' Delete the ranges
    For i = 1 To deleteList.Count
        Dim rangeStr As String
        rangeStr = deleteList(i)
        Dim startRow As Long, endRow As Long
        startRow = CLng(Split(rangeStr, ":")(0))
        endRow = CLng(Split(rangeStr, ":")(1))
        ws.Range(startRow & ":" & endRow).Delete Shift:=xlUp
    Next i
End Sub 