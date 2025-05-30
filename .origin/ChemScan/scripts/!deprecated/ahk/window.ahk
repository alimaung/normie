#Persistent  ; Keep the script running

; Hotkey to bring Excel to the front (Ctrl + Alt + E)
^!e::
{
    ; Find the Excel window by its title or class
    IfWinExist, Verzeichnis.xlsb
    {
        ; Activate the Excel window and bring it to the front
        WinActivate
    }
    else
    {
        MsgBox, Excel is not running.
    }
}
return

^!f::
{
    ; Find the Excel window by its title or class
    IfWinExist, ChemScan1.xlsm
    {
        ; Activate the Excel window and bring it to the front
        WinActivate
    }
    else
    {
        MsgBox, Excel is not running.
    }
}
return