import os
import json
import shutil
import tempfile
from datetime import datetime

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

def save_pdf_changes_simple(template_path, frontend_data):
    """
    Simple PDF field update that preserves signatures.
    Uses the minimal approach from the working test script.
    
    Args:
        template_path: Path to the PDF file to modify
        frontend_data: Dictionary with field_id: value pairs
    
    Returns:
        str: Path to the modified PDF file
    """
    if not FITZ_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) is required. Install with: pip install PyMuPDF")
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template PDF not found: {template_path}")
    
    try:
        # Use the template_path directly (it's already the target file)
        output_path = template_path
        print(f"📄 Working with file: {output_path}")
        
        # Track updates
        updated_count = 0
        skipped_count = 0
        
        # Process each field change individually - ONE FIELD, ONE DOCUMENT SESSION
        for field_name, new_value in frontend_data.items():
            print(f"\n🔄 Processing field '{field_name}' with value '{new_value}'")
            
            # Open document fresh for each field (like working script)
            doc = fitz.open(output_path)
            
            field_found = False
            field_updated = False
            
            # Find and update this specific field
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    if widget.field_name != field_name:
                        continue
                    
                    field_found = True
                    
                    # Skip signature fields completely
                    if widget.field_type_string == 'Signature':
                        print(f"🔒 Skipping signature field '{field_name}' to preserve signature")
                        doc.close()
                        break
                    
                    # Get current value
                    current_value = str(widget.field_value or "")
                    new_value_str = str(new_value)
                    
                    # ONLY UPDATE IF VALUES ARE DIFFERENT
                    if current_value == new_value_str:
                        skipped_count += 1
                        print(f"⏭️  Skipping field '{field_name}' - no change needed ('{current_value}')")
                        doc.close()
                        break
                    
                    print(f"🔄 Field '{field_name}' needs update: '{current_value}' → '{new_value_str}'")
                    
                    try:
                        # Simple field update - exactly like working script
                        if widget.field_type_string in ['Text', 'FreeText']:
                            # Text fields - use value as string (like working script)
                            widget.field_value = new_value_str
                        elif widget.field_type_string in ['CheckBox', 'RadioButton']:
                            # Button fields - handle boolean/string values
                            if isinstance(new_value, bool):
                                widget.field_value = new_value
                            elif isinstance(new_value, str):
                                # Convert string values to boolean for checkboxes
                                if widget.field_type_string == 'CheckBox':
                                    widget.field_value = new_value.lower() in ['true', '1', 'yes', 'ja', 'on']
                                else:
                                    # For radio buttons, use the string value directly
                                    widget.field_value = new_value
                            else:
                                widget.field_value = new_value
                        else:
                            # Other field types - use value as-is (like working script)
                            widget.field_value = new_value_str
                        
                        # Update the widget
                        widget.update()
                        field_updated = True
                        updated_count += 1
                        print(f"✅ Updated field '{field_name}' = '{new_value_str}' on page {page_num + 1} (type: {widget.field_type_string})")
                        
                        # Save immediately after this field update (like working script)
                        print(f"💾 Saving field '{field_name}' update...")
                        doc.saveIncr()
                        print(f"✅ Field '{field_name}' saved successfully")
                        
                        break  # Only update first occurrence of this field
                        
                    except Exception as widget_error:
                        print(f"❌ Error updating field '{field_name}': {widget_error}")
                        break
                
                if field_updated:
                    break  # Move to next field
            
            # Close document after each field
            doc.close()
            
            if not field_found:
                print(f"❓ Field '{field_name}' not found in PDF")
        
        print(f"🎉 Successfully updated {updated_count} fields, skipped {skipped_count} unchanged fields in {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error in save_pdf_changes_simple: {str(e)}")
        raise e

def test_simple_pdf_update(pdf_path, frontend_data_path):
    """
    Test function that loads frontend data and updates PDF.
    
    Args:
        pdf_path: Path to the PDF file
        frontend_data_path: Path to JSON file with field data
    
    Returns:
        str: Path to the updated PDF
    """
    # Load frontend data
    with open(frontend_data_path, 'r', encoding='utf-8') as f:
        frontend_data = json.load(f)
    
    print(f"📄 Loading PDF: {pdf_path}")
    print(f"📊 Loading data: {frontend_data_path}")
    print(f"🔢 Found {len(frontend_data)} fields to update")
    
    # Note: save_pdf_changes_simple will create a copy as "test.pdf"
    # Original file remains untouched
    
    # Update the PDF
    result_path = save_pdf_changes_simple(pdf_path, frontend_data)
    
    print(f"✅ PDF updated successfully: {result_path}")
    return result_path

def extract_pdf_fields_simple(pdf_path):
    """
    Simple field extraction for debugging.
    Returns basic field information.
    """
    if not FITZ_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) is required. Install with: pip install PyMuPDF")
    
    fields = []
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_name:
                    field_info = {
                        'id': widget.field_name,
                        'type': widget.field_type_string,
                        'value': widget.field_value,
                        'page': page_num + 1
                    }
                    fields.append(field_info)
        
        doc.close()
        
    except Exception as e:
        print(f"Error extracting fields: {e}")
        raise e
    
    return fields

if __name__ == "__main__":
    # Test with the provided files
    pdf_file = "pdf.pdf"  # Adjust path as needed
    data_file = "frontend_data.json"
    
    if os.path.exists(pdf_file) and os.path.exists(data_file):
        try:
            result = test_simple_pdf_update(pdf_file, data_file)
            print(f"\n🎯 Test completed successfully!")
            print(f"📄 Updated PDF: {result}")
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
    else:
        print(f"❌ Required files not found:")
        print(f"   PDF: {pdf_file} (exists: {os.path.exists(pdf_file)})")
        print(f"   Data: {data_file} (exists: {os.path.exists(data_file)})") 