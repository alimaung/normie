#!/usr/bin/env python3
"""
Comprehensive field debug script to find all field name patterns
"""
import re

def find_all_field_patterns(pdf_path: str):
    """Find all possible field name patterns in PDF."""
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    print(f"🔍 Comprehensive field pattern search in {pdf_path}")
    print(f"📄 PDF size: {len(pdf_data):,} bytes")
    print()
    
    # Pattern 1: Look for all /T patterns
    print("🔍 Pattern 1: All /T patterns")
    t_patterns = re.findall(rb'/T\s*([(<][^)>]*[)>]|\w+)', pdf_data)
    print(f"Found {len(t_patterns)} /T patterns:")
    for i, pattern in enumerate(t_patterns[:20]):  # Show first 20
        try:
            decoded = pattern.decode('ascii', errors='ignore')
            print(f"  {i+1}: {pattern} -> '{decoded}'")
        except:
            print(f"  {i+1}: {pattern}")
    if len(t_patterns) > 20:
        print(f"  ... and {len(t_patterns) - 20} more")
    print()
    
    # Pattern 2: Look for field type indicators with nearby names
    print("🔍 Pattern 2: Fields with /FT (field type)")
    ft_pattern = rb'/FT\s*/(\w+)'
    ft_matches = list(re.finditer(ft_pattern, pdf_data))
    print(f"Found {len(ft_matches)} /FT patterns:")
    
    for i, match in enumerate(ft_matches[:10]):  # Show first 10
        field_type = match.group(1).decode()
        pos = match.start()
        
        # Look for /T pattern nearby (within 500 bytes before/after)
        search_start = max(0, pos - 500)
        search_end = min(len(pdf_data), pos + 500)
        context = pdf_data[search_start:search_end]
        
        # Find /T patterns in this context
        local_t = re.findall(rb'/T\s*([(<][^)>]*[)>]|\w+)', context)
        
        print(f"  {i+1}: Type={field_type}, Nearby /T patterns: {local_t}")
    print()
    
    # Pattern 3: Look for specific field names we expect
    expected_fields = ["1", "2a", "3", "25a", "8", "16", "18a", "18b"]
    print("🔍 Pattern 3: Searching for specific expected field names")
    
    for field_name in expected_fields:
        print(f"Searching for '{field_name}':")
        
        # Multiple encoding patterns
        patterns = [
            f"/T({field_name})".encode(),
            f"/T<{field_name.encode().hex()}>".encode(),
            f"/T {field_name}".encode(),
            f"/T<{field_name.encode().hex().upper()}>".encode(),
            f"({field_name})".encode(),  # Just the parentheses
            field_name.encode(),  # Raw field name
        ]
        
        found_any = False
        for j, pattern in enumerate(patterns):
            if pattern in pdf_data:
                pos = pdf_data.find(pattern)
                print(f"  ✅ Pattern {j+1} found at {pos}: {pattern}")
                
                # Show context
                start = max(0, pos - 50)
                end = min(len(pdf_data), pos + 100)
                context = pdf_data[start:end]
                print(f"     Context: {context}")
                found_any = True
                break
        
        if not found_any:
            print(f"  ❌ '{field_name}' not found with any pattern")
    print()
    
    # Pattern 4: Look for object dictionaries that might contain fields
    print("🔍 Pattern 4: Objects with field-like content")
    
    # Find objects that have both /FT and some kind of name
    obj_pattern = rb'(\d+)\s+(\d+)\s+obj'
    obj_matches = list(re.finditer(obj_pattern, pdf_data))
    
    field_objects = []
    for match in obj_matches:
        obj_num = int(match.group(1))
        
        # Extract object content
        obj_start = match.end()
        endobj_pos = pdf_data.find(b'endobj', obj_start)
        
        if endobj_pos != -1:
            obj_content = pdf_data[obj_start:endobj_pos]
            
            # Check if this object has field indicators
            has_ft = b'/FT' in obj_content
            has_t = b'/T' in obj_content
            has_v = b'/V' in obj_content
            
            if has_ft and has_t:
                # Extract field type
                ft_match = re.search(rb'/FT\s*/(\w+)', obj_content)
                field_type = ft_match.group(1).decode() if ft_match else "Unknown"
                
                # Extract field name - try multiple patterns
                field_name = None
                name_patterns = [
                    rb'/T\s*\(([^)]*)\)',  # /T(name)
                    rb'/T\s*<([^>]*)>',    # /T<hex>
                    rb'/T\s*([A-Za-z0-9]+)', # /T name
                ]
                
                for pattern in name_patterns:
                    name_match = re.search(pattern, obj_content)
                    if name_match:
                        raw_name = name_match.group(1)
                        try:
                            if raw_name.startswith(b'<') or len(raw_name) % 2 == 0:
                                # Try hex decode
                                field_name = bytes.fromhex(raw_name.decode()).decode()
                            else:
                                field_name = raw_name.decode()
                            break
                        except:
                            field_name = raw_name.decode('ascii', errors='ignore')
                            break
                
                # Extract field value
                field_value = ""
                value_patterns = [
                    rb'/V\s*\(([^)]*)\)',  # /V(value)
                    rb'/V\s*/(\w+)',       # /V/name
                    rb'/V\s*<([^>]*)>',    # /V<hex>
                ]
                
                for pattern in value_patterns:
                    val_match = re.search(pattern, obj_content)
                    if val_match:
                        field_value = val_match.group(1).decode('ascii', errors='ignore')
                        break
                
                field_objects.append({
                    'object': obj_num,
                    'type': field_type,
                    'name': field_name,
                    'value': field_value,
                    'has_v': has_v
                })
    
    print(f"Found {len(field_objects)} field objects:")
    for field_obj in field_objects[:20]:  # Show first 20
        print(f"  Object {field_obj['object']}: name='{field_obj['name']}', type={field_obj['type']}, value='{field_obj['value']}'")
    
    if len(field_objects) > 20:
        print(f"  ... and {len(field_objects) - 20} more")
    
    return field_objects

if __name__ == "__main__":
    find_all_field_patterns("pdf.pdf") 