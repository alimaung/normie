import os
import json
import PyPDF2
import base64
import re
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import datetime
import tempfile
import shutil

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

def natural_sort_key(s):
    """
    Create a key for natural sorting that handles numbers properly.
    Splits string into list of numeric and non-numeric parts.
    """
    def convert(text):
        # Convert number strings to integers for proper sorting
        return int(text) if text.isdigit() else text.lower()
    
    # Split string into numeric and non-numeric parts
    parts = re.split('([0-9]+)', str(s))
    return [convert(c) for c in parts]

def clean_value(value):
    """
    Clean value for JSON serialization.
    Handles various PyPDF2 object types.
    """
    if value is None:
        return ""
    elif isinstance(value, (PyPDF2.generic.ByteStringObject, bytes)):
        try:
            # Try to decode as UTF-8 first
            return value.decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            # If that fails, encode as base64
            if isinstance(value, bytes):
                return base64.b64encode(value).decode('utf-8')
            else:
                return base64.b64encode(value.original_bytes).decode('utf-8')
    elif isinstance(value, PyPDF2.generic.TextStringObject):
        return str(value)
    elif isinstance(value, PyPDF2.generic.NameObject):
        return str(value)
    elif isinstance(value, (int, float, bool)):
        return value
    elif isinstance(value, (list, tuple)):
        return [clean_value(item) for item in value]
    elif isinstance(value, dict):
        return {str(k): clean_value(v) for k, v in value.items()}
    else:
        return str(value)

def extract_pdf_fields(pdf_path):
    """
    Extract form fields from a PDF file.
    Returns a list of field objects with id, name, type, and value.
    Uses PyPDF2 for extraction (to get proper field descriptions) but PyMuPDF for saving.
    """
    # Use PyPDF2 for extraction to get proper field descriptions from /TU
    return extract_pdf_fields_pypdf2(pdf_path)

def extract_pdf_fields_fitz(pdf_path):
    """
    Extract form fields using PyMuPDF (fitz).
    More reliable for complex PDFs.
    """
    fields = []
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_name:  # Only include named fields
                    # Get field value
                    field_value = widget.field_value or ""
                    
                    # Convert PyMuPDF field type to PyPDF2-like format for consistency
                    field_type = "/Tx"  # Default to text
                    if widget.field_type_string in ['CheckBox', 'RadioButton']:
                        field_type = "/Btn"
                    elif widget.field_type_string == 'Signature':
                        field_type = "/Sig"
                    
                    # For now, use field_name as display name
                    # In the future, we could add a mapping dictionary
                    field_name = widget.field_name
                    
                    fields.append({
                        'id': widget.field_name,
                        'name': field_name,
                        'type': field_type,
                        'value': str(field_value)
                    })
        
        doc.close()
        
        # Sort fields naturally
        fields.sort(key=lambda x: natural_sort_key(x['id']))
        
    except Exception as e:
        print(f"Error extracting fields with PyMuPDF: {e}")
        raise e
    
    return fields

def extract_pdf_fields_pypdf2(pdf_path):
    """
    Extract form fields using PyPDF2 (fallback method).
    """
    fields = []
    
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Check if the PDF has form fields
        if reader.get_fields():
            # Get all form fields
            form_fields = reader.get_fields()
            
            # Process each field
            field_ids = sorted(form_fields.keys(), key=natural_sort_key)
            for field_id in field_ids:
                field = form_fields[field_id]
                
                # Get field type
                field_type = field.get('/FT', 'Unknown')
                
                # Get field value and clean it for JSON serialization
                raw_value = field.get('/V', '')
                field_value = clean_value(raw_value)
                
                # Get human-readable name from /TU (tooltip/description) or use field_id as fallback
                field_name = field.get('/TU', field_id)
                if field_name:
                    field_name = clean_value(field_name)
                else:
                    field_name = field_id
                
                # Add field to result
                fields.append({
                    'id': field_id,
                    'name': field_name,
                    'type': str(field_type),
                    'value': field_value
                })
    
    return fields

