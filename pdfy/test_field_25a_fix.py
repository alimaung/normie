#!/usr/bin/env python3
"""
Test the fix for field 25a update
"""
import os
import shutil
from datetime import datetime
from low_level_pdf_editor import PurePDFEditor

def test_field_25a_fix():
    """Test that field 25a can now be updated."""
    print("🧪 Testing Field 25a Fix")
    print("=" * 60)
    
    # Create output file
    timestamp = datetime.now().strftime("%H%M%S")
    output_file = f"test_pdf/field_25a_fix_test_{timestamp}.pdf"
    
    # Create directory
    os.makedirs("test_pdf", exist_ok=True)
    
    # Copy original file
    shutil.copy2("pdf.pdf", output_file)
    
    try:
        # Initialize editor
        print("📄 Loading PDF...")
        editor = PurePDFEditor(output_file)
        
        # Check if field 25a exists
        if "25a" not in editor.form_fields:
            print("❌ Field 25a not found in form fields")
            return False
        
        field = editor.form_fields["25a"]
        original_value = field.current_value
        new_value = "Dr. Smith MODIFIED"
        
        print(f"📋 Field 25a Info:")
        print(f"   Original value: '{original_value}'")
        print(f"   New value: '{new_value}'")
        print(f"   Object number: {field.obj_num}")
        print(f"   Field type: {field.field_type}")
        
        # Test location finding
        print(f"\n🔍 Testing value location finding...")
        locations = editor._find_value_locations(original_value)
        print(f"   Found {len(locations)} locations for '{original_value}':")
        
        for i, location in enumerate(locations):
            if 'stream_object' in location:
                print(f"      {i+1}. {location['method']} in stream {location['stream_object']}")
            else:
                print(f"      {i+1}. {location['method']} at position {location['position']}")
        
        # Attempt update
        print(f"\n🔧 Attempting to update field 25a...")
        success = editor.update_field("25a", new_value)
        
        if success:
            print(f"✅ Field 25a updated successfully!")
            print(f"   New current value: '{field.current_value}'")
            
            # Save the changes
            saved_path = editor.save_incremental()
            print(f"💾 Saved to: {saved_path}")
            
            # Verify the change
            if field.current_value == new_value:
                print(f"🎉 VERIFICATION PASSED: Field value correctly updated")
                return True
            else:
                print(f"❌ VERIFICATION FAILED: Expected '{new_value}', got '{field.current_value}'")
                return False
        else:
            print(f"❌ Field 25a update failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_field_25a_fix() 