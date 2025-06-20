#!/usr/bin/env python3
"""
PDF-aware binary comparison tool to identify structural differences.
"""

import os
import re
import sys

def extract_pdf_objects(data):
    """
    Extract PDF objects from binary data for comparison.
    """
    objects = {}
    
    # Find all PDF objects (pattern: "n n obj")
    obj_pattern = rb'(\d+)\s+(\d+)\s+obj'
    matches = list(re.finditer(obj_pattern, data))
    
    for i, match in enumerate(matches):
        obj_num = int(match.group(1))
        gen_num = int(match.group(2))
        start_pos = match.start()
        
        # Find the end of this object
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            # Look for "endobj" or end of file
            endobj_match = re.search(rb'endobj', data[start_pos:])
            if endobj_match:
                end_pos = start_pos + endobj_match.end()
            else:
                end_pos = len(data)
        
        obj_data = data[start_pos:end_pos]
        objects[f"{obj_num}_{gen_num}"] = {
            'obj_num': obj_num,
            'gen_num': gen_num,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'data': obj_data,
            'size': len(obj_data)
        }
    
    return objects

def find_form_field_objects(data, objects):
    """
    Identify which objects contain form field data.
    """
    field_objects = {}
    
    for obj_id, obj_info in objects.items():
        obj_data = obj_info['data']
        
        # Look for field indicators
        if (b'/FT' in obj_data or  # Field Type
            b'/T (' in obj_data or  # Field Name
            b'/V (' in obj_data or  # Field Value
            b'/Tx' in obj_data):    # Text field
            
            # Try to extract field name
            field_name = None
            name_match = re.search(rb'/T\s*\(([^)]+)\)', obj_data)
            if name_match:
                field_name = name_match.group(1).decode('latin-1', errors='ignore')
            
            field_objects[obj_id] = {
                **obj_info,
                'field_name': field_name,
                'has_field_type': b'/FT' in obj_data,
                'has_field_value': b'/V (' in obj_data,
                'has_appearance': b'/AP' in obj_data,
                'has_rich_value': b'/RV' in obj_data
            }
    
    return field_objects

def compare_pdf_structure(file1, file2):
    """
    Compare PDF structure and identify differences.
    """
    print(f"Analyzing PDF structure differences between:")
    print(f"  File 1: {file1}")
    print(f"  File 2: {file2}")
    print("=" * 80)
    
    # Read both files
    with open(file1, 'rb') as f1:
        data1 = f1.read()
    with open(file2, 'rb') as f2:
        data2 = f2.read()
    
    print(f"File sizes: {len(data1)} vs {len(data2)} bytes")
    
    # Extract PDF objects
    print("\nExtracting PDF objects...")
    objects1 = extract_pdf_objects(data1)
    objects2 = extract_pdf_objects(data2)
    
    print(f"Objects found: {len(objects1)} vs {len(objects2)}")
    
    # Find form field objects
    print("\nIdentifying form field objects...")
    fields1 = find_form_field_objects(data1, objects1)
    fields2 = find_form_field_objects(data2, objects2)
    
    print(f"Form field objects: {len(fields1)} vs {len(fields2)}")
    
    # Compare headers
    print("\nPDF Header Comparison:")
    print("-" * 40)
    header1 = data1[:100].decode('latin-1', errors='ignore')
    header2 = data2[:100].decode('latin-1', errors='ignore')
    
    if header1 != header2:
        print("❌ Headers differ:")
        print(f"  File 1: {repr(header1[:50])}")
        print(f"  File 2: {repr(header2[:50])}")
    else:
        print("✅ Headers are identical")
    
    # Compare form field objects
    print("\nForm Field Object Comparison:")
    print("-" * 40)
    
    all_field_ids = set(fields1.keys()) | set(fields2.keys())
    
    for field_id in sorted(all_field_ids):
        field1 = fields1.get(field_id)
        field2 = fields2.get(field_id)
        
        if not field1:
            print(f"❌ Object {field_id} only in file 2")
            continue
        if not field2:
            print(f"❌ Object {field_id} only in file 1")
            continue
        
        # Compare field objects
        if field1['data'] == field2['data']:
            print(f"✅ Object {field_id} ({field1['field_name']}) - identical")
        else:
            print(f"❌ Object {field_id} ({field1['field_name']}) - DIFFERENT")
            print(f"    Size: {field1['size']} vs {field2['size']} bytes")
            
            # Check specific field name matches
            if field1['field_name'] in ['10', '31']:
                print(f"    ⚠️  This is one of the problematic fields!")
                analyze_field_differences(field1, field2)
    
    # Compare all objects
    print(f"\nAll Object Comparison:")
    print("-" * 40)
    
    all_obj_ids = set(objects1.keys()) | set(objects2.keys())
    different_objects = []
    
    for obj_id in sorted(all_obj_ids):
        obj1 = objects1.get(obj_id)
        obj2 = objects2.get(obj_id)
        
        if not obj1 or not obj2:
            different_objects.append(obj_id)
            continue
        
        if obj1['data'] != obj2['data']:
            different_objects.append(obj_id)
    
    print(f"Objects that differ: {len(different_objects)} out of {len(all_obj_ids)}")
    
    if different_objects:
        print("Different object IDs:", different_objects[:10])  # Show first 10
        if len(different_objects) > 10:
            print(f"... and {len(different_objects) - 10} more")

def analyze_field_differences(field1, field2):
    """
    Analyze specific differences in a form field object.
    """
    print(f"      Detailed field analysis:")
    
    data1 = field1['data']
    data2 = field2['data']
    
    # Look for specific differences
    differences = []
    
    # Check for appearance differences
    ap1 = b'/AP' in data1
    ap2 = b'/AP' in data2
    if ap1 != ap2:
        differences.append(f"Appearance dictionary presence: {ap1} vs {ap2}")
    
    # Check for rich value differences  
    rv1 = b'/RV' in data1
    rv2 = b'/RV' in data2
    if rv1 != rv2:
        differences.append(f"Rich value presence: {rv1} vs {rv2}")
    
    # Check field value differences
    val1_match = re.search(rb'/V\s*\(([^)]*)\)', data1)
    val2_match = re.search(rb'/V\s*\(([^)]*)\)', data2)
    
    if val1_match and val2_match:
        val1 = val1_match.group(1)
        val2 = val2_match.group(1)
        if val1 != val2:
            differences.append(f"Field values differ (lengths: {len(val1)} vs {len(val2)})")
    
    # Find first byte difference
    min_len = min(len(data1), len(data2))
    first_diff = None
    for i in range(min_len):
        if data1[i] != data2[i]:
            first_diff = i
            break
    
    if first_diff is not None:
        differences.append(f"First difference at byte {first_diff}")
        # Show context
        start = max(0, first_diff - 10)
        end = min(len(data1), first_diff + 10)
        context1 = data1[start:end].decode('latin-1', errors='ignore')
        context2 = data2[start:end].decode('latin-1', errors='ignore')
        print(f"        Context 1: {repr(context1)}")
        print(f"        Context 2: {repr(context2)}")
    
    for diff in differences:
        print(f"        - {diff}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python pdf_binary_analyzer.py <file1.pdf> <file2.pdf>")
        print("Example: python pdf_binary_analyzer.py clipping.pdf no_clipping.pdf")
        return
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    if not os.path.exists(file1):
        print(f"Error: File not found: {file1}")
        return
    
    if not os.path.exists(file2):
        print(f"Error: File not found: {file2}")
        return
    
    compare_pdf_structure(file1, file2)

if __name__ == "__main__":
    main() 