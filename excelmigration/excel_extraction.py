import json
import os
from pathlib import Path
import win32com.client as win32
import pythoncom

def normalize_url(url):
    """
    Normalize URLs by replacing relative paths with full network paths
    
    Args:
        url (str): The original URL
        
    Returns:
        str: The normalized URL
    """
    if not url:
        return url
    
    # Replace relative path with full network path
    if url.startswith("../.docs"):
        # Remove "../.docs" and replace with the full network path
        relative_part = url[8:]  # Remove "../.docs" (8 characters)
        # Convert forward slashes to backslashes for Windows network path consistency
        relative_part = relative_part.replace('/', '\\')
        normalized_url = f"file:///\\\\Dehesdna-a009a\\projekte\\k-z\\ofs\\Dokumentenservice\\TeileundStoffe{relative_part}"
        return normalized_url
    
    # If it's already a full file:// URL, return as is
    return url

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

def map_color_to_status(color):
    """
    Map color codes to status descriptions
    
    Args:
        color (str): Hex color code
        
    Returns:
        str: Status description
    """
    color_mapping = {
        "#FFCC99": "not approved",
        "#CCFFCC": "approved", 
        "#CCFF99": "approved for first order",
        "#FFFFFF": "processing"
    }
    
    return color_mapping.get(color, "unknown")

