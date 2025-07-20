Sub BuildConflictsList()
    Dim wsStaging As Worksheet, wsConflicts As Worksheet, wsMain As Worksheet
    Dim lastRow As Long, conflictRow As Long
    Dim antragNum As Variant
    Dim dictConflicts As Object
    Dim i As Long, userRow As Variant
    Dim rowsColl As Collection
    Dim col As Long
    Dim srcRange As Range, destRange As Range, foundCell As Range

    Set wsStaging = ThisWorkbook.Sheets("Staging")
    Set wsConflicts = ThisWorkbook.Sheets("Conflicts")
    Set wsMain = ThisWorkbook.Sheets("Teile und Stoffe")

    ' Clear conflicts except header row 1 - preserve formatting in A:D but remove borders and reset colors
    With wsConflicts.Range("A2:D" & wsConflicts.Rows.Count)
        .ClearContents
        .Borders.LineStyle = xlNone
        .Interior.Color = RGB(242, 242, 242) ' White, Background 1, Darker 15%
        .UnMerge
    End With
    wsConflicts.Range("E2:AB" & wsConflicts.Rows.Count).Clear

    lastRow = wsStaging.Cells(wsStaging.Rows.Count, "A").End(xlUp).Row
    conflictRow = 2

    Set dictConflicts = CreateObject("Scripting.Dictionary")

    ' Collect conflict Antragnummers (A=0)
    For i = 2 To lastRow
        If wsStaging.Cells(i, "A").Value = 0 Then
            antragNum = wsStaging.Cells(i, "E").Value
            If Not dictConflicts.Exists(antragNum) Then
                Set dictConflicts(antragNum) = New Collection
            End If
            dictConflicts(antragNum).Add i ' store staging row number
        End If
    Next i

    ' Write conflicts vertically
    For Each antragNum In dictConflicts.Keys
        Set rowsColl = dictConflicts(antragNum)
        Dim groupStartRow As Long
        groupStartRow = conflictRow

        ' First add the ORIGINAL row from main sheet
        Set foundCell = wsMain.Columns("A").Find(What:=antragNum, LookIn:=xlValues, LookAt:=xlWhole)
        If Not foundCell Is Nothing Then
            Dim mainRow As Long
            mainRow = foundCell.Row
            
            ' Merge A:C and write "ORIGINAL", put helper text in D
            wsConflicts.Range("A" & conflictRow & ":C" & conflictRow).Merge
            wsConflicts.Cells(conflictRow, "A").Value = "ORIGINAL"
            wsConflicts.Cells(conflictRow, "A").HorizontalAlignment = xlCenter
            wsConflicts.Cells(conflictRow, "A").Font.Bold = True
            wsConflicts.Cells(conflictRow, "D").Value = "Select"
            wsConflicts.Cells(conflictRow, "D").HorizontalAlignment = xlCenter
            wsConflicts.Cells(conflictRow, "D").Font.Italic = True
            
            ' Copy original data from main sheet (A:AB to E:AB in conflicts)
            Set srcRange = wsMain.Range(wsMain.Cells(mainRow, "A"), wsMain.Cells(mainRow, "AB"))
            Set destRange = wsConflicts.Range(wsConflicts.Cells(conflictRow, "E"), wsConflicts.Cells(conflictRow, "AB"))
            srcRange.Copy
            destRange.PasteSpecial Paste:=xlPasteAllUsingSourceTheme
            Application.CutCopyMode = False
            
            conflictRow = conflictRow + 1
        End If

        ' Loop through all user rows for this conflict vertically
        For Each userRow In rowsColl
            ' Copy B:D from staging to A:C in conflicts (ID, Name, Date)
            wsConflicts.Cells(conflictRow, "A").Value = wsStaging.Cells(userRow, "B").Value ' ID
            wsConflicts.Cells(conflictRow, "B").Value = wsStaging.Cells(userRow, "C").Value ' Name
            wsConflicts.Cells(conflictRow, "C").Value = wsStaging.Cells(userRow, "D").Value ' Date
            
            ' Leave column D empty for user resolution with background color and data validation
            wsConflicts.Cells(conflictRow, "D").Value = ""
            wsConflicts.Cells(conflictRow, "D").Interior.Color = RGB(217, 217, 217) ' White, Background 1, Darker 25%
            
            ' Add data validation for binary selection
            With wsConflicts.Cells(conflictRow, "D").Validation
                .Delete
                .Add Type:=xlValidateList, AlertStyle:=xlValidAlertStop, _
                     Formula1:="1,0"
                .IgnoreBlank = True
                .InCellDropdown = True
                .InputTitle = "Select Version"
                .InputMessage = "Choose 1 to select this version for merge, or 0 to reject it"
                .ErrorTitle = "Invalid Selection"
                .ErrorMessage = "Please select either 1 (accept) or 0 (reject)"
            End With

            ' Copy E:AB with full formatting (like staging does)
            Set srcRange = wsStaging.Range(wsStaging.Cells(userRow, "E"), wsStaging.Cells(userRow, "AB"))
            Set destRange = wsConflicts.Range(wsConflicts.Cells(conflictRow, "E"), wsConflicts.Cells(conflictRow, "AB"))
            srcRange.Copy
            destRange.PasteSpecial Paste:=xlPasteAllUsingSourceTheme
            Application.CutCopyMode = False

            conflictRow = conflictRow + 1
        Next userRow

        ' Add thick border around the entire conflict group
        Dim groupEndRow As Long
        groupEndRow = conflictRow - 1
        With wsConflicts.Range("A" & groupStartRow & ":AB" & groupEndRow)
            .BorderAround LineStyle:=xlContinuous, Weight:=xlThick, ColorIndex:=xlAutomatic
        End With

        ' Empty row after each group
        conflictRow = conflictRow + 1
    Next antragNum