def remove_appearance_streams_from_pdf(pdf_path):
    """
    Remove appearance streams (/AP) from PDF text form fields to prevent text clipping.
    This forces PDF viewers to regenerate appearance streams with proper text layout.
    Preserves appearance streams for checkboxes, radio buttons, and signatures.
    
    Args:
        pdf_path: Path to the PDF file to fix
    
    Returns:
        bool: True if changes were made, False otherwise
    """
    try:
        # Read the PDF data
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        print(f"Removing appearance streams from text fields to fix text clipping...")
        
        # Find all form field objects with appearance streams - use a broader pattern first
        # Look for objects with /Type/Annot, /Subtype/Widget, and /AP
        form_field_ap_pattern = rb'/Type\s*/Annot[^>]*?/Subtype\s*/Widget[^>]*?/AP\s*(?:<<[^>]*>>|\d+\s+\d+\s+R)'
        
        matches = list(re.finditer(form_field_ap_pattern, pdf_data, re.DOTALL))
        
        if not matches:
            print("No form field appearance streams found")
            return False
        
        print(f"Found {len(matches)} form field objects with appearance streams")
        
        modified_data = pdf_data
        total_changes = 0
        text_fields_processed = 0
        other_fields_skipped = 0
        
        # Process each match to check if it's a text field and remove /AP entries
        for match in reversed(matches):  # Process in reverse to maintain positions
            # Find the object boundaries
            obj_start = pdf_data.rfind(b' obj', 0, match.start())
            if obj_start == -1:
                continue
                
            # Find the actual start of the object number
            obj_start = pdf_data.rfind(b'\n', 0, obj_start) + 1
            if obj_start == 0:
                obj_start = pdf_data.rfind(b'\r', 0, obj_start) + 1
            
            # Find the end of the object
            obj_end = pdf_data.find(b'endobj', match.end())
            if obj_end == -1:
                continue
            obj_end += len(b'endobj')
            
            # Extract the object data
            obj_data = pdf_data[obj_start:obj_end]
            
            try:
                obj_text = obj_data.decode('latin-1', errors='replace')
            except:
                continue
            
            # Check if this object has /AP entries
            if '/AP' not in obj_text:
                continue
            
            # Determine field type and decide whether to remove appearance streams
            is_text_field = '/FT/Tx' in obj_text
            is_button_field = '/FT/Btn' in obj_text
            is_signature_field = ('/Lock' in obj_text or '/SigFlags' in obj_text or 
                                'Signature' in obj_text or '/Type/Sig' in obj_text)
            
            # Only remove appearance streams from text fields
            if is_text_field and not is_signature_field:
                print(f"Processing text field object...")
                
                # Remove /AP entries using multiple patterns
                obj_text_modified = obj_text
                
                # Pattern 1: /AP<<...>> (nested dictionary) - more flexible matching
                ap_dict_pattern = r'/AP\s*<<(?:[^<>]|<<[^<>]*>>)*>>'
                obj_text_modified = re.sub(ap_dict_pattern, '', obj_text_modified, flags=re.DOTALL)
                
                # Pattern 2: /AP <reference> (object reference)
                ap_ref_pattern = r'/AP\s+\d+\s+\d+\s+R'
                obj_text_modified = re.sub(ap_ref_pattern, '', obj_text_modified)
                
                # Pattern 3: Remove any remaining /AP entries
                ap_simple_pattern = r'/AP[^\s/]*'
                obj_text_modified = re.sub(ap_simple_pattern, '', obj_text_modified)
                
                # Clean up any double spaces
                obj_text_modified = re.sub(r'\s+', ' ', obj_text_modified)
                
                if obj_text_modified != obj_text:
                    # Convert back to bytes and replace in the PDF data
                    try:
                        modified_obj_data = obj_text_modified.encode('latin-1')
                        modified_data = modified_data[:obj_start] + modified_obj_data + modified_data[obj_end:]
                        total_changes += 1
                        text_fields_processed += 1
                        print(f"  ✅ Removed appearance streams (size change: {len(obj_data)} -> {len(modified_obj_data)} bytes)")
                    except Exception as e:
                        print(f"  ❌ Error encoding modified object: {e}")
                else:
                    print(f"  ℹ️ No /AP entries found to remove")
            
            elif is_button_field:
                print(f"Skipping button field (checkbox/radio) - preserving appearance streams")
                other_fields_skipped += 1
            elif is_signature_field:
                print(f"Skipping signature field - preserving appearance streams")
                other_fields_skipped += 1
            else:
                print(f"Skipping unknown field type - preserving appearance streams")
                other_fields_skipped += 1
        
        if total_changes > 0:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_path = temp_file.name
            temp_file.close()
            
            try:
                # Write the modified data to temp file
                with open(temp_path, 'wb') as f:
                    f.write(modified_data)
                
                # Replace the original file
                shutil.move(temp_path, pdf_path)
                
                print(f"Successfully removed appearance streams from {text_fields_processed} text field objects")
                print(f"Preserved appearance streams for {other_fields_skipped} non-text field objects")
                return True
                
            except Exception as e:
                # Clean up temp file if it exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                print(f"Error saving modified PDF: {e}")
                return False
        else:
            print(f"No text field appearance streams were removed")
            print(f"Analyzed {text_fields_processed + other_fields_skipped} form field objects")
            return False
            
    except Exception as e:
        print(f"Error removing appearance streams: {e}")
        return False

