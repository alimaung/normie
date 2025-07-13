#!/usr/bin/env python3
"""
Corrected radio button test using PDF_FIELD_DICT from pdf_service_simple.py.
This ensures we use the exact correct values for radio buttons.
"""

import os
import json
import shutil
from datetime import datetime
from pdf_service_simple import save_pdf_changes_simple, PDF_FIELD_DICT

def test_radio_corrected():
    """Test radio buttons with the correct values from PDF_FIELD_DICT."""
    print("🚀 Testing radio buttons with PDF_FIELD_DICT values...")
    
    original_pdf = "pdf.pdf"
    
    if not os.path.exists(original_pdf):
        print(f"❌ Original PDF not found: {original_pdf}")
        return
    
    # Create test directory
    test_dir = "test_field_types"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    print(f"\n{'='*60}")
    print("📋 ANALYSIS FROM PDF_FIELD_DICT")
    print(f"{'='*60}")
    
    # Get the problematic fields from PDF_FIELD_DICT
    problematic_fields = ["5", "6", "26", "27"]
    working_fields = ["13", "14"]
    
    print("\n❌ PROBLEMATIC FIELDS:")
    for field_id in problematic_fields:
        if field_id in PDF_FIELD_DICT:
            field_info = PDF_FIELD_DICT[field_id]
            print(f"\nField {field_id}: {field_info['name']}")
            if 'values' in field_info:
                print(f"  Available options:")
                for desc, value in field_info['values'].items():
                    print(f"    '{desc}' → '{value}'")
            else:
                print(f"  No values found (type: {field_info.get('type', 'unknown')})")
    
    print("\n✅ WORKING FIELDS:")
    for field_id in working_fields:
        if field_id in PDF_FIELD_DICT:
            field_info = PDF_FIELD_DICT[field_id]
            print(f"\nField {field_id}: {field_info['name']}")
            if 'values' in field_info:
                print(f"  Available options:")
                for desc, value in field_info['values'].items():
                    print(f"    '{desc}' → '{value}'")
    
    # Test cases using PDF_FIELD_DICT values
    test_cases = [
        {
            "name": "original_descriptive_values",
            "description": "Test with original descriptive values from frontend",
            "data": {
                "5": "Bedarfsänderung",      # Should map to "/1"
                "6": "Teil",                # Should map to "/1"
                "13": "Ja (Produktzulassung ist erforderlich)",  # Should map to "/0"
                "14": "kurzfristig",        # Should map to "/0"
                "26": "Nicht genehmigt",    # Should map to "/1"
                "27": "Ja"                  # Should map to "/0"
            }
        },
        {
            "name": "pdf_dict_values",
            "description": "Test with exact PDF_FIELD_DICT values",
            "data": {
                "5": "/1",   # Bedarfsänderung
                "6": "/1",   # Teil
                "13": "/0",  # Ja (Produktzulassung ist erforderlich)
                "14": "/0",  # kurzfristig
                "26": "/1",  # Nicht genehmigt
                "27": "/0"   # Ja
            }
        },
        {
            "name": "alternative_options",
            "description": "Test with alternative options from PDF_FIELD_DICT",
            "data": {
                "5": "/0",   # Neubedarf
                "6": "/0",   # Stoff
                "13": "/1",  # Nein (Produktzulassung ist nicht erforderlich)
                "14": "/1",  # langfristig
                "26": "/0",  # Genehmigt
                "27": "/1"   # Nein
            }
        },
        {
            "name": "field_26_all_options",
            "description": "Test all options for field 26 (3 options)",
            "data": {
                "26": "/2"   # Genehmigt mit Einschränkung
            }
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"🧪 TEST: {test_case['name']}")
        print(f"📝 {test_case['description']}")
        print(f"{'='*60}")
        
        # Create unique output file
        timestamp = datetime.now().strftime("%H%M%S")
        test_filename = f"{test_case['name']}_{timestamp}.pdf"
        test_output = os.path.join(test_dir, test_filename)
        
        try:
            # Copy original to test output
            shutil.copy2(original_pdf, test_output)
            print(f"📄 Created test copy: {test_output}")
            
            # Show what we're testing
            print(f"🔢 Testing fields:")
            for field_id, value in test_case['data'].items():
                field_info = PDF_FIELD_DICT.get(field_id, {})
                name = field_info.get('name', 'Unknown')
                
                # Try to find the descriptive name for the value
                desc_name = "Unknown"
                if 'values' in field_info:
                    for desc, pdf_value in field_info['values'].items():
                        if pdf_value == value or desc == value:
                            desc_name = desc
                            break
                
                print(f"   - Field {field_id}: '{value}' ({desc_name}) - {name}")
            
            # Run the test
            result_path = save_pdf_changes_simple(test_output, test_case['data'])
            
            print(f"✅ Test completed successfully!")
            print(f"📄 Result file: {result_path}")
            
            results[test_case['name']] = {
                'success': True,
                'file': result_path,
                'fields_tested': len(test_case['data'])
            }
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results[test_case['name']] = {
                'success': False,
                'error': str(e),
                'fields_tested': len(test_case['data'])
            }
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print(f"{'='*60}")
    
    for test_name, result in results.items():
        if result['success']:
            print(f"✅ {test_name}: SUCCESS")
            print(f"   📄 File: {result['file']}")
            print(f"   🔢 Fields: {result['fields_tested']}")
        else:
            print(f"❌ {test_name}: FAILED")
            print(f"   ❌ Error: {result['error']}")
            print(f"   🔢 Fields: {result['fields_tested']}")
    
    print(f"\n💡 KEY FINDINGS FROM PDF_FIELD_DICT:")
    print(f"Field 5 (Kennzeichnung des Bedarfs):")
    print(f"  - 'Neubedarf' → '/0'")
    print(f"  - 'Bedarfsänderung' → '/1'")
    print(f"Field 6 (Kennzeichnung des Produkts):")
    print(f"  - 'Stoff' → '/0'")
    print(f"  - 'Teil' → '/1'")
    print(f"Field 13 (Erzeugnisrelevant):")
    print(f"  - 'Ja (Produktzulassung ist erforderlich)' → '/0'")
    print(f"  - 'Nein (Produktzulassung ist nicht erforderlich)' → '/1'")
    print(f"Field 14 (Nutzung):")
    print(f"  - 'kurzfristig' → '/0'")
    print(f"  - 'langfristig' → '/1'")
    print(f"Field 26 (Ergebnis der Prüfung für Umweltschutz):")
    print(f"  - 'Genehmigt' → '/0'")
    print(f"  - 'Nicht genehmigt' → '/1'")
    print(f"  - 'Genehmigt mit Einschränkung' → '/2'")
    print(f"Field 27 (BImSch-Genehmigung erfoderlich?):")
    print(f"  - 'Ja' → '/0'")
    print(f"  - 'Nein' → '/1'")
    
    print(f"\n🎯 CORRECTED DATA FOR FUTURE USE:")
    corrected_data = {
        "5": "Bedarfsänderung",      # This should work now
        "6": "Teil",                # This should work now
        "13": "Ja (Produktzulassung ist erforderlich)",  # This was working
        "14": "kurzfristig",        # This was working
        "26": "Nicht genehmigt",    # This should work now
        "27": "Ja"                  # This should work now
    }
    
    corrected_file = "frontend_data_radio_final.json"
    with open(corrected_file, 'w', encoding='utf-8') as f:
        json.dump(corrected_data, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Created final corrected data file: {corrected_file}")
    print(f"   This uses the descriptive values that should map correctly via PDF_FIELD_DICT")

def main():
    """Main test function."""
    test_radio_corrected()

if __name__ == "__main__":
    main() 