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
    
    # Network drive base path
    network_base = r"\\dehesdna-a009a\projekte\k-z\Ofs\Dokumentenservice\TeileundStoffe"
    
    # Replace relative path with full network path
    if url.startswith("..") or url.startswith("./"):
        # Handle relative paths like "../Antrag/2025/053-2025_10002411_Freigabe.pdf"
        # Remove leading "../" and replace with the full network path
        if url.startswith("../"):
            relative_part = url[3:]  # Remove "../" (3 characters)
        elif url.startswith("..\\"):
            relative_part = url[3:]  # Remove "..\" (3 characters)
        elif url.startswith("./"):
            relative_part = url[2:]  # Remove "./" (2 characters)
        elif url.startswith(".\\"):
            relative_part = url[2:]  # Remove ".\" (2 characters)
        else:
            relative_part = url
        
        # Convert forward slashes to backslashes for Windows network path consistency
        relative_part = relative_part.replace('/', '\\')
        normalized_url = f"{network_base}\\{relative_part}"
        return normalized_url
    
    # Handle V: drive paths
    if url.startswith(("V:", "V:\\")):
        # Replace V: drive with network path
        relative_part = url[2:] if url.startswith("V:") else url[3:]  # Remove "V:" or "V:\"
        # Ensure proper path separator
        relative_part = relative_part.lstrip('\\/')
        normalized_url = f"{network_base}\\{relative_part}"
        return normalized_url
    
    # If it's already a full network path, return as is
    return url

