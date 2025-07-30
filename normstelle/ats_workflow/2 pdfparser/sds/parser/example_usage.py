#!/usr/bin/env python3
"""
Example usage of the SDS Parser

This script demonstrates how to use the SDSParser class programmatically
for parsing German Safety Data Sheets.
"""

from sds_parser import SDSParser
import json

def example_single_file():
    """Example: Parse a single SDS file"""
    print("=== Single File Example ===")
    
    # Create parser instance
    parser = SDSParser(fuzzy_threshold=80, debug=True)
    
    # Parse a single file (replace with actual path)
    pdf_path = "path/to/your/sds.pdf"
    result = parser.parse_file(pdf_path)
    
    # Check results
    if result['success']:
        print(f"✅ Successfully parsed {result['sections_found']}/16 sections")
        
        # Print section titles
        for num in range(1, 17):
            section = result['sections'][num]
            status = "✅" if section['found'] else "❌"
            print(f"  {status} Section {num}: {section['title']}")
    else:
        print(f"❌ Parsing failed: {result['error']}")
        if result['missing_sections']:
            print(f"Missing sections: {result['missing_sections']}")

def example_batch_processing():
    """Example: Process multiple SDS files"""
    print("\n=== Batch Processing Example ===")
    
    # Create parser instance
    parser = SDSParser(fuzzy_threshold=75, debug=False)
    
    # Process all PDFs in a folder (replace with actual path)
    folder_path = "path/to/sds/folder"
    results = parser.parse_batch(folder_path)
    
    # Analyze results
    successful = 0
    total = len(results)
    
    for result in results:
        if result.get('success'):
            successful += 1
            print(f"✅ {result['file_path']}: {result['sections_found']}/16 sections")
        else:
            print(f"❌ {result['file_path']}: {result.get('error', 'Unknown error')}")
    
    print(f"\n📊 Summary: {successful}/{total} files successfully parsed")

def example_custom_analysis():
    """Example: Custom analysis of parsing results"""
    print("\n=== Custom Analysis Example ===")
    
    parser = SDSParser(fuzzy_threshold=80)
    
    # Example analysis (replace with actual path)
    pdf_path = "path/to/your/sds.pdf"
    result = parser.parse_file(pdf_path)
    
    if not result['success']:
        print(f"Could not analyze file: {result['error']}")
        return
    
    # Analyze section completeness
    sections = result['sections']
    
    # Find sections with most/least content
    content_lengths = []
    for num, section in sections.items():
        if section['found']:
            length = len(section['content'])
            content_lengths.append((num, section['title'], length))
    
    if content_lengths:
        content_lengths.sort(key=lambda x: x[2], reverse=True)
        
        print("Sections by content length:")
        for num, title, length in content_lengths[:5]:  # Top 5
            print(f"  Section {num}: {length} chars - {title}")
        
        # Check for suspiciously short sections
        short_sections = [item for item in content_lengths if item[2] < 50]
        if short_sections:
            print(f"\n⚠️  Warning: {len(short_sections)} sections have very little content:")
            for num, title, length in short_sections:
                print(f"  Section {num}: {length} chars - {title}")

def example_json_export():
    """Example: Export results to JSON"""
    print("\n=== JSON Export Example ===")
    
    parser = SDSParser()
    
    # Parse file (replace with actual path)
    pdf_path = "path/to/your/sds.pdf"
    result = parser.parse_file(pdf_path)
    
    # Save to JSON file
    output_file = "sds_analysis_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✅ Results exported to {output_file}")
    except Exception as e:
        print(f"❌ Export failed: {e}")

if __name__ == "__main__":
    print("SDS Parser - Example Usage")
    print("Note: Update file paths in this script before running!")
    
    # Run examples (comment out as needed)
    example_single_file()
    example_batch_processing()
    example_custom_analysis()
    example_json_export()
    
    print("\nFor command-line usage, run:")
    print("python sds_parser.py --help") 