#!/usr/bin/env python3
"""
Fix Unicode escape sequences in PDF form fields.
This converts escaped sequences like \\260 back to proper Unicode characters.
"""

import sys
import os
import re
try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    print("Error: PyMuPDF is required for this script")
    print("Install with: pip install PyMuPDF")
    sys.exit(1)

def unescape_unicode_sequences(text):
    """
    Convert escaped Unicode sequences back to proper characters.
    Examples:
    - \\260 -> ° (degree symbol)
    - \\366 -> ö (o with umlaut)
    - \\337 -> ß (eszett)
    """
    if not text:
        return text
    
    original_text = text
    
    # Pattern to match escaped octal sequences like \\260, \\366, etc.
    def replace_octal(match):
        octal_str = match.group(1)
        try:
            # Convert octal to integer, then to character
            char_code = int(octal_str, 8)
            # Use Latin-1 encoding for PDF compatibility
            return chr(char_code)
        except (ValueError, OverflowError):
            # If conversion fails, return original
            return match.group(0)
    
    # Replace escaped octal sequences
    text = re.sub(r'\\\\(\d{3})', replace_octal, text)
    
    # Also handle some common escape sequences
    replacements = {
        '\\\\n': '\n',
        '\\\\r': '\r',
        '\\\\t': '\t',
        '\\\\\\\\': '\\',
    }
    
    for escaped, unescaped in replacements.items():
        text = text.replace(escaped, unescaped)
    
    return text

def fix_pdf_unicode_escapes(input_path, output_path, target_fields=None):
    """
    Fix Unicode escape sequences in PDF form fields.
    """
    print(f"Opening PDF: {input_path}")
    doc = fitz.open(input_path)
    
    fields_processed = []
    
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                field_name = widget.field_name
                
                # Process specific fields or all text fields if none specified
                if (target_fields is None or field_name in target_fields) and widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                    print(f"\nProcessing field: {field_name}")
                    
                    original_value = str(widget.field_value or '')
                    print(f"  Original length: {len(original_value)}")
                    
                    # Check if field has escaped sequences
                    if '\\\\' in original_value and re.search(r'\\\\(\d{3})', original_value):
                        print(f"  ✓ Found escaped Unicode sequences")
                        print(f"  Original: {original_value[:100]}...")
                        
                        # Fix the Unicode escapes
                        fixed_value = unescape_unicode_sequences(original_value)
                        print(f"  Fixed length: {len(fixed_value)}")
                        print(f"  Fixed: {fixed_value[:100]}...")
                        
                        # Show the specific changes
                        if original_value != fixed_value:
                            print(f"  Changes made:")
                            
                            # Find and show specific replacements
                            octal_matches = re.finditer(r'\\\\(\d{3})', original_value)
                            for match in octal_matches:
                                octal_seq = match.group(0)
                                octal_num = match.group(1)
                                try:
                                    char_code = int(octal_num, 8)
                                    unicode_char = chr(char_code)
                                    print(f"    {octal_seq} -> {unicode_char} (U+{char_code:04X})")
                                except:
                                    print(f"    {octal_seq} -> (conversion failed)")
                            
                            # Update the field
                            try:
                                widget.field_value = fixed_value
                                widget.update()
                                fields_processed.append(field_name)
                                print(f"  ✓ Field updated successfully")
                            except Exception as e:
                                print(f"  ✗ Error updating field: {e}")
                        else:
                            print(f"  ✓ No changes needed")
                    else:
                        print(f"  ✓ No escaped sequences found")
        
        if fields_processed:
            print(f"\n✓ Successfully fixed {len(fields_processed)} fields:")
            for field in fields_processed:
                print(f"  - {field}")
            
            print(f"\nSaving to: {output_path}")
            doc.save(output_path)
            print("✓ PDF saved successfully")
        else:
            print("\n✓ No fields needed fixing")
            if input_path != output_path:
                print(f"Copying original to: {output_path}")
                doc.save(output_path)
    
    finally:
        doc.close()
    
    return fields_processed

