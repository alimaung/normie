import re
import os
import csv
import sys
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
from rapidfuzz import process, fuzz
from selenium.webdriver.common.by import By
from typing import List, Tuple, Optional, Dict, Any
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from enhanced_logging import get_logger

# Initialize the logger with your desired configuration
logger = get_logger(
    name="my_application",          # Name of your logger
    level=logging.DEBUG,            # Console log level 
    colored=True,                   # Use colored output in console
    file_path="logs/app.log",       # Path to save logs
    file_level=logging.INFO,        # File logging level
    max_file_size=10*1024*1024,      # 5MB max file size
    backup_count=3                  # Keep 3 backup files
)

# Constants
EXCEL_FILES = {
    #'chemscan': Path(r'C:\Users\u8064927\Desktop\Rolls-Royce X Ali\.coding\Normstelle\ChemScan\xls\#ChemScan.xlsx'),
    'verzeichnis': Path(r'C:\Users\u8064927\Desktop\Rolls-Royce X Ali\.coding\Normstelle\ChemScan\xls\#Verzeichnis.xlsb'),
    'chemscan': Path(r'P:\k-z\Ofs\Normstelle\Teile-und-Stoffe\Chemscan\TKZ_AT&S_export_2024_04_24.xlsx'),        # WARNING: LIVE-DIRECTORY
    #'verzeichnis': Path(r'C:\Users\u8064927\Desktop\#Verzeichnis.xlsb')                                          # WARNING: LIVE-DIRECTORY
}

START_HOTKEY = 'shift+alt+s'
PAUSE_HOTKEY = 'alt+s'
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

class ExcelHandler:
    """Handles Excel operations including reading, writing, and hyperlink extraction."""
    
    def __init__(self):
        self.excel_app = None
        self.workbook = None
        self.worksheet = None
        
    def initialize_excel(self) -> None:
        """Initialize Excel application."""
        try:
            pythoncom.CoInitialize()
            self.excel_app = win32com.client.GetObject(None, "Excel.Application")
            logger.info("Excel application initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Excel: {e}")
            raise
            
    def open_workbook(self, file_path: str) -> None:
        """Open Excel workbook."""
        try:
            self.workbook = self.excel_app.Workbooks.Open(str(file_path))
            logger.info(f"Opened workbook: {file_path}")
        except Exception as e:
            logger.error(f"Failed to open workbook {file_path}: {e}")
            raise
            
    def select_worksheet(self, sheet_name: str) -> None:
        """Select worksheet by name."""
        try:
            self.worksheet = self.workbook.Sheets[sheet_name]
            logger.info(f"Selected worksheet: {sheet_name}")
        except Exception as e:
            logger.error(f"Failed to select worksheet {sheet_name}: {e}")
            raise
            
    def apply_filter(self, column: int, filter_values: List[str]) -> None:
        """Apply filter to worksheet."""
        if not filter_values:
            logger.warning("No filter values provided")
            return
            
        try:
            self.worksheet.Range(f'{self.column_letter(column-1)}1').AutoFilter(
                Field=column,
                Criteria1=filter_values,
                Operator=7  # xlFilterValues (OR logic)
            )
            logger.info(f"Applied filter to column {column}")
        except Exception as e:
            logger.error(f"Failed to apply filter: {e}")
            
    def get_cell_hyperlink(self, cell) -> Optional[str]:
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
    
    def process_cell_value(self, value: Any) -> str:
        """Formats cell value as string with proper handling of numeric types."""
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
    def column_letter(index: int) -> str:
        """Convert column index to Excel column letter (cached for performance)."""
        letter = ""
        while index >= 0:
            letter = chr(65 + (index % 26)) + letter
            index = index // 26 - 1
        return letter
    
    def get_row_data(self, row: int, max_columns: int = 27) -> List[str]:
        """Gets values and hyperlinks for a single row, combining them where applicable."""
        row_values = []
        
        for col_idx in range(max_columns):
            col_letter = self.column_letter(col_idx)
            cell = self.worksheet.Range(f'{col_letter}{row}')
            value = self.process_cell_value(cell.Value)
            
            # For specified columns, check for hyperlinks
            if col_letter in HYPERLINK_COLUMNS:
                hyperlink = self.get_cell_hyperlink(cell)
                if hyperlink and value.strip():
                    value = f"{value} | {hyperlink}"
                elif hyperlink:
                    value = hyperlink
            
            row_values.append(value)
        
        return row_values
    
    def get_headers(self, max_columns: int = 27) -> List[str]:
        """Gets the header row from the worksheet."""
        range_str = f'A1:{self.column_letter(max_columns-1)}1'
        headers = self.worksheet.Range(range_str).Value[0]  # Value returns a 2D array
        return [self.process_cell_value(header) for header in headers]
    
    def get_last_row(self, column: str = 'B') -> int:
        """Get the last used row in a specific column."""
        return self.worksheet.Cells(self.worksheet.Rows.Count, column).End(-4162).Row  # xlUp
    
    def mark_row_as_complete(self, row: int, color_index: int = 4) -> None:
        """Mark a row as complete by coloring it (4 = green)."""
        try:
            range_to_color = self.worksheet.Range(f'A{row}:{self.column_letter(26)}{row}')
            range_to_color.Interior.ColorIndex = color_index
            logger.info(f"Marked row {row} as complete")
        except Exception as e:
            logger.error(f"Failed to mark row {row} as complete: {e}")
    
    def focus_workbook(self) -> None:
        """Bring Excel workbook to front."""
        if self.workbook:
            WindowManager.bring_window_to_front(self.workbook.Name)
            
    def cleanup(self) -> None:
        """Clean up Excel resources."""
        try:
            pythoncom.CoUninitialize()
            logger.info("Excel resources cleaned up")
        except Exception as e:
            logger.error(f"Error during Excel cleanup: {e}")

