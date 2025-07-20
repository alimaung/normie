' ThisOutlookSession Module
' This code should be placed in the ThisOutlookSession module in Outlook VBA
' It will automatically start email polling when Outlook starts

Option Explicit

' Automatically start email polling when Outlook starts
Private Sub Application_Startup()
    ' Start email polling automatically when Outlook starts
    StartEmailPolling
End Sub 