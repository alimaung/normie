#!/usr/bin/env python3
"""
Test using exact PDF values from field dictionary instead of boolean values
"""

import fitz
import json
import shutil
import os
from pathlib import Path

# Test data with PDF values instead of boolean
test_data = {
    "1": "TEST-030-2025",  # text field
    "18a": "/Off",  # checkbox - set to off/unchecked
    "5": "/1",     # radio button - set to Bedarfsänderung (which is /1 according to field dict)
}

def test_pdf_values():
    """Test using exact PDF values for form fields"""
    
    # Source and target files
    source_pdf = Path("pdf.pdf")
    test_pdf = Path("test_pdf_values.pdf")
    
    # Copy original to test file
    shutil.copy2(source_pdf, test_pdf)
    
    print("Testing with exact PDF values...")
    
    # Open document
    doc = fitz.open(test_pdf)
    
    # Process each field
    for field_name, new_value in test_data.items():
        print(f"\nProcessing field '{field_name}' with value: {new_value}")
        
        # Find the field
        field_found = False
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    field_found = True
                    print(f"  Found field on page {page_num + 1}")
                    print(f"  Field type: {widget.field_type_string}")
                    print(f"  Current value: {widget.field_value}")
                    
                    # Set the exact PDF value
                    widget.field_value = new_value
                    widget.update()
                    
                    print(f"  Set value to: {new_value}")
                    break
            if field_found:
                break
        
        if not field_found:
            print(f"  WARNING: Field '{field_name}' not found!")
    
    # Save incrementally
    print(f"\nSaving document incrementally...")
    doc.saveIncr()
    doc.close()
    
    print(f"Test completed. Check {test_pdf} for signature validity.")
    
    # Verify the changes
    print("\nVerifying changes:")
    doc = fitz.open(test_pdf)
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name in test_data:
                print(f"  Field '{widget.field_name}': {widget.field_value}")
    doc.close()

if __name__ == "__main__":
    test_pdf_values() 