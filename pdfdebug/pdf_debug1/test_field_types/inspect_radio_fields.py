#!/usr/bin/env python3
"""
Simple script to inspect radio button fields in the PDF.
Shows field names, types, and possible values to understand why some fields fail.
"""

import os
import json

def inspect_pdf_radio_fields(pdf_path):
    """Inspect all radio button fields in the PDF."""
    print(f"🔍 Inspecting radio fields in: {pdf_path}")
    
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            if '/AcroForm' not in reader.trailer['/Root']:
                print("❌ No AcroForm found in PDF")
                return
            
            form = reader.trailer['/Root']['/AcroForm']
            if '/Fields' not in form:
                print("❌ No fields found in AcroForm")
                return
            
            fields = form['/Fields']
            print(f"📊 Total fields: {len(fields)}")
            
            radio_fields = []
            field_mapping = {}
            
            for i, field in enumerate(fields):
                field_obj = field.get_object()
                field_name = field_obj.get('/T', f'Field_{i}')
                field_type = field_obj.get('/FT')
                
                # Convert field name to string if it's a PyPDF2 object
                if hasattr(field_name, 'get_object'):
                    field_name = str(field_name)
                
                print(f"\nField {i}: '{field_name}' (Type: {field_type})")
                
                # Store field mapping
                field_mapping[str(i)] = field_name
                field_mapping[field_name] = str(i)
                
                # Check if it's a radio button field
                if field_type == '/Btn':  # Button field (could be radio or checkbox)
                    # Check for radio button specific properties
                    if '/Kids' in field_obj:
                        kids = field_obj['/Kids']
                        print(f"  📻 RADIO BUTTON GROUP with {len(kids)} options:")
                        
                        radio_info = {
                            'field_id': str(i),
                            'field_name': field_name,
                            'options': []
                        }
                        
                        for j, kid in enumerate(kids):
                            kid_obj = kid.get_object()
                            
                            # Get the appearance dictionary to find option values
                            if '/AP' in kid_obj and '/N' in kid_obj['/AP']:
                                ap_dict = kid_obj['/AP']['/N']
                                if hasattr(ap_dict, 'keys'):
                                    for key in ap_dict.keys():
                                        if key != '/Off':  # Skip the "off" state
                                            option_value = str(key).lstrip('/')
                                            radio_info['options'].append(option_value)
                                            print(f"    └─ Option {j}: '{option_value}'")
                        
                        radio_fields.append(radio_info)
                    else:
                        print(f"  🔘 CHECKBOX or SINGLE BUTTON")
                elif field_type == '/Tx':
                    print(f"  📝 TEXT FIELD")
                elif field_type == '/Ch':
                    print(f"  📋 CHOICE FIELD")
                else:
                    print(f"  ❓ OTHER TYPE: {field_type}")
            
            # Show our test data mapping
            print(f"\n{'='*60}")
            print("🎯 ANALYZING TEST DATA MAPPING")
            print(f"{'='*60}")
            
            test_data = {
                "5": "Bedarfsänderung",
                "6": "Teil",
                "13": "Ja (Produktzulassung ist erforderlich)",
                "14": "kurzfristig",
                "26": "Nicht genehmigt",
                "27": "Ja"
            }
            
            for field_id, test_value in test_data.items():
                print(f"\nTest Field {field_id}: '{test_value}'")
                
                # Find corresponding radio field
                matching_radio = None
                for radio in radio_fields:
                    if radio['field_id'] == field_id:
                        matching_radio = radio
                        break
                
                if matching_radio:
                    print(f"  ✅ Found radio field: '{matching_radio['field_name']}'")
                    print(f"  📻 Available options: {matching_radio['options']}")
                    
                    # Check if our test value matches any option
                    if test_value in matching_radio['options']:
                        print(f"  ✅ Test value matches available option")
                    else:
                        print(f"  ❌ Test value NOT found in available options!")
                        print(f"      Closest matches:")
                        for option in matching_radio['options']:
                            if test_value.lower() in option.lower() or option.lower() in test_value.lower():
                                print(f"        - '{option}'")
                else:
                    print(f"  ❌ No radio field found for ID {field_id}")
                    
                    # Check if field exists but isn't a radio button
                    if field_id in field_mapping:
                        actual_name = field_mapping[field_id]
                        print(f"      Field exists as: '{actual_name}' (might not be radio)")
            
            return radio_fields, field_mapping
            
    except Exception as e:
        print(f"❌ Error inspecting PDF: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def main():
    """Main inspection function."""
    print("🚀 Starting radio field inspection...")
    
    original_pdf = "pdf.pdf"
    
    if not os.path.exists(original_pdf):
        print(f"❌ Original PDF not found: {original_pdf}")
        return
    
    radio_fields, field_mapping = inspect_pdf_radio_fields(original_pdf)
    
    if radio_fields:
        print(f"\n{'='*60}")
        print("📋 RADIO FIELDS SUMMARY")
        print(f"{'='*60}")
        
        for radio in radio_fields:
            print(f"Field {radio['field_id']}: '{radio['field_name']}'")
            print(f"  Options: {', '.join(radio['options'])}")
    
    print(f"\n💡 This inspection should help identify:")
    print(f"1. Whether the failing fields are actually radio buttons")
    print(f"2. What the exact option values should be")
    print(f"3. If there's a mismatch between test data and available options")

if __name__ == "__main__":
    main() 