#!/usr/bin/env python3
"""
Fix line endings and refresh appearance streams to resolve text clipping.
"""

import sys
import os
import re
import fitz  # PyMuPDF

def fix_line_endings_in_pdf(input_file, output_file):
    """
    Fix line endings from \\n to \\r\\n in PDF objects and refresh appearance streams.
    """
    print(f"Reading PDF: {input_file}")
    
    try:
        with open(input_file, 'rb') as f:
            pdf_data = f.read()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return False
    
    print(f"Original PDF size: {len(pdf_data)} bytes")
    
    # Step 1: Fix line endings in PDF structure
    print("\nStep 1: Fixing line endings...")
    
    # Replace \n with \r\n in PDF structure (but be careful not to double up)
    # Look for patterns like "obj\n" and replace with "obj\r\n"
    modified_data = pdf_data
    
    # Fix object headers
    modified_data = re.sub(rb'(\d+\s+\d+\s+obj)\n', rb'\1\r\n', modified_data)
    
    # Count changes
    original_newlines = pdf_data.count(b'\n')
    modified_newlines = modified_data.count(b'\n')
    crlf_count = modified_data.count(b'\r\n')
    
    print(f"  Original \\n count: {original_newlines}")
    print(f"  Modified \\n count: {modified_newlines}")
    print(f"  CRLF (\\r\\n) count: {crlf_count}")
    
    # Step 2: Save intermediate file and use PyMuPDF to refresh fields
    temp_file = output_file.replace('.pdf', '_temp.pdf')
    
    try:
        with open(temp_file, 'wb') as f:
            f.write(modified_data)
        print(f"  Saved intermediate file: {temp_file}")
    except Exception as e:
        print(f"Error saving intermediate file: {e}")
        return False
    
    # Step 3: Use PyMuPDF to refresh appearance streams
    print("\nStep 2: Refreshing appearance streams with PyMuPDF...")
    
    try:
        doc = fitz.open(temp_file)
    except Exception as e:
        print(f"Error opening intermediate PDF: {e}")
        return False
    
    fields_refreshed = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        widgets = page.widgets()
        
        for widget in widgets:
            if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                field_name = widget.field_name
                
                # Focus on problematic fields
                if field_name in ["10", "31"]:
                    current_value = widget.field_value or ""
                    print(f"  Refreshing field '{field_name}' (length: {len(current_value)})")
                    
                    # Force refresh by setting the same value
                    # This triggers PyMuPDF to regenerate appearance streams
                    widget.field_value = current_value
                    widget.update()
                    fields_refreshed += 1
    
    print(f"  Fields refreshed: {fields_refreshed}")
    
    # Step 4: Save final file
    print(f"\nStep 3: Saving final PDF: {output_file}")
    
    try:
        doc.save(output_file)
        doc.close()
        
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"  Cleaned up temp file: {temp_file}")
        
        print("✅ PDF saved successfully!")
        return True
        
    except Exception as e:
        print(f"Error saving final PDF: {e}")
        doc.close()
        return False

def simulate_manual_edit(input_file, output_file):
    """
    Simulate the manual edit process that fixes the clipping.
    """
    print(f"Simulating manual edit process...")
    
    try:
        doc = fitz.open(input_file)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return False
    
    changes_made = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        widgets = page.widgets()
        
        for widget in widgets:
            if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                field_name = widget.field_name
                
                # Focus on problematic fields
                if field_name in ["10", "31"]:
                    current_value = widget.field_value or ""
                    print(f"  Processing field '{field_name}'...")
                    
                    # Simulate manual edit: add a character, then remove it
                    # This forces the PDF viewer to recalculate layout
                    temp_value = current_value + " "  # Add space
                    widget.field_value = temp_value
                    widget.update()
                    
                    # Remove the space (back to original)
                    widget.field_value = current_value
                    widget.update()
                    
                    changes_made += 1
                    print(f"    ✅ Simulated edit for field '{field_name}'")
    
    if changes_made > 0:
        print(f"\nSaving refreshed PDF: {output_file}")
        doc.save(output_file)
        print("✅ Manual edit simulation complete!")
    else:
        print("No fields found to refresh.")
    
    doc.close()
    return changes_made > 0

def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage: python fix_line_endings_and_refresh.py <input.pdf> [output.pdf]")
        print("If no output file is specified, '_fixed' will be added to the input filename.")
        return
    
    input_file = sys.argv[1]
    
    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    else:
        # Generate output filename
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_line_fixed{ext}"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
    
    print("PDF LINE ENDINGS & APPEARANCE STREAM FIXER")
    print("=" * 60)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    
    # Try the line endings fix first
    print("\n" + "="*60)
    print("METHOD 1: Fix line endings + refresh appearance streams")
    print("="*60)
    
    success1 = fix_line_endings_in_pdf(input_file, output_file.replace('.pdf', '_method1.pdf'))
    
    # Try the manual edit simulation
    print("\n" + "="*60)
    print("METHOD 2: Simulate manual edit process")
    print("="*60)
    
    success2 = simulate_manual_edit(input_file, output_file.replace('.pdf', '_method2.pdf'))
    
    if success1 or success2:
        print(f"\n🎉 One or both methods completed successfully!")
        print(f"Test the output files to see which method resolves the clipping issue.")
        if success1:
            print(f"  Method 1: {output_file.replace('.pdf', '_method1.pdf')}")
        if success2:
            print(f"  Method 2: {output_file.replace('.pdf', '_method2.pdf')}")
    else:
        print(f"\n❌ Both methods failed or made no changes.")

if __name__ == "__main__":
    main() 