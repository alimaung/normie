#!/usr/bin/env python3
"""
AcroForm Debug Script - Deep Analysis

This script examines the AcroForm structure in detail to understand
why form fields are not being parsed correctly.
"""

import os
import re
from typing import Dict, List, Any


def analyze_acroform(pdf_path: str):
    """Analyze the AcroForm structure in detail."""
    print(f"🔍 AcroForm Deep Analysis")
    print(f"📄 File: {pdf_path}")
    print("=" * 60)
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    print(f"📊 File size: {len(pdf_data):,} bytes")
    
    # 1. Find all objects first
    print(f"\n1. FINDING ALL OBJECTS:")
    obj_pattern = rb'(\d+)\s+(\d+)\s+obj\b'
    obj_matches = list(re.finditer(obj_pattern, pdf_data))
    print(f"   Found {len(obj_matches)} objects")
    
    # Store objects for analysis
    objects = {}
    for match in obj_matches:
        obj_num = int(match.group(1))
        gen_num = int(match.group(2))
        
        # Extract object content
        obj_start = match.end()
        endobj_pos = pdf_data.find(b'endobj', obj_start)
        if endobj_pos != -1:
            content = pdf_data[obj_start:endobj_pos].strip()
            objects[obj_num] = content
    
    # 2. Find root object
    print(f"\n2. FINDING ROOT OBJECT:")
    root_matches = list(re.finditer(rb'/Root\s+(\d+)\s+\d+\s+R', pdf_data))
    if root_matches:
        root_ref = int(root_matches[-1].group(1))
        print(f"   Root object: {root_ref}")
        
        if root_ref in objects:
            root_content = objects[root_ref]
            print(f"   Root content preview: {root_content[:200].decode('ascii', errors='ignore')}")
            
            # Look for AcroForm in root
            acroform_match = re.search(rb'/AcroForm\s+(\d+)\s+\d+\s+R', root_content)
            if acroform_match:
                acroform_ref = int(acroform_match.group(1))
                print(f"   AcroForm reference: {acroform_ref}")
                
                # 3. Analyze AcroForm object
                print(f"\n3. ANALYZING ACROFORM OBJECT {acroform_ref}:")
                if acroform_ref in objects:
                    acroform_content = objects[acroform_ref]
                    print(f"   AcroForm content:")
                    print(f"   {acroform_content.decode('ascii', errors='ignore')}")
                    
                    # Look for Fields array
                    fields_match = re.search(rb'/Fields\s*\[([^\]]*)\]', acroform_content)
                    if fields_match:
                        fields_array = fields_match.group(1)
                        print(f"\n   Fields array: {fields_array.decode('ascii', errors='ignore')}")
                        
                        # Extract field references
                        field_refs = re.findall(rb'(\d+)\s+\d+\s+R', fields_array)
                        print(f"   Field references: {[int(ref) for ref in field_refs]}")
                        
                        # 4. Analyze individual fields
                        print(f"\n4. ANALYZING INDIVIDUAL FIELDS:")
                        for i, field_ref in enumerate(field_refs):
                            field_num = int(field_ref)
                            print(f"\n   Field #{i+1} - Object {field_num}:")
                            
                            if field_num in objects:
                                field_content = objects[field_num]
                                print(f"      Content: {field_content.decode('ascii', errors='ignore')}")
                                
                                # Look for field name
                                name_patterns = [
                                    (rb'/T\s*\(([^)]*)\)', 'parentheses'),
                                    (rb'/T\s*<([^>]*)>', 'hex string'),
                                    (rb'/T\s*/([^\s/]+)', 'name'),
                                    (rb'/T\s+(\d+)\s+\d+\s+R', 'reference')
                                ]
                                
                                for pattern, desc in name_patterns:
                                    match = re.search(pattern, field_content)
                                    if match:
                                        print(f"      Field name ({desc}): {match.group(1).decode('ascii', errors='ignore')}")
                                        break
                                
                                # Look for field type
                                type_patterns = [
                                    (rb'/FT\s*/([^\s/]+)', 'FT'),
                                    (rb'/FT\s*\(([^)]*)\)', 'FT parentheses'),
                                    (rb'/Subtype\s*/([^\s/]+)', 'Subtype')
                                ]
                                
                                for pattern, desc in type_patterns:
                                    match = re.search(pattern, field_content)
                                    if match:
                                        print(f"      Field type ({desc}): {match.group(1).decode('ascii', errors='ignore')}")
                                        break
                                
                                # Look for field value
                                value_patterns = [
                                    (rb'/V\s*\(([^)]*)\)', 'parentheses'),
                                    (rb'/V\s*<([^>]*)>', 'hex string'),
                                    (rb'/V\s*/([^\s/]+)', 'name'),
                                    (rb'/V\s+(\d+)', 'number')
                                ]
                                
                                for pattern, desc in value_patterns:
                                    match = re.search(pattern, field_content)
                                    if match:
                                        print(f"      Field value ({desc}): {match.group(1).decode('ascii', errors='ignore')}")
                                        break
                                
                                # Look for Kids (sub-fields)
                                kids_match = re.search(rb'/Kids\s*\[([^\]]*)\]', field_content)
                                if kids_match:
                                    kids_array = kids_match.group(1)
                                    kid_refs = re.findall(rb'(\d+)\s+\d+\s+R', kids_array)
                                    print(f"      Kids: {[int(ref) for ref in kid_refs]}")
                                    
                                    # Analyze first kid
                                    if kid_refs:
                                        kid_num = int(kid_refs[0])
                                        if kid_num in objects:
                                            kid_content = objects[kid_num]
                                            print(f"      First kid content: {kid_content[:200].decode('ascii', errors='ignore')}")
                            else:
                                print(f"      Object {field_num} not found!")
                    else:
                        print(f"   No Fields array found in AcroForm")
                else:
                    print(f"   AcroForm object {acroform_ref} not found!")
            else:
                print(f"   No AcroForm reference found in root")
        else:
            print(f"   Root object {root_ref} not found!")
    else:
        print(f"   No root object found!")
    
    # 5. Search for specific field names
    print(f"\n5. SEARCHING FOR SPECIFIC FIELD NAMES:")
    test_field_names = ['1', '3', '25a', '2a', '8', '16', '18a', '18b', '18c', '18d', '15a', '15b', '5', '6', '13', '14', '26', '27']
    
    for field_name in test_field_names:
        # Search for field name in parentheses
        pattern = f'/T\\s*\\({re.escape(field_name)}\\)'.encode()
        matches = list(re.finditer(pattern, pdf_data))
        
        if matches:
            print(f"   Field '{field_name}': {len(matches)} matches")
            for match in matches:
                # Find which object this is in
                obj_start = pdf_data.rfind(b' obj', 0, match.start())
                if obj_start != -1:
                    obj_header = pdf_data[obj_start-10:obj_start+10]
                    obj_match = re.search(rb'(\d+)\s+\d+\s+obj', obj_header)
                    if obj_match:
                        obj_num = int(obj_match.group(1))
                        print(f"      Found in object {obj_num}")
        else:
            print(f"   Field '{field_name}': No matches")
    
    # 6. General field search
    print(f"\n6. GENERAL FIELD SEARCH:")
    
    # Look for all /T( patterns
    t_pattern = rb'/T\s*\(([^)]*)\)'
    t_matches = list(re.finditer(t_pattern, pdf_data))
    print(f"   Found {len(t_matches)} /T(...) patterns")
    
    for i, match in enumerate(t_matches[:10]):  # Show first 10
        field_name = match.group(1).decode('ascii', errors='ignore')
        print(f"      Field {i+1}: '{field_name}'")
        
        # Find object number
        obj_start = pdf_data.rfind(b' obj', 0, match.start())
        if obj_start != -1:
            obj_header = pdf_data[obj_start-10:obj_start+10]
            obj_match = re.search(rb'(\d+)\s+\d+\s+obj', obj_header)
            if obj_match:
                obj_num = int(obj_match.group(1))
                print(f"         In object {obj_num}")
    
    if len(t_matches) > 10:
        print(f"      ... and {len(t_matches) - 10} more")
    
    print(f"\n{'='*60}")
    print("🔍 AcroForm analysis complete!")
    print("💡 Use this information to fix the form field parsing")


def main():
    """Main function."""
    pdf_file = "pdf.pdf"
    
    if len(os.sys.argv) > 1:
        pdf_file = os.sys.argv[1]
    
    analyze_acroform(pdf_file)


if __name__ == "__main__":
    main() 