#!/usr/bin/env python3
"""
Script to refresh PDF text fields by adding and removing characters.
This simulates manual editing to force regeneration of field display and fix clipping.
"""

import sys
import os
try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    print("Error: PyMuPDF is required for this script")
    print("Install with: pip install PyMuPDF")
    sys.exit(1)

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("Warning: PyPDF2 not available, using PyMuPDF only")

def refresh_fields_fitz(input_path, output_path, target_fields=None, refresh_method="newline"):
    """
    Refresh text fields using PyMuPDF by temporarily modifying field values.
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
                    print(f"  Original value length: {len(original_value)}")
                    print(f"  Original value preview: {original_value[:50]}...")
                    
                    try:
                        if refresh_method == "newline":
                            # Method 1: Add newline, then remove it
                            print(f"  → Adding newline to refresh field display")
                            temp_value = original_value + "\n"
                            widget.field_value = temp_value
                            widget.update()
                            
                            print(f"  → Removing newline to restore original content")
                            widget.field_value = original_value
                            widget.update()
                        
                        elif refresh_method == "space":
                            # Method 2: Add space, then remove it
                            print(f"  → Adding space to refresh field display")
                            temp_value = original_value + " "
                            widget.field_value = temp_value
                            widget.update()
                            
                            print(f"  → Removing space to restore original content")
                            widget.field_value = original_value
                            widget.update()
                        
                        elif refresh_method == "rewrite":
                            # Method 3: Clear and rewrite the entire value
                            print(f"  → Clearing field to refresh display")
                            widget.field_value = ""
                            widget.update()
                            
                            print(f"  → Restoring original content")
                            widget.field_value = original_value
                            widget.update()
                        
                        elif refresh_method == "trim":
                            # Method 4: Trim whitespace and restore (often fixes formatting)
                            print(f"  → Trimming whitespace to refresh formatting")
                            trimmed_value = original_value.strip()
                            widget.field_value = trimmed_value
                            widget.update()
                            
                            if trimmed_value != original_value:
                                print(f"  → Whitespace was trimmed (length: {len(original_value)} → {len(trimmed_value)})")
                        
                        fields_processed.append(field_name)
                        print(f"  ✓ Field refreshed successfully")
                        
                    except Exception as e:
                        print(f"  ✗ Error refreshing field: {e}")
        
        if fields_processed:
            print(f"\n✓ Successfully refreshed {len(fields_processed)} fields:")
            for field in fields_processed:
                print(f"  - {field}")
            
            print(f"\nSaving to: {output_path}")
            doc.save(output_path)
            print("✓ PDF saved successfully")
        else:
            print("\n✓ No fields needed refreshing")
            if input_path != output_path:
                print(f"Copying original to: {output_path}")
                doc.save(output_path)
    
    finally:
        doc.close()
    
    return fields_processed

def refresh_fields_pypdf2(input_path, output_path, target_fields=None, refresh_method="newline"):
    """
    Refresh text fields using PyPDF2 by temporarily modifying field values.
    """
    if not PYPDF2_AVAILABLE:
        print("PyPDF2 not available")
        return []
    
    print(f"Using PyPDF2 method...")
    print(f"Opening PDF: {input_path}")
    
    fields_processed = []
    
    try:
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # Copy all pages
            for page in reader.pages:
                writer.add_page(page)
            
            # Process form fields
            if reader.get_fields():
                for field_name, field_obj in reader.get_fields().items():
                    if target_fields is None or field_name in target_fields:
                        # Only process text fields
                        field_type = field_obj.get('/FT', '')
                        if field_type == '/Tx':  # Text field
                            print(f"\nProcessing field: {field_name}")
                            
                            original_value = str(field_obj.get('/V', ''))
                            print(f"  Original value length: {len(original_value)}")
                            print(f"  Original value preview: {original_value[:50]}...")
                            
                            try:
                                if refresh_method == "newline":
                                    # Add newline then remove it (simulates manual edit)
                                    temp_value = original_value + "\n"
                                    # In PyPDF2, we just set the final cleaned value
                                    final_value = original_value
                                
                                elif refresh_method == "space":
                                    # Add space then remove it
                                    final_value = original_value
                                
                                elif refresh_method == "rewrite":
                                    # Just rewrite the value (forces regeneration)
                                    final_value = original_value
                                
                                elif refresh_method == "trim":
                                    # Trim whitespace
                                    final_value = original_value.strip()
                                    if final_value != original_value:
                                        print(f"  → Trimmed whitespace (length: {len(original_value)} → {len(final_value)})")
                                
                                # Update the field value
                                field_obj[PyPDF2.generic.NameObject('/V')] = PyPDF2.generic.TextStringObject(final_value)
                                
                                # Remove any appearance dictionaries to force regeneration
                                if '/AP' in field_obj:
                                    print(f"  → Removing appearance dictionary to force regeneration")
                                    del field_obj['/AP']
                                
                                fields_processed.append(field_name)
                                print(f"  ✓ Field refreshed successfully")
                                
                            except Exception as e:
                                print(f"  ✗ Error refreshing field: {e}")
            
            # Save the modified PDF
            if fields_processed:
                print(f"\n✓ Successfully refreshed {len(fields_processed)} fields:")
                for field in fields_processed:
                    print(f"  - {field}")
            
            print(f"\nSaving to: {output_path}")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            print("✓ PDF saved successfully")
    
    except Exception as e:
        print(f"✗ Error with PyPDF2 method: {e}")
        return []
    
    return fields_processed

def check_field_values(pdf_path, target_fields=None):
    """
    Check current field values and their properties.
    """
    print(f"Checking field values in: {pdf_path}")
    print("=" * 60)
    
    doc = fitz.open(pdf_path)
    field_info = {}
    
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                field_name = widget.field_name
                
                if target_fields is None or field_name in target_fields:
                    if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                        field_value = str(widget.field_value or '')
                        
                        field_info[field_name] = {
                            'value_length': len(field_value),
                            'has_newlines': '\n' in field_value,
                            'has_trailing_whitespace': field_value != field_value.strip(),
                            'starts_with_whitespace': field_value.startswith((' ', '\t', '\n')),
                            'ends_with_whitespace': field_value.endswith((' ', '\t', '\n')),
                            'field_type': widget.field_type_string,
                            'flags': widget.field_flags
                        }
                        
                        print(f"Field '{field_name}':")
                        print(f"  Value length: {len(field_value)}")
                        print(f"  Has newlines: {'\n' in field_value}")
                        print(f"  Has trailing whitespace: {field_value != field_value.strip()}")
                        print(f"  Preview: {field_value[:100]}...")
                        if len(field_value) > 100:
                            print(f"  Ending: ...{field_value[-50:]}")
                        print()
    
    finally:
        doc.close()
    
    return field_info

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Check values:  python refresh_text_fields.py <pdf_file> [field1,field2,...]")
        print("  Refresh:       python refresh_text_fields.py <input.pdf> <output.pdf> [method] [field1,field2,...]")
        print()
        print("Methods:")
        print("  newline  - Add and remove newline (default, simulates manual edit)")
        print("  space    - Add and remove space")
        print("  rewrite  - Clear and rewrite field content")
        print("  trim     - Trim whitespace from field values")
        print()
        print("Examples:")
        print("  python refresh_text_fields.py document.pdf 10,31")
        print("  python refresh_text_fields.py input.pdf output.pdf")
        print("  python refresh_text_fields.py input.pdf output.pdf newline 10,31")
        print("  python refresh_text_fields.py input.pdf output.pdf trim 10,31")
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
        
        print("CHECKING FIELD VALUES")
        print("=" * 60)
        check_field_values(input_path, target_fields)
        return
    
    # Parse arguments for refresh
    output_path = sys.argv[2]
    refresh_method = "newline"  # default
    target_fields = None
    
    # Parse method and fields
    if len(sys.argv) > 3:
        if sys.argv[3] in ['newline', 'space', 'rewrite', 'trim']:
            refresh_method = sys.argv[3]
            if len(sys.argv) > 4:
                target_fields = [f.strip() for f in sys.argv[4].split(',')]
        else:
            # No method specified, this must be fields
            target_fields = [f.strip() for f in sys.argv[3].split(',')]
    
    if target_fields:
        print(f"Target fields: {target_fields}")
    print(f"Refresh method: {refresh_method}")
    
    print(f"TEXT FIELD REFRESH - {refresh_method.upper()}")
    print("=" * 60)
    
    # Check current values first
    print("Current field values:")
    check_field_values(input_path, target_fields)
    
    # Perform the refresh
    print(f"\nProceeding to refresh fields using '{refresh_method}' method...")
    
    # Try PyMuPDF first (more reliable for field manipulation)
    try:
        processed = refresh_fields_fitz(input_path, output_path, target_fields, refresh_method)
        
        if processed:
            print(f"\n✓ Text field refresh completed successfully!")
            print(f"✓ Refreshed file saved as: {output_path}")
            
            # Verify the result
            print(f"\nVerifying result...")
            check_field_values(output_path, target_fields)
        
    except Exception as e:
        print(f"✗ PyMuPDF method failed: {e}")
        print("Trying PyPDF2 method...")
        processed = refresh_fields_pypdf2(input_path, output_path, target_fields, refresh_method)

if __name__ == "__main__":
    main() 