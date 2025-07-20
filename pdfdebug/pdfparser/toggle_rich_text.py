#!/usr/bin/env python3
"""
Script to enable, disable, or reset rich text formatting for PDF form fields.
This can fix text clipping issues by completely resetting rich text state.
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

def toggle_rich_text_pypdf2(input_path, output_path, action, target_fields=None):
    """
    Toggle rich text formatting using PyPDF2 for deeper control.
    action: 'enable', 'disable', or 'reset'
    """
    if not PYPDF2_AVAILABLE:
        print("PyPDF2 not available")
        return []
    
    print(f"Using PyPDF2 method to {action} rich text...")
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
                        
                        # Check current state
                        has_rich_value = '/RV' in field_obj
                        flags = field_obj.get('/Ff', 0)
                        RICH_TEXT_FLAG = 0x2000000  # Bit 25
                        has_rich_flag = bool(flags & RICH_TEXT_FLAG)
                        
                        print(f"  Current state:")
                        print(f"    Has /RV (Rich Value): {has_rich_value}")
                        print(f"    Has rich text flag: {has_rich_flag}")
                        print(f"    Current flags: {flags} (0x{flags:x})")
                        
                        if action == 'enable':
                            print(f"  → Enabling rich text formatting")
                            
                            # Set rich text flag
                            new_flags = flags | RICH_TEXT_FLAG
                            field_obj[PyPDF2.generic.NameObject('/Ff')] = PyPDF2.generic.NumberObject(new_flags)
                            print(f"    Set flags to: {new_flags} (0x{new_flags:x})")
                            
                            # Add rich value if not present (copy from regular value)
                            if not has_rich_value and '/V' in field_obj:
                                rich_value = field_obj['/V']
                                field_obj[PyPDF2.generic.NameObject('/RV')] = rich_value
                                print(f"    Added /RV: {rich_value}")
                            
                            fields_processed.append(field_name)
                        
                        elif action == 'disable':
                            print(f"  → Disabling rich text formatting")
                            
                            # Clear rich text flag
                            new_flags = flags & ~RICH_TEXT_FLAG
                            field_obj[PyPDF2.generic.NameObject('/Ff')] = PyPDF2.generic.NumberObject(new_flags)
                            print(f"    Set flags to: {new_flags} (0x{new_flags:x})")
                            
                            # Remove /RV if present
                            if has_rich_value:
                                del field_obj['/RV']
                                print(f"    Removed /RV")
                            
                            fields_processed.append(field_name)
                        
                        elif action == 'reset':
                            print(f"  → Resetting rich text formatting (enable then disable)")
                            
                            # First enable
                            new_flags = flags | RICH_TEXT_FLAG
                            field_obj[PyPDF2.generic.NameObject('/Ff')] = PyPDF2.generic.NumberObject(new_flags)
                            
                            # Add rich value
                            if '/V' in field_obj:
                                rich_value = field_obj['/V']
                                field_obj[PyPDF2.generic.NameObject('/RV')] = rich_value
                                print(f"    Temporarily enabled rich text")
                            
                            # Then disable
                            new_flags = new_flags & ~RICH_TEXT_FLAG
                            field_obj[PyPDF2.generic.NameObject('/Ff')] = PyPDF2.generic.NumberObject(new_flags)
                            
                            # Remove /RV
                            if '/RV' in field_obj:
                                del field_obj['/RV']
                            
                            # Also remove any appearance dictionaries that might cause issues
                            if '/AP' in field_obj:
                                print(f"    Removing appearance dictionary")
                                del field_obj['/AP']
                            
                            print(f"    Reset complete - final flags: {new_flags} (0x{new_flags:x})")
                            fields_processed.append(field_name)
            
            # Save the modified PDF
            print(f"\nSaving to: {output_path}")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            print("✓ PDF saved successfully")
    
    except Exception as e:
        print(f"✗ Error with PyPDF2 method: {e}")
        return []
    
    return fields_processed

def check_detailed_rich_text_status(pdf_path, target_fields=None):
    """
    Check detailed rich text status including all related properties.
    """
    print(f"Checking detailed rich text status in: {pdf_path}")
    print("=" * 80)
    
    # Check with PyMuPDF
    print("\nPyMuPDF Analysis:")
    print("-" * 40)
    doc = fitz.open(pdf_path)
    fitz_results = {}
    
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
                        
                        fitz_results[field_name] = {
                            'flags': flags,
                            'rich_text_flag': has_rich_text,
                            'field_value': str(widget.field_value or ''),
                            'field_type': widget.field_type_string
                        }
                        
                        status = "ENABLED" if has_rich_text else "disabled"
                        print(f"Field '{field_name}': Rich text {status} (flags: {flags}, 0x{flags:x})")
                    
                    except Exception as e:
                        print(f"Field '{field_name}': Error - {e}")
    
    finally:
        doc.close()
    
    # Check with PyPDF2 for more details
    if PYPDF2_AVAILABLE:
        print("\nPyPDF2 Analysis:")
        print("-" * 40)
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                if reader.get_fields():
                    for field_name, field_obj in reader.get_fields().items():
                        if target_fields is None or field_name in target_fields:
                            has_rich_value = '/RV' in field_obj
                            has_appearance = '/AP' in field_obj
                            flags = field_obj.get('/Ff', 0)
                            RICH_TEXT_FLAG = 0x2000000
                            has_rich_flag = bool(flags & RICH_TEXT_FLAG)
                            
                            print(f"Field '{field_name}':")
                            print(f"  Flags: {flags} (0x{flags:x})")
                            print(f"  Rich text flag: {has_rich_flag}")
                            print(f"  Has /RV: {has_rich_value}")
                            print(f"  Has /AP: {has_appearance}")
                            print(f"  Value: {field_obj.get('/V', 'None')}")
                            if has_rich_value:
                                print(f"  Rich Value: {field_obj.get('/RV', 'None')}")
                            
                            # Check for other potentially problematic properties
                            problematic_keys = ['/DA', '/Q', '/MaxLen']
                            for key in problematic_keys:
                                if key in field_obj:
                                    print(f"  {key}: {field_obj[key]}")
                            
                            print()
        
        except Exception as e:
            print(f"Error with PyPDF2 analysis: {e}")
    
    return fitz_results

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Check status:  python toggle_rich_text.py <pdf_file> [field1,field2,...]")
        print("  Enable:        python toggle_rich_text.py <input.pdf> <output.pdf> enable [field1,field2,...]")
        print("  Disable:       python toggle_rich_text.py <input.pdf> <output.pdf> disable [field1,field2,...]")
        print("  Reset:         python toggle_rich_text.py <input.pdf> <output.pdf> reset [field1,field2,...]")
        print()
        print("Examples:")
        print("  python toggle_rich_text.py document.pdf")
        print("  python toggle_rich_text.py input.pdf output.pdf reset")
        print("  python toggle_rich_text.py input.pdf output.pdf reset 10,31")
        print("  python toggle_rich_text.py input.pdf output.pdf disable 10,31")
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
        
        print("CHECKING DETAILED RICH TEXT STATUS")
        print("=" * 80)
        check_detailed_rich_text_status(input_path, target_fields)
        return
    
    # Parse arguments for action
    if len(sys.argv) < 4:
        print("Error: Action required (enable/disable/reset)")
        return
    
    output_path = sys.argv[2]
    action = sys.argv[3].lower()
    
    if action not in ['enable', 'disable', 'reset']:
        print(f"Error: Invalid action '{action}'. Use: enable, disable, or reset")
        return
    
    # Parse target fields if provided
    target_fields = None
    if len(sys.argv) > 4:
        target_fields = [f.strip() for f in sys.argv[4].split(',')]
        print(f"Target fields: {target_fields}")
    
    print(f"RICH TEXT FORMATTING - {action.upper()}")
    print("=" * 80)
    
    # Check current status first
    print("Current status:")
    check_detailed_rich_text_status(input_path, target_fields)
    
    # Perform the action
    print(f"\nProceeding to {action} rich text formatting...")
    processed = toggle_rich_text_pypdf2(input_path, output_path, action, target_fields)
    
    if processed:
        print(f"\n✓ Successfully {action}d rich text for {len(processed)} fields:")
        for field in processed:
            print(f"  - {field}")
        
        print(f"✓ File saved as: {output_path}")
        
        # Verify the result
        print(f"\nVerifying result...")
        check_detailed_rich_text_status(output_path, target_fields)
    else:
        print(f"\n⚠ No fields were processed")

if __name__ == "__main__":
    main() 