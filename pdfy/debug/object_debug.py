#!/usr/bin/env python3
"""
Debug script to check if specific field objects exist in PDF
"""
import re

def check_field_objects(pdf_path: str):
    """Check if specific field objects exist in PDF."""
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    # Field references from the Fields array
    field_refs = [235, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 236, 237, 985, 986, 987, 988, 989, 990, 991, 238, 239, 240, 241, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 242, 243, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 244, 245, 246, 247, 248, 176, 177, 178, 179, 180, 249, 250, 251, 252, 253, 254, 255, 256, 181, 182, 183, 184, 185, 186, 187, 257, 258, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 259, 198, 1056, 1057]
    
    print(f"🔍 Checking for field objects in {pdf_path}")
    print(f"📄 PDF size: {len(pdf_data):,} bytes")
    print()
    
    # Check for first 10 field references
    test_refs = field_refs[:10]
    
    for field_ref in test_refs:
        # Look for object header
        obj_header = f"{field_ref} 0 obj".encode()
        
        if obj_header in pdf_data:
            # Find the position
            pos = pdf_data.find(obj_header)
            print(f"✅ Found object {field_ref} at position {pos}")
            
            # Extract some content around it
            start = max(0, pos - 50)
            end = min(len(pdf_data), pos + 200)
            context = pdf_data[start:end]
            
            print(f"   Context: {context[:100].decode('ascii', errors='ignore')}...")
            
            # Look for field name pattern
            obj_start = pos + len(obj_header)
            endobj_pos = pdf_data.find(b'endobj', obj_start)
            
            if endobj_pos != -1:
                obj_content = pdf_data[obj_start:endobj_pos]
                
                # Look for field name /T
                name_match = re.search(rb'/T\s*\(([^)]*)\)', obj_content)
                if name_match:
                    field_name = name_match.group(1).decode('ascii', errors='ignore')
                    print(f"   Field name: '{field_name}'")
                
                # Look for field type
                type_match = re.search(rb'/FT\s*/(\w+)', obj_content)
                if type_match:
                    field_type = type_match.group(1).decode('ascii', errors='ignore')
                    print(f"   Field type: {field_type}")
                
                # Look for field value
                value_match = re.search(rb'/V\s*\(([^)]*)\)', obj_content)
                if value_match:
                    field_value = value_match.group(1).decode('ascii', errors='ignore')
                    print(f"   Field value: '{field_value}'")
                
            print()
        else:
            print(f"❌ Object {field_ref} not found")
    
    print()
    print("🔍 Checking all object headers in PDF...")
    
    # Find all object headers
    obj_pattern = rb'(\d+)\s+(\d+)\s+obj\b'
    matches = list(re.finditer(obj_pattern, pdf_data))
    
    object_numbers = []
    for match in matches:
        obj_num = int(match.group(1))
        object_numbers.append(obj_num)
    
    object_numbers.sort()
    
    print(f"📋 Found {len(object_numbers)} objects total")
    print(f"📋 Object range: {min(object_numbers)} to {max(object_numbers)}")
    print(f"📋 First 20 objects: {object_numbers[:20]}")
    print(f"📋 Last 20 objects: {object_numbers[-20:]}")
    
    # Check which field refs are actually in the PDF
    found_field_refs = []
    missing_field_refs = []
    
    for field_ref in field_refs:
        if field_ref in object_numbers:
            found_field_refs.append(field_ref)
        else:
            missing_field_refs.append(field_ref)
    
    print(f"📋 Found {len(found_field_refs)} field objects out of {len(field_refs)}")
    print(f"📋 Missing field objects: {len(missing_field_refs)}")
    
    if found_field_refs:
        print(f"📋 Found field objects: {found_field_refs[:10]}...")
    
    if missing_field_refs:
        print(f"📋 Missing field objects: {missing_field_refs[:10]}...")

if __name__ == "__main__":
    check_field_objects("pdf.pdf") 