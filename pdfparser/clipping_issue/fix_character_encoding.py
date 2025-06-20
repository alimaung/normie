#!/usr/bin/env python3
"""
Fix character encoding issues in PDF form fields by converting octal escape sequences
to proper Unicode characters.
"""

import sys
import os
import re
import fitz  # PyMuPDF

def convert_octal_escapes(text):
    """
    Convert octal escape sequences like \\260, \\337, \\366 to Unicode characters.
    """
    if not text:
        return text
    
    # Common German character mappings
    octal_mappings = {
        '\\260': '°',   # Degree symbol
        '\\337': 'ß',   # German sharp s
        '\\366': 'ö',   # o with umlaut
        '\\374': 'ü',   # u with umlaut
        '\\344': 'ä',   # a with umlaut
        '\\334': 'Ü',   # U with umlaut
        '\\304': 'Ä',   # A with umlaut
        '\\326': 'Ö',   # O with umlaut
    }
    
    result = text
    for octal, unicode_char in octal_mappings.items():
        result = result.replace(octal, unicode_char)
    
    # Generic octal escape pattern (\\nnn where nnn is 3 octal digits)
    def replace_octal(match):
        octal_str = match.group(1)
        try:
            # Convert octal to decimal, then to character
            decimal_value = int(octal_str, 8)
            if 32 <= decimal_value <= 255:  # Printable ASCII/Latin-1 range
                return chr(decimal_value)
            else:
                return match.group(0)  # Keep original if out of range
        except ValueError:
            return match.group(0)  # Keep original if conversion fails
    
    # Replace remaining octal escapes
    result = re.sub(r'\\(\d{3})', replace_octal, result)
    
    return result

def fix_pdf_encoding(input_file, output_file):
    """
    Fix character encoding issues in PDF form fields.
    """
    print(f"Opening PDF: {input_file}")
    
    try:
        doc = fitz.open(input_file)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return False
    
    changes_made = 0
    
    print(f"Processing {len(doc)} pages...")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get form fields on this page
        widgets = page.widgets()
        
        for widget in widgets:
            if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                field_name = widget.field_name
                current_value = widget.field_value or ""
                
                # Convert octal escapes
                fixed_value = convert_octal_escapes(current_value)
                
                if fixed_value != current_value:
                    print(f"Fixing field '{field_name}':")
                    print(f"  Before: {repr(current_value)}")
                    print(f"  After:  {repr(fixed_value)}")
                    
                    # Update the field value
                    widget.field_value = fixed_value
                    widget.update()
                    changes_made += 1
    
    if changes_made > 0:
        print(f"\nMade {changes_made} changes. Saving to: {output_file}")
        doc.save(output_file)
        print("✅ PDF saved successfully!")
    else:
        print("No changes needed.")
    
    doc.close()
    return changes_made > 0

def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage: python fix_character_encoding.py <input.pdf> [output.pdf]")
        print("If no output file is specified, '_fixed' will be added to the input filename.")
        return
    
    input_file = sys.argv[1]
    
    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    else:
        # Generate output filename
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_fixed{ext}"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
    
    print("PDF CHARACTER ENCODING FIXER")
    print("=" * 50)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print()
    
    success = fix_pdf_encoding(input_file, output_file)
    
    if success:
        print(f"\n🎉 Character encoding fixed! Check the output file: {output_file}")
    else:
        print(f"\n❌ No changes were made or an error occurred.")

if __name__ == "__main__":
    main() 