def check_unicode_escapes(pdf_path, target_fields=None):
    """
    Check for Unicode escape sequences in PDF form fields.
    """
    print(f"Checking for Unicode escapes in: {pdf_path}")
    print("=" * 60)
    
    doc = fitz.open(pdf_path)
    escape_fields = []
    
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                field_name = widget.field_name
                
                if target_fields is None or field_name in target_fields:
                    if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                        field_value = str(widget.field_value or '')
                        
                        # Check for escaped sequences
                        has_escapes = '\\\\' in field_value and re.search(r'\\\\(\d{3})', field_value)
                        
                        if has_escapes:
                            escape_fields.append(field_name)
                            print(f"Field '{field_name}': ❌ HAS ESCAPED SEQUENCES")
                            print(f"  Value: {field_value[:100]}...")
                            
                            # Show specific escape sequences
                            octal_matches = re.finditer(r'\\\\(\d{3})', field_value)
                            for match in octal_matches:
                                octal_seq = match.group(0)
                                octal_num = match.group(1)
                                try:
                                    char_code = int(octal_num, 8)
                                    unicode_char = chr(char_code)
                                    print(f"    Found: {octal_seq} -> {unicode_char} (U+{char_code:04X})")
                                except:
                                    print(f"    Found: {octal_seq} (conversion failed)")
                        else:
                            print(f"Field '{field_name}': ✅ Clean")
                        print()
    
    finally:
        doc.close()
    
    if escape_fields:
        print(f"✓ Found {len(escape_fields)} fields with escaped sequences:")
        for field in escape_fields:
            print(f"  - {field}")
    else:
        print(f"✓ No escaped sequences found")
    
    return escape_fields

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Check escapes:  python fix_unicode_escapes.py <pdf_file> [field1,field2,...]")
        print("  Fix escapes:    python fix_unicode_escapes.py <input.pdf> <output.pdf> [field1,field2,...]")
        print()
        print("Examples:")
        print("  python fix_unicode_escapes.py clipping.pdf")
        print("  python fix_unicode_escapes.py clipping.pdf fixed.pdf")
        print("  python fix_unicode_escapes.py clipping.pdf fixed.pdf 10,31")
        return
    
    input_path = sys.argv[1]
    
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        return
    
    # Check if this is just a status check
    if len(sys.argv) == 2 or (len(sys.argv) == 3 and not sys.argv[2].endswith('.pdf')):
        # Parse target fields if provided
        target_fields = None
        if len(sys.argv) == 3:
            target_fields = [f.strip() for f in sys.argv[2].split(',')]
            print(f"Target fields: {target_fields}")
        
        print("CHECKING UNICODE ESCAPES")
        print("=" * 60)
        check_unicode_escapes(input_path, target_fields)
        return
    
    # Parse arguments for fixing
    output_path = sys.argv[2]
    target_fields = None
    
    if len(sys.argv) > 3:
        target_fields = [f.strip() for f in sys.argv[3].split(',')]
        print(f"Target fields: {target_fields}")
    
    print(f"FIXING UNICODE ESCAPES")
    print("=" * 60)
    
    # Check current status first
    print("Current status:")
    escape_fields = check_unicode_escapes(input_path, target_fields)
    
    if escape_fields:
        print(f"\nProceeding to fix Unicode escapes...")
        processed = fix_pdf_unicode_escapes(input_path, output_path, target_fields)
        
        if processed:
            print(f"\n✓ Unicode escape fix completed successfully!")
            print(f"✓ Fixed file saved as: {output_path}")
            
            # Verify the fix
            print(f"\nVerifying fix...")
            remaining = check_unicode_escapes(output_path, target_fields)
            if not remaining:
                print("✓ Verification successful - no escaped sequences detected")
            else:
                print(f"⚠ Warning: {len(remaining)} fields still have escaped sequences")
    else:
        print(f"No action needed - copying to output file...")
        if input_path != output_path:
            import shutil
            shutil.copy2(input_path, output_path)
            print(f"✓ File copied to: {output_path}")

if __name__ == "__main__":
    main() 