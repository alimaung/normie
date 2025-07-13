#!/usr/bin/env python3
"""
Comprehensive Field Type Testing with Signature Preservation
Tests text fields, radio buttons, and checkboxes using the working methods
Based on successful test_comprehensive_fields.py implementation
"""

import json
import os
import shutil
from datetime import datetime
from pdf_service_simple import update_pdf_fields
import fitz

def test_field_types_comprehensive():
    """Test each field type separately with signature preservation"""
    
    # Test configuration
    source_pdf = "pdf.pdf"
    test_data_files = [
        "frontend_data_text_only.json",
        "frontend_data_radio_only.json", 
        "frontend_data_checkbox_only.json"
    ]
    
    # Check if source PDF exists
    if not os.path.exists(source_pdf):
        print(f"❌ Source PDF not found: {source_pdf}")
        return
    
    print(f"🔍 Comprehensive Field Type Testing")
    print(f"📄 Source PDF: {source_pdf}")
    print("=" * 70)
    
    # Test each field type
    for test_file in test_data_files:
        if not os.path.exists(test_file):
            print(f"❌ Test data file not found: {test_file}")
            continue
        
        # Determine field type from filename
        if "text" in test_file:
            field_type = "Text Fields"
        elif "radio" in test_file:
            field_type = "Radio Buttons"
        elif "checkbox" in test_file:
            field_type = "Checkboxes"
        else:
            field_type = "Unknown"
        
        print(f"\n🧪 Testing {field_type}")
        print("=" * 50)
        
        # Load test data
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        print(f"📊 Found {len(test_data)} fields to test")
        
        # Create test PDF
        timestamp = datetime.now().strftime("%H%M%S")
        test_pdf = f"test_pdf/test_{field_type.lower().replace(' ', '_')}_{timestamp}.pdf"
        shutil.copy2(source_pdf, test_pdf)
        
        # Check signature status before update
        print(f"🔍 Checking signature status before update...")
        signature_before = check_signature_status(test_pdf)
        print(f"   📋 Signatures before: {signature_before}")
        
        # Update PDF fields using the working method
        print(f"🔄 Updating PDF fields...")
        success = update_pdf_fields(test_pdf, test_data)
        
        if success:
            print(f"✅ Field updates completed successfully")
            
            # Check signature status after update
            print(f"🔍 Checking signature status after update...")
            signature_after = check_signature_status(test_pdf)
            print(f"   📋 Signatures after: {signature_after}")
            
            # Compare signature status
            if signature_before == signature_after:
                print(f"✅ Signatures preserved! Status unchanged.")
            else:
                print(f"❌ Signature status changed!")
                print(f"   Before: {signature_before}")
                print(f"   After:  {signature_after}")
            
            # Verify field values were actually set
            print(f"🔍 Verifying field values...")
            verify_field_values(test_pdf, test_data)
            
        else:
            print(f"❌ Field updates failed")
        
        print(f"📄 Test PDF saved: {test_pdf}")
    
    print(f"\n🎉 Comprehensive testing complete!")

def check_signature_status(pdf_path):
    """Check the signature status of a PDF"""
    try:
        doc = fitz.open(pdf_path)
        signature_count = 0
        signature_fields = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_type_string == 'Signature':
                    signature_count += 1
                    signature_fields.append({
                        'name': widget.field_name,
                        'page': page_num + 1,
                        'value': widget.field_value
                    })
        
        doc.close()
        
        return {
            'count': signature_count,
            'fields': signature_fields
        }
        
    except Exception as e:
        print(f"❌ Error checking signature status: {e}")
        return {'count': 0, 'fields': []}