def save_pdf_changes(template_path, fields):
    """
    Save changes back to the original PDF file.
    Uses PyMuPDF for reliable form field updates and removes appearance streams to prevent clipping.
    """
    # Use PyMuPDF approach directly - it's more reliable for preserving appearances
    if not FITZ_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) is required as fallback for PDF form editing. Install with: pip install PyMuPDF")
    
    try:
        # Open the PDF document with PyMuPDF
        doc = fitz.open(template_path)
        
        # Create a dictionary of field updates
        field_updates = {}
        for field in fields:
            field_id = field.get('id', '')
            field_value = field.get('value', '')
            if field_id:
                field_updates[field_id] = str(field_value)
        
        # Update form fields using PyMuPDF
        updated_count = 0
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_name in field_updates:
                    # Skip signature fields - don't update them
                    if widget.field_type_string == 'Signature':
                        print(f"Skipping signature field '{widget.field_name}' - preserving original")
                        continue
                        
                    new_value = field_updates[widget.field_name]
                    try:
                        # Handle different field types (same as standalone script)
                        if widget.field_type_string in ['Text', 'FreeText']:
                            widget.field_value = new_value
                        elif widget.field_type_string in ['CheckBox', 'RadioButton']:
                            # For checkboxes/radio buttons, handle boolean values
                            if new_value in ['/0', '/Yes', 'True', 'true', '1', True]:
                                widget.field_value = True
                            else:
                                widget.field_value = False
                        else:
                            # Default handling for other field types
                            widget.field_value = new_value
                        
                        widget.update()
                        updated_count += 1
                        print(f"Updated field '{widget.field_name}' to '{new_value}' on page {page_num + 1}")
                    except Exception as widget_error:
                        print(f"Error updating field '{widget.field_name}': {widget_error}")
        
        # Save the document using the same approach as the standalone script
        # Always use temporary file to avoid encryption/incremental save issues
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            # Save to temporary file first (like the standalone script)
            doc.save(temp_path)
            doc.close()
            
            # Replace original file with updated version
            shutil.move(temp_path, template_path)
            
            # IMPORTANT: Remove appearance streams to fix text clipping issues
            # This forces PDF viewers to regenerate appearance streams with proper text layout
            print("Applying text clipping fix...")
            remove_appearance_streams_from_pdf(template_path)
            
        except Exception as save_error:
            # Clean up temporary file if it exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
            doc.close()
            raise save_error
        
        print(f"Successfully updated {updated_count} fields in {template_path}")
        return template_path
        
    except Exception as e:
        print(f"Error saving PDF changes: {str(e)}")
        raise e