End Sub




Sub ClearConflictsArea()
    Dim ws As Worksheet
    Dim answer As VbMsgBoxResult
    
    answer = MsgBox("Are you sure you want to clear the conflicts area?", vbYesNo + vbExclamation, "Confirm Clear")
    If answer <> vbYes Then Exit Sub
    
    Set ws = ThisWorkbook.Sheets("Conflicts")
    
    ' Clear contents, borders, and reset colors from columns A to D, starting from row 2
    With ws.Range("A2:D" & ws.Rows.Count)
        .ClearContents
        .Borders.LineStyle = xlNone
        .Interior.Color = RGB(242, 242, 242) ' White, Background 1, Darker 15%
        .UnMerge
    End With
    
    ' Clear everything (contents + formatting) from column E onward, starting from row 2
    ws.Range("E2:AB" & ws.Rows.Count).Clear
End Sub

' Function to enforce binary selection - only one ✓ per conflict group
Sub EnforceBinarySelection(ByVal Target As Range)
    Dim ws As Worksheet
    Dim conflictStartRow As Long, conflictEndRow As Long
    Dim i As Long
    Dim currentRow As Long
    
    ' Only process single cell changes in column D
    If Target.Cells.Count > 1 Then Exit Sub
    If Target.Column <> 4 Then Exit Sub
    
    ' Check if value is 1, 0, or empty (handle potential errors)
    Dim selectedValue As String
    On Error GoTo ErrorHandler
    selectedValue = Trim(CStr(Target.Value))
    If selectedValue <> "1" And selectedValue <> "0" And selectedValue <> "" Then Exit Sub
    On Error GoTo 0
    
    Set ws = Target.Worksheet
    currentRow = Target.Row
    
    ' Find the conflict group boundaries by looking for thick borders
    conflictStartRow = currentRow
    conflictEndRow = currentRow
    
    ' Find start of group (look upward for thick border or merged cell)
    For i = currentRow - 1 To 2 Step -1
        If ws.Cells(i, "A").MergeCells Or _
           ws.Range("A" & i & ":AB" & i).Borders(xlEdgeTop).Weight = xlThick Then
            conflictStartRow = i + 1
            Exit For
        End If
        If ws.Cells(i, "A").Value = "" And ws.Cells(i, "B").Value = "" Then
            conflictStartRow = i + 1
            Exit For
        End If
    Next i
    
    ' Find end of group (look downward for empty row or thick border)
    For i = currentRow + 1 To ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
        If ws.Cells(i, "A").Value = "" And ws.Cells(i, "B").Value = "" Then
            conflictEndRow = i - 1
            Exit For
        End If
        If ws.Range("A" & i & ":AB" & i).Borders(xlEdgeBottom).Weight = xlThick Then
            conflictEndRow = i
            Exit For
        End If
    Next i
    
    ' Disable events to prevent infinite loop
    Application.EnableEvents = False
    
    ' Handle different selection scenarios
    If selectedValue = "1" Or selectedValue = "0" Then
        ' Set opposite values for all other rows in this conflict group (except ORIGINAL row)
        Dim oppositeValue As String
        oppositeValue = IIf(selectedValue = "1", "0", "1")
        
        For i = conflictStartRow To conflictEndRow
            If i <> currentRow And Not ws.Cells(i, "A").MergeCells Then
                ws.Cells(i, "D").Value = oppositeValue
            End If
        Next i
    ElseIf selectedValue = "" Then
        ' If current cell is cleared, clear all other cells in the group too
        For i = conflictStartRow To conflictEndRow
            If i <> currentRow And Not ws.Cells(i, "A").MergeCells Then
                ws.Cells(i, "D").Value = ""
            End If
        Next i
    End If
    
    ' Apply visual formatting to all rows in the conflict group
    For i = conflictStartRow To conflictEndRow
        If Not ws.Cells(i, "A").MergeCells Then ' Skip ORIGINAL row
            Dim rowValue As String
            rowValue = Trim(CStr(ws.Cells(i, "D").Value))
            
            ' Apply background color, but preserve red highlighting from changes
            Dim cell As Range
            For Each cell In ws.Range("E" & i & ":AB" & i)
                ' Check if this cell has red highlighting (change indicator)
                Dim isRedHighlight As Boolean
                isRedHighlight = (cell.Interior.Color = RGB(255, 50, 50)) ' Red highlighting from staging
                
                ' Skip red highlighted cells
                If Not isRedHighlight Then
                    Dim currentColor As Long
                    currentColor = cell.Interior.Color
                    
                    ' Check if we need to store the original color (first time changing)
                    Dim storedColor As Long
                    storedColor = GetStoredOriginalColor(cell)
                    
                    ' If no stored color and current color is one of the originals, store it
                    If storedColor = -1 Then
                        If currentColor = RGB(255, 204, 153) Or _
                           currentColor = RGB(204, 255, 204) Or _
                           currentColor = RGB(204, 255, 153) Or _
                           currentColor = RGB(255, 255, 255) Then
                            Call StoreOriginalColor(cell, currentColor)
                        End If
                    End If
                    
                    ' Apply the selection color
                    If rowValue = "1" Then
                        ' Selected: Green background
                        cell.Interior.Color = RGB(144, 238, 144) ' Light green
                    ElseIf rowValue = "0" Then
                        ' Rejected: Light red background
                        cell.Interior.Color = RGB(255, 182, 193) ' Light red
                    Else
                        ' Reset: Restore original background color
                        storedColor = GetStoredOriginalColor(cell)
                        If storedColor <> -1 Then
                            cell.Interior.Color = storedColor
                            Call ClearStoredColor(cell)
                        End If
                    End If
                End If
            Next cell
        End If
    Next i
    
    ' Re-enable events
    Application.EnableEvents = True
    Exit Sub
    
