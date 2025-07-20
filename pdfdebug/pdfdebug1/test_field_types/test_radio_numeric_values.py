#!/usr/bin/env python3
"""
Test script to verify radio buttons work with numeric values.
Based on the inspection, radio buttons expect numeric values like '0', '1', '2'.
"""

import os
import json
import shutil
from datetime import datetime
from pdf_service_simple import save_pdf_changes_simple

def test_radio_with_numeric_values():
    """Test radio buttons using numeric values instead of descriptive text."""
    print("🚀 Testing radio buttons with numeric values...")
    
    original_pdf = "pdf.pdf"
    
    if not os.path.exists(original_pdf):
        print(f"❌ Original PDF not found: {original_pdf}")
        return
    
    # Create test directory
    test_dir = "test_field_types"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # Test data with numeric values (based on radio button inspection)
    test_cases = [
        {
            "name": "failed_fields_numeric",
            "description": "Previously failed fields with numeric values",
            "data": {
                "5": "0",    # First option
                "6": "1",    # Second option  
                "26": "2",   # Third option (field 26 has 3 options)
                "27": "1"    # Second option
            }
        },
        {
            "name": "failed_fields_alt_numeric", 
            "description": "Previously failed fields with alternative numeric values",
            "data": {
                "5": "1",    # Second option
                "6": "0",    # First option
                "26": "0",   # First option
                "27": "0"    # First option
            }
        },
        {
            "name": "working_fields_numeric",
            "description": "Previously working fields with numeric values",
            "data": {
                "13": "1",   # Second option
                "14": "0"    # First option
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
                print(f"   - Field {field_id}: '{value}'")
            
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
    
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Open the result PDFs in Adobe Acrobat")
    print(f"2. Check if the radio buttons are now selected correctly")
    print(f"3. Verify signature validity")
    print(f"4. Compare with the original descriptive text approach")
    
    # Create a corrected JSON file for future reference
    corrected_data = {
        "5": "0",  # Assuming first option = "Bedarfsänderung"
        "6": "1",  # Assuming second option = "Teil"
        "13": "1", # This was working, so keep numeric equivalent
        "14": "0", # This was working, so keep numeric equivalent
        "26": "2", # Assuming third option = "Nicht genehmigt"
        "27": "1"  # Assuming second option = "Ja"
    }
    
    corrected_file = "frontend_data_radio_corrected.json"
    with open(corrected_file, 'w', encoding='utf-8') as f:
        json.dump(corrected_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Created corrected data file: {corrected_file}")
    print(f"   This uses numeric values that should work with radio buttons")

def main():
    """Main test function."""
    test_radio_with_numeric_values()

if __name__ == "__main__":
    main() 