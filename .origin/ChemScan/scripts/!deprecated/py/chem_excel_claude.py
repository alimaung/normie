import xlwings as xw
import keyboard
import pygetwindow as gw
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import logging
from pathlib import Path
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
EXCEL_FILES = {
    'chemscan': Path(r'C:\Users\Ali\Desktop\Rolls-Royce\ChemScan\xls\ChemScan.xlsx'),
    'verzeichnis': Path(r'C:\Users\Ali\Desktop\Rolls-Royce\ATS\xls\Verzeichnis.xlsb')
}
HOTKEY_COMBINATION = 'shift+alt+s'
EXIT_KEY = 'esc'
HYPERLINK_COLUMNS = 'MNOPQRSTU'  # Columns M to U

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
        active_window = gw.getActiveWindow()
        windows = gw.getWindowsWithTitle(window_title)

        if not windows:
            logger.warning(f"Window '{window_title}' not found.")
            return

        target_window = windows[0]
        if target_window == active_window:
            logger.info(f"'{window_title}' is already the active window.")
            return

        if target_window.isMinimized:
            target_window.restore()
        target_window.activate()
        logger.info(f"'{window_title}' brought to the front.")

class ExcelDataProcessor:
    def __init__(self):
        self.verzeichnis_sheet = None

    def _get_cell_hyperlink(self, cell) -> Optional[str]:
        """Extracts hyperlink from a cell if it exists."""
        try:
            if cell.api.Hyperlinks.Count > 0:
                return cell.api.Hyperlinks(1).Address
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

    def _get_row_data(self, worksheet: xw.Sheet, row: int) -> List[str]:
        """Gets values and hyperlinks for a single row, combining them where applicable."""
        row_values = []
        
        # Process columns A to X
        for col_idx in range(24):  # A to X (0 to 23)
            col_letter = chr(65 + col_idx)  # Convert number to letter (A=65 in ASCII)
            cell = worksheet.range(f'{col_letter}{row}')
            value = self._process_cell_value(cell.value)
            
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

    def _get_headers(self, worksheet: xw.Sheet) -> List[str]:
        """Gets the header row from the worksheet."""
        headers = worksheet.range('A1:X1').value
        return [self._process_cell_value(header) for header in headers]

    def fetch_filtered_data(self, worksheet: xw.Sheet) -> Tuple[List[str], List[List[str]]]:
        """Fetches filtered data from columns A to X including hyperlinks."""
        try:
            headers = self._get_headers(worksheet)
            last_row = worksheet.api.Cells(worksheet.api.Rows.Count, 'B').End(-4162).Row
            filtered_range = worksheet.range(f'A2:X{last_row}')
            visible_cells = filtered_range.api.SpecialCells(12)  # xlCellTypeVisible

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
            wb = xw.Book(EXCEL_FILES['verzeichnis'])
            self.verzeichnis_sheet = wb.sheets['Teile und Stoffe']

            # Apply filter
            self.verzeichnis_sheet.range('B1').api.AutoFilter(
                Field=2,
                Criteria1=filter_values,
                Operator=7  # xlFilterValues (OR logic)
            )

            # Get visible cells and select first one
            last_row = self.verzeichnis_sheet.api.Cells(self.verzeichnis_sheet.api.Rows.Count, 'B').End(-4162).Row
            visible_cells = self.verzeichnis_sheet.range(f'B2:B{last_row}').api.SpecialCells(12)

            WindowManager.bring_window_to_front(wb.name)
            wb.app.activate()
            wb.activate()

            if visible_cells:
                visible_cells.Item(1).Select()
            
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
            
            with open('filtered_data.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, 
                                  delimiter='\t',      # Use semicolon as delimiter
                                  quotechar='"',      # Use double quotes for escaping
                                  quoting=csv.QUOTE_ALL)  # Quote fields only when necessary
                writer.writerow(headers)  # Write headers
                writer.writerows(cleaned_data)    # Write data rows
            logger.info("Data successfully saved to filtered_data.csv")
        except Exception as e:
            logger.error(f"Error saving data to CSV: {e}")

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
            wb = xw.Book(EXCEL_FILES['chemscan'])
            cell_range = wb.app.selection

            if cell_range.column != 2 or not cell_range.value:
                return

            cell_data = CellData(
                row=cell_range.row,
                column=cell_range.column,
                value=cell_range.value,
                color=cell_range.color
            )

            self._log_cell_data(cell_data)
            category, values = self.processor.categorize_values(cell_data.value)
            logger.info(f"Value category: {category}")
            
            self.processor.process_verzeichnis(values)

        except Exception as e:
            logger.error(f"Error in hotkey handler: {e}")

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