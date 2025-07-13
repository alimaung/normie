#!/usr/bin/env python3
"""
Script to inspect the actual radio button options for specific fields.
This will help understand why some radio buttons aren't working correctly.
"""

import os
import PyPDF2

def get_radio_button_options(pdf_path, field_name):
    """Get the actual radio button options for a specific field."""
    print(f"\n🔍 Inspecting radio options for field '{field_name}'")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            if '/AcroForm' not in reader.trailer['/Root']:
                print("❌ No AcroForm found")
                return None
            
            form = reader.trailer['/Root']['/AcroForm']
            if '/Fields' not in form:
                print("❌ No fields found")
                return None
            
            fields = form['/Fields']
            
            # Find the specific field
            for i, field in enumerate(fields):
                field_obj = field.get_object()
                current_field_name = str(field_obj.get('/T', ''))
                
                if current_field_name == field_name:
                    print(f"✅ Found field '{field_name}' at index {i}")
                    
                    field_type = field_obj.get('/FT')
                    current_value = field_obj.get('/V', 'No value')
                    print(f"   Type: {field_type}")
                    print(f"   Current Value: {current_value}")
                    
                    if field_type == '/Btn' and '/Kids' in field_obj:
                        kids = field_obj['/Kids']
                        print(f"   📻 Radio button with {len(kids)} options:")
                        
                        options = []
                        for j, kid in enumerate(kids):
                            kid_obj = kid.get_object()
                            
                            # Try to get the export value from appearance states
                            if '/AP' in kid_obj:
                                ap = kid_obj['/AP']
                                if '/N' in ap:
                                    normal_ap = ap['/N']
                                    if hasattr(normal_ap, 'keys'):
                                        for key in normal_ap.keys():
                                            if str(key) != '/Off':
                                                option_value = str(key).lstrip('/')
                                                options.append(option_value)
                                                print(f"      Option {j}: '{option_value}'")
                                    else:
                                        print(f"      Option {j}: Normal appearance not accessible")
                                else:
                                    print(f"      Option {j}: No normal appearance")
                            
                            # Also check for AS (appearance state)
                            if '/AS' in kid_obj:
                                as_value = str(kid_obj['/AS']).lstrip('/')
                                print(f"      Current AS: '{as_value}'")
                        
                        return options
                    else:
                        print(f"   ❌ Not a radio button or no children")
                        return None
            
            print(f"❌ Field '{field_name}' not found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_field_values():
    """Check the radio button options for our problematic fields."""
    print("🚀 Checking radio button options for problematic fields...")
    
    pdf_path = "pdf.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    # Test data from the failing fields
    test_fields = {
        "5": "Bedarfsänderung",
        "6": "Teil",
        "26": "Nicht genehmigt", 
        "27": "Ja"
    }
    
    # Working fields for comparison
    working_fields = {
        "13": "Ja (Produktzulassung ist erforderlich)",
        "14": "kurzfristig"
    }
    
    print(f"\n{'='*60}")
    print("❌ CHECKING PROBLEMATIC FIELDS")
    print(f"{'='*60}")
    
    for field_name, test_value in test_fields.items():
        print(f"\n🔍 Field '{field_name}' - Testing value: '{test_value}'")
        options = get_radio_button_options(pdf_path, field_name)
        
        if options:
            print(f"   Available options: {options}")
            if test_value in options:
                print(f"   ✅ Test value matches available option")
            else:
                print(f"   ❌ Test value NOT in available options!")
                # Look for close matches
                close_matches = []
                for option in options:
                    if (test_value.lower() in option.lower() or 
                        option.lower() in test_value.lower()):
                        close_matches.append(option)
                
                if close_matches:
                    print(f"   🔍 Close matches: {close_matches}")
                else:
                    print(f"   🔍 No close matches found")
        else:
            print(f"   ❌ Could not retrieve options")
    
    print(f"\n{'='*60}")
    print("✅ CHECKING WORKING FIELDS")
    print(f"{'='*60}")
    
    for field_name, test_value in working_fields.items():
        print(f"\n🔍 Field '{field_name}' - Testing value: '{test_value}'")
        options = get_radio_button_options(pdf_path, field_name)
        
        if options:
            print(f"   Available options: {options}")
            if test_value in options:
                print(f"   ✅ Test value matches available option")
            else:
                print(f"   ❌ Test value NOT in available options!")

def main():
    """Main function."""
    check_field_values()
    
    print(f"\n💡 ANALYSIS:")
    print(f"1. If test values don't match available options, that's the problem")
    print(f"2. Radio buttons need exact option value matches")
    print(f"3. We may need to use the correct option values from the PDF")

if __name__ == "__main__":
    main() 