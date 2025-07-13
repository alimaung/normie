#!/usr/bin/env python3
"""
Deep inspection of PDF objects to understand the exact storage format.
"""

import sys
import os
import re

def extract_pdf_object_raw(pdf_data, obj_num):
    """
    Extract the raw PDF object data for detailed inspection.
    """
    # Find the object
    obj_pattern = rf'{obj_num}\s+0\s+obj'.encode()
    match = re.search(obj_pattern, pdf_data)
    
    if not match:
        return None
    
    start_pos = match.start()
    
    # Find end of object
    endobj_match = re.search(rb'endobj', pdf_data[start_pos:])
    if endobj_match:
        end_pos = start_pos + endobj_match.end()
    else:
        end_pos = len(pdf_data)
    
    obj_data = pdf_data[start_pos:end_pos]
    return obj_data

def analyze_object_differences(file1, file2, obj_num, field_name):
    """
    Analyze differences between the same object in two PDF files.
    """
    print(f"\n{'='*80}")
    print(f"DEEP ANALYSIS: Object {obj_num} (Field '{field_name}')")
    print(f"{'='*80}")
    
    # Read both files
    with open(file1, 'rb') as f1:
        data1 = f1.read()
    with open(file2, 'rb') as f2:
        data2 = f2.read()
    
    # Extract objects
    obj1 = extract_pdf_object_raw(data1, obj_num)
    obj2 = extract_pdf_object_raw(data2, obj_num)
    
    if not obj1 or not obj2:
        print(f"Could not extract object {obj_num} from one or both files")
        return
    
    print(f"Object sizes: {len(obj1)} vs {len(obj2)} bytes")
    print(f"Size difference: {len(obj1) - len(obj2)} bytes")
    
    # Convert to text for analysis
    try:
        text1 = obj1.decode('latin-1', errors='replace')
        text2 = obj2.decode('latin-1', errors='replace')
    except:
        print("Could not decode object data")
        return
    
    # Find differences
    if text1 == text2:
        print("✅ Objects are identical")
        return
    
    print("❌ Objects differ")
    
    # Find first difference
    min_len = min(len(text1), len(text2))
    first_diff = None
    for i in range(min_len):
        if text1[i] != text2[i]:
            first_diff = i
            break
    
    if first_diff is not None:
        print(f"\nFirst difference at position {first_diff}:")
        start = max(0, first_diff - 20)
        end = min(len(text1), first_diff + 20)
        
        print(f"File 1: {repr(text1[start:end])}")
        print(f"File 2: {repr(text2[start:end])}")
    
    # Extract field values specifically
    print(f"\nField Value Analysis:")
    print("-" * 40)
    
    # Look for /V entries
    v_pattern = r'/V\s*\(([^)]*)\)'
    
    v_match1 = re.search(v_pattern, text1)
    v_match2 = re.search(v_pattern, text2)
    
    if v_match1 and v_match2:
        val1 = v_match1.group(1)
        val2 = v_match2.group(1)
        
        print(f"Field value 1 length: {len(val1)}")
        print(f"Field value 2 length: {len(val2)}")
        print(f"Field value 1: {repr(val1)}")
        print(f"Field value 2: {repr(val2)}")
        
        # Character-by-character comparison
        if val1 != val2:
            print(f"\nCharacter-by-character differences:")
            min_val_len = min(len(val1), len(val2))
            
            diff_count = 0
            for i in range(min_val_len):
                if val1[i] != val2[i]:
                    print(f"  Pos {i}: '{val1[i]}' (code {ord(val1[i])}) vs '{val2[i]}' (code {ord(val2[i])})")
                    diff_count += 1
                    if diff_count > 10:  # Limit output
                        print(f"  ... and more differences")
                        break
            
            # Show extra characters
            if len(val1) > len(val2):
                extra = val1[len(val2):]
                print(f"  Extra in file 1: {repr(extra)}")
            elif len(val2) > len(val1):
                extra = val2[len(val1):]
                print(f"  Extra in file 2: {repr(extra)}")
    
    # Look for other potentially relevant entries
    print(f"\nOther Object Properties:")
    print("-" * 40)
    
    # Check for appearance streams
    ap_pattern = r'/AP\s*<<([^>]*)>>'
    ap_match1 = re.search(ap_pattern, text1, re.DOTALL)
    ap_match2 = re.search(ap_pattern, text2, re.DOTALL)
    
    print(f"Has appearance stream: {ap_match1 is not None} vs {ap_match2 is not None}")
    
    # Check for rich value
    rv_pattern = r'/RV\s*\(([^)]*)\)'
    rv_match1 = re.search(rv_pattern, text1)
    rv_match2 = re.search(rv_pattern, text2)
    
    print(f"Has rich value: {rv_match1 is not None} vs {rv_match2 is not None}")
    
    # Show hex dump of differences for binary analysis
    print(f"\nHex Dump Around First Difference:")
    print("-" * 40)
    
    if first_diff is not None:
        hex_start = max(0, first_diff - 10)
        hex_end = min(len(obj1), first_diff + 10)
        
        print("File 1 (clipping):")
        hex_bytes1 = obj1[hex_start:hex_end]
        hex_str1 = ' '.join(f'{b:02x}' for b in hex_bytes1)
        ascii_str1 = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in hex_bytes1)
        print(f"  {hex_str1}")
        print(f"  {ascii_str1}")
        
        hex_end2 = min(len(obj2), first_diff + 10)
        print("File 2 (no clipping):")
        hex_bytes2 = obj2[hex_start:hex_end2]
        hex_str2 = ' '.join(f'{b:02x}' for b in hex_bytes2)
        ascii_str2 = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in hex_bytes2)
        print(f"  {hex_str2}")
        print(f"  {ascii_str2}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python deep_pdf_inspect.py <clipping.pdf> <no_clipping.pdf>")
        return
    
    file1 = sys.argv[1]  # clipping.pdf
    file2 = sys.argv[2]  # no_clipping.pdf
    
    if not os.path.exists(file1):
        print(f"Error: File not found: {file1}")
        return
    
    if not os.path.exists(file2):
        print(f"Error: File not found: {file2}")
        return
    
    print("DEEP PDF OBJECT INSPECTION")
    print("=" * 80)
    print(f"Analyzing differences between:")
    print(f"  File 1 (clipping): {file1}")
    print(f"  File 2 (no clipping): {file2}")
    
    # Analyze the problematic fields based on previous findings
    field_mappings = {
        "10": 17,   # Object 17_0 contains field "10"
        "31": 226   # Object 226_0 contains field "31"
    }
    
    for field_name, obj_num in field_mappings.items():
        analyze_object_differences(file1, file2, obj_num, field_name)

if __name__ == "__main__":
    main() 