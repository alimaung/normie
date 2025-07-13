import win32gui as wg
import win32con
import win32api
import win32ui
import time
import subprocess
import psutil
import pygetwindow as gw
import pypdf as pp

def find_first_window():
    while True:
        #a = gw.getWindowsWithTitle("File Classifier")
        a = wg.FindWindow(None, "File Classifier")
        print(f"{a}")
        if a: return a
        time.sleep(0.5)

def find_second_window(x):
    while True:
        #b = gw.getWindowsWithTitle("File Classifier")
        b = wg.FindWindow(None, "File Classifier")
        if b != x and b != []:
            print(f"{b}")
            return b
        time.sleep(0.5)

# calculate relative position
def get_relative_mouse_position(hwnd):
    # Get window's top-left position
    window_rect = wg.GetWindowRect(hwnd)  # (left, top, right, bottom)
    
    # Get current mouse position (absolute screen coordinates)
    mouse_x, mouse_y = win32api.GetCursorPos()
    
    # Convert to relative position inside the window
    relative_x = mouse_x - window_rect[0]  # Subtract window's left position
    relative_y = mouse_y - window_rect[1]  # Subtract window's top position

    return relative_x, relative_y

def click_relative(hwnd, rel_x, rel_y):
    # Get window's top-left position
    window_rect = wg.GetWindowRect(hwnd)  # (left, top, right, bottom)
    
    # Convert relative position to absolute screen coordinates
    abs_x = window_rect[0] + rel_x
    abs_y = window_rect[1] + rel_y

    # Move the cursor to the absolute position
    win32api.SetCursorPos((abs_x, abs_y))
    time.sleep(0.1)  # Small delay to ensure the cursor is in place

    # Simulate a left mouse click
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, abs_x, abs_y, 0, 0)
    time.sleep(0.05)  # Short delay for realism
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, abs_x, abs_y, 0, 0)

    print(f"Clicked at relative position ({rel_x}, {rel_y}) → Absolute ({abs_x}, {abs_y})")

def monitor_explorer_subprocess(subprocess_name="File Classified"):
    # Monitor the explorer process for subprocesses
    for proc in psutil.process_iter(['pid', 'name', 'parent']):
        if proc.info['name'] == 'explorer.exe':
            for child in proc.children():
                if subprocess_name.lower() in child.info['name'].lower():
                    print(f"Found '{subprocess_name}' under explorer.exe with PID {child.info['pid']}")
                    return child
    return None

def set_classification(hwnd):
    click_relative(hwnd, 434, 63)
    time.sleep(0.1)
    click_relative(hwnd, 451, 157)
    time.sleep(0.1)
    click_relative(hwnd, 363, 404)



def get_metadata(file):
    with open(file, "rb") as pdf:
        reader = pp.PdfReader(pdf)
        meta = reader.metadata
        keywords = meta.get('/Keywords', 'Not found')
        if keywords == "Not found":
            print("NEED CLASSIFICATION")
            return False
        else:
            print("ALREADY CLASSIFIED")
            return True

def classify(classified, file):
    if classified == False:
        exe = r"C:\Program Files\Boldon James\File Classifier\x86\FileClassifier.exe"
        result = subprocess.Popen([exe, file], shell=True)

        x = find_first_window()
        hwnd = find_second_window(x)

        if hwnd:
            relative_x, relative_y = get_relative_mouse_position(hwnd)
            print(f"Mouse position relative to window: ({relative_x}, {relative_y})")
            time.sleep(0.1)
            set_classification(hwnd)
            while wg.IsWindow(hwnd):
                time.sleep(1)
            print("DONE!")
            classified = True
            time.sleep(2)
            return classified

        else:
            print("Window not found!")
    elif classified == True:
        return classified
    else:
        print("error")

def main(file):

    classified = get_metadata(file)
    state = classify(classified, file)
    return state

if __name__ == "__main__":
    main()