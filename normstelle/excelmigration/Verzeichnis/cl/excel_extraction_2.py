import json
import os
import time
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

def collect_all_hyperlinks(worksheet):
    """
    Collect all hyperlinks from worksheet in a single operation
    
    Args:
        worksheet: Excel worksheet object
        
    Returns:
        dict: Dictionary mapping (row, col) to hyperlink data
    """
    hyperlink_map = {}
    
    try:
        # Get all hyperlinks from the worksheet at once
        for hyperlink in worksheet.Hyperlinks:
            row = hyperlink.Range.Row
            col = hyperlink.Range.Column
            
            # Extract hyperlink properties
            address = hyperlink.Address if hasattr(hyperlink, 'Address') else None
            subaddress = hyperlink.SubAddress if hasattr(hyperlink, 'SubAddress') else None
            screentip = hyperlink.ScreenTip if hasattr(hyperlink, 'ScreenTip') else None
            
            # Combine address and subaddress if both exist
            if address and subaddress:
                full_target = f"{address}#{subaddress}"
            else:
                full_target = address or subaddress
            
            hyperlink_map[(row, col)] = {
                'address': address,
                'subaddress': subaddress,
                'full_target': full_target,
                'screentip': screentip
            }
            
    except Exception as e:
        print(f"Warning: Error collecting hyperlinks: {e}")
    
    return hyperlink_map

def extract_bulk_colors(worksheet, start_row, end_row):
    """
    Extract colors from column A in bulk
    
    Args:
        worksheet: Excel worksheet object
        start_row (int): Starting row number
        end_row (int): Ending row number
        
    Returns:
        list: List of hex color codes
    """
    colors = []
    
    try:
        # Get the range for column A
        color_range = worksheet.Range(f"A{start_row}:A{end_row}")
        
        # Process each cell in the range
        for cell in color_range:
            try:
                rgb_value = cell.Interior.Color
                hex_color = rgb_to_hex(rgb_value)
                colors.append(hex_color if hex_color else "#FFFFFF")
            except Exception as e:
                print(f"Warning: Could not extract color from cell: {e}")
                colors.append("#FFFFFF")
                
    except Exception as e:
        print(f"Warning: Error in bulk color extraction: {e}")
        # Fallback: return default colors
        colors = ["#FFFFFF"] * (end_row - start_row + 1)
    
    return colors

def excel_col_letter(col_num):
    """
    Convert column number to Excel column letter(s)
    1 -> A, 26 -> Z, 27 -> AA, etc.
    """
    result = ""
    while col_num > 0:
        col_num -= 1  # Make it 0-based
        result = chr(65 + (col_num % 26)) + result
        col_num //= 26
    return result

