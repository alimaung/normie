#!/usr/bin/env python3
"""
Test script to isolate which field types corrupt signatures.
Tests text fields, checkboxes, and radio buttons separately.
"""

import os
import shutil
from datetime import datetime
from pdf_service_simple import save_pdf_changes_simple

def test_field_type(data_file, test_name):
    """Test a specific field type and report results."""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"📄 Data file: {data_file}")
    print(f"{'='*60}")
    
    # Use original PDF for each test
    original_pdf = "pdf.pdf"
    
    if not os.path.exists(original_pdf):
        print(f"❌ Original PDF not found: {original_pdf}")
        return False
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return False
    
    # Create test_pdf directory if it doesn't exist
    test_dir = "test_pdf"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"📁 Created directory: {test_dir}")
    
    # Create unique output file for this test in test_pdf directory
    timestamp = datetime.now().strftime("%H%M%S")
    # Use the test name directly since it's now clean
    test_filename = f"test_{test_name}_{timestamp}.pdf"
    test_output = os.path.join(test_dir, test_filename)
    
    try:
        # Copy original to test output
        shutil.copy2(original_pdf, test_output)
        print(f"📄 Created test copy: {test_output}")
        
        # Load test data
        import json
        with open(data_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        print(f"🔢 Fields to test: {len(test_data)}")
        for field_id, value in test_data.items():
            print(f"   - {field_id}: '{value}'")
        
        # Run the test
        print(f"\n🔄 Running test...")
        result_path = save_pdf_changes_simple(test_output, test_data)
        
        print(f"✅ Test completed successfully!")
        print(f"📄 Result file: {result_path}")
        print(f"💡 Next: Open {result_path} in Adobe Acrobat to check signature validity")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all field type tests."""
    print("🚀 Starting field type isolation tests...")
    
    tests = [
        ("frontend_data_text_only.json", "text_fields"),
        ("frontend_data_checkbox_only.json", "checkboxes"), 
        ("frontend_data_radio_only.json", "radio_buttons")
    ]
    
    results = {}
    
    for data_file, test_name in tests:
        success = test_field_type(data_file, test_name)
        results[test_name] = success
        
        if success:
            print(f"✅ {test_name}: COMPLETED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print(f"{'='*60}")
    
    for test_name, success in results.items():
        status = "✅ COMPLETED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Open each result PDF in Adobe Acrobat")
    print(f"2. Check signature validity for each test")
    print(f"3. Identify which field type corrupts signatures")
    print(f"4. Focus debugging on the problematic field type")
    
    print(f"\n📁 Test files created in test_pdf/ directory:")
    test_dir = "test_pdf"
    if os.path.exists(test_dir):
        for file in sorted(os.listdir(test_dir)):
            if file.startswith('test_') and file.endswith('.pdf'):
                file_path = os.path.join(test_dir, file)
                size = os.path.getsize(file_path)
                print(f"   - {file} ({size:,} bytes)")

if __name__ == "__main__":
    main() 