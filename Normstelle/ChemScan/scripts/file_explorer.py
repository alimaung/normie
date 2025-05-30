import time
import win32gui
import win32con
import win32api
import subprocess
import os


def get_title(path): # which is path until folder
    parent = os.path.dirname(path)
    return parent

# Function to find the window by title
def find_window(ats):
    def enum_window(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            if str(ats) in win32gui.GetWindowText(hwnd).lower():
                windows.append(hwnd)
    windows = []
    win32gui.EnumWindows(enum_window, windows)
    return windows

# Function to get the monitor information
def get_monitors():
    monitors = []
    # Enumerate through display devices
    dev_enum = win32api.EnumDisplayMonitors()
    for monitor in dev_enum:
        # Get monitor info from each monitor
        monitor_info = win32api.GetMonitorInfo(monitor[0])
        monitors.append(monitor_info)
    return monitors

def move_windows(monitors, window1, window2):
    # Ensure there are at least 3 monitors connected
    if len(monitors) < 3:
        print("Error: Less than 3 monitors detected.")
    else:
        # Get monitor 3 (index 2)
        monitor = monitors[2]
        monitor_x = monitor['Monitor'][0]
        monitor_y = monitor['Monitor'][1]
        monitor_width = monitor['Monitor'][2] - monitor['Monitor'][0]
        monitor_height = monitor['Monitor'][3] - monitor['Monitor'][1]

        # Define the dimensions of the windows
        window_width = monitor_width // 2
        window_height = monitor_height // 2

        # Place the first window on the top left of monitor 3
        win32gui.MoveWindow(window1, monitor_x, monitor_y, window_width, window_height, True)

        # Place the second window directly below the first one
        win32gui.MoveWindow(window2, monitor_x, monitor_y + window_height, window_width, window_height, True)

        # Bring the windows to the front
        win32gui.ShowWindow(window1, win32con.SW_RESTORE)
        win32gui.ShowWindow(window2, win32con.SW_RESTORE)

def main(ats, sdb):
    # Launch two instances of File Explorer
    ats= r"C:\Users\u8064927\Desktop\Antrag_RRT129127.pdf"
    sdb= r"C:\Users\u8064927\Desktop\Antrag_RRT129127.pdf"

    subprocess.Popen(fr'explorer /select,{ats}')
    #subprocess.Popen(fr'explorer /select,{sdb}')
    #time.sleep(3)  # Wait for the second Explorer to open

    # Get the two explorer windows

    windows = find_window(ats)

    # Assume the first two found windows are the Explorer windows
    window1 = windows[0]
    window2 = windows[1]

    # Get the list of connected monitors
    monitors = get_monitors()

    move_windows(monitors, window1, window2)






