import win32com.client
import pythoncom
import keyboard
import pygetwindow as gw
import os


def run():
    pythoncom.CoInitialize()
    xlApp = win32com.client.Dispatch("Excel.Application")

    #xlApp.Visible = True
    wb = xlApp.Workbooks.Open(r'C:\Users\u8064927\Desktop\Ali.xlsx')

    xlApp.ActiveWorkbook.Worksheets('Sheet1').Activate

    address = xlApp.ActiveCell.Address


    value = xlApp.ActiveCell.Value
    col = xlApp.ActiveCell.Column
    row = xlApp.ActiveCell.Row

    colorindex:int = int(xlApp.ActiveCell.Interior.Color)

    r = colorindex % 256
    g = (colorindex // 256) % 256
    b = (colorindex // 65536) % 256

    hexcolor = f"#{r:02X}{g:02X}{b:02X}"
    #print(f"#{r:02X}{g:02X}{b:02X}")


    xlApp = None


    if col == 2:
        #print(value)
        category, values_to_filter = categorize_length(value)
        print(category)

        if hexcolor == '#FFFFFF':
            print(row, col, value, hexcolor)
        else:
            color_code = f"\033[38;2;{r};{g};{b}m" # Construct ANSI escape code
            print(f"{color_code}{row}, {col}, {value}, {hexcolor}\033[0m")

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

def open_verzeichnis(values):

    pythoncom.CoInitialize()
    xlApp = win32com.client.Dispatch("Excel.Application")

    #xlApp.Visible = True
    wb2 = xlApp.Workbooks.Open(r'C:\Users\u8064927\Desktop\AliVerzeichnis.xlsb')
    ws2 = xlApp.ActiveWorkbook.Worksheets('Teile und Stoffe')



    ws2.Range('B1').AutoFilter(
            Field=2,  # Column B
            Criteria1=values,  # Multiple criteria
            Operator=7  # 7 corresponds to xlFilterValues (OR logic)
        )

    # Scroll to the top
    visible_cells = ws2.Range('B2:B' + str(ws2.Cells(ws2.Rows.Count, 'B').End(-4162).Row)).SpecialCells(12)  # 12 corresponds to xlCellTypeVisible

    # Find window by title
    window_title = wb2.name
    bring_window_to_front(window_title)
    
    # Bring the workbook and Excel application into focus
    #xlApp.ActiveWorkbook.Worksheets('Teile und Stoffe').Activate

    
    # Select the first visible cell
    if visible_cells:
        try:
            first_visible_cell = visible_cells.Item(1)  # Access the first visible cell
            first_visible_cell.Select()  # Select the first visible cell
        except Exception as e:
            print(f"Error selecting cell: {e}")
    else:
        print("No visible cells found.")
        
    fetch_filtered_data_from_A_to_AA(ws2)

def bring_window_to_front(window_title):
    # Get the currently active window
    active_window = gw.getActiveWindow()
    print(active_window)

    # Get all windows with the specified title
    windows = gw.getWindowsWithTitle(window_title)
    print(windows)

    if windows:
        win = windows[0]  # Get the first matching window
        if win.isMinimized:
            win.restore()  # Restore the window if it’s minimized
            
        # Bring the window to the front without restoring it if it’s already visible
        win.activate()  # Bring the window to the front
        print(f"'{window_title}' brought to the front.")
    else:
        print("Window not found.")

def fetch_filtered_data_from_A_to_AA(ws2):
    """
    Fetches the data from columns A to AA for each visible row in the filtered range.
    Avoids duplicate entries by focusing on rows only.
    """
    # Get the last used row in column B (which is the filter column)
    last_row = ws2.Cells(ws2.Rows.Count, 'B').End(-4162).Row  # Get last used row in column B
    
    # Get the filtered range in columns A to X
    filtered_range = ws2.Range(f'A2:AA{last_row}')
    
    # Find the visible cells (filtered, non-hidden)
    visible_cells = filtered_range.SpecialCells(12)  # 12 corresponds to xlCellTypeVisible
    
    data = []
    row_numbers = set()  # Use a set to track unique rows and avoid duplicates
    
    if visible_cells:
        for cell in visible_cells:
            row = cell.Row  # Get the row number for the visible cell
            
            # If this row is not already processed (avoiding duplicates)
            if row not in row_numbers:
                row_numbers.add(row)  # Mark this row as processed
                
                # Collect values from columns A to AA for this row
                row_data = ws2.Range(f'A{row}:AA{row}').Value  # Returns a tuple, so we use [0] to get the list
                
                # Handle hyperlinks in columns M to U
                for col in range(13, 22):  # Columns M to U (13 to 22)
                    cell = ws2.Cells(row, col)
                    try:
                        if cell.Hyperlinks.Count > 0:
                            links = cell.Hyperlinks(1)
                            hyperlink_url = links.Address
                            hyperlink_text = cell.Value
                            filepath = "P:\k-z\Ofs\Dokumentenservice\TeileundStoffe"
                            hyperlink = hyperlink_url.strip("..\\")
                            full_path = os.path.join(full_path, hyperlink_url)
                            print(full_path)
                            row_data[col - 1] = (full_path)
                        else: 
                            print(col, 'no hyperlinks found')
                    except:
                        pass

                data.append(row_data)
    
    print(data)
    print(len(data))
    
    with open('test.txt', 'w', encoding='utf-8') as f:
        f.write(str(data))

keyboard.add_hotkey('shift+alt+s', run)

# Keep the program running to listen for the hotkey press
print("Press 'shift+alt+s' to trigger the hotkey.")
keyboard.wait('esc')  # This will keep the program running until 'esc' is pressed
