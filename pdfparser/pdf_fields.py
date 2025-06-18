import PyPDF2
import json
import base64
from collections import OrderedDict
import re

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

def clean_signature_field(field):
    """
    Clean signature field data for JSON serialization.
    Converts binary data to base64 and handles nested PDF objects.
    """
    if '/FT' in field and field['/FT'] == '/Sig' and '/V' in field:
        sig_value = field['/V']
        cleaned_sig = {}
        
        # Handle ByteRange
        if '/ByteRange' in sig_value:
            cleaned_sig['ByteRange'] = sig_value['/ByteRange']
            
        # Handle ContactInfo
        if '/ContactInfo' in sig_value:
            cleaned_sig['ContactInfo'] = str(sig_value['/ContactInfo'])
            
        # Handle Contents (binary data)
        if '/Contents' in sig_value:
            # Convert binary content to base64
            binary_content = sig_value['/Contents']
            if isinstance(binary_content, (bytes, PyPDF2.generic.ByteStringObject)):
                cleaned_sig['Contents'] = base64.b64encode(binary_content).decode('utf-8')
            else:
                cleaned_sig['Contents'] = str(binary_content)

        # Handle Filter
        if '/Filter' in sig_value:
            cleaned_sig['Filter'] = sig_value['/Filter']
        
        # Handle Location
        if '/Location' in sig_value:
            cleaned_sig['Location'] = sig_value['/Location']
        
        # Handle Timestamp
        if '/M' in sig_value:
            cleaned_sig['M'] = sig_value['/M']
            
        # Handle Name
        if '/Name' in sig_value:
            cleaned_sig['Name'] = sig_value['/Name']
            
        # Handle Reason
        if '/Reason' in sig_value:
            cleaned_sig['Reason'] = sig_value['/Reason']

        # Handle App
        if '/App' in sig_value:
            cleaned_sig['App'] = sig_value['/App']
            
        # Handle SubFilter
        if '/SubFilter' in sig_value:
            cleaned_sig['SubFilter'] = sig_value['/SubFilter']
                    
        # Replace original signature value with cleaned version
        field = field.copy()  # Create a copy to avoid modifying the original
        field['/V'] = cleaned_sig
        
    return field

def extract_form_fields(pdf_path, output_path):
    """
    Extract form fields from PDF and save to JSON, handling signature fields properly.
    Fields are sorted naturally by their keys.
    """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        form_fields = reader.get_fields()
        
        if form_fields:
            # Clean form fields and store in ordered dict
            cleaned_fields = OrderedDict()
            
            # Sort the field names using natural sort
            sorted_field_names = sorted(form_fields.keys(), key=natural_sort_key)
            
            # Process fields in sorted order
            for field_name in sorted_field_names:
                field_data = form_fields[field_name]
                # Remove /Kids entries
                if '/Kids' in field_data:
                    del field_data['/Kids']
                
                # Clean signature fields
                cleaned_field = clean_signature_field(field_data)
                cleaned_fields[field_name] = cleaned_field
            
            # Save to JSON
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json.dump(cleaned_fields, json_file, indent=4, ensure_ascii=False)
            
            return cleaned_fields
        return None

# Usage
pdf_path = r'030-2025_01044259_Freigabe.pdf'
output_path = 'form_fields.json'
form_fields = extract_form_fields(pdf_path, output_path)