def generate_filled_pdf(template_path, fields, output_path=None, overwrite_original=False):
    """
    Generate a filled PDF form using the provided template and field values.
    
    Args:
        template_path: Path to the PDF template
        fields: List of field dictionaries with id, value, type
        output_path: Optional output path. If None, creates a temporary file
        overwrite_original: If True, saves changes back to the template_path
    """
    # If overwrite_original is True, save to the original file
    if overwrite_original:
        output_path = template_path
    
    # If no output path is provided, create a temporary file
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        output_path = temp_file.name
        temp_file.close()
    
    try:
        # Create a copy of the template
        with open(template_path, 'rb') as template_file:
            reader = PyPDF2.PdfReader(template_file)
            writer = PyPDF2.PdfWriter()
            
            # Add all pages from the template
            for page_num in range(len(reader.pages)):
                writer.add_page(reader.pages[page_num])
            
            # Prepare field values in a dictionary format for PyPDF2
            form_values = {}
            
            # Update form fields
            for i, field in enumerate(fields):
                try:
                    field_id = field.get('id', '')
                    field_value = field.get('value', '')
                    field_type = field.get('type', '/Tx')
                    
                    print(f"Processing field {i}: id={field_id}, type={field_type}, value={field_value}")
                    
                    # Skip empty field IDs
                    if not field_id:
                        continue
                    
                    # Handle different field types
                    if field_type == '/Btn':
                        # Button fields (checkboxes, radio buttons)
                        if field_value in ['/0', '/Yes', True, 'true', 'True']:
                            form_values[field_id] = '/0'
                        else:
                            form_values[field_id] = '/1'
                    elif field_type == '/Tx':
                        # Text fields
                        form_values[field_id] = str(field_value)
                    else:
                        # Default handling for other field types
                        form_values[field_id] = str(field_value)
                except Exception as field_error:
                    print(f"Error processing field {i}: {str(field_error)}")
                    print(f"Field data: {field}")
            
            # Update all form fields at once
            if form_values:
                try:
                    # Try to update all fields at once
                    writer.update_page_form_field_values(writer.pages[0], form_values)
                except Exception as e:
                    print(f"Error updating all fields at once: {str(e)}")
                    # Fall back to updating fields one by one
                    for field_id, field_value in form_values.items():
                        try:
                            writer.update_page_form_field_values(writer.pages[0], {field_id: field_value})
                        except Exception as field_e:
                            print(f"Error updating field {field_id}: {str(field_e)}")
            
            # Write the output PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        
        return output_path
    except Exception as e:
        # Log the error details for debugging
        print(f"Error in generate_filled_pdf: {str(e)}")
        print(f"Fields type: {type(fields)}")
        if not isinstance(fields, list):
            print(f"Fields is not a list: {fields}")
        else:
            print(f"Number of fields: {len(fields)}")
            for i, field in enumerate(fields):
                print(f"Field {i}: {type(field)} - {field}")
        raise e

def get_pdf_field_mapping(pdf_path):
    """
    Extract field IDs and their types from a PDF form.
    Useful for creating field mappings.
    """
    mapping = {}
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        form_fields = reader.get_fields()
        
        for field_id, field in form_fields.items():
            field_type = field.get('/FT', 'Unknown')
            mapping[field_id] = {
                'type': str(field_type),
                'name': field_id  # Default name is the ID
            }
    
    return mapping

def get_field_type_and_value(field):
    """
    Get the type and value of a PDF form field.
    """
    field_type = None
    field_value = None
    
    if '/FT' in field:
        field_type = field['/FT']
        
        if field_type == '/Tx' and '/V' in field:  # Text field
            field_value = field['/V']
        elif field_type == '/Btn' and '/V' in field:  # Button/checkbox/radio
            field_value = field['/V']
        elif field_type == '/Sig' and '/V' in field:  # Signature
            if '/Name' in field['/V']:
                field_value = field['/V']['Name']
            else:
                field_value = "Signature"
    
    return field_type, field_value

def get_field_metadata():
    """
    Return the metadata for PDF form fields.
    This maps field IDs to human-readable names and types.
    """
    # This is a simplified version - you might want to load this from a config file
    return {
        "1": {
            "name": "Antragsnummer",
            "type": "text",
        },
        "2a": {
            "name": "Antragsteller Name",
            "type": "text",
        },
        "2b": {
            "name": "Antragserstellungsdatum",
            "type": "text",
        },
        "2c": {
            "name": "Antragsteller Abteilung",
            "type": "text",
        },
        # Add more field definitions as needed
        # This is just a sample - you should include all fields from pdf_decode.py
    }

def fill_pdf_form(template_path, form_data):
    """
    Fill a PDF form with provided data.
    Returns a BytesIO object containing the filled PDF.
    """
    # This is a placeholder - actual PDF form filling is complex
    # For a real implementation, you might need to use a library like pdftk or a PDF API service
    
    # For now, we'll just create a simple PDF with the form data
    buffer = BytesIO()
    
    # Create the PDF
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica", 12)
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Form Data")
    c.setFont("Helvetica", 12)
    
    # Add form data
    y = 750
    for field_id, value in form_data.items():
        metadata = get_field_metadata().get(field_id, {})
        field_name = metadata.get("name", field_id)
        
        c.drawString(50, y, f"{field_name} ({field_id}): {value}")
        y -= 20
        
        if y < 50:  # Start a new page if we run out of space
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 800
    
    c.save()
    buffer.seek(0)
    return buffer

