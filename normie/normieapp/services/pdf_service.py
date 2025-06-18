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
    """
    fields = []
    
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Check if the PDF has form fields
        if reader.get_fields():
            # Get all form fields
            form_fields = reader.get_fields()
            
            # Create a dictionary of field mappings (from field ID to human-readable name)
            field_mappings = {
                # Common field mappings for your PDF forms
                # This can be expanded based on your PDF templates
                "1": "Application Type",
                "2": "Application Number",
                "3": "Date",
                "4": "Product Name",
                "5": "Manufacturer",
                "6": "Part Number",
                "7": "Material Type",
                "8": "Description",
                "9": "Usage",
                "10": "Department",
                "11": "Location",
                "12": "Applicant",
                "13": "Phone",
                "14": "Email",
                # Add more mappings as needed
            }
            
            # Process each field
            field_ids = sorted(form_fields.keys(), key=natural_sort_key)
            for field_id in field_ids:
                field = form_fields[field_id]
                
                # Get field type
                field_type = field.get('/FT', 'Unknown')
                
                # Get field value and clean it for JSON serialization
                raw_value = field.get('/V', '')
                field_value = clean_value(raw_value)
                
                # Get human-readable name from mappings or use field_id
                field_name = field_mappings.get(field_id, field_id)
                
                # Add field to result
                fields.append({
                    'id': field_id,
                    'name': field_name,
                    'type': str(field_type),
                    'value': field_value
                })
    
    return fields

def generate_filled_pdf(template_path, fields, output_path=None):
    """
    Generate a filled PDF form using the provided template and field values.
    """
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
