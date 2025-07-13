#!/usr/bin/env python3
"""
Debug script to investigate why specific radio button fields didn't work.
Focuses on fields 5, 6, 26, and 27 from the radio button test.
"""

import os
import json
import shutil
from datetime import datetime
from pdf_service_simple import save_pdf_changes_simple

def analyze_pdf_fields(pdf_path):
    """Analyze all fields in the PDF to understand their structure."""
    print(f"\n📄 Analyzing PDF fields in: {pdf_path}")
    
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            if '/AcroForm' in reader.trailer['/Root']:
                form = reader.trailer['/Root']['/AcroForm']
                if '/Fields' in form:
                    fields = form['/Fields']
                    print(f"📊 Total fields found: {len(fields)}")
                    
                    for i, field in enumerate(fields):
                        field_obj = field.get_object()
                        field_name = field_obj.get('/T', 'Unknown')
                        field_type = field_obj.get('/FT', 'Unknown')
                        field_value = field_obj.get('/V', 'No value')
                        
                        print(f"Field {i}: Name='{field_name}', Type='{field_type}', Value='{field_value}'")
                        
                        # Check for radio button groups
                        if '/Kids' in field_obj:
                            kids = field_obj['/Kids']
                            print(f"  └─ Has {len(kids)} child fields (radio group)")
                            for j, kid in enumerate(kids):
                                kid_obj = kid.get_object()
                                kid_name = kid_obj.get('/T', f'Child_{j}')
                                kid_value = kid_obj.get('/V', 'No value')
                                print(f"    └─ Child {j}: Name='{kid_name}', Value='{kid_value}'")
                else:
                    print("❌ No fields found in AcroForm")
            else:
                print("❌ No AcroForm found in PDF")
                
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")

def test_individual_radio_field(pdf_path, field_id, field_value, test_name):
    """Test a single radio button field."""
    print(f"\n🧪 Testing individual field: {field_id} = '{field_value}'")
    
    # Create test data with just this field
    test_data = {str(field_id): field_value}
    
    # Create unique output file
    timestamp = datetime.now().strftime("%H%M%S")
    test_filename = f"radio_field_{field_id}_{timestamp}.pdf"
    test_output = os.path.join("test_field_types", test_filename)
    
    try:
        # Copy original to test output
        shutil.copy2(pdf_path, test_output)
        print(f"📄 Created test copy: {test_output}")
        
        # Run the test
        result_path = save_pdf_changes_simple(test_output, test_data)
        
        print(f"✅ Field {field_id} test completed: {result_path}")
        return True, result_path
        
    except Exception as e:
        print(f"❌ Field {field_id} test failed: {e}")
        return False, None

def debug_failed_radio_fields():
    """Debug the specific radio fields that failed."""
    print("🔍 Debugging failed radio button fields...")
    
    # Failed fields from the test
    failed_fields = {
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
    
    original_pdf = "pdf.pdf"
    
    if not os.path.exists(original_pdf):
        print(f"❌ Original PDF not found: {original_pdf}")
        return
    
    # Create test directory
    test_dir = "test_field_types"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # First, analyze the PDF structure
    analyze_pdf_fields(original_pdf)
    
    print(f"\n{'='*60}")
    print("🔍 TESTING FAILED FIELDS")
    print(f"{'='*60}")
    
    failed_results = {}
    for field_id, field_value in failed_fields.items():
        success, result_path = test_individual_radio_field(original_pdf, field_id, field_value, "failed")
        failed_results[field_id] = (success, result_path)
    
    print(f"\n{'='*60}")
    print("✅ TESTING WORKING FIELDS (for comparison)")
    print(f"{'='*60}")
    
    working_results = {}
    for field_id, field_value in working_fields.items():
        success, result_path = test_individual_radio_field(original_pdf, field_id, field_value, "working")
        working_results[field_id] = (success, result_path)
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 DEBUG SUMMARY")
    print(f"{'='*60}")
    
    print("\n❌ FAILED FIELDS:")
    for field_id, (success, path) in failed_results.items():
        status = "✅ PROCESSED" if success else "❌ ERROR"
        print(f"   {status}: Field {field_id} = '{failed_fields[field_id]}'")
        if path:
            print(f"      File: {path}")
    
    print("\n✅ WORKING FIELDS:")
    for field_id, (success, path) in working_results.items():
        status = "✅ PROCESSED" if success else "❌ ERROR"
        print(f"   {status}: Field {field_id} = '{working_fields[field_id]}'")
        if path:
            print(f"      File: {path}")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Compare the PDF structure analysis above")
    print(f"2. Check if failed fields have different naming or structure")
    print(f"3. Open individual test files to see what happened")
    print(f"4. Look for patterns in field IDs or values")

def main():
    """Main debug function."""
    print("🚀 Starting radio button field debugging...")
    debug_failed_radio_fields()

if __name__ == "__main__":
    main() 