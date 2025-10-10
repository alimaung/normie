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
    #if url.startswith("../.docs"):
    #    # Remove "../.docs" and replace with the full network path
    #    relative_part = url[8:]  # Remove "../.docs" (8 characters)
    #    # Convert forward slashes to backslashes for Windows network path consistency
    #    relative_part = relative_part.replace('/', '\\')
    #    normalized_url = f"file:///\\\\Dehesdna-a009a\\projekte\\k-z\\ofs\\Dokumentenservice\\TeileundStoffe{relative_part}"
    #    return normalized_url
    
    # If it's already a full file:// URL, return as is
    return url

def rgb_to_hex(rgb_value):
    """
    Convert RGB value to hex color code
    Enhanced to handle Win32 COM Excel indexed colors correctly
    
    Args:
        rgb_value (int/float): RGB value as integer or float from Win32 COM
        
    Returns:
        str: Hex color code
    """
    if rgb_value is None:
        return None
    
    try:
        # Convert to integer if it's a float
        rgb_int = int(rgb_value)
        
        # CRITICAL: Handle Win32 COM indexed colors first
        # These are the actual RGB integer values that Win32 COM returns for Excel indexed colors
        com_indexed_color_map = {
            13434828: "#CCFFCC",  # Light green (approved) - indexed 42
            10079487: "#CCFF99",  # Light green-yellow (approved for first order) - indexed 43  
            10079164: "#FFCC99",  # Light orange (not approved) - indexed 47
            16777215: "#FFFFFF",  # White (processing) - default
            # Add more mappings as needed when other indexed colors are encountered
        }
        
        # Check if this is a known indexed color first
        if rgb_int in com_indexed_color_map:
            return com_indexed_color_map[rgb_int]
        
        # If not a known indexed color, process as regular RGB
        # Extract RGB components from the integer (BGR format for Win32 COM)
        red = rgb_int & 255
        green = (rgb_int >> 8) & 255
        blue = (rgb_int >> 16) & 255
        
        hex_color = f"#{red:02X}{green:02X}{blue:02X}"
        
        # Debug: Log unknown colors for future mapping
        if hex_color not in ["#FFFFFF", "#000000"]:  # Ignore common defaults
            print(f"Debug: Unknown color RGB={rgb_int} -> {hex_color} (add to indexed_color_map if this is a standard Excel color)")
        
        return hex_color
    
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
    start_time = time.time()
    
    try:
        print(f"[{time.strftime('%H:%M:%S')}] Starting Excel extraction: {excel_file_path}")
        
        # Initialize COM
        com_start = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] Initializing COM...")
        pythoncom.CoInitialize()
        
        # Create Excel application
        excel_app = win32.Dispatch("Excel.Application")
        excel_app.Visible = False
        excel_app.DisplayAlerts = False
        print(f"[{time.strftime('%H:%M:%S')}] COM initialized in {time.time() - com_start:.3f}s")
        
        # Open workbook
        file_open_start = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] Opening Excel file...")
        workbook = excel_app.Workbooks.Open(os.path.abspath(excel_file_path))
        worksheet = workbook.ActiveSheet
        print(f"[{time.strftime('%H:%M:%S')}] File opened in {time.time() - file_open_start:.3f}s")
        
        # Get the used range to determine actual data bounds
        range_start = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] Analyzing worksheet dimensions...")
        used_range = worksheet.UsedRange
        max_col = min(used_range.Columns.Count, 27)  # Limit to AA (27 columns)
        actual_max_row = min(used_range.Rows.Count, max_row)
        
        print(f"[{time.strftime('%H:%M:%S')}] Worksheet analysis completed in {time.time() - range_start:.3f}s")
        print(f"[{time.strftime('%H:%M:%S')}] Worksheet has {actual_max_row} rows and {max_col} columns")
        
        # Get column headers (row 1)
        header_start = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] Extracting column headers...")
        headers = []
        for col in range(1, max_col + 1):
            cell_value = worksheet.Cells(1, col).Value
            headers.append(cell_value if cell_value else f"Column_{chr(ord('A') + col - 1)}")
        
        print(f"[{time.strftime('%H:%M:%S')}] Headers extracted in {time.time() - header_start:.3f}s")
        print(f"[{time.strftime('%H:%M:%S')}] Found {len(headers)} columns: {headers[:5]}{'...' if len(headers) > 5 else ''}")
        
        # Identify hyperlink columns (M to U = columns 13 to 21)
        hyperlink_col_indices = list(range(13, min(22, max_col + 1)))  # M=13, N=14, ..., U=21
        hyperlink_col_names = [headers[i-1] for i in hyperlink_col_indices if i <= len(headers)]
        print(f"[{time.strftime('%H:%M:%S')}] Hyperlink columns identified: {hyperlink_col_names}")
        
        # Performance estimation
        total_cells = (actual_max_row - 1) * max_col  # Exclude header row
        print(f"[{time.strftime('%H:%M:%S')}] Estimated cells to process: {total_cells:,}")
        print(f"[{time.strftime('%H:%M:%S')}] Starting row-by-row processing...")
        
        # Extract data row by row
        data_rows = []
        hyperlink_count = 0
        normalized_count = 0
        color_count = 0
        
        # Performance tracking
        row_processing_start = time.time()
        color_processing_time = 0
        hyperlink_processing_time = 0
        regular_cell_time = 0
        
        print(f"[{time.strftime('%H:%M:%S')}] Processing rows 2 to {actual_max_row}...")
        
        for row_num in range(2, actual_max_row + 1):
            row_start_time = time.time()
            row_data = {}
            
            # Extract color from column A (first column)
            color_start = time.time()
            cell_a = worksheet.Cells(row_num, 1)
            try:
                # Get interior color (background color)
                rgb_value = cell_a.Interior.Color
                cell_color = rgb_to_hex(rgb_value)
                
                # Enhanced debugging for color extraction
                if color_count <= 10:  # Debug first 10 colors found
                    print(f"[{time.strftime('%H:%M:%S')}]   Row {row_num}: Win32 RGB={rgb_value} -> Hex={cell_color}")
                
                if cell_color and cell_color != "#FFFFFF":  # Ignore default white
                    row_data['color'] = cell_color
                    row_data['status'] = map_color_to_status(cell_color)
                    color_count += 1
                    
                    # Debug: Show first few colors with full details
                    if color_count <= 5:
                        print(f"[{time.strftime('%H:%M:%S')}]   Row {row_num}, Column A: RGB={rgb_value} -> Color={cell_color} -> Status='{row_data['status']}'")
                else:
                    # Default to white/processing if no specific color
                    row_data['color'] = "#FFFFFF"
                    row_data['status'] = "processing"
                    
                    # Debug: Show some white values to verify they're actually white
                    if color_count == 0 and row_num <= 5:
                        print(f"[{time.strftime('%H:%M:%S')}]   Row {row_num}: White/default color detected (RGB={rgb_value})")
                    
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Warning: Could not extract color from row {row_num}: {e}")
                row_data['color'] = None
                row_data['status'] = "unknown"
            
            color_processing_time += time.time() - color_start
            
            # Process each column
            for col_idx, header in enumerate(headers):
                col_num = col_idx + 1  # Convert to 1-based column number
                
                if col_num > max_col:
                    break
                
                cell_start = time.time()
                cell = worksheet.Cells(row_num, col_num)
                
                # Check if this is a hyperlink column
                if col_num in hyperlink_col_indices:
                    hyperlink_start = time.time()
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
                                print(f"[{time.strftime('%H:%M:%S')}]   Row {row_num}, {header}: '{cell.Value}' -> {normalized_target[:50]}...")
                                
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
                        print(f"[{time.strftime('%H:%M:%S')}] Warning: Error processing hyperlink in row {row_num}, col {header}: {e}")
                        row_data[header] = {
                            'display_text': cell.Value,
                            'url': None,
                            'tooltip': None,
                            'error': str(e)
                        }
                    
                    hyperlink_processing_time += time.time() - hyperlink_start
                else:
                    # Regular data column
                    regular_start = time.time()
                    try:
                        row_data[header] = cell.Value
                    except Exception as e:
                        print(f"[{time.strftime('%H:%M:%S')}] Warning: Error reading cell value in row {row_num}, col {header}: {e}")
                        row_data[header] = None
                    regular_cell_time += time.time() - regular_start
            
            data_rows.append(row_data)
            
            # Enhanced progress indicator with timing
            if row_num % 100 == 0:
                elapsed = time.time() - row_processing_start
                rows_done = row_num - 1  # Exclude header row
                total_rows = actual_max_row - 1
                rows_per_sec = rows_done / elapsed if elapsed > 0 else 0
                eta_seconds = (total_rows - rows_done) / rows_per_sec if rows_per_sec > 0 else 0
                eta_time = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
                
                print(f"[{time.strftime('%H:%M:%S')}]   Progress: {rows_done}/{total_rows} rows ({rows_done/total_rows*100:.1f}%) - "
                      f"{rows_per_sec:.1f} rows/sec - ETA: {eta_time}")
            elif row_num % 500 == 0:
                elapsed = time.time() - row_processing_start
                rows_done = row_num - 1
                total_rows = actual_max_row - 1
                print(f"[{time.strftime('%H:%M:%S')}]   Processed {rows_done}/{total_rows} rows ({rows_done/total_rows*100:.1f}%) in {elapsed:.1f}s")
        
        # Row processing completed - show detailed timing
        row_processing_total = time.time() - row_processing_start
        
        print(f"[{time.strftime('%H:%M:%S')}] Row processing completed in {row_processing_total:.3f}s")
        print(f"[{time.strftime('%H:%M:%S')}] Successfully processed {len(data_rows)} rows")
        print(f"[{time.strftime('%H:%M:%S')}] Total hyperlinks found: {hyperlink_count}")
        print(f"[{time.strftime('%H:%M:%S')}] URLs normalized: {normalized_count}")
        print(f"[{time.strftime('%H:%M:%S')}] Colors extracted: {color_count}")
        
        # Performance breakdown
        print(f"[{time.strftime('%H:%M:%S')}] PERFORMANCE BREAKDOWN:")
        print(f"[{time.strftime('%H:%M:%S')}]   Color processing: {color_processing_time:.3f}s ({color_processing_time/row_processing_total*100:.1f}%)")
        print(f"[{time.strftime('%H:%M:%S')}]   Hyperlink processing: {hyperlink_processing_time:.3f}s ({hyperlink_processing_time/row_processing_total*100:.1f}%)")
        print(f"[{time.strftime('%H:%M:%S')}]   Regular cell processing: {regular_cell_time:.3f}s ({regular_cell_time/row_processing_total*100:.1f}%)")
        
        avg_row_time = row_processing_total / len(data_rows) if data_rows else 0
        print(f"[{time.strftime('%H:%M:%S')}]   Average time per row: {avg_row_time*1000:.2f}ms")
        
        # Create the final data structure
        json_start = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] Creating JSON data structure...")
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
                'extraction_method': 'win32com',
                'performance': {
                    'total_processing_time': row_processing_total,
                    'color_processing_time': color_processing_time,
                    'hyperlink_processing_time': hyperlink_processing_time,
                    'regular_cell_time': regular_cell_time,
                    'average_row_time_ms': avg_row_time * 1000,
                    'rows_per_second': len(data_rows) / row_processing_total if row_processing_total > 0 else 0
                }
            },
            'data': data_rows
        }
        
        # Handle None values for JSON serialization
        print(f"[{time.strftime('%H:%M:%S')}] Cleaning data for JSON serialization...")
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
        print(f"[{time.strftime('%H:%M:%S')}] JSON structure created in {time.time() - json_start:.3f}s")
        
        # Determine output file path
        if output_json_path is None:
            excel_path = Path(excel_file_path)
            output_json_path = excel_path.parent / f"{excel_path.stem}.json"
        
        # Write to JSON file
        write_start = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] Writing JSON to: {output_json_path}")
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False, default=str)
        
        write_time = time.time() - write_start
        total_time = time.time() - start_time
        
        print(f"[{time.strftime('%H:%M:%S')}] JSON written in {write_time:.3f}s")
        print(f"[{time.strftime('%H:%M:%S')}] Successfully created JSON file with {len(data_rows)} rows")
        print(f"[{time.strftime('%H:%M:%S')}] Output file: {output_json_path}")
        
        # Final timing summary
        print(f"\n[{time.strftime('%H:%M:%S')}] ={'='*60}")
        print(f"[{time.strftime('%H:%M:%S')}] FINAL TIMING SUMMARY")
        print(f"[{time.strftime('%H:%M:%S')}] ={'='*60}")
        print(f"[{time.strftime('%H:%M:%S')}] Total execution time: {total_time:.3f}s")
        print(f"[{time.strftime('%H:%M:%S')}] Row processing: {row_processing_total:.3f}s ({row_processing_total/total_time*100:.1f}%)")
        print(f"[{time.strftime('%H:%M:%S')}] JSON creation+writing: {time.time() - json_start:.3f}s ({(time.time() - json_start)/total_time*100:.1f}%)")
        print(f"[{time.strftime('%H:%M:%S')}] ={'='*60}")
        
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
        main_start = time.time()
        print(f"\n[{time.strftime('%H:%M:%S')}] ={'='*60}")
        print(f"[{time.strftime('%H:%M:%S')}] ORIGINAL EXCEL EXTRACTION WITH DETAILED TIMING")
        print(f"[{time.strftime('%H:%M:%S')}] ={'='*60}")
        
        # Extract data and hyperlinks in one pass
        data = extract_excel_to_json_unified(str(excel_file))
        
        main_total = time.time() - main_start
        
        # Print enhanced summary
        print(f"\n[{time.strftime('%H:%M:%S')}] ={'='*60}")
        print(f"[{time.strftime('%H:%M:%S')}] ENHANCED EXTRACTION SUMMARY")
        print(f"[{time.strftime('%H:%M:%S')}] ={'='*60}")
        print(f"[{time.strftime('%H:%M:%S')}] Source file: {excel_file.name}")
        print(f"[{time.strftime('%H:%M:%S')}] Total rows extracted: {data['metadata']['total_rows']}")
        print(f"[{time.strftime('%H:%M:%S')}] Total columns: {data['metadata']['total_columns']}")
        print(f"[{time.strftime('%H:%M:%S')}] Hyperlink columns: {', '.join(data['metadata']['hyperlink_columns'])}")
        print(f"[{time.strftime('%H:%M:%S')}] URLs normalized: {data['metadata']['url_normalization']['normalized_count']}")
        print(f"[{time.strftime('%H:%M:%S')}] Colors extracted: {data['metadata'].get('colors_extracted', False)}")
        print(f"[{time.strftime('%H:%M:%S')}] Extraction method: {data['metadata']['extraction_method']}")
        
        # Show performance data
        if 'performance' in data['metadata']:
            perf = data['metadata']['performance']
            print(f"[{time.strftime('%H:%M:%S')}] Performance metrics:")
            print(f"[{time.strftime('%H:%M:%S')}]   Rows per second: {perf['rows_per_second']:.2f}")
            print(f"[{time.strftime('%H:%M:%S')}]   Average time per row: {perf['average_row_time_ms']:.2f}ms")
            print(f"[{time.strftime('%H:%M:%S')}]   Color processing: {perf['color_processing_time']:.3f}s")
            print(f"[{time.strftime('%H:%M:%S')}]   Hyperlink processing: {perf['hyperlink_processing_time']:.3f}s")
            print(f"[{time.strftime('%H:%M:%S')}]   Regular cell processing: {perf['regular_cell_time']:.3f}s")
        
        # Show sample data
        if data['data']:
            print(f"\n[{time.strftime('%H:%M:%S')}] First row sample:")
            first_row = data['data'][0]
            
            # Show color and status
            print(f"[{time.strftime('%H:%M:%S')}]   Color: {first_row.get('color', 'None')}")
            print(f"[{time.strftime('%H:%M:%S')}]   Status: {first_row.get('status', 'None')}")
            
            # Show regular columns
            regular_cols = ['Antrag-nummer', 'Teile-nummer', 'Freigabe']
            for col in regular_cols:
                if col in first_row:
                    print(f"[{time.strftime('%H:%M:%S')}]   {col}: {first_row[col]}")
            
            # Show hyperlink columns
            print(f"\n[{time.strftime('%H:%M:%S')}] Hyperlink columns sample:")
            for col in data['metadata']['hyperlink_columns'][:3]:
                if col in first_row and first_row[col]:
                    if isinstance(first_row[col], dict):
                        print(f"[{time.strftime('%H:%M:%S')}]   {col}: {first_row[col]['display_text']} -> {first_row[col]['url'][:50]}...")
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}]   {col}: {first_row[col]}")
        
        print(f"\n[{time.strftime('%H:%M:%S')}] MAIN FUNCTION TOTAL TIME: {main_total:.3f}s")
        print(f"[{time.strftime('%H:%M:%S')}] ={'='*60}")
                        
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Failed to extract data: {str(e)}")

if __name__ == "__main__":
    main()
