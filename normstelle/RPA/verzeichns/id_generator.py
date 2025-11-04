"""
ID Generator Module for CMSR Automation

Generates TKZ numbers and Antragsnummer by reading existing Excel files
and incrementing the last used numbers.

TKZ Format: 01044397 -> 01044398 (8-digit text with leading zeros)
Antragsnummer Format: 158/2025 -> 159/2025 (XXX/YYYY)

Uses COM interface to preserve Excel text formatting.
"""

import win32com.client
import re, time
from datetime import datetime
from pathlib import Path

def get_last_tkz_number(tkz_file_path):
    """
    Read TKZ.xls file using COM and find the last (highest) TKZ number.
    Preserves text formatting including leading zeros.
    Returns the last TKZ number as integer.
    """
    print(f"Reading TKZ file using COM: {tkz_file_path}")
    
    # Ensure we have a Path object and get absolute path
    tkz_path = Path(tkz_file_path)
    absolute_path = tkz_path.resolve()
    
    try:
        # Create Excel COM object
        excel_app = win32com.client.Dispatch("Excel.Application")
        excel_app.Visible = True
        excel_app.DisplayAlerts = False
        
        # Open workbook with absolute path as string
        workbook = excel_app.Workbooks.Open(str(absolute_path))
        worksheet = workbook.Worksheets(1)  # First sheet
        
        # Get the used range to find how many rows have data
        used_range = worksheet.UsedRange
        last_row = used_range.Rows.Count
        
        print(f"DEBUG: Worksheet has {last_row} rows with data")
        
        # Read first 10 values to understand structure
        print(f"DEBUG: First 10 values in column A:")
        for row in range(1, min(11, last_row + 1)):
            cell_value = worksheet.Cells(row, 1).Value
            cell_text = worksheet.Cells(row, 1).Text  # Get formatted text
            print(f"  Row {row}: Value='{cell_value}' Text='{cell_text}' (Value type: {type(cell_value)})")
        
        # Read last 10 values
        print(f"DEBUG: Last 10 values in column A:")
        start_row = max(1, last_row - 9)
        for row in range(start_row, last_row + 1):
            cell_value = worksheet.Cells(row, 1).Value
            cell_text = worksheet.Cells(row, 1).Text
            print(f"  Row {row}: Value='{cell_value}' Text='{cell_text}' (Value type: {type(cell_value)})")
        
        # Find the last TKZ number by reading from bottom up
        # This is much faster than reading all 5000+ rows
        print(f"DEBUG: Searching for last TKZ number from bottom up...")
        
        last_tkz = None
        
        # Start from the last row and work backwards
        for row in range(last_row, 0, -1):  # Count backwards from last_row to 1
            cell_text = worksheet.Cells(row, 1).Text
            
            if not cell_text or cell_text.strip() == "":
                continue
            
            cell_text = str(cell_text).strip()
            
            # Skip header row
            if cell_text.lower() in ['teilenummer', 'tkz', 'number']:
                continue
            
            # Look for 8-digit TKZ numbers
            match = re.search(r'\b(\d{8})\b', cell_text)
            if match:
                tkz_str = match.group(1)
                tkz_num = int(tkz_str)
                print(f"DEBUG: Found last TKZ {tkz_num:08d} in row {row}: '{cell_text}'")
                last_tkz = tkz_num
                break  # Found the last one, stop searching
            
            # Also try 7-digit numbers (in case some don't have leading zero)
            match7 = re.search(r'\b(\d{7})\b', cell_text)
            if match7:
                tkz_str = match7.group(1)
                tkz_num = int(tkz_str)
                if tkz_num >= 1000000:  # Valid 7-digit TKZ
                    print(f"DEBUG: Found last TKZ {tkz_num:08d} in row {row}: '{cell_text}' (7-digit)")
                    last_tkz = tkz_num
                    break  # Found the last one, stop searching
        
        # Close Excel
        workbook.Close()
        excel_app.Quit()
        
        if last_tkz is not None:
            print(f"Found last TKZ number: {last_tkz:08d}")
            return last_tkz
        else:
            print("ERROR: No valid TKZ numbers found!")
            print("STOPPING: Cannot generate new TKZ without knowing the last number")
            raise ValueError("No TKZ numbers found in Excel file")
            
    except Exception as e:
        print(f"ERROR reading TKZ file: {e}")
        # Clean up Excel if still running
        try:
            if 'excel_app' in locals():
                excel_app.Quit()
        except:
            pass
        raise

