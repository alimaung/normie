#!/usr/bin/env python3
"""
Fix Unicode escape sequences directly in raw PDF data.
This works on the actual PDF object data where the escapes are stored.
"""

import sys
import os
import re

def fix_unicode_escapes_in_pdf_data(pdf_data):
    """
    Fix Unicode escape sequences directly in PDF binary data.
    """
    # Convert to string for processing (using latin-1 to preserve bytes)
    pdf_text = pdf_data.decode('latin-1')
    
    # Track changes made
    changes_made = []
    
    # Pattern to find PDF objects with field values containing escaped sequences
    # Look for /V (field value) entries with escaped octal sequences
    def fix_field_value(match):
        full_match = match.group(0)
        field_value = match.group(1)
        
        original_value = field_value
        
        # Fix common Unicode escapes found in your PDFs
        replacements = {
            '\\\\260': '°',    # degree symbol
            '\\\\366': 'ö',    # o with umlaut  
            '\\\\337': 'ß',    # eszett (sharp s)
            '\\\\344': 'ä',    # a with umlaut
            '\\\\374': 'ü',    # u with umlaut
            '\\\\304': 'Ä',    # A with umlaut
            '\\\\326': 'Ö',    # O with umlaut
            '\\\\334': 'Ü',    # U with umlaut
            '\\\\351': 'é',    # e with acute
            '\\\\350': 'è',    # e with grave
        }
        
        for escaped, unicode_char in replacements.items():
            if escaped in field_value:
                field_value = field_value.replace(escaped, unicode_char)
                changes_made.append(f"{escaped} -> {unicode_char}")
        
        # If we made changes, return the fixed version
        if field_value != original_value:
            return f'/V({field_value})'
        else:
            return full_match
    
    # Pattern to match /V(field_value) entries
    pdf_text = re.sub(r'/V\(([^)]*)\)', fix_field_value, pdf_text)
    
    # Convert back to bytes
    fixed_pdf_data = pdf_text.encode('latin-1')
    
    return fixed_pdf_data, changes_made

def fix_pdf_unicode_escapes_raw(input_path, output_path):
    """
    Fix Unicode escapes in PDF by modifying raw PDF data.
    """
    print(f"Reading PDF data from: {input_path}")
    
    # Read the raw PDF data
    with open(input_path, 'rb') as f:
        pdf_data = f.read()
    
    print(f"Original file size: {len(pdf_data)} bytes")
    
    # Fix Unicode escapes
    print("Fixing Unicode escape sequences...")
    fixed_data, changes = fix_unicode_escapes_in_pdf_data(pdf_data)
    
    print(f"Fixed file size: {len(fixed_data)} bytes")
    print(f"Size difference: {len(pdf_data) - len(fixed_data)} bytes")
    
    if changes:
        print(f"\nChanges made:")
        for change in set(changes):  # Remove duplicates
            print(f"  {change}")
        
        # Save the fixed PDF
        print(f"\nSaving fixed PDF to: {output_path}")
        with open(output_path, 'wb') as f:
            f.write(fixed_data)
        
        print("✓ PDF saved successfully")
        return True
    else:
        print("\n✓ No Unicode escape sequences found to fix")
        
        # Copy original if no changes needed
        if input_path != output_path:
            import shutil
            shutil.copy2(input_path, output_path)
            print(f"✓ Original file copied to: {output_path}")
        
        return False

def check_raw_unicode_escapes(pdf_path):
    """
    Check for Unicode escape sequences in raw PDF data.
    """
    print(f"Checking raw PDF data for Unicode escapes: {pdf_path}")
    print("=" * 60)
    
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    # Convert to string for analysis
    pdf_text = pdf_data.decode('latin-1', errors='ignore')
    
    # Look for field values with escaped sequences
    field_pattern = r'/V\(([^)]*\\\\[0-9]{3}[^)]*)\)'
    matches = re.finditer(field_pattern, pdf_text)
    
    escape_count = 0
    for match in matches:
        field_value = match.group(1)
        escape_count += 1
        
        print(f"Found field with escapes #{escape_count}:")
        print(f"  Value: {field_value[:100]}...")
        
        # Find specific escape sequences
        octal_pattern = r'\\\\([0-9]{3})'
        octal_matches = re.finditer(octal_pattern, field_value)
        
        for octal_match in octal_matches:
            octal_seq = octal_match.group(0)
            octal_num = octal_match.group(1)
            try:
                char_code = int(octal_num, 8)
                unicode_char = chr(char_code)
                print(f"    {octal_seq} -> {unicode_char} (U+{char_code:04X})")
            except:
                print(f"    {octal_seq} -> (conversion failed)")
        print()
    
    if escape_count > 0:
        print(f"✓ Found {escape_count} fields with Unicode escape sequences")
    else:
        print("✓ No Unicode escape sequences found in raw PDF data")
    
    return escape_count > 0

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Check escapes:  python fix_raw_unicode_escapes.py <pdf_file>")
        print("  Fix escapes:    python fix_raw_unicode_escapes.py <input.pdf> <output.pdf>")
        print()
        print("Examples:")
        print("  python fix_raw_unicode_escapes.py clipping.pdf")
        print("  python fix_raw_unicode_escapes.py clipping.pdf fixed.pdf")
        return
    
    input_path = sys.argv[1]
    
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        return
    
    # Check if this is just a status check
    if len(sys.argv) == 2:
        print("CHECKING RAW UNICODE ESCAPES")
        print("=" * 60)
        check_raw_unicode_escapes(input_path)
        return
    
    # Fix the escapes
    output_path = sys.argv[2]
    
    print("FIXING RAW UNICODE ESCAPES")
    print("=" * 60)
    
    # Check current status first
    print("Current status:")
    has_escapes = check_raw_unicode_escapes(input_path)
    
    if has_escapes:
        print(f"\nProceeding to fix Unicode escapes...")
        success = fix_pdf_unicode_escapes_raw(input_path, output_path)
        
        if success:
            print(f"\n✓ Unicode escape fix completed!")
            
            # Verify the fix
            print(f"\nVerifying fix...")
            remaining = check_raw_unicode_escapes(output_path)
            if not remaining:
                print("✓ Verification successful - no escaped sequences detected")
            else:
                print("⚠ Warning: Some escaped sequences may still remain")
    else:
        print(f"\nNo Unicode escapes found to fix")

if __name__ == "__main__":
    main() 