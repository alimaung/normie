Private Sub Worksheet_Change(ByVal Target As Range)
    Dim wbMain As Workbook
    Dim wsMain As Worksheet
    Dim wsThis As Worksheet
    Dim searchVal As String
    Dim foundCell As Range
    Dim copyRange As Range
    Dim pasteRange As Range
    Dim mainPath As String
    
    On Error GoTo CleanExit
    ' Only act if change was in one cell in column A
    If Target.CountLarge > 1 Then Exit Sub
    If Intersect(Target, Me.Range("A:A")) Is Nothing Then Exit Sub
    If Target.Value = "" Then Exit Sub
    
    Application.EnableEvents = False
    Application.ScreenUpdating = False
    
    searchVal = Target.Value
    Set wsThis = Me
    
    ' Path to the main workbook - update if needed
    mainPath = ThisWorkbook.Path & "\Verzeichnis.xlsb"
    
    ' Try to open main workbook if not already open
    On Error Resume Next
    Set wbMain = Workbooks("Verzeichnis.xlsb")
    On Error GoTo CleanExit
    
    If wbMain Is Nothing Then
        Set wbMain = Workbooks.Open(mainPath, ReadOnly:=True)
        wbMain.Windows(1).Visible = False
    End If
    
    Set wsMain = wbMain.Sheets("Teile und Stoffe")
    
    ' Search for Antrag-nummer in column A of main sheet
    Set foundCell = wsMain.Columns("A").Find(What:=searchVal, LookIn:=xlValues, LookAt:=xlWhole)
    
    If Not foundCell Is Nothing Then
        ' Copy columns A:AA from main sheet row foundCell.Row
        Set copyRange = wsMain.Range("A" & foundCell.Row & ":AA" & foundCell.Row)
        Set pasteRange = wsThis.Range("A" & Target.Row)
        
        ' Copy values and formats
        copyRange.Copy
        pasteRange.PasteSpecial Paste:=xlPasteAll
        Application.CutCopyMode = False
        wsThis.Cells(Target.Row, "AB").Value = 0
    Else
        MsgBox "Antragnummer '" & searchVal & "' not found in main workbook.", vbExclamation
    End If

CleanExit:
    Application.EnableEvents = True
    Application.ScreenUpdating = True
End Sub