class BrowserHandler:
    """Handles browser operations for the ChemScan application."""
    
    def __init__(self):
        self._driver = None
    
    @property
    def driver(self):
        """Lazy initialization of the webdriver."""
        if self._driver is None:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self._driver = webdriver.Chrome(options=chrome_options)
            self._driver.switch_to.window(self._driver.window_handles[-1])  # Pinned ChemScan
            logger.info("WebDriver initialized")
        return self._driver
    
    def reset_browser(self) -> None:
        """Reset browser state to prepare for next operation."""
        try:
            self.driver.refresh()
            logger.info("Browser reset complete")
        except Exception as e:
            logger.error(f"Error resetting browser: {e}")
    
    def search_chemical_by_code(self, tkz: str) -> List:
        """Search for chemical by its code and return matching rows."""
        driver = self.driver
        
        try:
            # Click on internal designation button
            intern_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, 
                '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]'))
            )
            intern_btn.click()
            
            # Enter TKZ
            tkz_input = driver.find_element(By.XPATH, 
                '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/input[1]')
            tkz_input.clear()
            tkz_input.send_keys(tkz)
            
            # Send TKZ
            send = driver.find_element(By.XPATH, 
                '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/button')
            send.click()
            
            # Wait for page load to complete (top loading bar)
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/header/div[2]'))
            )
            
            # Locate the table body
            table_body_xpath = '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody'
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, table_body_xpath)))
            table_body = driver.find_element(By.XPATH, table_body_xpath)
            
            # Get all rows within the tbody
            rows = table_body.find_elements(By.TAG_NAME, 'tr')
            row_count = len(rows)
            logger.info(f"Found {row_count} rows for chemical code {tkz}")
            
            return rows
            
        except Exception as e:
            logger.error(f"Error searching for chemical code {tkz}: {e}")
            return []
    
    def open_chemical_detail(self, row_index: int) -> bool:
        """Open chemical detail view for a specific row."""
        driver = self.driver
        
        try:
            # Handle three-dot menu and eye click
            three_dot = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, 
                f'/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[{row_index}]/td[11]/div/div/a'))
            )
            ActionChains(driver).move_to_element(three_dot).perform()
            
            eye = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, 
                f'/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[{row_index}]/td[11]/div/div/ul/li[2]/ul/li[4]/a'))
            )
            eye.click()
            
            # Scroll to info section
            info = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, 
                '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[1]/nav/a[12]'))
            )
            info.click()
            
            logger.info(f"Opened chemical detail for row {row_index}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to open chemical detail for row {row_index}: {e}")
            return False
    
    def upload_file(self, file_path: str, comment: str) -> bool:
        """Upload a file to the chemical detail view."""
        if not os.path.isfile(file_path):
            logger.warning(f"File does not exist: {file_path}")
            return False
            
        driver = self.driver
        
        try:
            # Click upload attachment button
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, 
                '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[2]/div[2]/a'))
            ).click()
            
            # Wait for page load to complete
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.XPATH, '/html/body/div[10]'))
            )
            
            # Enter comment
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, 
                "/html/body/div[9]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea"))
            ).send_keys(comment)
            
            # Click on file upload area
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "uploader.empty.input-widget-file"))
            ).click()
            
            # Handle file dialog using Windows GUI automation
            self._handle_file_dialog(file_path)
            
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
            status_element = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, 
                '/html/body/div[6]/div[2]/main/div[2]/div[1]/div/div/div/div'))
            )
            
            logger.info(f"Uploaded file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            return False
    
    def _handle_file_dialog(self, file_path: str) -> None:
        """Handle Windows file dialog for file upload."""
        try:
            hwnd = WindowManager.find_window("Open")
            if not hwnd:
                logger.error("File dialog not found")
                return
            
            time.sleep(1)
            
            # Find and interact with edit box
            edit_box = wg.FindWindowEx(hwnd, 0, "ComboBoxEx32", None)
            edit_box = wg.FindWindowEx(edit_box, 0, "ComboBox", None)
            edit_box = wg.FindWindowEx(edit_box, 0, "Edit", None)
            
            if not edit_box:
                logger.error("Edit box not found in file dialog")
                return
            
            # Set file path
            wg.SendMessage(edit_box, win32con.WM_SETTEXT, None, file_path)
            
            # Click Open button
            open_button = wg.FindWindowEx(hwnd, 0, "Button", "&Open")
            if not open_button:
                logger.error("Open button not found in file dialog")
                return
            
            wg.SendMessage(hwnd, win32con.WM_COMMAND, 1, open_button)
            logger.debug(f"File dialog handled for: {file_path}")
            
        except Exception as e:
            logger.error(f"Error handling file dialog: {e}")

class DataProcessor:
    """Processes data between Excel and the browser application."""
    
    def __init__(self):
        self.excel_handler = ExcelHandler()
        self.browser_handler = BrowserHandler()
        self.original_rows = {}  # Map IDs to original Excel rows
    
    def extract_filtered_data(self, worksheet_name: str, filter_values: List[str]) -> List[List[str]]:
        """Extract filtered data from Excel."""
        try:
            # Initialize Excel
            self.excel_handler.initialize_excel()
            self.excel_handler.open_workbook(str(EXCEL_FILES['verzeichnis']))
            self.excel_handler.select_worksheet(worksheet_name)
            
            # Apply filter
            self.excel_handler.apply_filter(2, filter_values)
            
            # Get visible cells and select first one
            last_row = self.excel_handler.get_last_row('B')
            
            try:
                # Focus Excel
                self.excel_handler.focus_workbook()
                
                # Extract headers and filtered data
                headers = self.excel_handler.get_headers()
                
                # Get filtered data
                data = []
                visible_rows = set()
                
                try:
                    # Get visible cells range
                    visible_cells = self.excel_handler.worksheet.Range(f'V2:V{last_row}').SpecialCells(12)  # xlCellTypeVisible
                    
                    # Focus on first visible cell
                    visible_cells.Item(1).Select()
                    
                    # Extract visible rows
                    for cell in visible_cells:
                        row = cell.Row
                        if row not in visible_rows:
                            visible_rows.add(row)
                            row_data = self.excel_handler.get_row_data(row)
                            data.append(row_data)
                            # Store original row for later marking
                            self.original_rows[row_data[0]] = row
                    
                    logger.info(f"Extracted {len(data)} rows of filtered data")
                    
                    if data:
                        return headers, data
                        
                except Exception as e:
                    logger.warning(f"No visible cells found after filtering: {e}")
                
            except Exception as e:
                logger.error(f"Error extracting filtered data: {e}")
                
            return [], []
            
        finally:
            # Clean up Excel resources
            self.excel_handler.cleanup()
    
    def save_data_to_csv(self, headers: List[str], data: List[List[str]]) -> None:
        """Save extracted data to CSV file."""
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
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error saving data to CSV: {e}")
            return None
    
    def process_row_data(self, raw_data: List[List[str]]) -> List[Dict[str, Any]]:
        """Process raw data into structured dictionaries for upload."""
        if not raw_data:
            return []
        
        processed_data = []
        for row in raw_data:
            try:
                # Ensure row has enough elements
                if len(row) < 18:
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
                    "ats_comment": f"AT&S_{id_val}_{tkz}_{loc}_TEST",
                    "sdb_comment": f"ChemScan_{id_val}_{tkz}_{loc}_TEST",
                    "row_id": id_val  # Used to map back to original row
                }
                
                processed_data.append(entry)
                
            except Exception as e:
                logger.error(f"Error processing row: {e}")
                
        logger.info(f"Processed {len(processed_data)} rows of data")
        return processed_data
    
    def process_chemicals(self, chemical_data: List[Dict[str, Any]]) -> None:
        """Process chemicals in browser application."""
        if not chemical_data:
            logger.warning("No data to process")
            return
        
        processed_items = []
        
        for item in chemical_data:
            try:
                # Search for chemical by code
                chem_rows = self.browser_handler.search_chemical_by_code(item["tkz"])
                
                if not chem_rows:
                    logger.warning(f"No rows found for chemical code: {item['tkz']}")
                    continue
                
                # Process each row found
                for index, _ in enumerate(chem_rows, start=1):
                    # Open chemical detail
                    if not self.browser_handler.open_chemical_detail(index):
                        continue
                    
                    # Upload files
                    files_uploaded = False
                    
                    # Upload ATS file if exists
                    if item.get("ats") and os.path.isfile(item["ats"]):
                        ats_uploaded = self.browser_handler.upload_file(item["ats"], item["ats_comment"])
                        files_uploaded = files_uploaded or ats_uploaded
                    
                    # Upload SDB file if exists
                    if item.get("sdb") and os.path.isfile(item["sdb"]):
                        sdb_uploaded = self.browser_handler.upload_file(item["sdb"], item["sdb_comment"])
                        files_uploaded = files_uploaded or sdb_uploaded
                    
                    # Reset browser for next operation
                    self.browser_handler.reset_browser()
                    
                    if files_uploaded:
                        processed_items.append(item)
                
            except Exception as e:
                logger.error(f"Error processing chemical {item.get('id', 'unknown')}: {e}")
                self.browser_handler.reset_browser()
        
        # Mark processed rows as complete in Excel
        self.mark_completed_rows(processed_items)
    
    def mark_completed_rows(self, processed_items: List[Dict[str, Any]]) -> None:
        """Mark rows as completed in Excel."""
        if not processed_items:
            logger.warning("No processed items to mark as complete")
            return
        
        try:
            # Initialize Excel
            self.excel_handler.initialize_excel()
            self.excel_handler.open_workbook(str(EXCEL_FILES['verzeichnis']))
            self.excel_handler.select_worksheet('Teile und Stoffe')
            
            # Mark each row as complete
            for item in processed_items:
                row_id = item.get("row_id")
                if row_id and row_id in self.original_rows:
                    excel_row = self.original_rows[row_id]
                    self.excel_handler.mark_row_as_complete(excel_row)
            
            logger.info(f"Marked {len(processed_items)} rows as complete")
            
        except Exception as e:
            logger.error(f"Error marking rows as complete: {e}")
            
        finally:
            # Clean up Excel resources
            self.excel_handler.cleanup()

