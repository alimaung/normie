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
    
    # Test values for field 5 - Use string values with / prefix (matching working examples)
    test_values = [
        {"value": "/0", "clean_value": "/0", "description": "Neubedarf", "filename": "field_5_value_0.pdf"},
        {"value": "/1", "clean_value": "/1", "description": "Bedarfsänderung", "filename": "field_5_value_1.pdf"}
    ]
    
    for test in test_values:
        print(f"\n🧪 Testing: {test['description']} (Setting value: {test['clean_value']})")
        
        # Create test file
        test_pdf = test['filename']
        shutil.copy2(source_pdf, test_pdf)
        
        # Open and modify
        try:
            doc = fitz.open(test_pdf)
            field_found = False
            
            # Find and process field 5 widgets directly without storing references
            field_5_info = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                for widget in page.widgets():
                    if widget.field_name == "5":
                        try:
                            on_state = widget.on_state()
                            field_5_info.append({
                                'page_num': page_num,
                                'on_state': on_state,
                                'current_value': widget.field_value,
                                'field_type': widget.field_type_string
                            })
                            print(f"   📊 Found widget on page {page_num + 1}, on_state: {on_state}, current: {widget.field_value}")
                        except Exception as e:
                            print(f"   ❌ Error getting widget info: {e}")
            
            if field_5_info:
                field_found = True
                print(f"   ✅ Found {len(field_5_info)} widget(s) for field '5'")
                
                # Determine target on_state
                target_on_state = None
                if test['clean_value'] == "/0":
                    target_on_state = "0"
                    print(f"   🎯 Looking for widget with on_state '0' for Neubedarf")
                elif test['clean_value'] == "/1":
                    target_on_state = "1"
                    print(f"   🎯 Looking for widget with on_state '1' for Bedarfsänderung")
                
                # Now set the correct radio button by finding widgets again
                if target_on_state:
                    try:
                        for page_num in range(len(doc)):
                            page = doc[page_num]
                            for widget in page.widgets():
                                if widget.field_name == "5":
                                    try:
                                        widget_on_state = widget.on_state()
                                        if str(widget_on_state) == target_on_state:
                                            # Set this widget to its on_state
                                            widget.field_value = widget.on_state()
                                            print(f"   ✅ Setting widget (on_state '{widget_on_state}') to selected ({test['description']})")
                                        else:
                                            # Set other widgets to False (off)
                                            widget.field_value = False
                                            print(f"   ✅ Setting widget (on_state '{widget_on_state}') to off")
                                        widget.update()
                                    except Exception as e:
                                        print(f"   ❌ Error setting widget: {e}")
                        
                        # Verify the final values
                        print(f"   📊 Final values:")
                        for page_num in range(len(doc)):
                            page = doc[page_num]
                            for i, widget in enumerate(page.widgets()):
                                if widget.field_name == "5":
                                    try:
                                        final_value = widget.field_value
                                        on_state = widget.on_state()
                                        print(f"   📊 Widget (on_state '{on_state}'): '{final_value}'")
                                    except Exception as e:
                                        print(f"   ❌ Error reading final value: {e}")
                        
                    except Exception as e:
                        print(f"   ❌ Failed to set radio button: {e}")
            
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