def get_signature_details(pdf_path):
    """
    Extract detailed signature information from PDF using PyMuPDF.
    Returns a dictionary with signature details for each signature field.
    """
    signature_details = {}
    
    if not FITZ_AVAILABLE:
        return signature_details
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_name and widget.field_type_string == 'Signature':
                    sig_info = {
                        'field_name': widget.field_name,
                        'page': page_num + 1,
                        'signed': False,
                        'signer_name': '',
                        'sign_date': '',
                        'reason': '',
                        'location': '',
                        'contact_info': ''
                    }
                    
                    # Check if signature is actually signed
                    if widget.field_value:
                        sig_info['signed'] = True
                        
                        # Try to extract signature details
                        try:
                            # Get signature annotation if available
                            annots = page.annots()
                            for annot in annots:
                                if annot.type[1] == 'Widget' and hasattr(annot, 'widget'):
                                    if annot.widget.field_name == widget.field_name:
                                        # Try to get signature dictionary
                                        sig_dict = annot.get_signature()
                                        if sig_dict:
                                            sig_info['signer_name'] = sig_dict.get('name', '')
                                            sig_info['sign_date'] = sig_dict.get('date', '')
                                            sig_info['reason'] = sig_dict.get('reason', '')
                                            sig_info['location'] = sig_dict.get('location', '')
                                            sig_info['contact_info'] = sig_dict.get('contact_info', '')
                        except Exception as sig_error:
                            print(f"Could not extract signature details for {widget.field_name}: {sig_error}")
                    
                    signature_details[widget.field_name] = sig_info
        
        doc.close()
        
    except Exception as e:
        print(f"Error extracting signature details: {e}")
    
    return signature_details

def save_pdf_changes_pypdf2_fixed(template_path, fields):
    """
    Save changes using PyPDF2 with appearance dictionary fix to prevent text clipping.
    This approach removes the Normal appearance that causes text clipping issues.
    """
    try:
        # Create a temporary file for the updated PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_path = temp_file.name
        temp_file.close()
        
        # Create a copy of the template
        with open(template_path, 'rb') as template_file:
            reader = PyPDF2.PdfReader(template_file)
            writer = PyPDF2.PdfWriter()
            
            # Add all pages from the template
            for page_num in range(len(reader.pages)):
                writer.add_page(reader.pages[page_num])
            
            # Prepare field values in a dictionary format for PyPDF2
            form_values = {}
            
            # Update form fields
            for field in fields:
                field_id = field.get('id', '')
                field_value = field.get('value', '')
                field_type = field.get('type', '/Tx')
                
                # Skip empty field IDs
                if not field_id:
                    continue
                
                # Handle different field types
                if field_type == '/Btn':
                    # Button fields (checkboxes, radio buttons)
                    if field_value in ['/0', '/Yes', True, 'true', 'True']:
                        form_values[field_id] = '/0'
                    else:
                        form_values[field_id] = '/1'
                elif field_type == '/Tx':
                    # Text fields
                    form_values[field_id] = str(field_value)
                else:
                    # Default handling for other field types
                    form_values[field_id] = str(field_value)
            
            # Update all form fields at once
            if form_values:
                for page in writer.pages:
                    try:
                        writer.update_page_form_field_values(page, form_values)
                        
                        # Alternative approach: Set need_appearances flag to let PDF viewer handle rendering
                        # This tells the PDF viewer to generate appearances dynamically
                        if hasattr(writer, '_root_object') and writer._root_object:
                            acro_form = writer._root_object.get('/AcroForm')
                            if acro_form:
                                acro_form_obj = acro_form.get_object()
                                # Set NeedAppearances to True - this tells PDF viewers to generate appearances
                                acro_form_obj[PyPDF2.generic.NameObject('/NeedAppearances')] = PyPDF2.generic.BooleanObject(True)
                                print("Set NeedAppearances flag to True")
                    except Exception as page_error:
                        print(f"Error updating page: {page_error}")
            
            # Write the output PDF
            with open(temp_path, 'wb') as output_file:
                writer.write(output_file)
        
        # Replace original file with updated version
        shutil.move(temp_path, template_path)
        
        print(f"Successfully updated fields using PyPDF2 with appearance fix")
        return template_path
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"Error in PyPDF2 save with appearance fix: {str(e)}")
        raise e
