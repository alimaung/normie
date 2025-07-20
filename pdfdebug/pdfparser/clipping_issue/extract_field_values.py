#!/usr/bin/env python3
"""
Extract and compare exact field values from PDF files.
"""

import sys
import os
import re

def extract_field_value_from_object(data, obj_num):
    """
    Extract field value from a specific PDF object.
    """
    # Find the object
    obj_pattern = rf'{obj_num}\s+0\s+obj'.encode()
    match = re.search(obj_pattern, data)
    
    if not match:
        return None, f"Object {obj_num} not found"
    
    start_pos = match.start()
    
    # Find end of object
    endobj_match = re.search(rb'endobj', data[start_pos:])
    if endobj_match:
        end_pos = start_pos + endobj_match.end()
    else:
        end_pos = len(data)
    
    obj_data = data[start_pos:end_pos]
    
    # Extract field value using /V
    value_match = re.search(rb'/V\s*\(([^)]*)\)', obj_data)
    if value_match:
        raw_value = value_match.group(1)
        # Decode the value
        try:
            decoded_value = raw_value.decode('utf-8', errors='replace')
        except:
            decoded_value = raw_value.decode('latin-1', errors='replace')
        
        return decoded_value, None
    
    return None, "No /V field found in object"

def analyze_field_differences(file1, file2, field_mappings):
    """
    Analyze differences in specific fields between two PDF files.
    """
    print(f"Extracting field values from:")
    print(f"  File 1 (clipping): {file1}")
    print(f"  File 2 (no clipping): {file2}")
    print("=" * 80)
    
    # Read both files
    with open(file1, 'rb') as f1:
        data1 = f1.read()
    with open(file2, 'rb') as f2:
        data2 = f2.read()
    
    for field_name, obj_num in field_mappings.items():
        print(f"\nField '{field_name}' (Object {obj_num}):")
        print("-" * 60)
        
        # Extract values
        value1, error1 = extract_field_value_from_object(data1, obj_num)
        value2, error2 = extract_field_value_from_object(data2, obj_num)
        
        if error1:
            print(f"  Error in file 1: {error1}")
        if error2:
            print(f"  Error in file 2: {error2}")
        
        if value1 is not None and value2 is not None:
            print(f"  Value lengths: {len(value1)} vs {len(value2)}")
            print(f"  Values identical: {value1 == value2}")
            
            if value1 != value2:
                print(f"  ❌ VALUES DIFFER!")
                
                # Show character-by-character comparison for first differences
                min_len = min(len(value1), len(value2))
                first_diff = None
                for i in range(min_len):
                    if value1[i] != value2[i]:
                        first_diff = i
                        break
                
                if first_diff is not None:
                    print(f"  First difference at position {first_diff}:")
                    start = max(0, first_diff - 10)
                    end = min(len(value1), first_diff + 10)
                    
                    print(f"    File 1: {repr(value1[start:end])}")
                    print(f"    File 2: {repr(value2[start:end])}")
                    
                    # Show character codes
                    if first_diff < len(value1) and first_diff < len(value2):
                        char1 = value1[first_diff]
                        char2 = value2[first_diff]
                        print(f"    Char codes: {ord(char1)} vs {ord(char2)}")
                        print(f"    Characters: {repr(char1)} vs {repr(char2)}")
                
                # Show length differences
                if len(value1) != len(value2):
                    if len(value1) > len(value2):
                        extra = value1[len(value2):]
                        print(f"  Extra in file 1: {repr(extra)}")
                    else:
                        extra = value2[len(value1):]
                        print(f"  Extra in file 2: {repr(extra)}")
                
                # Show full values if they're short enough
                if len(value1) < 200:
                    print(f"  Full value 1: {repr(value1)}")
                if len(value2) < 200:
                    print(f"  Full value 2: {repr(value2)}")
                
                # Analyze line endings
                analyze_line_endings(value1, value2)
            else:
                print(f"  ✅ Values are identical")

def analyze_line_endings(value1, value2):
    """
    Analyze line ending differences between two values.
    """
    print(f"  Line ending analysis:")
    
    # Count different line endings
    lf1 = value1.count('\n')
    cr1 = value1.count('\r')
    crlf1 = value1.count('\r\n')
    
    lf2 = value2.count('\n')
    cr2 = value2.count('\r')
    crlf2 = value2.count('\r\n')
    
    print(f"    File 1: LF={lf1}, CR={cr1}, CRLF={crlf1}")
    print(f"    File 2: LF={lf2}, CR={cr2}, CRLF={crlf2}")
    
    if (lf1, cr1, crlf1) != (lf2, cr2, crlf2):
        print(f"    ❌ Line ending differences detected!")
        
        # Show where line endings occur
        for i, char in enumerate(value1):
            if char in '\r\n':
                context_start = max(0, i-5)
                context_end = min(len(value1), i+5)
                context = value1[context_start:context_end]
                print(f"      File 1 pos {i}: {repr(context)}")
                break
        
        for i, char in enumerate(value2):
            if char in '\r\n':
                context_start = max(0, i-5)
                context_end = min(len(value2), i+5)
                context = value2[context_start:context_end]
                print(f"      File 2 pos {i}: {repr(context)}")
                break

def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_field_values.py <clipping.pdf> <no_clipping.pdf>")
        return
    
    file1 = sys.argv[1]  # clipping.pdf
    file2 = sys.argv[2]  # no_clipping.pdf
    
    if not os.path.exists(file1):
        print(f"Error: File not found: {file1}")
        return
    
    if not os.path.exists(file2):
        print(f"Error: File not found: {file2}")
        return
    
    # Based on the analyzer output, these are the object numbers for fields 10 and 31
    field_mappings = {
        "10": 17,   # Object 17_0 contains field "10"
        "31": 226   # Object 226_0 contains field "31"
    }
    
    analyze_field_differences(file1, file2, field_mappings)

if __name__ == "__main__":
    main() 