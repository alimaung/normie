#!/usr/bin/env python3
"""
Comprehensive Field Testing
Tests various field types: radio buttons, checkboxes, and multi-option radio buttons
"""

import fitz
import shutil
import os
from datetime import datetime

def test_comprehensive_fields():
    """Test multiple field types with various values"""
    
    # Check if source PDF exists
    source_pdf = "pdf.pdf"
    if not os.path.exists(source_pdf):
        print(f"❌ Source PDF not found: {source_pdf}")
        return
    
    print(f"🔍 Testing Comprehensive Field Values")
    print(f"📄 Source PDF: {source_pdf}")
    print("=" * 70)
    
    # Define test configurations
    test_configs = [
        # Field 5 - Radio buttons (2 options)
        {
            "name": "field_5_radio_tests",
            "tests": [
                {"field": "5", "value": "/0", "description": "Field 5: Neubedarf", "filename": "test_field_5_neubedarf.pdf"},
                {"field": "5", "value": "/1", "description": "Field 5: Bedarfsänderung", "filename": "test_field_5_bedarfsaenderung.pdf"}
            ]
        },
        
        # Checkboxes 18a, 18b, 18c, 18d
        {
            "name": "checkbox_18_tests",
            "tests": [
                {"field": "18a", "value": True, "description": "Checkbox 18a: Checked", "filename": "test_checkbox_18a_checked.pdf"},
                {"field": "18a", "value": False, "description": "Checkbox 18a: Unchecked", "filename": "test_checkbox_18a_unchecked.pdf"},
                {"field": "18b", "value": True, "description": "Checkbox 18b: Checked", "filename": "test_checkbox_18b_checked.pdf"},
                {"field": "18b", "value": False, "description": "Checkbox 18b: Unchecked", "filename": "test_checkbox_18b_unchecked.pdf"},
                {"field": "18c", "value": True, "description": "Checkbox 18c: Checked", "filename": "test_checkbox_18c_checked.pdf"},
                {"field": "18c", "value": False, "description": "Checkbox 18c: Unchecked", "filename": "test_checkbox_18c_unchecked.pdf"},
                {"field": "18d", "value": True, "description": "Checkbox 18d: Checked", "filename": "test_checkbox_18d_checked.pdf"},
                {"field": "18d", "value": False, "description": "Checkbox 18d: Unchecked", "filename": "test_checkbox_18d_unchecked.pdf"}
            ]
        },
        
        # Field 26 - Multi-option radio buttons (3 options)
        {
            "name": "field_26_radio_tests",
            "tests": [
                {"field": "26", "value": "/0", "description": "Field 26: Genehmigt", "filename": "test_field_26_genehmigt.pdf"},
                {"field": "26", "value": "/1", "description": "Field 26: Nicht genehmigt", "filename": "test_field_26_nicht_genehmigt.pdf"},
                {"field": "26", "value": "/2", "description": "Field 26: Genehmigt mit Einschränkung", "filename": "test_field_26_mit_einschraenkung.pdf"}
            ]
        }
    ]
    
    # Process each test configuration
    for config in test_configs:
        print(f"\n🔧 {config['name'].upper()}")
        print("=" * 50)
        
        for test in config['tests']:
            print(f"\n🧪 Testing: {test['description']}")
            
            # Create test file
            test_pdf = test['filename']
            shutil.copy2(source_pdf, test_pdf)
            
            # Open and modify
            try:
                doc = fitz.open(test_pdf)
                field_found = False
                
                # Handle different field types
                if test['field'] in ["5", "26"]:  # Radio button fields
                    field_found = handle_radio_button_field(doc, test)
                elif test['field'] in ["18a", "18b", "18c", "18d"]:  # Checkbox fields
                    field_found = handle_checkbox_field(doc, test)
                
                if not field_found:
                    print(f"   ❌ Field '{test['field']}' not found in PDF")
                
                # Save the PDF
                print(f"   💾 Saving to: {test_pdf}")
                doc.saveIncr()
                doc.close()
                
                # Verify the saved file
                verify_saved_file(test_pdf, test['field'])
                
            except Exception as e:
                print(f"   ❌ Error processing {test_pdf}: {e}")
    
    print(f"\n✅ Comprehensive testing complete!")
    print(f"📁 Check the generated PDF files:")
    for config in test_configs:
        for test in config['tests']:
            if os.path.exists(test['filename']):
                print(f"   - {test['filename']}")

