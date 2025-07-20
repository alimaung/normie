#!/usr/bin/env python3
"""
Test Field 5 Button Values
Tests radio button field 5 with both possible values and saves separate PDFs
"""

import fitz
import shutil
import os
from datetime import datetime

def test_field_5():
    """Test field 5 with both values"""
    
    # Check if source PDF exists
    source_pdf = "pdf.pdf"
    if not os.path.exists(source_pdf):
        print(f"❌ Source PDF not found: {source_pdf}")
        return
    
    print(f"🔍 Testing Field 5 Button Values")
    print(f"📄 Source PDF: {source_pdf}")
    print("=" * 50)
    
    # Test values for field 5 - FIXED: use 1 and 2 instead of 0 and 1
    test_values = [
        {"value": "/0", "clean_value": 1, "description": "Neubedarf", "filename": "field_5_value_0.pdf"},
        {"value": "/1", "clean_value": 2, "description": "Bedarfsänderung", "filename": "field_5_value_1.pdf"}
    ]
    
    for test in test_values:
        print(f"\n🧪 Testing: {test['description']} (PDF value: {test['value']} → PyMuPDF value: {test['clean_value']})")
        
        # Create test file
        test_pdf = test['filename']
        shutil.copy2(source_pdf, test_pdf)
        
        # Open and modify
        try:
            doc = fitz.open(test_pdf)
            field_found = False
            
            # Find field 5
            for page_num in range(len(doc)):
                page = doc[page_num]
                for widget in page.widgets():
                    if widget.field_name == "5":
                        field_found = True
                        print(f"   ✅ Found field '5' on page {page_num + 1}")
                        print(f"   📊 Field type: {widget.field_type_string}")
                        print(f"   📊 Current value: {widget.field_value}")
                        
                        # Set the correct radio button value
                        try:
                            widget.field_value = test['clean_value']
                            widget.update()
                            
                            # Verify the value was set
                            new_value = widget.field_value
                            print(f"   ✅ Set to '{test['clean_value']}' → Result: '{new_value}'")
                            
                        except Exception as e:
                            print(f"   ❌ Failed to set '{test['clean_value']}': {e}")
                        
                        break
                
                if field_found:
                    break
            
            if not field_found:
                print(f"   ❌ Field '5' not found in PDF")
            
            # Save the PDF
            print(f"   💾 Saving to: {test_pdf}")
            doc.saveIncr()
            doc.close()
            
            # Verify the saved file
            print(f"   🔍 Verifying saved file...")
            verify_doc = fitz.open(test_pdf)
            for page in verify_doc:
                for widget in page.widgets():
                    if widget.field_name == "5":
                        final_value = widget.field_value
                        print(f"   📊 Final value in saved PDF: '{final_value}'")
                        break
            verify_doc.close()
            
        except Exception as e:
            print(f"   ❌ Error processing {test_pdf}: {e}")
    
    print(f"\n✅ Testing complete!")
    print(f"📁 Check the generated PDF files:")
    for test in test_values:
        if os.path.exists(test['filename']):
            print(f"   - {test['filename']} ({test['description']})")

def main():
    """Main function"""
    test_field_5()

if __name__ == "__main__":
    main() 