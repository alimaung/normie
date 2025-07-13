# TKZ Parser - Extract unique values from all columns for multiple TKZ sections
# Reads from Teilenummern_0104...._TKZ1.json, TKZ2.json, TKZ3.json 
# and creates separate directories (cols1, cols2, cols3) for each section

import json
import os
from pathlib import Path

def extract_unique_values_from_tkz_section(json_file, section_name, cols_dir_name):
    """
    Extract unique values from all columns in a specific TKZ section JSON file
    and save each column's unique values to separate text files in the specified directory
    
    Args:
        json_file (str): Path to the JSON file
        section_name (str): Name of the TKZ section (e.g., 'TKZ1')
        cols_dir_name (str): Directory name for output (e.g., 'cols1')
    
    Returns:
        dict: Summary statistics for this section
    """
    
    if not os.path.exists(json_file):
        print(f"Warning: {json_file} not found! Skipping {section_name}")
        return None
    
    print(f"\nReading data from {json_file}...")
    
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Get column names from metadata
    columns = data['metadata']['columns']
    total_rows = data['metadata']['total_rows']
    section_metadata = data['metadata'].get('section_name', section_name)
    extraction_range = data['metadata'].get('extraction_range', 'Unknown')
    
    print(f"Found {len(columns)} columns and {total_rows} rows in {section_metadata}")
    print(f"Extraction range: {extraction_range}")
    print(f"Columns: {columns}")
    
    # Create section-specific cols directory
    cols_dir = Path(cols_dir_name)
    cols_dir.mkdir(exist_ok=True)
    print(f"Created/using directory: {cols_dir}")
    
    # Process each column
    section_stats = {
        'section_name': section_metadata,
        'total_rows': total_rows,
        'total_columns': len(columns),
        'extraction_range': extraction_range,
        'output_directory': str(cols_dir),
        'files_created': 0,
        'total_unique_values': 0
    }
    
    for column in columns:
        print(f"\nProcessing column: {column}")
        
        # Extract unique values for this column (filtering out None/empty values)
        unique_values = set()
        
        for item in data['data']:
            value = item.get(column)
            
            # Skip None, empty strings, and whitespace-only values
            if value is not None and str(value).strip():
                # Clean the value (strip whitespace and convert to string)
                cleaned_value = str(value).strip()
                unique_values.add(cleaned_value)
        
        # Sort the unique values for consistent output
        sorted_values = sorted(unique_values)
        
        print(f"  Found {len(sorted_values)} unique values")
        section_stats['total_unique_values'] += len(sorted_values)
        
        # Create safe filename (replace problematic characters)
        safe_filename = column.replace('/', '_').replace('\\', '_').replace(':', '_').replace(' ', '_')
        output_file = cols_dir / f"{safe_filename}.txt"
        
        # Save to text file
        with open(output_file, 'w', encoding='utf-8') as file:
            for value in sorted_values:
                file.write(f"{value}\n")
        
        section_stats['files_created'] += 1
        print(f"  Saved to: {output_file}")
        
        # Show first few values as preview
        if sorted_values:
            preview_count = min(3, len(sorted_values))
            print(f"  Preview (first {preview_count}): {sorted_values[:preview_count]}")
    
    return section_stats

def extract_all_tkz_sections():
    """
    Extract unique values from all TKZ sections
    """
    # Define the sections and their corresponding files/directories
    sections = {
        'TKZ1': {
            'json_file': 'Teilenummern_0104..._TKZ1.json',
            'cols_dir': 'cols1'
        },
        'TKZ2': {
            'json_file': 'Teilenummern_0104..._TKZ2.json', 
            'cols_dir': 'cols2'
        },
        'TKZ3': {
            'json_file': 'Teilenummern_0104..._TKZ3.json',
            'cols_dir': 'cols3'
        }
    }
    
    all_stats = {}
    
    print("="*60)
    print("TKZ PARSER - PROCESSING ALL SECTIONS")
    print("="*60)
    
    # Process each section
    for section_name, section_info in sections.items():
        print(f"\n{'='*40}")
        print(f"Processing {section_name}")
        print(f"{'='*40}")
        
        stats = extract_unique_values_from_tkz_section(
            section_info['json_file'],
            section_name,
            section_info['cols_dir']
        )
        
        if stats:
            all_stats[section_name] = stats
            print(f"✓ {section_name} processed successfully")
        else:
            all_stats[section_name] = None
            print(f"✗ {section_name} failed or skipped")
    
    # Print overall summary
    print(f"\n{'='*60}")
    print("TKZ PARSER SUMMARY - ALL SECTIONS")
    print(f"{'='*60}")
    
    total_rows = 0
    total_files = 0
    total_unique_values = 0
    
    for section_name, stats in all_stats.items():
        if stats:
            total_rows += stats['total_rows']
            total_files += stats['files_created']
            total_unique_values += stats['total_unique_values']
            
            print(f"{section_name}:")
            print(f"  Rows processed: {stats['total_rows']}")
            print(f"  Range: {stats['extraction_range']}")
            print(f"  Files created: {stats['files_created']}")
            print(f"  Output directory: {stats['output_directory']}")
            print(f"  Total unique values: {stats['total_unique_values']}")
            
            # List files in this section's directory
            cols_dir = Path(stats['output_directory'])
            if cols_dir.exists():
                print(f"  Files created:")
                for txt_file in sorted(cols_dir.glob('*.txt')):
                    file_size = txt_file.stat().st_size
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        line_count = sum(1 for _ in f)
                    print(f"    {txt_file.name} ({line_count} unique values, {file_size} bytes)")
            print()
        else:
            print(f"{section_name}: FAILED or SKIPPED")
    
    print(f"OVERALL TOTALS:")
    print(f"  Total rows processed: {total_rows}")
    print(f"  Total files created: {total_files}")
    print(f"  Total unique values extracted: {total_unique_values}")
    print(f"  Directories created: cols1, cols2, cols3")

if __name__ == "__main__":
    extract_all_tkz_sections()
