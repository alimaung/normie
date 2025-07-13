#!/usr/bin/env python3
"""
Check if radio button updates might be affecting signature fields
"""

import fitz

def check_signature_field_interaction():
    """Check if radio button and signature fields might be related"""
    
    pdf_path = "pdf.pdf"
    
    print("🔍 Checking Signature Field Interaction")
    print("=" * 50)
    
    try:
        doc = fitz.open(pdf_path)
        
        # Get all fields
        radio_fields = []
        signature_fields = []
        all_fields = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                field_info = {
                    'name': widget.field_name,
                    'type': widget.field_type_string,
                    'page': page_num + 1,
                    'value': widget.field_value
                }
                all_fields.append(field_info)
                
                if widget.field_type_string == 'RadioButton':
                    radio_fields.append(field_info)
                elif widget.field_type_string == 'Signature':
                    signature_fields.append(field_info)
        
        print(f"📊 Total fields found: {len(all_fields)}")
        print(f"📊 Radio button fields: {len(radio_fields)}")
        print(f"📊 Signature fields: {len(signature_fields)}")
        
        print("\n🔘 Radio Button Fields:")
        for field in radio_fields:
            print(f"   {field['name']} (page {field['page']}) = '{field['value']}'")
        
        print("\n✍️  Signature Fields:")
        for field in signature_fields:
            print(f"   {field['name']} (page {field['page']}) = '{field['value']}'")
        
        # Check for any field name similarities
        print("\n🔍 Checking for field name conflicts:")
        radio_names = set(f['name'] for f in radio_fields)
        signature_names = set(f['name'] for f in signature_fields)
        
        conflicts = radio_names.intersection(signature_names)
        if conflicts:
            print(f"❌ CONFLICTS FOUND: {conflicts}")
        else:
            print("✅ No field name conflicts")
        
        # Check if signature fields are near radio fields
        print("\n📍 Field proximity check:")
        for sig_field in signature_fields:
            nearby_radios = [r for r in radio_fields if r['page'] == sig_field['page']]
            if nearby_radios:
                print(f"   Signature '{sig_field['name']}' on page {sig_field['page']} has {len(nearby_radios)} radio buttons on same page")
                for radio in nearby_radios:
                    print(f"     - {radio['name']}")
        
        doc.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_signature_field_interaction() 