import win32com.client
import pythoncom
import keyboard
import pygetwindow as gw
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import logging
from pathlib import Path
import csv
import subprocess
import os
import pyperclip
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import win32gui as wg
import win32con
import win32api
import psutil
import pypdf as pp

# Configure logging module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s - %(lineno)d'
)
logger = logging.getLogger(__name__)

# Constants
EXCEL_FILES = {
    'chemscan': Path(r'C:\Users\u8064927\Desktop\Rolls-Royce X Ali\.coding\Normstelle\ChemScan\xls\#ChemScan.xlsx'),
    'verzeichnis': Path(r'C:\Users\u8064927\Desktop\Rolls-Royce X Ali\.coding\Normstelle\ChemScan\xls\#Verzeichnis.xlsb'),
    #'chemscan': Path(r'C:\Users\u8064927\Desktop\#ChemScan.xlsx'),         # WARNING: LIVE-DIRECTORY
    #'verzeichnis': Path(r'C:\Users\u8064927\Desktop\#Verzeichnis.xlsb')    # WARNING: LIVE-DIRECTORY
}

HOTKEY_COMBINATION = 'shift+alt+s'
EXIT_KEY = 'esc'
HYPERLINK_COLUMNS = 'MNOPQRSTU'  # Columns M to U
DATA_FOLDER = r'C:\Users\u8064927\Desktop\Rolls-Royce X Ali\.coding\Normstelle\ChemScan\scripts\data\data.csv'

@dataclass
class CellData:
    """Data class to store cell information"""
    row: int
    column: int
    value: str
    color: Optional[tuple]

class WindowManager:
    @staticmethod
    def bring_window_to_front(window_title: str) -> None:
        """Brings the specified window to the front if it exists."""
        # window is active before already
        #active_window = gw.getActiveWindow()
        windows = gw.getWindowsWithTitle(window_title)

        if not windows:
            logger.warning(f"Window '{window_title}' not found.")
            return

        #  already active, cancelled 
        target_window = windows[0]
        #if target_window == active_window:
        #    logger.info(f"'{window_title}' is already the active window.")
        #    return

        if target_window.isMinimized:
            target_window.restore()
        #target_window.activate()
        logger.info(f"'{window_title}' brought to the front.")

