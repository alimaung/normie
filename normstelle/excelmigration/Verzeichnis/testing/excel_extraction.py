import json
import os
from pathlib import Path
import win32com.client as win32
import pythoncom
import sys

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

def _excel_col_letter(n):
    """
    Convert 1-based column index to Excel column letter(s).
    Example: 1 -> A, 26 -> Z, 27 -> AA
    """
    letters = []
    while n > 0:
        n, rem = divmod(n - 1, 26)
        letters.append(chr(65 + rem))
    return ''.join(reversed(letters))

def _build_hyperlink_map(worksheet, row_start, row_end, col_start, col_end):
    """
    Build a mapping of (row, col) -> (address, subaddress, screentip) for hyperlinks
    within the specified rectangular region.
    """
    link_map = {}
    if col_start > col_end or row_start > row_end:
        return link_map
    try:
        link_range = worksheet.Range(worksheet.Cells(row_start, col_start), worksheet.Cells(row_end, col_end))
        hyperlinks = link_range.Hyperlinks
        for hl in hyperlinks:
            try:
                rng = hl.Range
                r = rng.Row
                c = rng.Column
                address = getattr(hl, 'Address', None)
                subaddress = getattr(hl, 'SubAddress', None)
                screentip = getattr(hl, 'ScreenTip', None)
                link_map[(r, c)] = (address, subaddress, screentip)
            except Exception:
                # Skip malformed hyperlink entries
                continue
    except Exception:
        # If hyperlink collection access fails, fall back to per-cell handling in caller
        return {}
    return link_map

