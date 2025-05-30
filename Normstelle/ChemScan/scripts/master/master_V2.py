import os
import csv
import time
import logging
import win32api
import win32con
import keyboard
import pythoncom
import pyperclip
import subprocess
import pypdf as pp
import win32gui as wg
import win32com.client
import pygetwindow as gw
from pathlib import Path
from selenium import webdriver
from functools import lru_cache
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from typing import List, Tuple, Optional, Dict, Any
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

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
HYPERLINK_COLUMNS = set('MNOPQRSTU')  # Columns M to U
DATA_FOLDER = Path(r'C:\Users\u8064927\Desktop\Rolls-Royce X Ali\.coding\Normstelle\ChemScan\scripts\data\data.csv')
WAIT_TIMEOUT = 10

@dataclass
class CellData:
    """Data class to store cell information"""
    row: int
    column: int
    value: str
    color: Optional[Tuple[int, int, int]]


class WindowManager:
    @staticmethod
    def bring_window_to_front(window_title: str) -> None:
        """Brings the specified window to the front if it exists."""
        windows = gw.getWindowsWithTitle(window_title)

        if not windows:
            logger.warning(f"Window '{window_title}' not found.")
            return

        target_window = windows[0]
        if target_window.isMinimized:
            target_window.restore()
            
        logger.info(f"'{window_title}' brought to the front.")

    @staticmethod
    def find_window(title: str, timeout: int = 10) -> int:
        """Find window by title with timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            hwnd = wg.FindWindow(None, title)
            if hwnd:
                logger.debug(f"Found window: {title}")
                return hwnd
            time.sleep(0.5)
        logger.warning(f"Window '{title}' not found after {timeout}s.")
        return 0

    @staticmethod
    def click_relative_position(hwnd: int, rel_x: int, rel_y: int) -> None:
        """Click at a position relative to a window's top-left corner."""
        if not hwnd:
            logger.error("No window handle provided for click_relative_position")
            return
            
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

        logger.debug(f"Clicked at relative position ({rel_x}, {rel_y}) → Absolute ({abs_x}, {abs_y})")