class ExcelDataProcessor:
    def __init__(self):
        self.excel = win32com.client.Dispatch("Excel.Application")
        self.verzeichnis_sheet = None

    def _get_cell_hyperlink(self, cell) -> Optional[str]:
        """Extracts hyperlink from a cell if it exists."""
        try:
            if cell.Hyperlinks.Count > 0:
                address = cell.Hyperlinks(cell.Hyperlinks.Count).Address # get latest link always
                if address.startswith('..'):
                    wb_path = Path(cell.Parent.Parent.Path)
                    #print(wb_path)
                    try:
                        absolute_path = wb_path / address.replace('\\', '/')
                        return str(absolute_path.resolve())
                    except:
                        return address
                return address
            return None
        except Exception:
            return None

    def _process_cell_value(self, value: any) -> str:
        """Processes cell value to ensure proper string formatting."""
        if value is None:
            return ""
        # Convert numbers to strings without decimal places if they're whole numbers
        if isinstance(value, (int, float)):
            if float(value).is_integer():
                return str(int(value))
            return str(value)
        return str(value)
    
    def generate_col_idx(self, index):
        letter = ""
        while index >= 0:
            letter = chr(65 + (index % 26)) + letter
            index = index // 26 - 1
        return letter

    def _get_row_data(self, worksheet, row: int) -> List[str]:
        """Gets values and hyperlinks for a single row, combining them where applicable."""
        row_values = []
        
        # Process columns A to X
        for col_idx in range(27):  # A to X (0 to 23)
            col_letter = self.generate_col_idx(col_idx)  # Convert number to letter (A=65 in ASCII)
            cell = worksheet.Range(f'{col_letter}{row}')
            value = self._process_cell_value(cell.Value)
            
            # For columns M to U, check for hyperlinks
            if col_letter in HYPERLINK_COLUMNS:
                hyperlink = self._get_cell_hyperlink(cell)
                if hyperlink:
                    # Only add hyperlink if the cell has a value
                    if value.strip():
                        value = f"{value} | {hyperlink}"
                    else:
                        value = hyperlink
            
            row_values.append(value)
        
        return row_values

    def _get_headers(self, worksheet) -> List[str]:
        """Gets the header row from the worksheet."""
        headers = worksheet.Range('A1:AA1').Value[0]  # Value returns a 2D array
        return [self._process_cell_value(header) for header in headers]

    def fetch_filtered_data(self, worksheet) -> Tuple[List[str], List[List[str]]]:
        """Fetches filtered data from columns A to AA including hyperlinks."""
        try:
            headers = self._get_headers(worksheet)
            last_row = worksheet.Cells(worksheet.Rows.Count, 'B').End(-4162).Row  # xlUp
            filtered_range = worksheet.Range(f'A2:AA{last_row}')
            visible_cells = filtered_range.SpecialCells(12)  # xlCellTypeVisible

            data = []
            row_numbers = set()

            if visible_cells:
                for cell in visible_cells:
                    row = cell.Row
                    if row not in row_numbers:
                        row_numbers.add(row)
                        row_data = self._get_row_data(worksheet, row)
                        data.append(row_data)

            logger.info(f"Fetched {len(data)} rows of filtered data with hyperlinks")
            return headers, data

        except Exception as e:
            logger.error(f"Error fetching filtered data: {e}")
            return [], []

    def process_verzeichnis(self, filter_values: List[str]) -> None:
        """Opens and processes the Verzeichnis workbook."""
        try:
            pythoncom.CoInitialize()
            self.excel = win32com.client.GetObject(None, "Excel.Application")

            wb = self.excel.Workbooks.Open(str(EXCEL_FILES['verzeichnis']))
            self.verzeichnis_sheet = wb.Sheets['Teile und Stoffe']

            # Apply filter
            self.verzeichnis_sheet.Range('B1').AutoFilter(
                Field=2,
                Criteria1=filter_values,
                Operator=7  # xlFilterValues (OR logic)
            )

            # Get visible cells and select first one
            last_row = self.verzeichnis_sheet.Cells(self.verzeichnis_sheet.Rows.Count, 'B').End(-4162).Row
            visible_cells = self.verzeichnis_sheet.Range(f'V2:V{last_row}').SpecialCells(12)
 
            # Focus Verzeichnis
            WindowManager.bring_window_to_front(wb.Name)

            if visible_cells:
                visible_cells.Item(1).Select()
                logger.debug(f"\033[33{visible_cells}\033m")

                headers, filtered_data = self.fetch_filtered_data(self.verzeichnis_sheet)
                self._save_data_to_csv(headers, filtered_data)
                    
        except Exception as e:
            logger.error(f"Error processing Verzeichnis: {e}")

    def _save_data_to_csv(self, headers: List[str], data: List[List[str]]) -> None:
        """Saves the filtered data to a CSV file with proper handling of special characters."""
        try:
            # Remove newlines in each cell of data
            headers = [header.replace("\n", "").replace("\r", "") for header in headers]
            
            cleaned_data = []
            for row in data:
                cleaned_row = [cell.replace("\n", "").replace("\r", "") for cell in row]
                cleaned_data.append(cleaned_row)
            
            with open(DATA_FOLDER, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, 
                                  delimiter='\t',
                                  quotechar='"',
                                  quoting=csv.QUOTE_ALL)
                writer.writerow(headers)
                writer.writerows(cleaned_data)
            logger.info("Data successfully saved to filtered_data.csv")

            print(f"CLEANED_DATA: {cleaned_data}")
            #self.open_files_in_explorer(cleaned_data)
            self.handle_browser_operation(cleaned_data)
            

        except Exception as e:
            logger.error(f"Error saving data to CSV: {e}")

    def handle_browser_operation(self, cleaned_data):
        proc_data = self.filter(cleaned_data)
        self.cs_control(proc_data)


    def open_files_in_explorer(self, data: List[List[str]]):
        """Opens the links for Anträge und SDB in the file explorer
           Col 13 Antrag, Col 16 SDB
        """

        # TODO: Verify links
        try:
            for row in data:
                try:
                    ats = row[12].split("|")[1].replace("\\\\dehesdna-a009a\\projekte", "P:") # Get filepath
                    ats_raw = row[12].split("|")[1] # Get filepath
                    ats_path = Path(fr"{ats_raw}")
                    if ats_path.exists():
                        logger.error(f"Datei nicht gefunden!: {ats_raw}")
                    else:
                        #subprocess.Popen(fr'explorer /select,{ats}')
                        subprocess.Popen(fr'explorer {ats}')
                        print(f"ATS: {ats}")
                except Exception as e:
                    logger.error(f"Kein AT&S gefunden!: {e}")
                
                try:
                    sdb = row[17].split("|")[1].replace("\\\\dehesdna-a009a\\projekte", "P:")
                    if os.path.exists(sdb):
                        logger.error(f"Datei nicht gefunden!: {ats}")
                    else:
                        #subprocess.Popen(fr'explorer /select,{sdb}')
                        subprocess.Popen(fr'explorer {sdb}')
                        print(f"SDB: {sdb}")
                except Exception as e:
                    logger.error(f"Kein ChemScan gefunden!: {e}")

        except Exception as e:
            logger.error(f"Error opening files: {e}")

    def driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=chrome_options)
        driver.switch_to.window(driver.window_handles[-1]) # Pinned ChemScan
        return driver

    def filter(self, data):
        proc_data = []
        for row in data:
            ats = row[12].split("|")[1].replace("\\\\dehesdna-a009a\\projekte", "P:").strip()
            sdb = row[17].split("|")[1].replace("\\\\dehesdna-a009a\\projekte", "P:").strip()


            tkz = row[1]
            id = row[0].replace("/", "-")
            loc = row[10]

            ats_comment = "AT&S_" + id + "_" + tkz + "_" + loc
            sdb_comment = "ChemScan_" + id + "_" + tkz + "_" + loc

            dict = {}
            dict["id"] = id
            dict["tkz"] = tkz
            dict["ats"] = ats
            dict["sdb"] = sdb
            dict["loc"] = loc
            dict["ats_comment"] = ats_comment
            dict["sdb_comment"] = sdb_comment
            dict["exists"] = None
            dict["pdf"] = None
            dict["class"] = None

            proc_data.append(dict)

            
 
    def open_chem(self, driver, data):
    # Detect interne Bezeichnung button

        tkz = data["tkz"]
        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]'))) 
            intern_btn = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]')
            intern_btn.click()
            #print("FULL XPATH")
        except Exception as e:

            print(f"FAILED CSS_SELECTOR: {e}")

        # enter tkz
        tkz_input = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/input[1]')
        tkz_input.send_keys(tkz)

        # send tkz
        send = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/button')
        send.click()

        time.sleep(1)

        # TODO: what behaviour to set for several rows? open each in a new tab? 
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/a'))) 
        three_dot = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/a')
        hover = ActionChains(driver).move_to_element(three_dot)
        hover.perform()

        # eye
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/ul/li[2]/ul/li[4]/a'))) 
        eye = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/ul/li[2]/ul/li[4]/a')
        eye.click()

        # Scroll to bottom
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[1]/nav/a[12]'))) 
        info = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[1]/nav/a[12]')
        info.click()

        # Detect entries of requests and safety
        nothing = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[2]/div/div/div[12]/div[2]/div/div/div/div/div/div/div[2]/div/div/div/div[2]/div[3]/p')
        if nothing.text == "Keine Einträge gefunden": print("nothing found")
        else: print("something there")

        return driver

    def upload_files(self, driver, data):
        # ats, ats comment
        # sdb, sdb comment


        for row in data:
            # write the comment 
            # TODO: comment string generation based on file

            keys = [(data["ats"], data["ats_comment"]), (data["sdb"], data["sdb_comment"])]

            for value_key, comment_key in keys:
                # click upload an attachment btn
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[2]/div[2]/a')))
                driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[2]/div[2]/a').click()

                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea")))
                driver.find_element(By.XPATH, '/html/body/div[9]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea').send_keys(comment_key, "TEST")

                # attach the file
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "uploader.empty.input-widget-file")))
                driver.find_element(By.CLASS_NAME, "uploader.empty.input-widget-file").click()

                # Find the file dialog window
                def find_window():
                    while True:
                        hwnd = wg.FindWindow(None, "Open")  # The title of the file dialog window
                        if hwnd: return hwnd
                        time.sleep(0.5)
                hwnd = find_window()

                time.sleep(1)
                
                # Find the edit box where the file path is entered
                edit_box = wg.FindWindowEx(hwnd, 0, "ComboBoxEx32", None)
                edit_box = wg.FindWindowEx(edit_box, 0, "ComboBox", None)
                edit_box = wg.FindWindowEx(edit_box, 0, "Edit", None)

                # Set the file path
                wg.SendMessage(edit_box, win32con.WM_SETTEXT, None, value_key)

                # Find and click the "Open" button
                open_button = wg.FindWindowEx(hwnd, 0, "Button", "&Open")
                wg.SendMessage(hwnd, win32con.WM_COMMAND, 1, open_button)

                # detect change of file name in html
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]")))
                datei = driver.find_element(By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]")
                initial_text = datei.text

                # save when the initial string changes
                WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]").text != initial_text)
                driver.find_element(By.XPATH, '/html/body/div[9]/div[13]/div/div/div/span[2]/button').click()

                # detect upload state success/fail
                WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[1]/div/div/div')))
                fail = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[1]/div/div/div/div')
                if fail.text == "Attachment created successfully": print("UPLOAD SUCCESS")
                elif fail.text == "Sie haben keine Berechtigung um diese Aktion auszuführen.": print("UPLOAD FAILED")
                else: print("ALERT NOT FOUND")
                print(fail.text)

            return driver

    def reset(self, driver):
        # back to home
        driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div/div/a').click()

        # reset the filter (not nessessarily)
        #WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]/span/span/span")))
        #driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]/span/span/span').click()

        # wait until page load
        WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.XPATH, '/html/body/div[10]')))

    def preprocess_data(self, list):
        print(f"list: {list}")
        for row in list:
            print(f"row: {row}")
            tkz = row["tkz"]
            paths = []
            for key, value in row.items():
                if key in ["ats", "sdb"]: # filepaths

                    # 1. Check if file exists
                    if os.path.isfile(value) is True:
                        print(f"file {key}: {value} exists")
                        row["exists"] = True
                    else:
                        print(f"file {key}: {value} doesnt exists")
                        row["exists"] = False
                        continue
                        #return None
                    
                    # 2. Check if file is .pdf
                    ext = os.path.basename(value)
                    if ext.endswith(".pdf"):
                        paths.append(value)
                        print("YESYES")
                        row["pdf"] = True
                    else:
                        print("NONONO")
                        row["pdf"] = False

                    # 3. Check if file is classified
                    isclassified = self.cs_classify(value)
                    if isclassified == True:
                        print("classified")
                        row["class"] = isclassified
                    else:
                        print(f"classification failed for: {value}")
                        row["class"] = isclassified

            print(f"new row: {row}")
        print(f"new list: {list}")
        return list
                
    def cs_control(self, dict):
        driver = self.driver()
        data = self.preprocess_data(dict)
        
        for row in data:
            open = self.open_chem(driver, row)
            close = self.upload_files(open, row)
            self.reset(close)


   
    def find_first_window(self):
        while True:
            #a = gw.getWindowsWithTitle("File Classifier")
            a = wg.FindWindow(None, "File Classifier")
            print(f"{a}")
            if a: return a
            time.sleep(0.5)

    def find_second_window(self, x):
        while True:
            #b = gw.getWindowsWithTitle("File Classifier")
            b = wg.FindWindow(None, "File Classifier")
            if b != x and b != []:
                print(f"{b}")
                return b
            time.sleep(0.5)

    def get_relative_mouse_position(self, hwnd):
        # Get window's top-left position
        window_rect = wg.GetWindowRect(hwnd)  # (left, top, right, bottom)
        
        # Get current mouse position (absolute screen coordinates)
        mouse_x, mouse_y = win32api.GetCursorPos()
        
        # Convert to relative position inside the window
        relative_x = mouse_x - window_rect[0]  # Subtract window's left position
        relative_y = mouse_y - window_rect[1]  # Subtract window's top position

        return relative_x, relative_y

    def click_relative(self, hwnd, rel_x, rel_y):
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

    def monitor_explorer_subprocess(self, subprocess_name="File Classified"):
        # Monitor the explorer process for subprocesses
        for proc in psutil.process_iter(['pid', 'name', 'parent']):
            if proc.info['name'] == 'explorer.exe':
                for child in proc.children():
                    if subprocess_name.lower() in child.info['name'].lower():
                        print(f"Found '{subprocess_name}' under explorer.exe with PID {child.info['pid']}")
                        return child
        return None

    def set_classification(self, hwnd):
        self.click_relative(hwnd, 434, 63)
        time.sleep(0.1)
        self.click_relative(hwnd, 451, 157)
        time.sleep(0.1)
        self.click_relative(hwnd, 363, 404)

    def get_metadata(self, file):
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

    def classify(self, classified, file):
        if classified == False:
            exe = r"C:\Program Files\Boldon James\File Classifier\x86\FileClassifier.exe"
            result = subprocess.Popen([exe, file], shell=True)

            x = self.find_first_window()
            hwnd = self.find_second_window(x)

            if hwnd:
                relative_x, relative_y = self.get_relative_mouse_position(hwnd)
                print(f"Mouse position relative to window: ({relative_x}, {relative_y})")
                time.sleep(0.1)
                self.set_classification(hwnd)
                while wg.IsWindow(hwnd):
                    time.sleep(1)
                print("DONE!")
                classified = True
                return classified

            else:
                print("Window not found!")
        elif classified == True:
            return classified
        else:
            print("error")

    def cs_classify(self, file):

        classified = self.get_metadata(file)
        state = self.classify(classified, file)
        return state

    @staticmethod
    def categorize_values(value: str) -> Tuple[str, List[str]]:
        """Categorizes and splits input values."""
        if not value:
            return "Empty value", []

        values = [v.strip() for v in value.split(',')]
        num_values = len(values)

        categories = {
            0: ("Empty value", []),
            1: ("Single value detected", values),
            2: ("Double values detected", values)
        }

        return categories.get(num_values, ("Multiple values detected", values))

