#!/usr/bin/env python3
"""
Test different value formats for checkboxes and radio buttons
"""

import fitz
import shutil
from pathlib import Path

def test_checkbox_formats():
    """Test different formats for checkbox values"""
    
    formats_to_test = [
        ("boolean_true", True),
        ("boolean_false", False),
        ("string_ja", "Ja"),
        ("string_nein", "Nein"),
        ("pdf_ja", "/Ja"),
        ("pdf_off", "/Off"),
        ("string_yes", "Yes"),
        ("string_no", "No"),
        ("string_on", "On"),
        ("string_off", "Off"),
        ("int_1", 1),
        ("int_0", 0),
    ]
    
    for format_name, value in formats_to_test:
        print(f"\n=== Testing checkbox with {format_name}: {value} ===")
        
        # Create test file
        source_pdf = Path("pdf.pdf")
        test_pdf = Path(f"checkbox_test_{format_name}.pdf")
        shutil.copy2(source_pdf, test_pdf)
        
        # Open and modify
        doc = fitz.open(test_pdf)
        
        # Find checkbox field 18a
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == "18a":
                    print(f"  Found checkbox field on page {page_num + 1}")
                    print(f"  Current value: {widget.field_value}")
                    print(f"  Field type: {widget.field_type_string}")
                    
                    try:
                        widget.field_value = value
                        widget.update()
                        print(f"  Successfully set to: {value}")
                        
                        # Verify immediately
                        print(f"  Verification: {widget.field_value}")
                        
                    except Exception as e:
                        print(f"  ERROR setting value: {e}")
                    break
        
        # Save and close
        doc.saveIncr()
        doc.close()
        
        # Verify by reopening
        doc = fitz.open(test_pdf)
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == "18a":
                    print(f"  Final verification: {widget.field_value}")
                    break
        doc.close()

def test_radio_formats():
    """Test different formats for radio button values"""
    
    formats_to_test = [
        ("string_neubedarf", "Neubedarf"),
        ("string_bedarfsaenderung", "Bedarfsänderung"),
        ("pdf_0", "/0"),
        ("pdf_1", "/1"),
        ("int_0", 0),
        ("int_1", 1),
        ("string_0", "0"),
        ("string_1", "1"),
    ]
    
    for format_name, value in formats_to_test:
        print(f"\n=== Testing radio button with {format_name}: {value} ===")
        
        # Create test file
        source_pdf = Path("pdf.pdf")
        test_pdf = Path(f"radio_test_{format_name}.pdf")
        shutil.copy2(source_pdf, test_pdf)
        
        # Open and modify
        doc = fitz.open(test_pdf)
        
        # Find radio button field 5
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == "5":
                    print(f"  Found radio field on page {page_num + 1}")
                    print(f"  Current value: {widget.field_value}")
                    print(f"  Field type: {widget.field_type_string}")
                    
                    try:
                        widget.field_value = value
                        widget.update()
                        print(f"  Successfully set to: {value}")
                        
                        # Verify immediately
                        print(f"  Verification: {widget.field_value}")
                        
                    except Exception as e:
                        print(f"  ERROR setting value: {e}")
                    break
        
        # Save and close
        doc.saveIncr()
        doc.close()
        
        # Verify by reopening
        doc = fitz.open(test_pdf)
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == "5":
                    print(f"  Final verification: {widget.field_value}")
                    break
        doc.close()

if __name__ == "__main__":
    print("Testing checkbox value formats...")
    test_checkbox_formats()
    
    print("\n" + "="*50)
    print("Testing radio button value formats...")
    test_radio_formats() 