def get_last_antragsnummer(verzeichnis_file_path):
    """
    Read Verzeichnis.xlsb file using COM and find the last Antragsnummer for current year.
    Returns the last number and current year.
    """
    print(f"Reading Verzeichnis file using COM: {verzeichnis_file_path}")
    
    # Ensure we have a Path object and get absolute path
    verzeichnis_path = Path(verzeichnis_file_path)
    absolute_path = verzeichnis_path.resolve()
    
    current_year = datetime.now().year
    
    try:
        # Create Excel COM object
        excel_app = win32com.client.Dispatch("Excel.Application")
        excel_app.Visible = True
        excel_app.DisplayAlerts = False
        
        # Open workbook with absolute path as string
        # verzeichnis_file_path=r"Q:\DocumentManagement\NormstelleShare\TeileundStoffe\Datei\Verzeichnis.xlsb"
        print(f"\033[31m\n{absolute_path}\n\033[0m")
        workbook = excel_app.Workbooks.Open(str(absolute_path), ReadOnly=True)
        print(f"\033[32m\n{workbook}\n\033[0m")
        worksheet = workbook.Worksheets(1)  # First sheet
        print(f"\033[34m\n{worksheet}\n\033[0m")
        
        # Get the used range
        used_range = worksheet.UsedRange
        last_row = used_range.Rows.Count
        
        print(f"DEBUG: Verzeichnis worksheet has {last_row} rows with data")
        print(f"DEBUG: Looking for Antragsnummer pattern for year {current_year}")
        
        # Read first 10 values to understand structure
        print(f"DEBUG: First 10 values in column A:")
        for row in range(1, min(11, last_row + 1)):
            cell_value = worksheet.Cells(row, 1).Value
            cell_text = worksheet.Cells(row, 1).Text
            print(f"  Row {row}: Value='{cell_value}' Text='{cell_text}' (Value type: {type(cell_value)})")
        
        # Find the last Antragsnummer for current year by reading from bottom up
        print(f"DEBUG: Searching for last Antragsnummer for {current_year} from bottom up...")
        
        last_antrag = None
        
        # Start from the last row and work backwards
        for row in range(last_row, 0, -1):
            cell_text = worksheet.Cells(row, 1).Text
            
            if not cell_text or cell_text.strip() == "":
                continue
            
            cell_text = str(cell_text).strip()
            
            # Skip header row
            if 'antrag' in cell_text.lower() or 'nummer' in cell_text.lower():
                continue
            
            # Look for pattern XXX/YYYY where YYYY is current year
            match = re.search(rf'(\d+)/{current_year}', cell_text)
            if match:
                antrag_num = int(match.group(1))
                print(f"DEBUG: Found last Antragsnummer {antrag_num}/{current_year} in row {row}: '{cell_text}'")
                last_antrag = antrag_num
                break  # Found the last one for this year, stop searching
        
        # Close Excel
        workbook.Close()
        excel_app.Quit()
        
        if last_antrag is not None:
            print(f"Found last Antragsnummer for {current_year}: {last_antrag}/{current_year}")
            return last_antrag, current_year
        else:
            print(f"ERROR: No Antragsnummer found for {current_year}!")
            print("STOPPING: Cannot generate new Antragsnummer without knowing the last number")
            raise ValueError(f"No Antragsnummer found for year {current_year} in Excel file")
            
    except Exception as e:
        print(f"ERROR reading Verzeichnis file: {e}")
        # Clean up Excel if still running
        try:
            if 'excel_app' in locals():
                excel_app.Quit()
        except:
            pass
        raise

def generate_new_ids(tkz_file_path, verzeichnis_file_path):
    """
    Generate new TKZ and Antragsnummer by incrementing the last used numbers.
    
    Returns:
        tuple: (new_tkz_str, new_antragsnummer_str)
        Example: ("01044398", "159/2025")
    """
    print("Generating new IDs...")
    
    # Get last TKZ number and increment
    last_tkz = get_last_tkz_number(tkz_file_path)
    new_tkz = last_tkz + 1
    new_tkz_str = f"{new_tkz:08d}"  # Format as 8-digit string with leading zeros
    
    # Get last Antragsnummer and increment
    last_antrag, year = get_last_antragsnummer(verzeichnis_file_path)
    new_antrag = last_antrag + 1
    new_antragsnummer_str = f"{new_antrag}/{year}"
    
    print(f"Generated new TKZ: {new_tkz_str}")
    print(f"Generated new Antragsnummer: {new_antragsnummer_str}")
    
    return new_tkz_str, new_antragsnummer_str

def validate_id_generation(tkz_file_path, verzeichnis_file_path):
    """
    Test function to validate ID generation without actually using the IDs.
    """
    print("=== ID Generation Validation ===")
    
    try:
        new_tkz, new_antrag = generate_new_ids(tkz_file_path, verzeichnis_file_path)
        print(f"✓ Successfully generated IDs:")
        print(f"  New TKZ: {new_tkz}")
        print(f"  New Antragsnummer: {new_antrag}")
        return True
    except Exception as e:
        print(f"✗ Error generating IDs: {e}")
        return False

# Test function
if __name__ == "__main__":
    # Test with actual file paths
    base_path = Path(__file__).parent
    tkz_path = base_path / "TKZ.xls"
    verzeichnis_path = base_path / "Verzeichnis.xlsb"
    
    if tkz_path.exists() and verzeichnis_path.exists():
        validate_id_generation(tkz_path, verzeichnis_path)
    else:
        print("Excel files not found for testing")
        print(f"TKZ path: {tkz_path}")
        print(f"Verzeichnis path: {verzeichnis_path}")
