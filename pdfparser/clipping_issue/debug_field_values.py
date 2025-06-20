#!/usr/bin/env python3
"""
Debug what PyMuPDF actually reads from form field values.
"""

import sys
import os
import fitz  # PyMuPDF

def debug_field_values(pdf_file):
    """
    Debug form field values as seen by PyMuPDF.
    """
    print(f"Opening PDF: {pdf_file}")
    
    try:
        doc = fitz.open(pdf_file)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return
    
    print(f"Processing {len(doc)} pages...")
    
    field_count = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get form fields on this page
        widgets = page.widgets()
        
        for widget in widgets:
            if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                field_name = widget.field_name
                field_value = widget.field_value or ""
                
                # Focus on the problematic fields
                if field_name in ["10", "31"]:
                    field_count += 1
                    print(f"\n{'='*60}")
                    print(f"Field '{field_name}' (Page {page_num + 1})")
                    print(f"{'='*60}")
                    print(f"Field value length: {len(field_value)}")
                    print(f"Field value: {repr(field_value)}")
                    print(f"Field value (display): {field_value}")
                    
                    # Check for escape sequences
                    has_escapes = '\\' in field_value and any(
                        seq in field_value for seq in ['\\260', '\\337', '\\366', '\\374', '\\344']
                    )
                    print(f"Contains escape sequences: {has_escapes}")
                    
                    # Character-by-character analysis for problematic characters
                    print(f"\nCharacter analysis:")
                    for i, char in enumerate(field_value):
                        if ord(char) > 127 or char == '\\':
                            print(f"  Pos {i}: '{char}' (code {ord(char)}, hex {hex(ord(char))})")
                    
                    # Check specific problematic substrings
                    if field_name == "10":
                        if "28" in field_value:
                            temp_part = field_value[field_value.find("28"):field_value.find("28")+10]
                            print(f"Temperature part: {repr(temp_part)}")
                        if "schlie" in field_value:
                            schlie_part = field_value[field_value.find("schlie"):field_value.find("schlie")+15]
                            print(f"'schlie' part: {repr(schlie_part)}")
                    
                    if field_name == "31":
                        if "gr" in field_value:
                            gr_part = field_value[field_value.find("gr"):field_value.find("gr")+10]
                            print(f"'gr' part: {repr(gr_part)}")
    
    print(f"\nTotal problematic fields found: {field_count}")
    doc.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python debug_field_values.py <pdf_file>")
        return
    
    pdf_file = sys.argv[1]
    
    if not os.path.exists(pdf_file):
        print(f"Error: File not found: {pdf_file}")
        return
    
    print("PYMUPDF FIELD VALUE DEBUGGER")
    print("=" * 50)
    
    debug_field_values(pdf_file)

if __name__ == "__main__":
    main() 