def extract_excel_to_json_v2(excel_file_path, output_json_path=None, max_row=5000):
    """
    Optimized extraction using bulk value reads and a single hyperlink collection pass.
    - Reads A1:AA{N} values in one call
    - Reads colors only from column A per row
    - Maps hyperlinks from M..U via one collection
    """
    excel_app = None
    workbook = None
    try:
        print(f"Reading Excel file (v2): {excel_file_path}")

        pythoncom.CoInitialize()
        excel_app = win32.Dispatch("Excel.Application")
        excel_app.Visible = False
        excel_app.DisplayAlerts = False

        workbook = excel_app.Workbooks.Open(os.path.abspath(excel_file_path))
        worksheet = workbook.ActiveSheet

        used_range = worksheet.UsedRange
        max_col = min(used_range.Columns.Count, 27)
        actual_max_row = min(used_range.Rows.Count, max_row)

        # Bulk read all values A1:AA{actual_max_row}
        last_col_letter = _excel_col_letter(max_col)
        values_range = worksheet.Range(f"A1:{last_col_letter}{actual_max_row}")
        values_matrix = values_range.Value
        # Normalize to list of lists for consistent indexing
        # pywin32 returns a tuple-of-tuples for multi-cell ranges, or a scalar for single cell
        if actual_max_row == 1 and max_col == 1:
            values_matrix = [[values_matrix]]
        elif actual_max_row == 1:
            values_matrix = [list(values_matrix)]
        else:
            values_matrix = [list(row) for row in values_matrix]

        headers = []
        header_row = values_matrix[0]
        for idx in range(max_col):
            cell_value = header_row[idx]
            headers.append(cell_value if cell_value else f"Column_{_excel_col_letter(idx+1)}")

        # Hyperlink map for M..U
        hyperlink_col_start = 13
        hyperlink_col_end = min(21, max_col)
        hyperlink_map = _build_hyperlink_map(worksheet, 2, actual_max_row, hyperlink_col_start, hyperlink_col_end)

        data_rows = []
        hyperlink_count = 0
        normalized_count = 0
        color_count = 0

        for r in range(2, actual_max_row + 1):
            row_index = r - 1  # 0-based for values_matrix
            row_vals = values_matrix[row_index]
            row_data = {}

            # Color/status from column A
            try:
                rgb_value = worksheet.Cells(r, 1).Interior.Color
                cell_color = rgb_to_hex(rgb_value)
                if cell_color and cell_color != "#FFFFFF":
                    row_data['color'] = cell_color
                    row_data['status'] = map_color_to_status(cell_color)
                    color_count += 1
                else:
                    row_data['color'] = "#FFFFFF"
                    row_data['status'] = "processing"
            except Exception:
                row_data['color'] = None
                row_data['status'] = "unknown"

            # Iterate columns using bulk values; enrich hyperlink columns via map
            for c_idx, header in enumerate(headers):
                c = c_idx + 1
                if c > max_col:
                    break
                cell_value = row_vals[c_idx]

                if hyperlink_col_start <= c <= hyperlink_col_end:
                    link_info = hyperlink_map.get((r, c))
                    if link_info:
                        address, subaddress, screentip = link_info
                        full_target = f"{address}#{subaddress}" if address and subaddress else (address or subaddress)
                        original_target = full_target
                        normalized_target = normalize_url(full_target)
                        if original_target != normalized_target:
                            normalized_count += 1
                        row_data[header] = {
                            'display_text': cell_value,
                            'url': normalized_target,
                            'original_url': original_target if original_target != normalized_target else None,
                            'tooltip': screentip
                        }
                        hyperlink_count += 1
                    else:
                        # No hyperlink object; infer if value looks like a path
                        if cell_value:
                            s = str(cell_value).strip()
                            if (s.startswith(('C:', 'D:', 'E:', '\\', './', '../')) or '\\' in s or s.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx'))):
                                normalized_path = normalize_url(s)
                                row_data[header] = {
                                    'display_text': cell_value,
                                    'url': normalized_path,
                                    'original_url': s if s != normalized_path else None,
                                    'tooltip': None,
                                    'type': 'inferred_file_path'
                                }
                                if s != normalized_path:
                                    normalized_count += 1
                            else:
                                row_data[header] = {
                                    'display_text': cell_value,
                                    'url': None,
                                    'tooltip': None
                                }
                        else:
                            row_data[header] = None
                else:
                    row_data[header] = cell_value

            data_rows.append(row_data)
            if (r - 1) % 500 == 0:
                print(f"  [v2] Processed {r - 1} rows...")

        print(f"[v2] Successfully processed {len(data_rows)} rows")
        print(f"[v2] Total hyperlinks found: {hyperlink_count}")
        print(f"[v2] URLs normalized: {normalized_count}")
        print(f"[v2] Colors extracted: {color_count}")

        data_dict = {
            'metadata': {
                'total_rows': len(data_rows),
                'total_columns': len(headers),
                'columns': headers,
                'source_file': os.path.basename(excel_file_path),
                'hyperlinks_extracted': True,
                'hyperlink_columns': [h for h in headers[hyperlink_col_start-1:hyperlink_col_end]],
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
                'extraction_method': 'win32com_v2_bulk'
            },
            'data': data_rows
        }

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

        if output_json_path is None:
            excel_path = Path(excel_file_path)
            output_json_path = excel_path.parent / f"{excel_path.stem}.json"

        print(f"Writing JSON to: {output_json_path}")
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False, default=str)

        print(f"[v2] Successfully created JSON file with {len(data_rows)} rows")
        print(f"Output file: {output_json_path}")

        return data_dict

    except Exception as e:
        print(f"Error during extraction (v2): {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
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
    """Main function to run extraction (v1 or v2)"""
    script_dir = Path(__file__).parent
    excel_file = script_dir / "Verzeichnis.xlsx"

    # Minimal CLI flags (non-breaking): --v2, --excel PATH, --max-row N, --out PATH
    args = sys.argv[1:]
    use_v2 = False
    out_override = None
    max_row = 5000
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--v2":
            use_v2 = True
            i += 1
        elif arg == "--excel" and i + 1 < len(args):
            excel_file = Path(args[i + 1])
            i += 2
        elif arg == "--max-row" and i + 1 < len(args):
            try:
                max_row = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif arg == "--out" and i + 1 < len(args):
            out_override = Path(args[i + 1])
            i += 2
        else:
            i += 1

    if not excel_file.exists():
        print(f"Error: Excel file not found at {excel_file}")
        return

    try:
        if use_v2:
            data = extract_excel_to_json_v2(str(excel_file), output_json_path=str(out_override) if out_override else None, max_row=max_row)
        else:
            data = extract_excel_to_json_unified(str(excel_file), output_json_path=str(out_override) if out_override else None, max_row=max_row)

        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"Source file: {excel_file.name}")
        print(f"Total rows extracted: {data['metadata']['total_rows']}")
        print(f"Total columns: {data['metadata']['total_columns']}")
        if 'hyperlink_columns' in data['metadata']:
            print(f"Hyperlink columns: {', '.join(data['metadata']['hyperlink_columns'])}")
        if 'url_normalization' in data['metadata']:
            print(f"URLs normalized: {data['metadata']['url_normalization']['normalized_count']}")
        print(f"Colors extracted: {data['metadata'].get('colors_extracted', False)}")
        print(f"Extraction method: {data['metadata']['extraction_method']}")

        if data['data']:
            print(f"\nFirst row sample:")
            first_row = data['data'][0]
            print(f"  Color: {first_row.get('color', 'None')}")
            print(f"  Status: {first_row.get('status', 'None')}")
            regular_cols = ['Antrag-nummer', 'Teile-nummer', 'Freigabe']
            for col in regular_cols:
                if col in first_row:
                    print(f"  {col}: {first_row[col]}")
            if 'hyperlink_columns' in data['metadata']:
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
