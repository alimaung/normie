import json
import os
from pathlib import Path
import win32com.client as win32
import pythoncom

def rgb_to_hex(rgb_value):
    """
    Convert RGB value to hex color code
    
    Args:
        rgb_value (int/float): RGB value as integer or float
        
    Returns:
        str: Hex color code
    """
    if rgb_value is None:
        return None
    
    try:
        # Convert to integer if it's a float
        rgb_int = int(rgb_value)
        
        # Extract RGB components from the integer
        red = rgb_int & 255
        green = (rgb_int >> 8) & 255
        blue = (rgb_int >> 16) & 255
        
        return f"#{red:02X}{green:02X}{blue:02X}"
    
    except (ValueError, TypeError) as e:
        print(f"Warning: Could not convert RGB value {rgb_value} to hex: {e}")
        return None

def debug_specific_rows(excel_file_path):
    """
    Debug specific rows with known states and URLs
    
    Args:
        excel_file_path (str): Path to the Excel file
    """
    excel_app = None
    workbook = None
    
    # Define test rows
    color_test_rows = {
        3857: "red",
        5040: "red & strikethrough"
    }
    
    url_test_rows = [1989, 4353, 4377, 4759]
    
    try:
        print(f"=== DEBUG SPECIFIC ROWS ===")
        print(f"Excel file: {excel_file_path}")
        print(f"Testing color rows: {list(color_test_rows.keys())}")
        print(f"Testing URL rows: {url_test_rows}")
        print()
        
        # Initialize COM
        pythoncom.CoInitialize()
        
        # Create Excel application
        excel_app = win32.Dispatch("Excel.Application")
        excel_app.Visible = False
        excel_app.DisplayAlerts = False
        
        # Open workbook
        workbook = excel_app.Workbooks.Open(os.path.abspath(excel_file_path))
        worksheet = workbook.ActiveSheet
        
        # Get column headers
        headers = []
        for col in range(1, 12):  # A to K
            cell_value = worksheet.Cells(1, col).Value
            headers.append(cell_value if cell_value else f"Column_{chr(ord('A') + col - 1)}")
        
        print(f"Column headers: {headers}")
        print()
        
        # Test color detection rows
        print("=== COLOR DETECTION TESTS ===")
        for row_num, expected in color_test_rows.items():
            print(f"\nRow {row_num} (Expected: {expected}):")
            
            try:
                cell_a = worksheet.Cells(row_num, 1)
                cell_value = cell_a.Value
                
                # Test interior color (background)
                rgb_value = cell_a.Interior.Color
                interior_color = rgb_to_hex(rgb_value)
                
                # Test font color
                font_rgb = cell_a.Font.Color
                font_color = rgb_to_hex(int(font_rgb)) if font_rgb != -4142 else "automatic"
                
                # Test strikethrough
                strikethrough = cell_a.Font.Strikethrough
                
                print(f"  Cell value: '{cell_value}'")
                print(f"  Interior color (background): {interior_color}")
                print(f"  Font color: {font_color}")
                print(f"  Strikethrough: {strikethrough}")
                
                # Determine status using interior color method
                status_interior = "active"
                if interior_color and interior_color != "#FFFFFF":
                    if interior_color == "#FF0000" or (interior_color.startswith("#") and 
                        int(interior_color[1:3], 16) > 200 and 
                        int(interior_color[3:5], 16) < 50 and 
                        int(interior_color[5:7], 16) < 50):
                        status_interior = "discontinued"
                
                # Determine status using font color method
                status_font = "active"
                if font_color != "automatic" and isinstance(font_color, str) and font_color.startswith("#"):
                    if font_color == "#FF0000" or (
                        int(font_color[1:3], 16) > 200 and 
                        int(font_color[3:5], 16) < 50 and 
                        int(font_color[5:7], 16) < 50):
                        status_font = "discontinued"
                        if strikethrough:
                            status_font = "discontinued (strikethrough confirmed)"
                
                print(f"  Status (interior color): {status_interior}")
                print(f"  Status (font color): {status_font}")
                
            except Exception as e:
                print(f"  ERROR: {e}")
        
        # Test URL detection rows
        print("\n=== URL DETECTION TESTS ===")
        for row_num in url_test_rows:
            print(f"\nRow {row_num}:")
            
            try:
                # Check all columns for URLs, focus on column K
                for col in range(1, 12):
                    cell = worksheet.Cells(row_num, col)
                    cell_value = cell.Value
                    header = headers[col-1]
                    
                    if cell.Hyperlinks.Count > 0:
                        hyperlink = cell.Hyperlinks(1)
                        target = hyperlink.Address
                        subaddress = hyperlink.SubAddress if hasattr(hyperlink, 'SubAddress') else None
                        
                        # Combine address and subaddress if both exist
                        if target and subaddress:
                            full_target = f"{target}#{subaddress}"
                        else:
                            full_target = target or subaddress
                        
                        tooltip = hyperlink.ScreenTip if hasattr(hyperlink, 'ScreenTip') else None
                        
                        print(f"  {header} (Col {chr(ord('A') + col - 1)}): HYPERLINK FOUND")
                        print(f"    Display text: '{cell_value}'")
                        print(f"    URL: {full_target}")
                        if tooltip:
                            print(f"    Tooltip: {tooltip}")
                    
                    elif cell_value and col == 11:  # Column K - show even if no hyperlink
                        print(f"  {header} (Col K): '{cell_value}' (NO HYPERLINK)")
                
            except Exception as e:
                print(f"  ERROR: {e}")
        
        # Test a few random rows for comparison
        print("\n=== RANDOM ROWS FOR COMPARISON ===")
        test_random_rows = [10, 100, 1000, 2000, 3000]
        
        for row_num in test_random_rows:
            try:
                cell_a = worksheet.Cells(row_num, 1)
                cell_value = cell_a.Value
                interior_color = rgb_to_hex(cell_a.Interior.Color)
                
                if cell_value:  # Only show rows with data
                    print(f"Row {row_num}: '{cell_value}' | Interior color: {interior_color}")
                    
            except Exception as e:
                pass
        
        print(f"\n=== DEBUG COMPLETE ===")
        
    except Exception as e:
        print(f"Error during debug: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up COM objects
        try:
            if workbook:
                workbook.Close(SaveChanges=False)
            if excel_app:
                excel_app.Quit()
        except:
            pass
        
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def main():
    """Main function to run the debug"""
    # Get the directory of this script
    script_dir = Path(__file__).parent
    excel_file = script_dir / "Teilenummern_0104....xls"
    
    if not excel_file.exists():
        print(f"Error: Excel file not found at {excel_file}")
        return
    
    debug_specific_rows(str(excel_file))

if __name__ == "__main__":
    main() 