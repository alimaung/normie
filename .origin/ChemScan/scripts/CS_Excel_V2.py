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
                address = cell.Hyperlinks(1).Address
                #print(address)
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
            #self.excel.Visible = True
            #wb.Activate()

            if visible_cells:
                visible_cells.Item(1).Select()
                logger.debug(f"\033[33{visible_cells}\033m")

                if len(visible_cells) > 1: # number of rows
                    print("MORE ROWS")
                    pass
                else:
                    print("ONE ROW")
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

            #print(f"CLEANED_DATA: {cleaned_data}")
            self.open_files_in_explorer(cleaned_data)
            #lb.filter(cleaned_data)

        except Exception as e:
            logger.error(f"Error saving data to CSV: {e}")

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
                        subprocess.Popen(fr'explorer /select,{ats}')
                        print(f"ATS: {ats}")
                except Exception as e:
                    logger.error(f"Kein AT&S gefunden!: {e}")
                
                try:
                    sdb = row[17].split("|")[1].replace("\\\\dehesdna-a009a\\projekte", "P:")
                    if os.path.exists(sdb):
                        logger.error(f"Datei nicht gefunden!: {ats}")
                    else:
                        subprocess.Popen(fr'explorer /select,{sdb}')
                        print(f"SDB: {sdb}")
                except Exception as e:
                    logger.error(f"Kein ChemScan gefunden!: {e}")

                # Reveal the files in the explorer
                #subprocess.Popen(fr'explorer /select,{ats}')
                #subprocess.Popen(fr'explorer /select,{sdb}')

        except Exception as e:
            logger.error(f"Error opening files: {e}")


    


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