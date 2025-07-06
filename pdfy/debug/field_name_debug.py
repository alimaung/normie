#!/usr/bin/env python3
"""
Debug script to find actual field names directly in PDF
"""
import re

def find_fields_by_name(pdf_path: str):
    """Find form fields by searching for their names directly."""
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    # Expected field names from form_fields.json
    expected_fields = [
        "1", "2a", "2b", "2c", "2d", "3", "4", "5", "6", "7", "8", "9", "10", 
        "11", "12a", "12b", "13", "14", "15a", "15b", "16", "17a", "17b", "17c",
        "18a", "18b", "18c", "18d", "18e", "19", "20", "21", "22a", "22a1", "22a2",
        "22b", "22b1", "22b2", "25a", "25b", "25c", "26", "27", "28", "29", "30", "31"
    ]
    
    print(f"🔍 Searching for actual field names in {pdf_path}")
    print(f"📄 PDF size: {len(pdf_data):,} bytes")
    print()
    
    found_fields = {}
    
    for field_name in expected_fields:
        print(f"🔍 Searching for field '{field_name}'...")
        
        # Pattern 1: /T(field_name)
        pattern1 = f"/T({field_name})".encode()
        
        # Pattern 2: /T<hex_encoded_name>
        hex_name = field_name.encode().hex()
        pattern2 = f"/T<{hex_name}>".encode()
        
        # Pattern 3: /T field_name (without parentheses, less common)
        pattern3 = f"/T {field_name}".encode()
        
        patterns = [pattern1, pattern2, pattern3]
        
        for i, pattern in enumerate(patterns, 1):
            if pattern in pdf_data:
                pos = pdf_data.find(pattern)
                print(f"   ✅ Found with pattern {i} at position {pos}: {pattern}")
                
                # Find which object this belongs to
                # Search backwards for the nearest object header
                obj_pattern = rb'(\d+)\s+(\d+)\s+obj'
                
                # Search in a reasonable range before this position
                search_start = max(0, pos - 2000)
                search_data = pdf_data[search_start:pos]
                
                # Find all object headers before this position
                obj_matches = list(re.finditer(obj_pattern, search_data))
                
                if obj_matches:
                    last_obj_match = obj_matches[-1]
                    obj_num = int(last_obj_match.group(1))
                    gen_num = int(last_obj_match.group(2))
                    obj_offset = search_start + last_obj_match.start()
                    
                    print(f"   📋 Field '{field_name}' found in object {obj_num} (gen {gen_num}) at offset {obj_offset}")
                    
                    # Extract object content to see field details
                    obj_start = search_start + last_obj_match.end()
                    endobj_pos = pdf_data.find(b'endobj', obj_start)
                    
                    if endobj_pos != -1:
                        obj_content = pdf_data[obj_start:endobj_pos]
                        
                        # Look for field type
                        type_match = re.search(rb'/FT\s*/(\w+)', obj_content)
                        field_type = type_match.group(1).decode() if type_match else "Unknown"
                        
                        # Look for field value
                        value_patterns = [
                            rb'/V\s*\(([^)]*)\)',  # Value in parentheses
                            rb'/V\s*/(\w+)',       # Value as name
                            rb'/V\s*<([^>]*)>',    # Value in hex
                        ]
                        
                        field_value = ""
                        for val_pattern in value_patterns:
                            val_match = re.search(val_pattern, obj_content)
                            if val_match:
                                field_value = val_match.group(1).decode('ascii', errors='ignore')
                                break
                        
                        found_fields[field_name] = {
                            'object': obj_num,
                            'type': field_type,
                            'value': field_value,
                            'offset': obj_offset
                        }
                        
                        print(f"   📋 Type: {field_type}, Value: '{field_value}'")
                        
                break
        else:
            print(f"   ❌ Field '{field_name}' not found")
        
        print()
    
    print("📋 SUMMARY:")
    print(f"Found {len(found_fields)} out of {len(expected_fields)} expected fields")
    
    if found_fields:
        print("\n📋 Found fields:")
        for name, info in found_fields.items():
            print(f"  {name}: Object {info['object']}, Type={info['type']}, Value='{info['value']}'")
    
    return found_fields

if __name__ == "__main__":
    find_fields_by_name("pdf.pdf") 