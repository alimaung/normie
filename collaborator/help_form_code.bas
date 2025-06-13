Private Sub btnClose_Click()
    Me.Hide
End Sub

Private Sub btnMoreHelp_Click()
    ' Get the context from the form's Tag property
    Dim context As String
    context = Me.Tag
    
    ' Close the current help form
    Me.Hide
    
    ' Open the comprehensive HTML help
    Call OpenMoreHelp(context)
    
    ' Close the form completely
    Unload Me
End Sub

Private Sub UserForm_QueryClose(Cancel As Integer, CloseMode As Integer)
    Me.Hide
    Cancel = True
End Sub