def extract_excel_to_json_optimized(excel_file_path, output_json_path=None, max_row=5000):
    """
    Extract data and hyperlinks from Excel file using optimized bulk operations
    
    Args:
        excel_file_path (str): Path to the Excel file
        output_json_path (str, optional): Path for output JSON file
        max_row (int): Maximum row to process (including header)
    
    Returns:
        dict: Extracted data as dictionary
    """
    excel_app = None
    workbook = None
    start_time = time.time()
    
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
        
        # OPTIMIZATION 1: Bulk read headers (row 1)
        header_time = time.time()
        headers = []
        header_range = worksheet.Range(f"A1:{excel_col_letter(max_col)}1")
        header_values = header_range.Value[0] if header_range.Value else []
        
        for col_idx in range(max_col):
            if col_idx < len(header_values) and header_values[col_idx]:
                headers.append(header_values[col_idx])
            else:
                headers.append(f"Column_{chr(ord('A') + col_idx)}")
        
        print(f"Headers extracted in {time.time() - header_time:.3f}s: {headers[:5]}{'...' if len(headers) > 5 else ''}")
        
        # Identify hyperlink columns (M to U = columns 13 to 21)
        hyperlink_col_indices = list(range(13, min(22, max_col + 1)))  # M=13, N=14, ..., U=21
        hyperlink_col_names = [headers[i-1] for i in hyperlink_col_indices if i <= len(headers)]
        print(f"Hyperlink columns: {hyperlink_col_names}")
        
        # OPTIMIZATION 2: Bulk read all data
        data_time = time.time()
        print(f"Bulk reading data range A2:{excel_col_letter(max_col)}{actual_max_row}...")
        
        if actual_max_row > 1:  # Only if there's data beyond headers
            data_range = worksheet.Range(f"A2:{excel_col_letter(max_col)}{actual_max_row}")
            all_data = data_range.Value
            
            # Handle single row case (Excel returns tuple instead of tuple of tuples)
            if actual_max_row == 2:  # Only one data row
                all_data = [all_data] if all_data else []
        else:
            all_data = []
        
        print(f"Bulk data read in {time.time() - data_time:.3f}s")
        
        # OPTIMIZATION 3: Bulk extract colors
        color_time = time.time()
        print(f"Bulk extracting colors from column A...")
        
        if actual_max_row > 1:
            colors = extract_bulk_colors(worksheet, 2, actual_max_row)
        else:
            colors = []
        
        print(f"Colors extracted in {time.time() - color_time:.3f}s")
        
        # OPTIMIZATION 4: Collect all hyperlinks at once
        hyperlink_time = time.time()
        print(f"Collecting all hyperlinks...")
        
        hyperlink_map = collect_all_hyperlinks(worksheet)
        
        print(f"Hyperlinks collected in {time.time() - hyperlink_time:.3f}s: {len(hyperlink_map)} found")
        
        # OPTIMIZATION 5: Process data in memory
        process_time = time.time()
        print(f"Processing {len(all_data)} rows in memory...")
        
        data_rows = []
        hyperlink_count = 0
        normalized_count = 0
        color_count = 0
        
        for row_idx, row_data_tuple in enumerate(all_data):
            row_num = row_idx + 2  # Excel row number (starting from row 2)
            row_data = {}
            
            # Extract color and status for this row
            if row_idx < len(colors):
                cell_color = colors[row_idx]
                if cell_color and cell_color != "#FFFFFF":  # Ignore default white
                    row_data['color'] = cell_color
                    row_data['status'] = map_color_to_status(cell_color)
                    color_count += 1
                else:
                    row_data['color'] = "#FFFFFF"
                    row_data['status'] = "processing"
            else:
                row_data['color'] = "#FFFFFF"
                row_data['status'] = "processing"
            
            # Process each column for this row
            for col_idx, header in enumerate(headers):
                col_num = col_idx + 1  # Convert to 1-based column number
                
                if col_num > max_col:
                    break
                
                # Get cell value from bulk data
                cell_value = None
                if row_data_tuple and col_idx < len(row_data_tuple):
                    cell_value = row_data_tuple[col_idx]
                
                # Check if this is a hyperlink column
                if col_num in hyperlink_col_indices:
                    # Check if there's a hyperlink for this cell
                    hyperlink_data = hyperlink_map.get((row_num, col_num))
                    
                    if hyperlink_data:
                        # Process hyperlink
                        full_target = hyperlink_data['full_target']
                        original_target = full_target
                        normalized_target = normalize_url(full_target)
                        
                        if original_target != normalized_target:
                            normalized_count += 1
                        
                        row_data[header] = {
                            'display_text': cell_value,
                            'url': normalized_target,
                            'original_url': original_target if original_target != normalized_target else None,
                            'tooltip': hyperlink_data['screentip']
                        }
                        hyperlink_count += 1
                        
                    elif cell_value:
                        # Check if the cell value looks like a file path
                        cell_value_str = str(cell_value).strip()
                        if (cell_value_str.startswith(('C:', 'D:', 'E:', '\\\\', './', '../')) or 
                            '\\' in cell_value_str or 
                            cell_value_str.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx'))):
                            
                            # Normalize the inferred file path
                            normalized_path = normalize_url(cell_value_str)
                            
                            row_data[header] = {
                                'display_text': cell_value,
                                'url': normalized_path,
                                'original_url': cell_value_str if cell_value_str != normalized_path else None,
                                'tooltip': None,
                                'type': 'inferred_file_path'
                            }
                            
                            if cell_value_str != normalized_path:
                                normalized_count += 1
                        else:
                            # Regular text value in hyperlink column
                            row_data[header] = {
                                'display_text': cell_value,
                                'url': None,
                                'tooltip': None
                            }
                    else:
                        # Empty cell in hyperlink column
                        row_data[header] = None
                else:
                    # Regular data column
                    row_data[header] = cell_value
            
            data_rows.append(row_data)
            
            # Progress indicator for large datasets
            if (row_idx + 1) % 1000 == 0:
                print(f"  Processed {row_idx + 1} rows...")
        
        print(f"Data processing completed in {time.time() - process_time:.3f}s")
        
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
                'extraction_method': 'win32com_optimized',
                'performance': {
                    'total_time': time.time() - start_time,
                    'bulk_operations_used': True
                }
            },
            'data': data_rows
        }
        
        print(f"Successfully processed {len(data_rows)} rows")
        print(f"Total hyperlinks found: {hyperlink_count}")
        print(f"URLs normalized: {normalized_count}")
        print(f"Colors extracted: {color_count}")
        print(f"Total processing time: {time.time() - start_time:.3f}s")
        
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
            output_json_path = excel_path.parent / f"{excel_path.stem}_optimized.json"
        
        # Write to JSON file
        write_time = time.time()
        print(f"Writing JSON to: {output_json_path}")
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"JSON written in {time.time() - write_time:.3f}s")
        print(f"Successfully created optimized JSON file with {len(data_rows)} rows")
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
    """Main function to run the optimized extraction"""
    # Get the directory of this script
    script_dir = Path(__file__).parent
    excel_file = script_dir / "Verzeichnis.xlsx"
    
    if not excel_file.exists():
        print(f"Error: Excel file not found at {excel_file}")
        return
    
    try:
        start_time = time.time()
        print("="*60)
        print("OPTIMIZED EXCEL EXTRACTION")
        print("="*60)
        
        # Extract data and hyperlinks using optimized method
        data = extract_excel_to_json_optimized(str(excel_file))
        
        total_time = time.time() - start_time
        
        # Print summary
        print("\n" + "="*60)
        print("OPTIMIZED EXTRACTION SUMMARY")
        print("="*60)
        print(f"Source file: {excel_file.name}")
        print(f"Total rows extracted: {data['metadata']['total_rows']}")
        print(f"Total columns: {data['metadata']['total_columns']}")
        print(f"Hyperlink columns: {', '.join(data['metadata']['hyperlink_columns'])}")
        print(f"URLs normalized: {data['metadata']['url_normalization']['normalized_count']}")
        print(f"Colors extracted: {data['metadata'].get('colors_extracted', False)}")
        print(f"Extraction method: {data['metadata']['extraction_method']}")
        print(f"TOTAL TIME: {total_time:.3f}s")
        
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

