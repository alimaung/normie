#!/usr/bin/env python3
"""
Test script for the simple PDF update method.
This script will use the frontend_data.json to update a PDF file.
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pdf_service_simple import save_pdf_changes_simple, extract_pdf_fields_simple

def main():
    """
    Main test function that processes the PDF with frontend data.
    """
    # Define file paths
    pdf_file = "pdf.pdf"
    data_file = "frontend_data.json"
    
    # Check if files exist
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        print("Please ensure 'pdf.pdf' is in the current directory")
        return False
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        print("Please ensure 'frontend_data.json' is in the current directory")
        return False
    
    # Load frontend data
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            frontend_data = json.load(f)
        print(f"✅ Loaded {len(frontend_data)} fields from {data_file}")
    except Exception as e:
        print(f"❌ Error loading frontend data: {e}")
        return False
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"pdf_backup_{timestamp}.pdf"
    try:
        shutil.copy2(pdf_file, backup_file)
        print(f"💾 Created backup: {backup_file}")
    except Exception as e:
        print(f"⚠️  Warning: Could not create backup: {e}")
    
    # Extract current fields for comparison
    print("\n🔍 Extracting current PDF fields...")
    try:
        current_fields = extract_pdf_fields_simple(pdf_file)
        print(f"Found {len(current_fields)} form fields in PDF")
        
        # Show field types
        field_types = {}
        for field in current_fields:
            field_type = field['type']
            field_types[field_type] = field_types.get(field_type, 0) + 1
        
        print("Field types found:")
        for field_type, count in field_types.items():
            print(f"  - {field_type}: {count} fields")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not extract current fields: {e}")
        current_fields = []
    
    # Show which fields will be updated
    print(f"\n📝 Fields to update from frontend data:")
    update_count = 0
    for field_id, value in frontend_data.items():
        # Check if field exists in PDF
        field_exists = any(f['id'] == field_id for f in current_fields)
        status = "✅" if field_exists else "❓"
        print(f"  {status} {field_id}: '{value}'")
        if field_exists:
            update_count += 1
    
    print(f"\n🎯 Will attempt to update {update_count} fields")
    
    # Update the PDF
    print(f"\n🔄 Updating PDF with simple method...")
    try:
        result_path = save_pdf_changes_simple(pdf_file, frontend_data)
        print(f"🎉 PDF updated successfully!")
        print(f"📄 Result: {result_path}")
        
        # Verify the update by extracting fields again
        print(f"\n🔍 Verifying updates...")
        updated_fields = extract_pdf_fields_simple(pdf_file)
        
        # Compare some key fields
        verification_fields = ['1', '3', '26', '33']  # Some fields from frontend_data
        print("Verification of key fields:")
        for field_id in verification_fields:
            if field_id in frontend_data:
                expected = frontend_data[field_id]
                actual = None
                for field in updated_fields:
                    if field['id'] == field_id:
                        actual = field['value']
                        break
                
                if actual is not None:
                    match = "✅" if str(actual) == str(expected) else "❌"
                    print(f"  {match} Field {field_id}: expected='{expected}', actual='{actual}'")
                else:
                    print(f"  ❓ Field {field_id}: not found in PDF")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating PDF: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting simple PDF update test...")
    print("=" * 50)
    
    success = main()
    
    print("=" * 50)
    if success:
        print("✅ Test completed successfully!")
        print("\n📋 Next steps:")
        print("1. Open the updated PDF in Adobe Acrobat")
        print("2. Check if signatures show 'validity unknown' instead of 'invalid'")
        print("3. Verify that form fields are properly filled")
    else:
        print("❌ Test failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure pdf.pdf exists in the current directory")
        print("2. Ensure frontend_data.json exists in the current directory")
        print("3. Check that PyMuPDF is installed: pip install PyMuPDF")
    
    print("\n📁 Files in current directory:")
    for file in sorted(os.listdir('.')):
        if file.endswith(('.pdf', '.json', '.py')):
            size = os.path.getsize(file)
            print(f"  - {file} ({size:,} bytes)") 