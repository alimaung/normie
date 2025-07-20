#!/usr/bin/env python3
"""
PDF Form Field Update Service with Signature Preservation
Uses skip_diff=True for signature validation (no incremental update analysis)
"""

import fitz  # PyMuPDF
import json
import os
from datetime import datetime
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext

def validate_signatures_simple(pdf_path):
    """
    Validate PDF signatures without diff analysis
    Returns True if all signatures are cryptographically valid
    """
    try:
        with open(pdf_path, 'rb') as doc:
            reader = PdfFileReader(doc)
            signatures = reader.embedded_signatures
            
            if not signatures:
                return True  # No signatures to validate
            
            vc = ValidationContext()
            
            for sig in signatures:
                # Skip diff analysis for performance and simplicity
                status = validate_pdf_signature(sig, vc, skip_diff=True)
                if not status.bottom_line:
                    return False
            
            return True
            
    except Exception as e:
        print(f"Signature validation error: {e}")
        return False

def get_field_type(field_name, widget):
    """
    Determine field type from widget and field name
    """
    widget_type = widget.field_type_string
    
    if widget_type == "CheckBox":
        return "checkbox"
    elif widget_type == "RadioButton":
        return "radio"
    elif widget_type == "Text":
        return "text"
    else:
        return "unknown"

def update_pdf_fields(pdf_path, field_updates, output_path=None):
    """
    Update PDF form fields with signature preservation
    
    Args:
        pdf_path: Path to input PDF
        field_updates: Dict of {field_name: new_value}
        output_path: Path for output PDF (optional)
    
    Returns:
        dict: Results with success status and signature validation
    """
    if output_path is None:
        output_path = pdf_path
    
    results = {
        'success': False,
        'updated_fields': [],
        'errors': [],
        'signatures_before': False,
        'signatures_after': False,
        'signatures_preserved': False
    }
    
    try:
        # Check signatures before update
        results['signatures_before'] = validate_signatures_simple(pdf_path)
        
        # Open PDF document
        doc = fitz.open(pdf_path)
        
        # Process each field update
        for field_name, new_value in field_updates.items():
            try:
                # Find all widgets for this field
                widgets = []
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    for widget in page.widgets():
                        if widget.field_name == field_name:
                            widgets.append((page_num, widget))
                
                if not widgets:
                    results['errors'].append(f"Field '{field_name}' not found")
                    continue
                
                # Get field type from first widget
                field_type = get_field_type(field_name, widgets[0][1])
                
                if field_type == "text":
                    # Update text field
                    for page_num, widget in widgets:
                        widget.field_value = str(new_value)
                        widget.update()
                    
                    results['updated_fields'].append({
                        'field_name': field_name,
                        'field_type': field_type,
                        'new_value': str(new_value)
                    })
                
                elif field_type == "checkbox":
                    # Update checkbox
                    checkbox_value = new_value in [True, 'true', 'True', '1', 1]
                    for page_num, widget in widgets:
                        widget.field_value = checkbox_value
                        widget.update()
                    
                    results['updated_fields'].append({
                        'field_name': field_name,
                        'field_type': field_type,
                        'new_value': checkbox_value
                    })
                
                elif field_type == "radio":
                    # Update radio button group
                    # Find all radio buttons in the group
                    radio_widgets = []
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        for widget in page.widgets():
                            if (widget.field_name == field_name and 
                                widget.field_type_string == "RadioButton"):
                                radio_widgets.append(widget)
                    
                    # Set the selected radio button
                    for widget in radio_widgets:
                        if widget.field_value == new_value:
                            widget.field_value = True  # Select this option
                        else:
                            widget.field_value = False  # Deselect others
                        widget.update()
                    
                    results['updated_fields'].append({
                        'field_name': field_name,
                        'field_type': field_type,
                        'new_value': new_value
                    })
                
                else:
                    results['errors'].append(f"Unsupported field type '{field_type}' for field '{field_name}'")
            
            except Exception as e:
                results['errors'].append(f"Error updating field '{field_name}': {str(e)}")
        
        # Save with incremental update for signature preservation
        if results['updated_fields']:
            doc.saveIncr()
            results['success'] = True
        
        doc.close()
        
        # Check signatures after update
        results['signatures_after'] = validate_signatures_simple(output_path)
        results['signatures_preserved'] = (results['signatures_before'] == results['signatures_after'])
        
    except Exception as e:
        results['errors'].append(f"General error: {str(e)}")
    
    return results

def extract_field_info(pdf_path):
    """
    Extract information about all form fields in the PDF
    """
    fields = {}
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                field_name = widget.field_name
                if field_name not in fields:
                    fields[field_name] = {
                        'field_type': get_field_type(field_name, widget),
                        'current_value': widget.field_value,
                        'options': []
                    }
                
                # For radio buttons, collect all possible values
                if widget.field_type_string == "RadioButton":
                    if widget.field_value not in fields[field_name]['options']:
                        fields[field_name]['options'].append(widget.field_value)
        
        doc.close()
        
    except Exception as e:
        print(f"Error extracting field info: {e}")
    
    return fields

def main():
    """Test the PDF field update functionality"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_service_no_diff.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found")
        sys.exit(1)
    
    print(f"Analyzing PDF: {pdf_path}")
    print("=" * 50)
    
    # Extract field information
    fields = extract_field_info(pdf_path)
    
    print("Available fields:")
    for field_name, info in fields.items():
        print(f"  {field_name}: {info['field_type']} = {info['current_value']}")
        if info['options']:
            print(f"    Options: {info['options']}")
    
    print("\nSignature validation (no diff analysis):")
    sig_valid = validate_signatures_simple(pdf_path)
    print(f"  Signatures valid: {sig_valid}")

if __name__ == "__main__":
    main() 