def extract_excel_to_json_unified(excel_file_path, output_json_path=None, max_row=5000):
    """
    Extract data and hyperlinks from Excel file using win32com
    
    Args:
        excel_file_path (str): Path to the Excel file
        output_json_path (str, optional): Path for output JSON file
        max_row (int): Maximum row to process (including header)
    
    Returns:
        dict: Extracted data as dictionary
    """
    excel_app = None
    workbook = None
    
    try:
        print(f"Reading Excel file: {excel_file_path}")
        
        # Initialize COM
        pythoncom.CoInitialize()
        
        # Create Excel application
        excel_app = win32.Dispatch("Excel.Application")
        excel_app.Visible = False
        excel_app.DisplayAlerts = False
        
        # Open workbook
        workbook = excel_app.Workbooks.Open(os.path.abspath(excel_file_path))
        worksheet = workbook.ActiveSheet
        
        # Get the used range to determine actual data bounds
        used_range = worksheet.UsedRange
        max_col = min(used_range.Columns.Count, 27)  # Limit to AA (27 columns)
        actual_max_row = min(used_range.Rows.Count, max_row)
        
        print(f"Worksheet has {actual_max_row} rows and {max_col} columns")
        
        # Get column headers (row 1)
        headers = []
        for col in range(1, max_col + 1):
            cell_value = worksheet.Cells(1, col).Value
            headers.append(cell_value if cell_value else f"Column_{chr(ord('A') + col - 1)}")
        
        print(f"Found {len(headers)} columns: {headers[:5]}{'...' if len(headers) > 5 else ''}")
        
        # Identify hyperlink columns (M to U = columns 13 to 21)
        hyperlink_col_indices = list(range(13, min(22, max_col + 1)))  # M=13, N=14, ..., U=21
        hyperlink_col_names = [headers[i-1] for i in hyperlink_col_indices if i <= len(headers)]
        print(f"Hyperlink columns: {hyperlink_col_names}")
        
        # Extract data row by row
        data_rows = []
        hyperlink_count = 0
        normalized_count = 0
        color_count = 0
        
        print(f"Processing rows 2 to {actual_max_row}...")
        
        for row_num in range(2, actual_max_row + 1):
            row_data = {}
            
            # Extract color from column A (first column)
            cell_a = worksheet.Cells(row_num, 1)
            try:
                # Get interior color (background color)
                rgb_value = cell_a.Interior.Color
                cell_color = rgb_to_hex(rgb_value)
                
                if cell_color and cell_color != "#FFFFFF":  # Ignore default white
                    row_data['color'] = cell_color
                    row_data['status'] = map_color_to_status(cell_color)
                    color_count += 1
                    
                    # Debug: Show first few colors
                    if color_count <= 5:
                        print(f"  Row {row_num}, Column A: Color {cell_color} -> Status: {row_data['status']}")
                else:
                    # Default to white/processing if no specific color
                    row_data['color'] = "#FFFFFF"
                    row_data['status'] = "processing"
                    
            except Exception as e:
                print(f"Warning: Could not extract color from row {row_num}: {e}")
                row_data['color'] = None
                row_data['status'] = "unknown"
            
            # Process each column
            for col_idx, header in enumerate(headers):
                col_num = col_idx + 1  # Convert to 1-based column number
                
                if col_num > max_col:
                    break
                    
                cell = worksheet.Cells(row_num, col_num)
                
                # Check if this is a hyperlink column
                if col_num in hyperlink_col_indices:
                    try:
                        # Check if cell has hyperlink
                        if cell.Hyperlinks.Count > 0:
                            hyperlink = cell.Hyperlinks(1)
                            target = hyperlink.Address
                            subaddress = hyperlink.SubAddress if hasattr(hyperlink, 'SubAddress') else None
                            
                            # Combine address and subaddress if both exist
                            if target and subaddress:
                                full_target = f"{target}#{subaddress}"
                            else:
                                full_target = target or subaddress
                            
                            # Normalize the URL
                            original_target = full_target
                            normalized_target = normalize_url(full_target)
                            
                            if original_target != normalized_target:
                                normalized_count += 1
                            
                            row_data[header] = {
                                'display_text': cell.Value,
                                'url': normalized_target,
                                'original_url': original_target if original_target != normalized_target else None,
                                'tooltip': hyperlink.ScreenTip if hasattr(hyperlink, 'ScreenTip') else None
                            }
                            hyperlink_count += 1
                            
                            # Debug: Show first few hyperlinks
                            if hyperlink_count <= 5:
                                print(f"  Row {row_num}, {header}: '{cell.Value}' -> {normalized_target[:50]}...")
                                
                        elif cell.Value:
                            # Check if the cell value looks like a file path
                            cell_value = str(cell.Value).strip()
                            if (cell_value.startswith(('C:', 'D:', 'E:', '\\\\', './', '../')) or 
                                '\\' in cell_value or 
                                cell_value.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx'))):
                                
                                # Normalize the inferred file path
                                normalized_path = normalize_url(cell_value)
                                
                                row_data[header] = {
                                    'display_text': cell.Value,
                                    'url': normalized_path,
                                    'original_url': cell_value if cell_value != normalized_path else None,
                                    'tooltip': None,
                                    'type': 'inferred_file_path'
                                }
                                
                                if cell_value != normalized_path:
                                    normalized_count += 1
                            else:
                                # Regular text value in hyperlink column
                                row_data[header] = {
                                    'display_text': cell.Value,
                                    'url': None,
                                    'tooltip': None
                                }
                        else:
                            # Empty cell in hyperlink column
                            row_data[header] = None
                            
                    except Exception as e:
                        print(f"Warning: Error processing hyperlink in row {row_num}, col {header}: {e}")
                        row_data[header] = {
                            'display_text': cell.Value,
                            'url': None,
                            'tooltip': None,
                            'error': str(e)
                        }
                else:
                    # Regular data column
                    try:
                        row_data[header] = cell.Value
                    except Exception as e:
                        print(f"Warning: Error reading cell value in row {row_num}, col {header}: {e}")
                        row_data[header] = None
            
            data_rows.append(row_data)
            
            # Progress indicator
            if row_num % 500 == 0:
                print(f"  Processed {row_num - 1} rows...")
        
        print(f"Successfully processed {len(data_rows)} rows")
        print(f"Total hyperlinks found: {hyperlink_count}")
        print(f"URLs normalized: {normalized_count}")
        print(f"Colors extracted: {color_count}")
        
        # Create the final data structure
        data_dict = {
            'metadata': {
                'total_rows': len(data_rows),
                'total_columns': len(headers),
                'columns': headers,
                'source_file': os.path.basename(excel_file_path),
                'hyperlinks_extracted': True,
                'hyperlink_columns': hyperlink_col_names,
                'colors_extracted': True,
                'color_mapping': {
                    '#FFCC99': 'not approved',
                    '#CCFFCC': 'approved',
                    '#CCFF99': 'approved for first order',
                    '#FFFFFF': 'processing'
                },
                'url_normalization': {
                    'applied': True,
                    'rule': 'Replace "../.docs" with "file:///\\\\Dehesdna-a009a\\projekte\\k-z\\ofs\\Dokumentenservice\\TeileundStoffe"',
                    'normalized_count': normalized_count
                },
                'extraction_method': 'win32com'
            },
            'data': data_rows
        }
        
        # Handle None values for JSON serialization
        def clean_none_values(obj):
            if isinstance(obj, dict):
                return {k: clean_none_values(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_none_values(item) for item in obj]
            elif obj is None:
                return None
            else:
                return obj
        
        data_dict = clean_none_values(data_dict)
        
        # Determine output file path
        if output_json_path is None:
            excel_path = Path(excel_file_path)
            output_json_path = excel_path.parent / f"{excel_path.stem}.json"
        
        # Write to JSON file
        print(f"Writing JSON to: {output_json_path}")
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Successfully created JSON file with {len(data_rows)} rows")
        print(f"Output file: {output_json_path}")
        
        return data_dict
        
    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
        
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
    """Main function to run the unified extraction"""
    # Get the directory of this script
    script_dir = Path(__file__).parent
    excel_file = script_dir / "Verzeichnis.xlsx"
    
    if not excel_file.exists():
        print(f"Error: Excel file not found at {excel_file}")
        return
    
    try:
        # Extract data and hyperlinks in one pass
        data = extract_excel_to_json_unified(str(excel_file))
        
        # Print summary
        print("\n" + "="*60)
        print("UNIFIED EXTRACTION SUMMARY")
        print("="*60)
        print(f"Source file: {excel_file.name}")
        print(f"Total rows extracted: {data['metadata']['total_rows']}")
        print(f"Total columns: {data['metadata']['total_columns']}")
        print(f"Hyperlink columns: {', '.join(data['metadata']['hyperlink_columns'])}")
        print(f"URLs normalized: {data['metadata']['url_normalization']['normalized_count']}")
        print(f"Colors extracted: {data['metadata'].get('colors_extracted', False)}")
        print(f"Extraction method: {data['metadata']['extraction_method']}")
        
        # Show sample data
        if data['data']:
            print(f"\nFirst row sample:")
            first_row = data['data'][0]
            
            # Show color and status
            print(f"  Color: {first_row.get('color', 'None')}")
            print(f"  Status: {first_row.get('status', 'None')}")
            
            # Show regular columns
            regular_cols = ['Antrag-nummer', 'Teile-nummer', 'Freigabe']
            for col in regular_cols:
                if col in first_row:
                    print(f"  {col}: {first_row[col]}")
            
            # Show hyperlink columns
            print(f"\nHyperlink columns sample:")
            for col in data['metadata']['hyperlink_columns'][:3]:
                if col in first_row and first_row[col]:
                    if isinstance(first_row[col], dict):
                        print(f"  {col}: {first_row[col]['display_text']} -> {first_row[col]['url'][:50]}...")
                    else:
                        print(f"  {col}: {first_row[col]}")
                        
    except Exception as e:
        print(f"Failed to extract data: {str(e)}")

if __name__ == "__main__":
    main()