def process_hyperlink_cell(cell, row_num, cell_description):
    """
    Process a cell that may contain a hyperlink
    
    Args:
        cell: Excel cell object
        row_num: Row number for error reporting
        cell_description: Description of the cell for error reporting
        
    Returns:
        tuple: (file_url, original_url, display_text, normalized)
    """
    file_url = None
    original_url = None
    display_text = None
    normalized = False
    
    try:
        # Check if cell has hyperlink
        if cell.Hyperlinks.Count > 0:
            hyperlink = cell.Hyperlinks(1)
            target = hyperlink.Address
            subaddress = hyperlink.SubAddress if hasattr(hyperlink, 'SubAddress') else None
            
            # Combine address and subaddress if both exist
            if target and subaddress:
                original_url = f"{target}#{subaddress}"
            else:
                original_url = target or subaddress
            
            # Normalize the URL
            file_url = normalize_url(original_url)
            display_text = cell.Value
            
            if file_url != original_url:
                normalized = True
                print(f"  Normalized {cell_description} URL: {original_url} -> {file_url}")
        elif cell.Value:
            # Check if the cell value looks like a file path
            cell_value = str(cell.Value).strip()
            if (cell_value.startswith(('V:', 'V:\\', '..', './', '.\\')) or 
                '\\' in cell_value or 
                cell_value.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx'))):
                
                original_url = cell_value
                # Normalize the inferred file path
                file_url = normalize_url(cell_value)
                display_text = cell_value
                
                if file_url != original_url:
                    normalized = True
                    print(f"  Normalized {cell_description} URL from text: {original_url} -> {file_url}")
            else:
                # Just a regular text value, not a URL
                display_text = cell_value
    except Exception as e:
        print(f"Warning: Error processing {cell_description} hyperlink in row {row_num}: {e}")
    
    return file_url, original_url, display_text, normalized

def extract_teilenummer_links(excel_file_path, output_json_path=None):
    """
    Extract links to Teilenummer from Excel file, filtering by rows with color #CCFF99 in column E
    
    Args:
        excel_file_path (str): Path to the Excel file
        output_json_path (str, optional): Path for output JSON file
    
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
        
        # Select the first sheet (Teile und Stoffe)
        worksheet = workbook.Sheets("Teile und Stoffe")
        
        # Get the used range to determine actual data bounds
        used_range = worksheet.UsedRange
        max_row = used_range.Rows.Count
        
        print(f"Worksheet has {max_row} rows")
        
        # Extract data row by row
        filtered_rows = []
        filtered_count = 0
        normalized_count = 0
        
        print(f"Processing rows 2 to {max_row}...")
        
        for row_num in range(2, max_row + 1):
            # Check if column E has the target color #CCFF99
            cell_e = worksheet.Cells(row_num, 5)  # Column E is index 5
            
            try:
                # Get interior color (background color)
                rgb_value = cell_e.Interior.Color
                
                # Convert to integer if it's a float
                rgb_int = int(rgb_value)
                
                # Extract RGB components from the integer
                red = rgb_int & 255
                green = (rgb_int >> 8) & 255
                blue = (rgb_int >> 16) & 255
                
                cell_color = f"#{red:02X}{green:02X}{blue:02X}"
                
                # Only process rows with color #CCFF99 in column E
                if cell_color == "#CCFF99":
                    # Get values from columns A (Antrag-nummer), B (Teile-nummer), K (Location)
                    antrag_nummer = worksheet.Cells(row_num, 1).Value.replace("/", "-")
                    teile_nummer = worksheet.Cells(row_num, 2).Value
                    location = worksheet.Cells(row_num, 11).Value  # Column K is index 11
                    
                    # Process URL from column M (File URL)
                    file_url_cell = worksheet.Cells(row_num, 13)  # Column M is index 13
                    file_url, original_url, display_text, file_normalized = process_hyperlink_cell(
                        file_url_cell, row_num, "File URL (Column M)")
                    
                    if file_normalized:
                        normalized_count += 1
                    
                    # Process URL from column R (Chemscan)
                    chemscan_cell = worksheet.Cells(row_num, 18)  # Column R is index 18
                    chemscan_url, chemscan_original_url, chemscan_display_text, chemscan_normalized = process_hyperlink_cell(
                        chemscan_cell, row_num, "Chemscan (Column R)")
                    
                    if chemscan_normalized:
                        normalized_count += 1
                    
                    # Construct comment
                    comment = f"ATS_{antrag_nummer}_{teile_nummer}_{location} --NUR ERSTBESTELLUNG--"
                    
                    # Add to filtered rows
                    filtered_rows.append({
                        "Antrag-nummer": antrag_nummer,
                        "Teile-nummer": teile_nummer,
                        "Location": location,
                        "File_URL": file_url,
                        "Original_URL": original_url if original_url != file_url else None,
                        "Display_Text": display_text,
                        "Chemscan_URL": chemscan_url,
                        "Chemscan_Original_URL": chemscan_original_url if chemscan_original_url != chemscan_url else None,
                        "Chemscan_Display_Text": chemscan_display_text,
                        "Comment": comment
                    })
                    
                    filtered_count += 1
                    
                    # Debug: Show first few filtered rows
                    if filtered_count <= 5:
                        print(f"  Row {row_num}: Antrag={antrag_nummer}, Teile={teile_nummer}, Location={location}")
                        print(f"    File URL: {file_url}")
                        print(f"    Chemscan URL: {chemscan_url}")
            
            except Exception as e:
                print(f"Warning: Could not process row {row_num}: {e}")
        
        print(f"Successfully filtered {filtered_count} rows with color #CCFF99 in column E")
        print(f"URLs normalized: {normalized_count}")
        
        # Create the final data structure
        data_dict = {
            "metadata": {
                "total_filtered_rows": filtered_count,
                "source_file": os.path.basename(excel_file_path),
                "filter_criteria": "Color #CCFF99 in column E",
                "comment_format": "ATS_{Antrag-nummer}_{Teile-nummer}_{Location} --NUR ERSTBESTELLUNG--",
                "url_normalization": {
                    "applied": True,
                    "normalized_count": normalized_count,
                    "network_base": r"\\dehesdna-a009a\projekte\k-z\Ofs\Dokumentenservice\TeileundStoffe"
                }
            },
            "teilenummer_links": filtered_rows
        }
        
        # Determine output file path
        if output_json_path is None:
            excel_path = Path(excel_file_path)
            output_json_path = excel_path.parent / f"{excel_path.stem}_teilenummer_links.json"
        
        # Write to JSON file
        print(f"Writing JSON to: {output_json_path}")
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Successfully created JSON file with {filtered_count} filtered rows")
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
    """Main function to extract Teilenummer links"""
    # Get the directory of this script
    script_dir = Path(__file__).parent
    excel_file = script_dir / "Verzeichnis.xlsx"
    
    if not excel_file.exists():
        print(f"Error: Excel file not found at {excel_file}")
        return
    
    try:
        # Extract Teilenummer links
        data = extract_teilenummer_links(str(excel_file))
        
        # Print summary
        print("\n" + "="*60)
        print("TEILENUMMER LINKS EXTRACTION SUMMARY")
        print("="*60)
        print(f"Source file: {excel_file.name}")
        print(f"Total filtered rows: {data['metadata']['total_filtered_rows']}")
        print(f"Filter criteria: {data['metadata']['filter_criteria']}")
        print(f"Comment format: {data['metadata']['comment_format']}")
        print(f"URLs normalized: {data['metadata']['url_normalization']['normalized_count']}")
        
        # Show sample data
        if data['teilenummer_links']:
            print(f"\nFirst row sample:")
            first_row = data['teilenummer_links'][0]
            for key, value in first_row.items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"Failed to extract data: {str(e)}")

if __name__ == "__main__":
    main() 