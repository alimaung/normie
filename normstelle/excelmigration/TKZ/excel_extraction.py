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

def extract_excel_section_to_json(excel_file_path, output_json_path=None, start_row=2, end_row=5200, start_col=1, end_col=11, section_name="TKZ"):
    """
    Extract data from Excel file using win32com from specified range
    
    Args:
        excel_file_path (str): Path to the Excel file
        output_json_path (str, optional): Path for output JSON file
        start_row (int): Starting row (1-based)
        end_row (int): Ending row (1-based)
        start_col (int): Starting column (1-based, A=1)
        end_col (int): Ending column (1-based, K=11)
        section_name (str): Name of the section being extracted
    
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
        worksheet = workbook.Worksheets("Teilenummern")  # Access the worksheet named Teilenummern
        
        print(f"Extracting {section_name} data from range A{start_row}:K{end_row} (rows {start_row}-{end_row}, columns {start_col}-{end_col})")
        
        # Get column headers (row 1) for the specified range
        headers = []
        for col in range(start_col, end_col + 1):
            cell_value = worksheet.Cells(1, col).Value
            headers.append(cell_value if cell_value else f"Column_{chr(ord('A') + col - 1)}")
        
        print(f"Found {len(headers)} columns: {headers}")
        
        # Only apply advanced processing to TKZ1 section
        use_advanced_processing = (section_name == "TKZ1")
        
        if use_advanced_processing:
            print(f"Using advanced processing (hyperlinks + color detection) for {section_name}")
        else:
            print(f"Using basic processing for {section_name}")
        
        data_rows = []
        empty_rows_skipped = 0
        hyperlink_count = 0
        color_count = 0
        
        if use_advanced_processing:
            # Advanced processing for TKZ1 (row by row with hyperlinks and color)
            total_rows_to_process = end_row - start_row + 1
            print(f"Processing {total_rows_to_process} rows with advanced features...")
            
            for row in range(start_row, end_row + 1):
                row_data = {}
                row_has_data = False
                
                # Extract font color from column A (correct method based on debug results)
                try:
                    cell_a = worksheet.Cells(row, 1)
                    
                    # Get font color (this is where the red formatting is)
                    font_rgb = cell_a.Font.Color
                    font_color = rgb_to_hex(int(font_rgb)) if font_rgb != -4142 else None
                    
                    # Get strikethrough property
                    strikethrough = cell_a.Font.Strikethrough
                    
                    if font_color and font_color != "#000000":  # Not default black
                        row_data['font_color'] = font_color
                        row_data['strikethrough'] = strikethrough
                        
                        # Determine status based on font color (red = discontinued)
                        if font_color == "#FF0000" or (font_color.startswith("#") and 
                            int(font_color[1:3], 16) > 200 and 
                            int(font_color[3:5], 16) < 50 and 
                            int(font_color[5:7], 16) < 50):
                            
                            # Both red font and strikethrough are considered "discontinued"
                            row_data['status'] = "discontinued"
                        else:
                            row_data['status'] = "active"
                        color_count += 1
                        
                        # Show first few color detections for verification
                        if color_count <= 3:
                            print(f"  Found color {color_count}: Row {row}, font color: {font_color}, strikethrough: {strikethrough}, status: {row_data['status']}")
                    else:
                        row_data['status'] = "active"
                        
                except Exception as e:
                    row_data['status'] = "active"
                
                for col_idx, col in enumerate(range(start_col, end_col + 1)):
                    header = headers[col_idx]
                    cell = worksheet.Cells(row, col)
                    cell_value = cell.Value
                    
                    # Check if this cell has any data
                    if cell_value is not None and str(cell_value).strip():
                        row_has_data = True
                    
                    # Handle column K (Zusatzinfo) hyperlinks using proven method
                    if col == 11:  # Column K
                        try:
                            if cell.Hyperlinks.Count > 0:
                                hyperlink = cell.Hyperlinks(1)
                                target = hyperlink.Address
                                subaddress = hyperlink.SubAddress if hasattr(hyperlink, 'SubAddress') else None
                                
                                # Combine address and subaddress if both exist
                                if target and subaddress:
                                    full_target = f"{target}#{subaddress}"
                                else:
                                    full_target = target or subaddress
                                
                                row_data[header] = {
                                    'display_text': cell_value,
                                    'url': full_target,
                                    'tooltip': hyperlink.ScreenTip if hasattr(hyperlink, 'ScreenTip') else None
                                }
                                hyperlink_count += 1
                                
                                # Show first few hyperlinks found
                                if hyperlink_count <= 3:
                                    print(f"  Found hyperlink {hyperlink_count}: Row {row}, '{cell_value}' -> {full_target[:50]}...")
                                    
                            else:
                                row_data[header] = cell_value
                        except Exception as e:
                            print(f"Warning: Error processing hyperlink in row {row}, col K: {e}")
                            row_data[header] = cell_value
                    else:
                        row_data[header] = cell_value
                
                # Skip completely empty rows
                if not row_has_data:
                    empty_rows_skipped += 1
                    continue
                
                data_rows.append(row_data)
                
                # Progress indicator every 250 rows
                rows_processed = row - start_row + 1
                if rows_processed % 250 == 0:
                    progress_pct = (rows_processed / total_rows_to_process) * 100
                    print(f"  Progress: {rows_processed}/{total_rows_to_process} rows ({progress_pct:.1f}%) | Data rows: {len(data_rows)} | Hyperlinks: {hyperlink_count} | Colors: {color_count}")
        
        else:
            # Basic batch processing for TKZ2 and TKZ3 (faster)
            print(f"Reading data from range A{start_row}:K{end_row}...")
            
            # Read the entire range at once for better performance
            data_range = worksheet.Range(f"A{start_row}:K{end_row}")
            data_values = data_range.Value
            
            total_batch_rows = len(data_values)
            print(f"Processing {total_batch_rows} rows in batch mode...")
            
            # Convert to list of dictionaries
            for idx, row_values in enumerate(data_values):
                # Check if row has any data
                row_has_data = any(val is not None and str(val).strip() for val in row_values if val is not None)
                
                if not row_has_data:
                    empty_rows_skipped += 1
                    continue
                
                row_data = {}
                for col_idx, header in enumerate(headers):
                    row_data[header] = row_values[col_idx] if col_idx < len(row_values) else None
                
                # Default status for non-TKZ1 sections
                row_data['status'] = "active"
                
                data_rows.append(row_data)
                
                # Progress indicator every 500 rows for batch mode
                if (idx + 1) % 500 == 0:
                    progress_pct = ((idx + 1) / total_batch_rows) * 100
                    print(f"  Batch progress: {idx + 1}/{total_batch_rows} rows ({progress_pct:.1f}%) | Data rows: {len(data_rows)} | Empty skipped: {empty_rows_skipped}")
        
        print(f"Successfully processed {len(data_rows)} rows (skipped {empty_rows_skipped} empty rows)")
        if use_advanced_processing:
            print(f"Hyperlinks found: {hyperlink_count}")
            print(f"Colors processed: {color_count}")
        
        # Create the final data structure
        metadata = {
            'section_name': section_name,
            'total_rows': len(data_rows),
            'empty_rows_skipped': empty_rows_skipped,
            'total_columns': len(headers),
            'columns': headers + ['status'],  # Add status to column list
            'source_file': os.path.basename(excel_file_path),
            'extraction_range': f"A{start_row}:K{end_row}",
            'start_row': start_row,
            'end_row': end_row,
            'start_col': start_col,
            'end_col': end_col,
            'extraction_method': 'win32com'
        }
        
        if use_advanced_processing:
            metadata['features'] = {
                'hyperlink_extraction': 'Column K (Zusatzinfo)',
                'font_color_detection': 'Column A font color',
                'strikethrough_detection': 'Column A font strikethrough',
                'status_detection': 'Based on red font color detection',
                'empty_row_filtering': True,
                'advanced_processing': True
            }
            metadata['hyperlinks_found'] = hyperlink_count
            metadata['colors_processed'] = color_count
            if use_advanced_processing:
                metadata['columns'].extend(['font_color', 'strikethrough'])  # Add new columns for TKZ1
        else:
            metadata['features'] = {
                'empty_row_filtering': True,
                'advanced_processing': False,
                'processing_mode': 'batch_optimized'
            }
        
        data_dict = {
            'metadata': metadata,
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
            output_json_path = excel_path.parent / f"{excel_path.stem}_{section_name}.json"
        
        # Write to JSON file
        print(f"Writing JSON to: {output_json_path}")
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Successfully created JSON file with {len(data_rows)} rows")
        print(f"Empty rows skipped: {empty_rows_skipped}")
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

def extract_all_tkz_sections(excel_file_path):
    """
    Extract all three TKZ sections from the Excel file
    
    Args:
        excel_file_path (str): Path to the Excel file
        
    Returns:
        dict: Dictionary containing data for all sections
    """
    sections = {
        'TKZ1': {'start_row': 2, 'end_row': 5200},
        'TKZ2': {'start_row': 5204, 'end_row': 5604}, 
        'TKZ3': {'start_row': 5605, 'end_row': 12380}
    }
    
    all_data = {}
    
    for section_name, range_info in sections.items():
        print(f"\n{'='*40}")
        print(f"Extracting {section_name}")
        print(f"{'='*40}")
        
        try:
            data = extract_excel_section_to_json(
                excel_file_path,
                start_row=range_info['start_row'],
                end_row=range_info['end_row'],
                start_col=1,
                end_col=11,
                section_name=section_name
            )
            
            all_data[section_name] = data
            
            print(f"✓ {section_name} extracted successfully")
            print(f"  Rows: {data['metadata']['total_rows']}")
            print(f"  Range: {data['metadata']['extraction_range']}")
            
        except Exception as e:
            print(f"✗ Failed to extract {section_name}: {str(e)}")
            all_data[section_name] = None
    
    return all_data

def main():
    """Main function to run the TKZ extraction for all sections"""
    # Get the directory of this script
    script_dir = Path(__file__).parent
    excel_file = script_dir / "Teilenummern_0104....xls"
    
    if not excel_file.exists():
        print(f"Error: Excel file not found at {excel_file}")
        return
    
    try:
        # Extract all three sections
        all_data = extract_all_tkz_sections(str(excel_file))
        
        # Print overall summary
        print("\n" + "="*60)
        print("TKZ EXTRACTION SUMMARY - ALL SECTIONS")
        print("="*60)
        print(f"Source file: {excel_file.name}")
        
        total_rows = 0
        for section_name, data in all_data.items():
            if data:
                section_rows = data['metadata']['total_rows']
                total_rows += section_rows
                print(f"{section_name}: {section_rows} rows ({data['metadata']['extraction_range']})")
                
                # Show sample data for first section only
                if section_name == 'TKZ1' and data['data']:
                    print(f"\nSample from {section_name} (first row):")
                    first_row = data['data'][0]
                    
                    # Show first few columns
                    for i, col in enumerate(data['metadata']['columns'][:5]):
                        if col in first_row:
                            print(f"  {col}: {first_row[col]}")
                    
                    if len(data['metadata']['columns']) > 5:
                        print(f"  ... and {len(data['metadata']['columns']) - 5} more columns")
            else:
                print(f"{section_name}: FAILED")
        
        print(f"\nTotal rows extracted: {total_rows}")
        print(f"JSON files created: Teilenummern_0104..._TKZ1.json, TKZ2.json, TKZ3.json")
                        
    except Exception as e:
        print(f"Failed to extract data: {str(e)}")

if __name__ == "__main__":
    main()
