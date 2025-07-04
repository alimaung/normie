#!/usr/bin/env python3
"""
Enhanced test script to check PyMuPDF incremental save with field modifications.
This will test what happens when we modify fields and save incrementally on signed PDFs.
"""

import fitz
import sys
import os
import shutil

def test_incremental_save_with_modifications(pdf_path):
    """
    Test incremental save with actual field modifications to see signature impact.
    """
    print(f"Testing incremental save with field modifications: {pdf_path}")
    print("=" * 70)
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return False
    
    # Create output path in same directory as input
    input_dir = os.path.dirname(pdf_path)
    output_path = os.path.join(input_dir, "test.pdf")
    
    try:
        # First, copy the original to our test file
        shutil.copy2(pdf_path, output_path)
        print(f"📄 Created test copy: {output_path}")
        
        # Open the test copy
        doc = fitz.open(output_path)
        print(f"✅ Successfully opened test PDF")
        print(f"   Pages: {len(doc)}")
        
        # Check incremental save capability
        can_save_incremental = doc.can_save_incrementally()
        print(f"   Can save incrementally: {can_save_incremental}")
        
        # Check for signatures and their status
        print(f"\n🔍 Analyzing signature fields:")
        signature_fields = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_type_string == 'Signature':
                    sig_info = {
                        'name': widget.field_name,
                        'page': page_num + 1,
                        'has_value': bool(widget.field_value),
                        'value': str(widget.field_value) if widget.field_value else "Empty"
                    }
                    signature_fields.append(sig_info)
                    print(f"   - {sig_info['name']} (page {sig_info['page']})")
                    print(f"     Signed: {sig_info['has_value']}")
                    if sig_info['has_value']:
                        print(f"     Value: {sig_info['value'][:100]}...")  # First 100 chars
        
        # Find and display field 1
        print(f"\n🔍 Looking for field '1' to modify:")
        field_1_found = False
        field_1_original_value = ""
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_name == "1":
                    field_1_found = True
                    field_1_original_value = str(widget.field_value or "")
                    print(f"   ✅ Found field '1' on page {page_num + 1}")
                    print(f"   Original value: '{field_1_original_value}'")
                    print(f"   Field type: {widget.field_type_string}")
                    break
        
        if not field_1_found:
            print(f"   ❌ Field '1' not found!")
            doc.close()
            return False
        
        # Test 1: Modify field 1 and save incrementally
        print(f"\n🧪 Test 1: Modify field 1 and save incrementally")
        
        new_value = f"MODIFIED_TEST_{field_1_original_value}"
        field_modified = False
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_name == "1":
                    try:
                        widget.field_value = new_value
                        widget.update()
                        field_modified = True
                        print(f"   ✅ Modified field '1' to: '{new_value}'")
                        break
                    except Exception as e:
                        print(f"   ❌ Error modifying field '1': {e}")
                        doc.close()
                        return False
        
        if not field_modified:
            print(f"   ❌ Failed to modify field '1'")
            doc.close()
            return False
        
        # Save incrementally
        print(f"   💾 Saving incrementally...")
        try:
            doc.saveIncr()
            print(f"   ✅ Incremental save completed")
        except Exception as e:
            print(f"   ❌ Incremental save failed: {e}")
            doc.close()
            return False
        
        doc.close()
        
        # Test 2: Verify the modification and check signatures
        print(f"\n🧪 Test 2: Verify modifications and signature status")
        
        doc = fitz.open(output_path)
        
        # Check if field 1 was actually modified
        field_1_new_value = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_name == "1":
                    field_1_new_value = str(widget.field_value or "")
                    break
        
        print(f"   Field '1' current value: '{field_1_new_value}'")
        if field_1_new_value == new_value:
            print(f"   ✅ Field modification persisted correctly")
        else:
            print(f"   ❌ Field modification was lost!")
        
        # Re-check signature status
        print(f"   🔍 Re-checking signature fields after modification:")
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_type_string == 'Signature':
                    has_value = bool(widget.field_value)
                    print(f"     - {widget.field_name}: Signed = {has_value}")
        
        doc.close()
        
        # Test 3: Check if we can still save incrementally after modification
        print(f"\n🧪 Test 3: Check incremental save capability after modification")
        
        doc = fitz.open(output_path)
        can_save_after_mod = doc.can_save_incrementally()
        print(f"   Can save incrementally after modification: {can_save_after_mod}")
        
        doc.close()
        
        print("\n" + "=" * 70)
        print("📋 SUMMARY:")
        print(f"   Test file created: {output_path}")
        print(f"   Original field '1' value: '{field_1_original_value}'")
        print(f"   Modified field '1' value: '{field_1_new_value}'")
        print(f"   Modification successful: {field_1_new_value == new_value}")
        print(f"   Can save incrementally (before): {can_save_incremental}")
        print(f"   Can save incrementally (after): {can_save_after_mod}")
        print(f"   Signature fields found: {len(signature_fields)}")
        
        for sig in signature_fields:
            print(f"     - {sig['name']}: {'Signed' if sig['has_value'] else 'Empty'}")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Open {output_path} in Adobe Acrobat")
        print(f"   2. Check signature validation status")
        print(f"   3. Compare with original PDF signature status")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def main():
    """Main function to run the test."""
    if len(sys.argv) != 2:
        print("Usage: python test_incremental_save.py <pdf_file_path>")
        print("Example: python test_incremental_save.py document.pdf")
        print("\nThis will:")
        print("  - Copy the PDF to test.pdf in the same directory")
        print("  - Modify field '1' with a test value")
        print("  - Save incrementally")
        print("  - Report on signature status before/after")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Make sure we have PyMuPDF
    try:
        print(f"PyMuPDF version: {fitz.version}")
    except:
        print("❌ PyMuPDF not available")
        sys.exit(1)
    
    success = test_incremental_save_with_modifications(pdf_path)
    
    if success:
        print("\n✅ All tests completed successfully")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 