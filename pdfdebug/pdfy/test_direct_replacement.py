#!/usr/bin/env python3
"""
Test Direct Content Replacement for Flattened PDF Fields
"""
import os
import shutil
from datetime import datetime
from low_level_pdf_editor import PurePDFEditor

def test_direct_replacement():
    """Test direct content replacement on flattened PDF."""
    print("🧪 Testing Direct Content Replacement")
    print("=" * 60)
    
    # Test data
    test_updates = {
        "1": "999/2026",                    # Change 030/2025 to 999/2026
        "2a": "John Doe UPDATED",          # Change Ali Maung to John Doe UPDATED
        "3": "New Product Name",           # Change Piccolo-Öko-Entwickler Typ 25
        "25a": "Dr. Smith MODIFIED",       # Change Dr. Karsten Bartz
        "16": "5 Liter CHANGED"           # Change 1 Liter to 5 Liter CHANGED
    }
    
    # Create output file
    timestamp = datetime.now().strftime("%H%M%S")
    output_file = f"test_pdf/direct_replacement_test_{timestamp}.pdf"
    
    # Create directory
    os.makedirs("test_pdf", exist_ok=True)
    
    # Copy original file
    shutil.copy2("pdf.pdf", output_file)
    
    try:
        # Initialize editor
        print("📄 Loading PDF...")
        editor = PurePDFEditor(output_file)
        
        # Create backup
        backup_path = editor.create_backup()
        print(f"📁 Backup created: {backup_path}")
        
        # Show original values
        print("\n📋 ORIGINAL VALUES:")
        for field_id, field in editor.form_fields.items():
            print(f"   {field_id}: '{field.current_value}'")
        
        # Update fields
        print(f"\n🔧 UPDATING FIELDS:")
        successful_updates = 0
        
        for field_id, new_value in test_updates.items():
            print(f"\n   Updating field '{field_id}' to '{new_value}'...")
            if editor.update_field(field_id, new_value):
                successful_updates += 1
                print(f"   ✅ Successfully updated field '{field_id}'")
            else:
                print(f"   ❌ Failed to update field '{field_id}'")
        
        # Save changes
        print(f"\n💾 SAVING CHANGES...")
        if successful_updates > 0:
            saved_path = editor.save_incremental()
            print(f"✅ Saved to: {saved_path}")
        else:
            print("⚠️ No changes to save")
        
        # Show final values
        print("\n📋 FINAL VALUES:")
        for field_id, field in editor.form_fields.items():
            if field_id in test_updates:
                expected = test_updates[field_id]
                actual = field.current_value
                status = "✅" if actual == expected else "❌"
                print(f"   {status} {field_id}: '{actual}' (expected: '{expected}')")
            else:
                print(f"   📝 {field_id}: '{field.current_value}' (unchanged)")
        
        # Results
        print(f"\n📊 RESULTS:")
        print(f"   Fields updated: {successful_updates}/{len(test_updates)}")
        print(f"   Output file: {output_file}")
        print(f"   Backup file: {backup_path}")
        
        if successful_updates == len(test_updates):
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️ Some tests failed")
            
        return successful_updates == len(test_updates)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_direct_replacement() 