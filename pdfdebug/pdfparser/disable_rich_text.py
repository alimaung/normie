#!/usr/bin/env python3
"""
Script to disable rich text formatting for specific PDF form fields.
This fixes text clipping issues caused by rich text formatting.
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

def disable_rich_text_fitz(input_path, output_path, target_fields=None):
    """
    Disable rich text formatting using PyMuPDF.
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
                
                # Process specific fields or all fields if none specified
                if target_fields is None or field_name in target_fields:
                    print(f"\nProcessing field: {field_name}")
                    
                    # Get the annotation object
                    annot = widget.parent
                    if annot:
                        # Check if field has rich text enabled
                        has_rich_text = False
                        
                        # Try to access the field's PDF object directly
                        try:
                            # Get field flags
                            flags = widget.field_flags
                            print(f"  Current flags: {flags}")
                            
                            # Rich text flag is bit 25 (0x2000000)
                            RICH_TEXT_FLAG = 0x2000000
                            if flags & RICH_TEXT_FLAG:
                                has_rich_text = True
                                print(f"  ✓ Rich text formatting is ENABLED")
                                
                                # Disable rich text by clearing the flag
                                new_flags = flags & ~RICH_TEXT_FLAG
                                print(f"  → Disabling rich text (new flags: {new_flags})")
                                
                                # Update the widget flags
                                widget.field_flags = new_flags
                                widget.update()
                                
                                fields_processed.append(field_name)
                            else:
                                print(f"  ✓ Rich text formatting is already disabled")
                        
                        except Exception as e:
                            print(f"  ✗ Error processing field flags: {e}")
        
        if fields_processed:
            print(f"\n✓ Successfully disabled rich text for {len(fields_processed)} fields:")
            for field in fields_processed:
                print(f"  - {field}")
            
            print(f"\nSaving to: {output_path}")
            doc.save(output_path)
            print("✓ PDF saved successfully")
        else:
            print("\n✓ No fields needed rich text formatting disabled")
            if input_path != output_path:
                print(f"Copying original to: {output_path}")
                doc.save(output_path)
    
    finally:
        doc.close()
    
    return fields_processed

def disable_rich_text_pypdf2(input_path, output_path, target_fields=None):
    """
    Disable rich text formatting using PyPDF2 (alternative method).
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
                        print(f"\nProcessing field: {field_name}")
                        
                        # Check for rich text indicators
                        has_rich_value = '/RV' in field_obj
                        
                        flags = field_obj.get('/Ff', 0)
                        RICH_TEXT_FLAG = 0x2000000  # Bit 25
                        has_rich_flag = bool(flags & RICH_TEXT_FLAG)
                        
                        print(f"  Has /RV (Rich Value): {has_rich_value}")
                        print(f"  Has rich text flag: {has_rich_flag}")
                        
                        if has_rich_value or has_rich_flag:
                            print(f"  ✓ Rich text formatting detected")
                            
                            # Remove /RV if present
                            if has_rich_value:
                                print(f"  → Removing /RV (Rich Value)")
                                del field_obj['/RV']
                            
                            # Clear rich text flag
                            if has_rich_flag:
                                new_flags = flags & ~RICH_TEXT_FLAG
                                print(f"  → Clearing rich text flag ({flags} → {new_flags})")
                                field_obj[PyPDF2.generic.NameObject('/Ff')] = PyPDF2.generic.NumberObject(new_flags)
                            
                            fields_processed.append(field_name)
                        else:
                            print(f"  ✓ No rich text formatting detected")
            
            # Save the modified PDF
            if fields_processed:
                print(f"\n✓ Successfully processed {len(fields_processed)} fields:")
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

def check_rich_text_status(pdf_path, target_fields=None):
    """
    Check which fields have rich text formatting enabled.
    """
    print(f"Checking rich text status in: {pdf_path}")
    print("=" * 60)
    
    doc = fitz.open(pdf_path)
    rich_text_fields = []
    
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                field_name = widget.field_name
                
                if target_fields is None or field_name in target_fields:
                    try:
                        flags = widget.field_flags
                        RICH_TEXT_FLAG = 0x2000000
                        has_rich_text = bool(flags & RICH_TEXT_FLAG)
                        
                        status = "ENABLED" if has_rich_text else "disabled"
                        print(f"Field '{field_name}': Rich text {status}")
                        
                        if has_rich_text:
                            rich_text_fields.append(field_name)
                    
                    except Exception as e:
                        print(f"Field '{field_name}': Error checking status - {e}")
    
    finally:
        doc.close()
    
    if rich_text_fields:
        print(f"\n✓ Found {len(rich_text_fields)} fields with rich text enabled:")
        for field in rich_text_fields:
            print(f"  - {field}")
    else:
        print(f"\n✓ No fields have rich text formatting enabled")
    
    return rich_text_fields

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Check status:    python disable_rich_text.py <pdf_file> [field1,field2,...]")
        print("  Disable rich text: python disable_rich_text.py <input.pdf> <output.pdf> [field1,field2,...]")
        print()
        print("Examples:")
        print("  python disable_rich_text.py document.pdf")
        print("  python disable_rich_text.py input.pdf output.pdf")
        print("  python disable_rich_text.py input.pdf output.pdf 10,31")
        return
    
    input_path = sys.argv[1]
    
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        return
    
    # Parse target fields if provided
    target_fields = None
    field_arg_index = 3 if len(sys.argv) > 2 and not sys.argv[2].endswith('.pdf') else 2
    
    if len(sys.argv) > field_arg_index:
        target_fields = [f.strip() for f in sys.argv[field_arg_index].split(',')]
        print(f"Target fields: {target_fields}")
    
    # Check if output path is provided
    if len(sys.argv) > 2 and sys.argv[2].endswith('.pdf'):
        output_path = sys.argv[2]
        
        print("DISABLING RICH TEXT FORMATTING")
        print("=" * 60)
        
        # First check current status
        rich_text_fields = check_rich_text_status(input_path, target_fields)
        
        if rich_text_fields:
            print(f"\nProceeding to disable rich text formatting...")
            
            # Try PyMuPDF first (more reliable)
            try:
                processed = disable_rich_text_fitz(input_path, output_path, target_fields)
                
                if processed:
                    print(f"\n✓ Rich text formatting disabled successfully!")
                    print(f"✓ Fixed file saved as: {output_path}")
                    
                    # Verify the fix
                    print(f"\nVerifying fix...")
                    remaining = check_rich_text_status(output_path, target_fields)
                    if not remaining:
                        print("✓ Verification successful - no rich text formatting detected")
                    else:
                        print(f"⚠ Warning: {len(remaining)} fields still have rich text enabled")
                
            except Exception as e:
                print(f"✗ PyMuPDF method failed: {e}")
                print("Trying PyPDF2 method...")
                processed = disable_rich_text_pypdf2(input_path, output_path, target_fields)
        else:
            print(f"No action needed - copying to output file...")
            if input_path != output_path:
                import shutil
                shutil.copy2(input_path, output_path)
                print(f"✓ File copied to: {output_path}")
    
    else:
        # Just check status
        print("CHECKING RICH TEXT STATUS")
        print("=" * 60)
        check_rich_text_status(input_path, target_fields)

if __name__ == "__main__":
    main() 