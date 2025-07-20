#!/usr/bin/env python3
"""
Test script to examine radio button signature impact
Tests different approaches to updating radio buttons
"""

import fitz
import shutil
import os
from datetime import datetime

def test_radio_signature_approaches():
    """Test different approaches to radio button updates"""
    
    source_pdf = "pdf.pdf"
    
    if not os.path.exists(source_pdf):
        print(f"❌ Source PDF not found: {source_pdf}")
        return
    
    print("🔍 Testing Radio Button Signature Impact")
    print("=" * 60)
    
    # Test data
    test_cases = [
        {
            "name": "single_field_update",
            "description": "Update single radio field with current method",
            "field_updates": {"5": "/1"}
        },
        {
            "name": "multiple_field_update", 
            "description": "Update multiple radio fields simultaneously",
            "field_updates": {"5": "/1", "6": "/0", "13": "/1"}
        },
        {
            "name": "minimal_update_approach",
            "description": "Test minimal update approach (batch updates)",
            "field_updates": {"5": "/1"}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Test: {test_case['name']}")
        print(f"📄 Description: {test_case['description']}")
        print("-" * 40)
        
        # Create test PDF
        timestamp = datetime.now().strftime("%H%M%S")
        test_pdf = f"test_pdf/radio_signature_test_{test_case['name']}_{timestamp}.pdf"
        shutil.copy2(source_pdf, test_pdf)
        
        # Check signature before
        signature_before = check_signature_status(test_pdf)
        print(f"🔒 Signatures before: {signature_before['count']} fields")
        
        # Apply different update approaches
        if test_case['name'] == "minimal_update_approach":
            success = update_radio_minimal(test_pdf, test_case['field_updates'])
        else:
            success = update_radio_standard(test_pdf, test_case['field_updates'])
        
        if success:
            # Check signature after
            signature_after = check_signature_status(test_pdf)
            print(f"🔒 Signatures after: {signature_after['count']} fields")
            
            # Compare
            if signature_before['count'] == signature_after['count']:
                print("✅ Signature count preserved")
                
                # Check if signature field values changed
                signatures_changed = False
                for before_sig in signature_before['fields']:
                    after_sig = next((s for s in signature_after['fields'] if s['name'] == before_sig['name']), None)
                    if after_sig and before_sig['value'] != after_sig['value']:
                        signatures_changed = True
                        print(f"⚠️  Signature field '{before_sig['name']}' value changed: '{before_sig['value']}' -> '{after_sig['value']}'")
                
                if not signatures_changed:
                    print("✅ Signature field values unchanged")
                else:
                    print("❌ Some signature field values changed")
            else:
                print("❌ Signature count changed")
        else:
            print("❌ Update failed")
        
        print(f"📄 Test PDF: {test_pdf}")

def update_radio_standard(pdf_path, field_updates):
    """Standard radio button update approach (current method)"""
    try:
        doc = fitz.open(pdf_path)
        
        for field_name, new_value in field_updates.items():
            print(f"   🔄 Updating field '{field_name}' -> '{new_value}'")
            
            # Convert new_value to target on_state
            target_on_state = str(new_value).lstrip("/")
            
            # Set the correct radio button
            for page_num in range(len(doc)):
                page = doc[page_num]
                for widget in page.widgets():
                    if widget.field_name == field_name:
                        widget_on_state = widget.on_state()
                        if str(widget_on_state) == target_on_state:
                            widget.field_value = widget.on_state()
                        else:
                            widget.field_value = False
                        widget.update()
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_radio_minimal(pdf_path, field_updates):
    """Minimal radio button update approach (batch updates)"""
    try:
        doc = fitz.open(pdf_path)
        
        # Collect all widgets to update first
        widget_updates = []
        
        for field_name, new_value in field_updates.items():
            print(f"   🔄 Preparing field '{field_name}' -> '{new_value}'")
            
            target_on_state = str(new_value).lstrip("/")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                for widget in page.widgets():
                    if widget.field_name == field_name:
                        widget_on_state = widget.on_state()
                        if str(widget_on_state) == target_on_state:
                            widget_updates.append((widget, widget.on_state()))
                        else:
                            widget_updates.append((widget, False))
        
        # Apply all updates at once
        print(f"   🔄 Applying {len(widget_updates)} widget updates...")
        for widget, value in widget_updates:
            widget.field_value = value
            widget.update()
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_signature_status(pdf_path):
    """Check signature status"""
    try:
        doc = fitz.open(pdf_path)
        signature_count = 0
        signature_fields = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_type_string == 'Signature':
                    signature_count += 1
                    signature_fields.append({
                        'name': widget.field_name,
                        'page': page_num + 1,
                        'value': widget.field_value
                    })
        
        doc.close()
        
        return {
            'count': signature_count,
            'fields': signature_fields
        }
        
    except Exception as e:
        print(f"❌ Error checking signature: {e}")
        return {'count': 0, 'fields': []}

if __name__ == "__main__":
    test_radio_signature_approaches() 