class HotkeyHandler:
    def __init__(self):
        self.processor = ExcelDataProcessor()

    def handle_hotkey(self) -> None:
        """Handles the hotkey press event."""
        try:
            pythoncom.CoInitialize()
            self.excel = win32com.client.GetObject(None, "Excel.Application")
            
            chemscan_wb = None

            for wb in self.excel.Workbooks:
                if wb.name == EXCEL_FILES['chemscan'].name:
                    chemscan_wb = wb
                    break

            if not chemscan_wb:
                logger.warning("ChemScan workbook not open")
                return
            
            cell_range = self.excel.Selection
            cell_value = self.excel.Selection.Value

            # check if TKZ column is selected
            if cell_range.Column != 2 or not cell_range.Value:
                return

            cell_data = CellData(
                row=cell_range.Row,
                column=cell_range.Column,
                value=str(cell_range.Value),
                color=self._get_cell_color(cell_range)
            )

            # copy to clipboard helper
            pyperclip.copy(str(cell_value))

            self._log_cell_data(cell_data)
            category, values = self.processor.categorize_values(cell_data.value)
            logger.info(f"Value category: {category}")
            
            self.processor.process_verzeichnis(values)

        except Exception as e:
            logger.error(f"Error in hotkey handler: {e}")

    def _get_cell_color(self, cell) -> Optional[Tuple[int, int, int]]:
        """Gets the RGB color of a cell."""
        try:
            color = cell.Interior.Color
            if color:
                # Convert BGR to RGB (Excel uses BGR)
                blue = color & 255
                green = (color >> 8) & 255
                red = (color >> 16) & 255
                return (red, green, blue)
            return None
        except:
            return None

    @staticmethod
    def _log_cell_data(cell_data: CellData) -> None:
        """Logs cell data with color formatting if applicable."""
        if cell_data.color:
            color_code = f"\033[38;2;{cell_data.color[0]};{cell_data.color[1]};{cell_data.color[2]}m"
            logger.info(f"{color_code}{cell_data.row}, {cell_data.column}, {cell_data.value}, {cell_data.color}\033[0m")
        else:
            logger.info(f"{cell_data.row}, {cell_data.column}, {cell_data.value}, {cell_data.color}")

def main():
    """Main function to initialize and run the application."""
    try:
        handler = HotkeyHandler()
        keyboard.add_hotkey(HOTKEY_COMBINATION, handler.handle_hotkey)
        logger.info(f"Press '{HOTKEY_COMBINATION}' to trigger the hotkey.")
        logger.info(f"Press '{EXIT_KEY}' to exit.")
        keyboard.wait(EXIT_KEY)
    except Exception as e:
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main()