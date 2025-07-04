#!/usr/bin/env python3
"""
Test signature preservation with different value formats
"""

import fitz
import shutil
from pathlib import Path

def test_signature_preservation():
    """Test if using exact PDF values preserves signatures"""
    
    # Test cases
    test_cases = [
        {
            "name": "text_only",
            "description": "Text field only (known to work)",
            "fields": {"1": "TEST-TEXT-ONLY"}
        },
        {
            "name": "checkbox_boolean",
            "description": "Checkbox with boolean True",
            "fields": {"1": "TEST-CHECKBOX-BOOL", "18a": True}
        },
        {
            "name": "checkbox_string",
            "description": "Checkbox with string 'Yes'",
            "fields": {"1": "TEST-CHECKBOX-STR", "18a": "Yes"}
        },
        {
            "name": "checkbox_pdf_value",
            "description": "Checkbox with PDF value '/Ja'",
            "fields": {"1": "TEST-CHECKBOX-PDF", "18a": "/Ja"}
        },
        {
            "name": "radio_int",
            "description": "Radio button with integer 0",
            "fields": {"1": "TEST-RADIO-INT", "5": 0}
        },
        {
            "name": "radio_string",
            "description": "Radio button with string '0'",
            "fields": {"1": "TEST-RADIO-STR", "5": "0"}
        },
        {
            "name": "radio_pdf_value",
            "description": "Radio button with PDF value '/0'",
            "fields": {"1": "TEST-RADIO-PDF", "5": "/0"}
        },
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print(f"Fields: {test_case['fields']}")
        
        # Create test file
        source_pdf = Path("pdf.pdf")
        test_pdf = Path(f"signature_test_{test_case['name']}.pdf")
        shutil.copy2(source_pdf, test_pdf)
        
        # Open and modify
        doc = fitz.open(test_pdf)
        
        # Process each field
        for field_name, new_value in test_case['fields'].items():
            print(f"\nProcessing field '{field_name}' = {new_value}")
            
            field_found = False
            for page_num in range(len(doc)):
                page = doc[page_num]
                for widget in page.widgets():
                    if widget.field_name == field_name:
                        field_found = True
                        print(f"  Found: {widget.field_type_string} on page {page_num + 1}")
                        print(f"  Current: {widget.field_value}")
                        
                        try:
                            widget.field_value = new_value
                            widget.update()
                            print(f"  Set to: {new_value}")
                            print(f"  Verify: {widget.field_value}")
                        except Exception as e:
                            print(f"  ERROR: {e}")
                        break
                if field_found:
                    break
            
            if not field_found:
                print(f"  WARNING: Field '{field_name}' not found!")
        
        # Save incrementally
        doc.saveIncr()
        doc.close()
        
        print(f"\nSaved: {test_pdf}")
        print("*** Please check signature validity in Adobe Acrobat ***")

if __name__ == "__main__":
    test_signature_preservation() 