def verify_field_values(pdf_path, expected_data):
    """Verify that field values were actually set correctly"""
    try:
        doc = fitz.open(pdf_path)
        verification_results = []
        
        for field_name, expected_value in expected_data.items():
            field_found = False
            
            # Determine field type
            field_type = get_field_type(doc, field_name)
            
            if field_type == "radio":
                # For radio buttons, check if the correct widget is selected
                target_on_state = str(expected_value).lstrip("/")
                radio_correct = False
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    for widget in page.widgets():
                        if widget.field_name == field_name:
                            field_found = True
                            widget_on_state = str(widget.on_state())
                            actual_value = widget.field_value
                            
                            # Check if this is the widget that should be selected
                            if widget_on_state == target_on_state:
                                if str(actual_value) == widget_on_state:
                                    radio_correct = True
                                    break
                
                if field_found:
                    if radio_correct:
                        verification_results.append(f"   ✅ {field_name}: radio button '{target_on_state}' selected (correct)")
                    else:
                        verification_results.append(f"   ❌ {field_name}: radio button '{target_on_state}' not selected")
                else:
                    verification_results.append(f"   ❓ {field_name}: radio field not found")
            
            elif field_type == "checkbox":
                # For checkboxes, handle the different value formats
                actual_value = None
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    for widget in page.widgets():
                        if widget.field_name == field_name:
                            field_found = True
                            actual_value = widget.field_value
                            break
                    if field_found:
                        break
                
                if field_found:
                    # Convert expected boolean to checkbox format
                    expected_bool = bool(expected_value)
                    if isinstance(expected_value, str):
                        expected_bool = expected_value.lower() in ['true', '1', 'yes', 'on', 'checked']
                    
                    # Check if actual value matches expected state
                    actual_str = str(actual_value)
                    if expected_bool:
                        # Expected checked - should be "Yes" or similar
                        if actual_str in ['Yes', 'True', '1', 'On']:
                            verification_results.append(f"   ✅ {field_name}: checkbox checked ('{actual_str}') (correct)")
                        else:
                            verification_results.append(f"   ❌ {field_name}: expected checked, got '{actual_str}'")
                    else:
                        # Expected unchecked - should be "Off", "False", or empty
                        if actual_str in ['Off', 'False', '0', '', 'No']:
                            verification_results.append(f"   ✅ {field_name}: checkbox unchecked ('{actual_str}') (correct)")
                        else:
                            verification_results.append(f"   ❌ {field_name}: expected unchecked, got '{actual_str}'")
                else:
                    verification_results.append(f"   ❓ {field_name}: checkbox field not found")
            
            else:
                # For text fields, use simple comparison
                actual_value = None
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    for widget in page.widgets():
                        if widget.field_name == field_name:
                            field_found = True
                            actual_value = widget.field_value
                            break
                    if field_found:
                        break
                
                if field_found:
                    # Convert values for comparison
                    expected_str = str(expected_value)
                    actual_str = str(actual_value)
                    
                    if actual_str == expected_str:
                        verification_results.append(f"   ✅ {field_name}: '{actual_str}' (correct)")
                    else:
                        verification_results.append(f"   ❌ {field_name}: expected '{expected_str}', got '{actual_str}'")
                else:
                    verification_results.append(f"   ❓ {field_name}: field not found")
        
        doc.close()
        
        # Print verification results
        for result in verification_results:
            print(result)
        
        return verification_results
        
    except Exception as e:
        print(f"❌ Error verifying field values: {e}")
        return []

def get_field_type(doc, field_name):
    """Helper function to determine field type"""
    widget_count = 0
    widget_type_str = None
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                widget_count += 1
                widget_type_str = widget.field_type_string.lower()
    
    if widget_count == 0:
        return "unknown"
    
    # Handle different widget types
    if "checkbox" in widget_type_str:
        return "checkbox"
    elif "radiobutton" in widget_type_str or "button" in widget_type_str:
        # If multiple widgets exist, it's a radio button group
        if widget_count > 1:
            return "radio"
        else:
            return "checkbox"
    elif "text" in widget_type_str:
        return "text"
    else:
        return "unknown"

def create_test_data_if_missing():
    """Create test data files if they don't exist"""
    
    # Sample test data for each field type
    test_data_configs = {
        "frontend_data_text_only.json": {
            "1": "Test Antragsnummer 12345",
            "2a": "Max Mustermann",
            "2b": "2025-01-15",
            "2c": "Entwicklung",
            "2d": "+49 123 456789"
        },
        "frontend_data_radio_only.json": {
            "5": "/1",   # Bedarfsänderung
            "6": "/0",   # Stoff
            "13": "/1",  # Nein (Produktzulassung nicht erforderlich)
            "14": "/0",  # kurzfristig
            "15a": "/1"  # Nein (nicht lagerhaltig)
        },
        "frontend_data_checkbox_only.json": {
            "18a": True,   # EU-Sicherheitsdatenblatt: Ja
            "18b": False,  # Technisches Datenblatt: Nein
            "18c": True,   # Gefährdungsbeurteilung: Ja
            "18d": False,  # Produktzulassung: Nein
            "23a3": True   # KMR (TRGS 905): Ja
        }
    }
    
    for filename, data in test_data_configs.items():
        if not os.path.exists(filename):
            print(f"📝 Creating test data file: {filename}")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            print(f"✅ Test data file exists: {filename}")

def main():
    """Main function"""
    
    print("🔧 Comprehensive Field Type Testing with Signature Preservation")
    print("=" * 70)
    
    # Create test data files if missing
    create_test_data_if_missing()
    
    # Run comprehensive tests
    test_field_types_comprehensive()

if __name__ == "__main__":
    main() 