import pygetwindow as gw

# Find window by title
window_title = "Verzeichnis.xlsb"
windows = gw.getWindowsWithTitle(window_title)

if windows:
    # Bring the first matching window to the front
    win = windows[0]
    win.restore()  # Restore the window if it’s minimized
else:
    print("Window not found.")