class ChemicalProcessor:
    """Main class for processing chemicals from Excel to browser application."""
    
    def __init__(self):
        self.data_processor = DataProcessor()
    
    def process_chemicals(self, filter_values: List[str], worksheet_name: str = 'Teile und Stoffe') -> None:
        """Process chemicals based on filter values."""
        if not filter_values:
            logger.warning("No filter values provided")
            return
        
        try:
            # Extract data from Excel
            headers, raw_data = self.data_processor.extract_filtered_data(worksheet_name, filter_values)
            
            if not raw_data:
                logger.warning("No data extracted from Excel")
                return
            
            # Save data to CSV
            cleaned_data = self.data_processor.save_data_to_csv(headers, raw_data)
            
            if not cleaned_data:
                logger.warning("Failed to save data to CSV")
                return
            
            # Process row data
            processed_data = self.data_processor.process_row_data(cleaned_data)
            
            if not processed_data:
                logger.warning("No data to process after filtering")
                return
            
            # Process chemicals in browser
            self.data_processor.process_chemicals(processed_data)
            
            logger.info("Chemical processing completed successfully")
            
        except Exception as e:
            logger.error(f"Error in chemical processing: {e}")

class HotkeyHandler:
    def __init__(self):
        self.processor = ExcelHandler()
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
                #self._log_cell_data(cell_data)
                #category, values = self.processor.categorize_values(cell_data.value)
                #logger.info(f"Value category: {category}")
                val = cell_data.value

                if not val:
                    return "Empty value", []

                values = [v.strip() for v in val.split(',') if v.strip()]
                num_values = len(values)

                categories = {
                    0: ("Empty value", []),
                    1: ("Single value detected", values),
                    2: ("Double values detected", values)
                }
                
                # Store the original row number for later coloring
                self.processor.original_row = cell_data.row
                self.processor.excel = self.excel  # Pass Excel reference to processor

                # Process the values if any exist
                if values:
                    self.processor.process_cell_value(values)
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
        keyboard.add_hotkey(START_HOTKEY, handler.handle_hotkey)
        logger.info(f"Press '{START_HOTKEY}' to trigger the hotkey.")
        logger.info(f"Press '{EXIT_KEY}' to exit.")
        
        # Monitor for exit key
        keyboard.wait(EXIT_KEY)
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
    finally:
        logger.info("Application terminated")


if __name__ == "__main__":
    main()