def handle_radio_button_field(doc, test):
    """Handle radio button fields (5, 26)"""
    field_found = False
    field_name = test['field']
    target_value = test['value']
    
    # Find and process radio button widgets
    field_info = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                try:
                    on_state = widget.on_state()
                    field_info.append({
                        'page_num': page_num,
                        'on_state': on_state,
                        'current_value': widget.field_value,
                        'field_type': widget.field_type_string
                    })
                    print(f"   📊 Found widget on page {page_num + 1}, on_state: {on_state}, current: {widget.field_value}")
                except Exception as e:
                    print(f"   ❌ Error getting widget info: {e}")
    
    if field_info:
        field_found = True
        print(f"   ✅ Found {len(field_info)} widget(s) for field '{field_name}'")
        
        # Determine target on_state (remove "/" prefix)
        target_on_state = target_value.lstrip("/")
        print(f"   🎯 Looking for widget with on_state '{target_on_state}' for {test['description']}")
        
        # Set the correct radio button
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                for widget in page.widgets():
                    if widget.field_name == field_name:
                        try:
                            widget_on_state = widget.on_state()
                            if str(widget_on_state) == target_on_state:
                                # Set this widget to its on_state
                                widget.field_value = widget.on_state()
                                print(f"   ✅ Setting widget (on_state '{widget_on_state}') to selected")
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
                for widget in page.widgets():
                    if widget.field_name == field_name:
                        try:
                            final_value = widget.field_value
                            on_state = widget.on_state()
                            print(f"   📊 Widget (on_state '{on_state}'): '{final_value}'")
                        except Exception as e:
                            print(f"   ❌ Error reading final value: {e}")
            
        except Exception as e:
            print(f"   ❌ Failed to set radio button: {e}")
    
    return field_found

def handle_checkbox_field(doc, test):
    """Handle checkbox fields (18a, 18b, 18c, 18d)"""
    field_found = False
    field_name = test['field']
    target_value = test['value']  # True or False
    
    # Find and process checkbox widgets
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                field_found = True
                print(f"   ✅ Found checkbox '{field_name}' on page {page_num + 1}")
                print(f"   📊 Field type: {widget.field_type_string}")
                print(f"   📊 Current value: {widget.field_value}")
                
                try:
                    # For checkboxes, use True/False or on_state()
                    if target_value:
                        # Check the checkbox
                        try:
                            on_state = widget.on_state()
                            widget.field_value = on_state
                            print(f"   ✅ Setting checkbox to checked (on_state: {on_state})")
                        except:
                            widget.field_value = True
                            print(f"   ✅ Setting checkbox to checked (True)")
                    else:
                        # Uncheck the checkbox
                        widget.field_value = False
                        print(f"   ✅ Setting checkbox to unchecked (False)")
                    
                    widget.update()
                    
                    # Verify the value was set
                    new_value = widget.field_value
                    print(f"   📊 Result after setting: '{new_value}'")
                    
                except Exception as e:
                    print(f"   ❌ Failed to set checkbox: {e}")
                
                break  # Found the field, no need to continue searching
    
    return field_found

def verify_saved_file(pdf_path, field_name):
    """Verify the saved file contains the expected field value"""
    print(f"   🔍 Verifying saved file...")
    try:
        verify_doc = fitz.open(pdf_path)
        for page in verify_doc:
            for widget in page.widgets():
                if widget.field_name == field_name:
                    final_value = widget.field_value
                    print(f"   📊 Final value in saved PDF: '{final_value}'")
        verify_doc.close()
    except Exception as e:
        print(f"   ❌ Error verifying saved file: {e}")

def main():
    """Main function"""
    test_comprehensive_fields()

if __name__ == "__main__":
    main() 