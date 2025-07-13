#!/usr/bin/env python3
"""
Fix octal escape sequences directly in PDF object data.
"""

import sys
import os
import re

def convert_octal_to_unicode_bytes(text_bytes):
    """
    Convert octal escape sequences in PDF object data to proper Unicode bytes.
    """
    # Convert bytes to string for processing
    try:
        text = text_bytes.decode('latin-1')
    except:
        return text_bytes  # Return original if can't decode
    
    # Common German character mappings (octal -> Unicode)
    octal_mappings = {
        '\\\\260': '°',   # Degree symbol (\\260 -> °)
        '\\\\337': 'ß',   # German sharp s (\\337 -> ß)  
        '\\\\366': 'ö',   # o with umlaut (\\366 -> ö)
        '\\\\374': 'ü',   # u with umlaut (\\374 -> ü)
        '\\\\344': 'ä',   # a with umlaut (\\344 -> ä)
        '\\\\334': 'Ü',   # U with umlaut (\\334 -> Ü)
        '\\\\304': 'Ä',   # A with umlaut (\\304 -> Ä)
        '\\\\326': 'Ö',   # O with umlaut (\\326 -> Ö)
    }
    
    result = text
    changes_made = False
    
    for octal, unicode_char in octal_mappings.items():
        if octal in result:
            result = result.replace(octal, unicode_char)
            changes_made = True
    
    if changes_made:
        # Convert back to bytes
        try:
            return result.encode('latin-1')
        except:
            return text_bytes  # Return original if encoding fails
    
    return text_bytes

def fix_pdf_objects(input_file, output_file):
    """
    Fix octal escape sequences in PDF objects.
    """
    print(f"Reading PDF: {input_file}")
    
    try:
        with open(input_file, 'rb') as f:
            pdf_data = f.read()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return False
    
    print(f"Original PDF size: {len(pdf_data)} bytes")
    
    # Find and fix specific objects (17 and 226 based on our analysis)
    target_objects = [17, 226]  # Objects containing fields "10" and "31"
    
    modified_data = pdf_data
    total_changes = 0
    
    for obj_num in target_objects:
        print(f"\nProcessing object {obj_num}...")
        
        # Find the object
        obj_pattern = rf'{obj_num}\s+0\s+obj'.encode()
        match = re.search(obj_pattern, modified_data)
        
        if not match:
            print(f"  Object {obj_num} not found")
            continue
        
        start_pos = match.start()
        
        # Find end of object
        endobj_match = re.search(rb'endobj', modified_data[start_pos:])
        if endobj_match:
            end_pos = start_pos + endobj_match.end()
        else:
            print(f"  Could not find end of object {obj_num}")
            continue
        
        # Extract object data
        obj_data = modified_data[start_pos:end_pos]
        original_obj_data = obj_data
        
        # Fix octal escapes in this object
        fixed_obj_data = convert_octal_to_unicode_bytes(obj_data)
        
        if fixed_obj_data != original_obj_data:
            print(f"  ✅ Fixed octal escapes in object {obj_num}")
            print(f"  Size change: {len(original_obj_data)} -> {len(fixed_obj_data)} bytes")
            
            # Replace in the full PDF data
            modified_data = modified_data[:start_pos] + fixed_obj_data + modified_data[end_pos:]
            total_changes += 1
            
            # Show what was changed
            try:
                orig_text = original_obj_data.decode('latin-1', errors='replace')
                fixed_text = fixed_obj_data.decode('latin-1', errors='replace')
                
                # Find differences
                if '\\260' in orig_text or '\\337' in orig_text or '\\366' in orig_text:
                    print(f"  Changes made:")
                    if '\\260' in orig_text:
                        print(f"    \\260 -> ° (degree symbol)")
                    if '\\337' in orig_text:
                        print(f"    \\337 -> ß (sharp s)")
                    if '\\366' in orig_text:
                        print(f"    \\366 -> ö (o umlaut)")
            except:
                pass
        else:
            print(f"  No changes needed for object {obj_num}")
    
    if total_changes > 0:
        print(f"\nSaving fixed PDF to: {output_file}")
        print(f"Total objects modified: {total_changes}")
        print(f"Final PDF size: {len(modified_data)} bytes")
        
        try:
            with open(output_file, 'wb') as f:
                f.write(modified_data)
            print("✅ PDF saved successfully!")
            return True
        except Exception as e:
            print(f"Error saving PDF: {e}")
            return False
    else:
        print("No changes were made.")
        return False

def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage: python fix_pdf_objects.py <input.pdf> [output.pdf]")
        print("If no output file is specified, '_fixed' will be added to the input filename.")
        return
    
    input_file = sys.argv[1]
    
    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    else:
        # Generate output filename
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_objects_fixed{ext}"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
    
    print("PDF OBJECT-LEVEL ENCODING FIXER")
    print("=" * 50)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    
    success = fix_pdf_objects(input_file, output_file)
    
    if success:
        print(f"\n🎉 PDF objects fixed! Test the output file: {output_file}")
        print("The clipping issue should now be resolved.")
    else:
        print(f"\n❌ No changes were made or an error occurred.")

if __name__ == "__main__":
    main() 