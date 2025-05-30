from openpyxl import load_workbook
import win32com.client
import pythoncom
import keyboard
import pygetwindow as gw
import csv
from typing import List, Tuple, Optional, Dict

def on_hotkey(): 
    pythoncom.CoInitialize()
    xlApp = win32com.client.Dispatch("Excel.Application")
    #xlApp.Visible = True

    xlApp.Workbooks.Open(r'C:\Users\u8064927\Desktop\Ali.xlsx')

    xlApp.ActiveWorkbook.Worksheets('Sheet1').Activate
    cellRange = xlApp.ActiveCell.Address
    print(xlApp.ActiveCell.Address)
    
    xlApp = None

    if cellRange.Column == 2 and cellRange.value:
        rowNum = cellRange.row
        colNum = cellRange.column
        value = cellRange.value
        color = cellRange.color
        
        # Categorize the cell value length
        category, values_to_filter = categorize_length(value)
        # Print category for debugging purposes
        print(category)
        
        if color == None:
            print(rowNum, colNum, value, color)
        else:
            color_code = f"\033[38;2;{color[0]};{color[1]};{color[2]}m" # Construct ANSI escape code
            print(f"{color_code}{rowNum}, {colNum}, {value}, {color}\033[0m")
        
        open_verzeichnis(values_to_filter)    
    else:
        pass

def categorize_length(value):
    """
    Categorizes the cell value based on its length.
    Handles cases like:
    - Single value (length 8-10)
    - Double values (length between 8-10)
    - Triple values (length > 18)
    """
    # Remove leading/trailing spaces and split by commas if multiple values exist
    values = [v.strip() for v in value.split(',')]

    # Check the number of values and categorize them
    if len(values) == 1:
        return "Single value detected", values
    elif len(values) == 2:
        return "Double values detected", values
    elif len(values) > 2:
        return "Multiple values detected", values
    else:
        return "Invalid value format", []

def bring_window_to_front(window_title):
    # Get the currently active window
    active_window = gw.getActiveWindow()

    # Get all windows with the specified title
    windows = gw.getWindowsWithTitle(window_title)

    if windows:
        win = windows[0]  # Get the first matching window

        # Check if the window is already active
        if win == active_window:
            print(f"'{window_title}' is already the active window.")
        else:
            # If window is minimized, restore it
            if win.isMinimized:
                win.restore()  # Restore the window if it’s minimized
            
            # Bring the window to the front without restoring it if it’s already visible
            win.activate()  # Bring the window to the front
            print(f"'{window_title}' brought to the front.")
    else:
        print("Window not found.")

def open_verzeichnis(values):
    wb2 = load_workbook(r'P:\k-z\Ofs\Dokumentenservice\TeileundStoffe\Datei\Ali.xlsb')
    ws2 = wb2.sheets['Teile und Stoffe']
            
    ws2.range('B1').api.AutoFilter(
            Field=2,  # Column B
            Criteria1=values,  # Multiple criteria
            Operator=7  # 7 corresponds to xlFilterValues (OR logic)
        )

    # Scroll to the top
    visible_cells = ws2.range('B2:B' + str(ws2.api.Cells(ws2.api.Rows.Count, 'B').End(-4162).Row)).api.SpecialCells(12)  # 12 corresponds to xlCellTypeVisible

    # Find window by title
    window_title = wb2.name
    bring_window_to_front(window_title)
    
    # Bring the workbook and Excel application into focus
    wb2.app.activate()  # Activate Excel
    wb2.activate()  # Activate the workbook
    
    # Select the first visible cell
    if visible_cells:
        try:
            first_visible_cell = visible_cells.Item(1)  # Access the first visible cell
            first_visible_cell.Select()  # Select the first visible cell
        except Exception as e:
            print(f"Error selecting cell: {e}")
    else:
        print("No visible cells found.")
        
    fetch_filtered_data_from_A_to_X(ws2)

def fetch_filtered_data_from_A_to_X(ws2):
    """
    Fetches the data from columns A to X for each visible row in the filtered range.
    Avoids duplicate entries by focusing on rows only.
    """
    # Get the last used row in column B (which is the filter column)
    last_row = ws2.api.Cells(ws2.api.Rows.Count, 'B').End(-4162).Row  # Get last used row in column B
    
    # Get the filtered range in columns A to X
    filtered_range = ws2.range(f'A2:X{last_row}')
    
    # Find the visible cells (filtered, non-hidden)
    visible_cells = filtered_range.api.SpecialCells(12)  # 12 corresponds to xlCellTypeVisible
    
    data = []
    row_numbers = set()  # Use a set to track unique rows and avoid duplicates
    
    if visible_cells:
        for cell in visible_cells:
            row = cell.Row  # Get the row number for the visible cell
            
            # If this row is not already processed (avoiding duplicates)
            if row not in row_numbers:
                row_numbers.add(row)  # Mark this row as processed
                
                # Collect values from columns A to X for this row
                row_data = ws2.range(f'A{row}:X{row}').value  # Returns a tuple, so we use [0] to get the list
                
                # Handle hyperlinks in columns M to U
                for col in range(12, 21):  # Columns M to U (12 to 21)
                    cell = ws2.range(row, col)
                    try:
                        if cell.hyperlink.count > 0:  # Check if the cell contains any hyperlinks
                            # Get both the hyperlink URL and the text
                            hyperlink_url = cell.hyperlink[0].address
                            hyperlink_text = cell.value
                            row_data[col - 1] = (hyperlink_text, hyperlink_url)  # Replace the text with a tuple of (text, url)
                    except:
                        pass

                data.append(row_data)
    
    print(data)
    print(len(data))
    
    with open('test.txt', 'w', encoding='utf-8') as f:
        f.write(str(data))

keyboard.add_hotkey('shift+alt+s', on_hotkey)

# Keep the program running to listen for the hotkey press
print("Press 'shift+alt+s' to trigger the hotkey.")
keyboard.wait('esc')  # This will keep the program running until 'esc' is pressed