class ExcelDataProcessor:
    def __init__(self):
        self.excel = None
        self.verzeichnis_sheet = None
        self._driver = None
        
    @property
    def driver(self):
        """Lazy initialization of the webdriver."""
        if self._driver is None:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self._driver = webdriver.Chrome(options=chrome_options)
            self._driver.switch_to.window(self._driver.window_handles[-1])  # Pinned ChemScan
        return self._driver

    def _get_cell_hyperlink(self, cell) -> Optional[str]:
        """Extracts hyperlink from a cell if it exists."""
        try:
            if cell.Hyperlinks.Count > 0:
                address = cell.Hyperlinks(cell.Hyperlinks.Count).Address  # get latest link always
                if address.startswith('..'):
                    wb_path = Path(cell.Parent.Parent.Path)
                    try:
                        absolute_path = wb_path / address.replace('\\', '/')
                        return str(absolute_path.resolve())
                    except:
                        return address
                return address
            return None
        except Exception as e:
            logger.debug(f"Error getting hyperlink: {e}")
            return None

    def _process_cell_value(self, value: Any) -> str:
        """Processes cell value to ensure proper string formatting."""
        if value is None:
            return ""
        # Convert numbers to strings without decimal places if they're whole numbers
        if isinstance(value, (int, float)):
            if float(value).is_integer():
                return str(int(value))
            return str(value)
        return str(value)
    
    @staticmethod
    @lru_cache(maxsize=128)
    def generate_col_idx(index: int) -> str:
        """Convert column index to Excel column letter (cached for performance)."""
        letter = ""
        while index >= 0:
            letter = chr(65 + (index % 26)) + letter
            index = index // 26 - 1
        return letter

    def _get_row_data(self, worksheet, row: int) -> List[str]:
        """Gets values and hyperlinks for a single row, combining them where applicable."""
        row_values = []
        
        # Process columns A to AA (27 columns)
        for col_idx in range(27):  
            col_letter = self.generate_col_idx(col_idx)
            cell = worksheet.Range(f'{col_letter}{row}')
            value = self._process_cell_value(cell.Value)
            
            # For columns M to U, check for hyperlinks
            if col_letter in HYPERLINK_COLUMNS:
                hyperlink = self._get_cell_hyperlink(cell)
                if hyperlink and value.strip():
                    value = f"{value} | {hyperlink}"
                elif hyperlink:
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
            
            try:
                visible_cells = filtered_range.SpecialCells(12)  # xlCellTypeVisible
            except:
                logger.warning("No visible cells found after filtering")
                return headers, []

            data = []
            row_numbers = set()

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
        if not filter_values:
            logger.warning("No filter values provided")
            return
            
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
            
            try:
                visible_cells = self.verzeichnis_sheet.Range(f'V2:V{last_row}').SpecialCells(12)
                
                # Focus Verzeichnis
                WindowManager.bring_window_to_front(wb.Name)
    
                visible_cells.Item(1).Select()
                headers, filtered_data = self.fetch_filtered_data(self.verzeichnis_sheet)
                if filtered_data:
                    self._save_data_to_csv(headers, filtered_data)
            except:
                logger.warning("No visible cells found after filtering")
                    
        except Exception as e:
            logger.error(f"Error processing Verzeichnis: {e}")
        finally:
            pythoncom.CoUninitialize()

    def _save_data_to_csv(self, headers: List[str], data: List[List[str]]) -> None:
        """Saves the filtered data to a CSV file with proper handling of special characters."""
        if not data:
            logger.warning("No data to save to CSV")
            return
            
        try:
            # Remove newlines in each cell of data
            headers = [header.replace("\n", "").replace("\r", "") for header in headers]
            
            cleaned_data = []
            for row in data:
                cleaned_row = [cell.replace("\n", "").replace("\r", "") for cell in row]
                cleaned_data.append(cleaned_row)
            
            # Ensure parent directory exists
            DATA_FOLDER.parent.mkdir(parents=True, exist_ok=True)
            
            with open(DATA_FOLDER, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, 
                                  delimiter='\t',
                                  quotechar='"',
                                  quoting=csv.QUOTE_ALL)
                writer.writerow(headers)
                writer.writerows(cleaned_data)
            logger.info(f"Data successfully saved to {DATA_FOLDER}")

            processed_data = self.filter(cleaned_data)
            if processed_data:
                self.cs_control(processed_data)

        except Exception as e:
            logger.error(f"Error saving data to CSV: {e}")

    def filter(self, data: List[List[str]]) -> List[Dict[str, Any]]:
        """Process raw data into structured dictionaries."""
        if not data:
            return []
            
        processed_data = []
        for row in data:
            try:
                # Ensure row has enough elements
                if len(row) < 18:  # Need at least 18 elements for index 17
                    logger.warning(f"Row has insufficient data: {row}")
                    continue
                
                # Get key values
                id_val = row[0].replace("/", "-")
                tkz = row[1]
                loc = row[10]
                
                # Process ATS data
                ats_raw = row[12].split("|")[1].strip() if "|" in row[12] else ""
                ats = ats_raw.replace("\\\\dehesdna-a009a\\projekte", "P:") if ats_raw else ""
                
                # Process SDB data
                sdb_raw = row[17].split("|")[1].strip() if "|" in row[17] else ""
                sdb = sdb_raw.replace("\\\\dehesdna-a009a\\projekte", "P:") if sdb_raw else ""
                
                # Skip if no valid files
                if not ats and not sdb:
                    logger.warning(f"No valid ATS or SDB paths for row with ID: {id_val}")
                    continue
                
                # Create data dict
                entry = {
                    "id": id_val,
                    "tkz": tkz,
                    "ats": ats,
                    "sdb": sdb,
                    "loc": loc,
                    "ats_comment": f"AT&S_{id_val}_{tkz}_{loc}",
                    "sdb_comment": f"ChemScan_{id_val}_{tkz}_{loc}",
                    "exists": None,
                    "pdf": None,
                    "class": None
                }
                
                processed_data.append(entry)
                
            except Exception as e:
                logger.error(f"Error processing row: {e}")
                
        return processed_data

    def cs_control(self, data: List[Dict[str, Any]]) -> None:
        """Main control flow for ChemScan processing."""
        if not data:
            logger.warning("No data to process in cs_control")
            return
            
        processed_data = self.preprocess_data(data)
        if not processed_data:
            logger.warning("No valid data after preprocessing")
            return
            
        for row in processed_data:
            try:
                self.open_chem(row)
                self.upload_files(row)
                self.reset_browser()
            except Exception as e:
                logger.error(f"Error processing row {row.get('id', 'unknown')}: {e}")
                self.reset_browser()  # Try to reset browser to continue with next item
        
        # Color the row green when processing is complete
        if hasattr(self, 'original_row') and self.original_row:
            self.color_row_green(self.original_row)

    def open_chem(self, data: Dict[str, Any]) -> None:
        """Open chemical data in browser application."""
        if not data or "tkz" not in data:
            logger.error("Invalid data for open_chem")
            return
            
        tkz = data["tkz"]
        driver = self.driver
        
        try:
            # Click on internal designation button
            try:
                intern_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, 
                    '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]'))
                )
                intern_btn.click()
            except Exception as e:
                logger.error(f"Failed to find internal designation button: {e}")
                return

            # Enter TKZ
            tkz_input = driver.find_element(By.XPATH, 
                '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/input[1]')
            tkz_input.clear()  # Clear any existing text
            tkz_input.send_keys(tkz)

            # Send TKZ
            send = driver.find_element(By.XPATH, 
                '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/button')
            send.click()

            # Wait for results
            time.sleep(1)

            # Handle three-dot menu and eye click
            try:
                three_dot = WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, 
                    '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/a'))
                )
                ActionChains(driver).move_to_element(three_dot).perform()
                
                eye = WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, 
                    '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/ul/li[2]/ul/li[4]/a'))
                )
                eye.click()
            except Exception as e:
                logger.error(f"Failed to navigate to detail view: {e}")
                return

            # Scroll to info section
            try:
                info = WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, 
                    '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[1]/nav/a[12]'))
                )
                info.click()
            except Exception as e:
                logger.error(f"Failed to navigate to info section: {e}")
                return

            # Check for entries
            try:
                nothing = driver.find_element(By.XPATH, 
                    '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[2]/div/div/div[12]/div[2]/div/div/div/div/div/div/div[2]/div/div/div/div[2]/div[3]/p')
                if nothing.text == "Keine Einträge gefunden":
                    logger.info("No entries found in info section")
                else:
                    logger.info("Entries found in info section")
            except Exception as e:
                logger.debug(f"Could not check for entries: {e}")

        except Exception as e:
            logger.error(f"Error in open_chem: {e}")

    def upload_files(self, data: Dict[str, Any]) -> None:
        """Upload ATS and SDB files."""
        if not data:
            logger.error("No data provided for upload_files")
            return
            
        driver = self.driver
        file_pairs = []
        
        # Only add files that exist
        if data.get("ats") and os.path.isfile(data["ats"]):
            file_pairs.append((data["ats"], data["ats_comment"]))
            
        if data.get("sdb") and os.path.isfile(data["sdb"]):
            file_pairs.append((data["sdb"], data["sdb_comment"]))
            
        if not file_pairs:
            logger.warning("No valid files to upload")
            return
            
        for file_path, comment in file_pairs:
            try:
                # Click upload attachment button
                WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, 
                    '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[2]/div[2]/a'))
                ).click()

                # Enter comment
                WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, 
                    "/html/body/div[9]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea"))
                ).send_keys(comment)

                # Click on file upload area
                WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "uploader.empty.input-widget-file"))
                ).click()

                # Handle file dialog
                hwnd = WindowManager.find_window("Open")
                if not hwnd:
                    logger.error("File dialog not found")
                    continue
                    
                time.sleep(1)
                
                # Find and interact with edit box
                edit_box = wg.FindWindowEx(hwnd, 0, "ComboBoxEx32", None)
                edit_box = wg.FindWindowEx(edit_box, 0, "ComboBox", None)
                edit_box = wg.FindWindowEx(edit_box, 0, "Edit", None)
                
                if not edit_box:
                    logger.error("Edit box not found in file dialog")
                    continue

                # Set file path
                wg.SendMessage(edit_box, win32con.WM_SETTEXT, None, file_path)

                # Click Open button
                open_button = wg.FindWindowEx(hwnd, 0, "Button", "&Open")
                if not open_button:
                    logger.error("Open button not found in file dialog")
                    continue
                    
                wg.SendMessage(hwnd, win32con.WM_COMMAND, 1, open_button)

                # Wait for file name to appear
                file_name_element = WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, 
                    "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]"))
                )
                initial_text = file_name_element.text

                # Wait for file name to change (indicating upload)
                def file_name_changed(driver):
                    try:
                        current_text = driver.find_element(By.XPATH, 
                            "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]").text
                        return current_text != initial_text
                    except:
                        return False
                
                WebDriverWait(driver, 30).until(file_name_changed)
                
                # Click save button
                driver.find_element(By.XPATH, 
                    '/html/body/div[9]/div[13]/div/div/div/span[2]/button').click()

                # Check upload status
                try:
                    status_element = WebDriverWait(driver, 30).until(
                        EC.visibility_of_element_located((By.XPATH, 
                        '/html/body/div[6]/div[2]/main/div[2]/div[1]/div/div/div/div'))
                    )
                    status_text = status_element.text
                    
                    if "successfully" in status_text.lower():
                        logger.info(f"Successfully uploaded: {os.path.basename(file_path)}")
                    else:
                        logger.warning(f"Upload issue: {status_text}")
                        
                except Exception as e:
                    logger.error(f"Could not determine upload status: {e}")

            except Exception as e:
                logger.error(f"Error uploading file {os.path.basename(file_path)}: {e}")

    def reset_browser(self) -> None:
        """Reset browser to initial state."""
        driver = self.driver
        try:
            # Click home button
            driver.find_element(By.XPATH, 
                '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div/div/a').click()
            
            # Wait for page load to complete
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.XPATH, '/html/body/div[10]'))
            )
            logger.info("Browser reset to initial state")
            
        except Exception as e:
            logger.error(f"Error resetting browser: {e}")

    def preprocess_data(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check if files exist, are PDFs, and classify them if needed."""
        processed_data = []
        
        for row in data_list:
            try:
                file_valid = False
                
                # Process ATS and SDB files
                for key in ["ats", "sdb"]:
                    if not row.get(key):
                        continue
                        
                    file_path = row[key]
                    
                    # Check if file exists
                    if os.path.isfile(file_path):
                        row["exists"] = True
                        logger.info(f"File {key}: {os.path.basename(file_path)} exists")
                        file_valid = True
                    else:
                        logger.warning(f"File {key}: {os.path.basename(file_path)} doesn't exist")
                        continue
                    
                    # Check if file is PDF
                    if file_path.lower().endswith(".pdf"):
                        row["pdf"] = True
                    else:
                        row["pdf"] = False
                        logger.warning(f"File {key} is not a PDF: {os.path.basename(file_path)}")
                    
                    # Check classification
                    try:
                        is_classified = self.cs_classify(file_path)
                        row["class"] = is_classified
                        if is_classified:
                            logger.info(f"File {key} is classified: {os.path.basename(file_path)}")
                        else:
                            logger.info(f"File {key} needs classification: {os.path.basename(file_path)}")
                    except Exception as e:
                        logger.error(f"Error checking classification for {os.path.basename(file_path)}: {e}")
                
                if file_valid:
                    processed_data.append(row)
                    
            except Exception as e:
                logger.error(f"Error preprocessing data for row {row.get('id', 'unknown')}: {e}")
                
        return processed_data

    def cs_classify(self, file_path: str) -> bool:
        """Check if PDF is classified and classify if needed."""
        if not os.path.isfile(file_path):
            logger.error(f"File does not exist: {file_path}")
            return False
            
        try:
            # Check if already classified
            classified = self.get_metadata(file_path)
            if classified:
                logger.info(f"File already classified: {os.path.basename(file_path)}")
                return True
                
            # Classify the file
            exe = r"C:\Program Files\Boldon James\File Classifier\x86\FileClassifier.exe"
            subprocess.Popen([exe, file_path], shell=True)
            
            # Find classifier windows
            first_hwnd = WindowManager.find_window("File Classifier")
            if not first_hwnd:
                logger.error("First classifier window not found")
                return False
                
            # Wait for second window
            second_hwnd = None
            start_time = time.time()
            while time.time() - start_time < 10:
                curr_hwnd = WindowManager.find_window("File Classifier")
                if curr_hwnd and curr_hwnd != first_hwnd:
                    second_hwnd = curr_hwnd
                    break
                time.sleep(0.5)
                
            if not second_hwnd:
                logger.error("Second classifier window not found")
                return False
                
            # Set classification
            time.sleep(0.5)
            WindowManager.click_relative_position(second_hwnd, 434, 63)
            time.sleep(0.2)
            WindowManager.click_relative_position(second_hwnd, 451, 157)
            time.sleep(0.2)
            WindowManager.click_relative_position(second_hwnd, 363, 404)
            
            # Wait for window to close
            start_time = time.time()
            while time.time() - start_time < 30 and wg.IsWindow(second_hwnd):
                time.sleep(1)
                
            logger.info(f"Classification complete for: {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            logger.error(f"Error in cs_classify: {e}")
            return False

    def get_metadata(self, file_path: str) -> bool:
        """Check if PDF is already classified by examining metadata."""
        try:
            with open(file_path, "rb") as pdf:
                reader = pp.PdfReader(pdf)
                meta = reader.metadata
                keywords = meta.get('/Keywords', 'Not found')
                return keywords != "Not found"
        except Exception as e:
            logger.error(f"Error reading PDF metadata: {e}")
            return False

    @staticmethod
    def categorize_values(value: str) -> Tuple[str, List[str]]:
        """Categorizes and splits input values."""
        if not value:
            return "Empty value", []

        values = [v.strip() for v in value.split(',') if v.strip()]
        num_values = len(values)

        categories = {
            0: ("Empty value", []),
            1: ("Single value detected", values),
            2: ("Double values detected", values)
        }

        return categories.get(num_values, ("Multiple values detected", values))

    def color_row_green(self, row: int) -> None:
        """Colors the row from column A to column D green."""
        try:
            # Get a reference to the ChemScan workbook
            for wb in self.excel.Workbooks:
                if wb.name == EXCEL_FILES['chemscan'].name:
                    active_sheet = wb.ActiveSheet
                    # Set the range from column A to column D in the specified row
                    range_to_color = active_sheet.Range(
                        active_sheet.Cells(row, 1),  # Column A
                        active_sheet.Cells(row, 4)   # Column D
                    )
                    range_to_color.Interior.Color = self._rgb_to_bgr(163, 245, 43)  # #A3F52B in RGB
                    logger.info(f"Row {row} colored green (columns A-D) to indicate completion")
                    return
            logger.warning("ChemScan workbook not found when trying to color row")
        except Exception as e:
            logger.error(f"Error coloring row: {e}")

    @staticmethod
    def _rgb_to_bgr(r: int, g: int, b: int) -> int:
        """Converts RGB color to Excel's BGR format."""
        return (b << 16) | (g << 8) | r

class HotkeyHandler:
    def __init__(self):
        self.processor = ExcelDataProcessor()
        self.excel = None

    def handle_hotkey(self) -> None:
        """Handles the hotkey press event."""
        try:
            pythoncom.CoInitialize()
            try:
                self.excel = win32com.client.GetObject(None, "Excel.Application")
                
                # Check if Excel is running and has a selection
                if not self.excel or not self.excel.Selection:
                    logger.warning("Excel not running or no selection")
                    return
                    
                # Get active workbook
                active_wb = self.excel.ActiveWorkbook
                if not active_wb:
                    logger.warning("No active workbook")
                    return
                    
                # Check if ChemScan workbook is open
                chemscan_name = EXCEL_FILES['chemscan'].name
                is_chemscan = False
                
                for wb in self.excel.Workbooks:
                    if wb.name == chemscan_name:
                        is_chemscan = True
                        break

                if not is_chemscan:
                    logger.warning("ChemScan workbook not open")
                    return
                
                # Get cell selection
                cell_range = self.excel.Selection
                cell_value = cell_range.Value

                # Check if TKZ column is selected and has a value
                if cell_range.Column != 2 or not cell_value:
                    logger.warning("Invalid column selection or empty value")
                    return

                # Create cell data object
                cell_data = CellData(
                    row=cell_range.Row,
                    column=cell_range.Column,
                    value=str(cell_value),
                    color=self._get_cell_color(cell_range)
                )

                # Copy to clipboard for convenience
                pyperclip.copy(str(cell_value))

                # Log cell data and process
                self._log_cell_data(cell_data)
                category, values = self.processor.categorize_values(cell_data.value)
                logger.info(f"Value category: {category}")

                # Store the original row number for later coloring
                self.processor.original_row = cell_data.row
                self.processor.excel = self.excel  # Pass Excel reference to processor

                # Process the values if any exist
                if values:
                    self.processor.process_verzeichnis(values)
                else:
                    logger.warning("No values to process")
                    
            except pythoncom.com_error as ce:
                logger.error(f"COM Error: {ce}")
                
        except Exception as e:
            logger.error(f"Error in hotkey handler: {e}", exc_info=True)
        finally:
            pythoncom.CoUninitialize()  # Ensure COM is properly uninitialized

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
        except Exception as e:
            logger.debug(f"Could not get cell color: {e}")
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
        logger.info("Starting ChemScan assistant application")
        handler = HotkeyHandler()
        keyboard.add_hotkey(HOTKEY_COMBINATION, handler.handle_hotkey)
        logger.info(f"Press '{HOTKEY_COMBINATION}' to trigger the hotkey.")
        logger.info(f"Press '{EXIT_KEY}' to exit.")
        
        # Monitor for exit key
        keyboard.wait(EXIT_KEY)
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
    finally:
        logger.info("Application terminated")


if __name__ == "__main__":
    main()