ErrorHandler:
    ' Handle any type conversion errors silently and re-enable events
    Application.EnableEvents = True
    Exit Sub
End Sub


' Helper function to store original color in cell comment
Sub StoreOriginalColor(cell As Range, originalColor As Long)
    On Error Resume Next
    ' Clear existing comment
    If Not cell.Comment Is Nothing Then
        cell.Comment.Delete
    End If
    ' Store color as comment text
    cell.AddComment "OrigColor:" & CStr(originalColor)
    cell.Comment.Visible = False
    On Error GoTo 0
End Sub

' Helper function to get stored original color from cell comment
Function GetStoredOriginalColor(cell As Range) As Long
    On Error Resume Next
    If Not cell.Comment Is Nothing Then
        Dim commentText As String
        commentText = cell.Comment.Text
        If Left(commentText, 10) = "OrigColor:" Then
            GetStoredOriginalColor = CLng(Mid(commentText, 11))
            Exit Function
        End If
    End If
    On Error GoTo 0
    GetStoredOriginalColor = -1 ' Not found
End Function

' Helper function to clear stored color comment
Sub ClearStoredColor(cell As Range)
    On Error Resume Next
    If Not cell.Comment Is Nothing Then
        If Left(cell.Comment.Text, 10) = "OrigColor:" Then
            cell.Comment.Delete
        End If
    End If
    On Error GoTo 0
End Sub