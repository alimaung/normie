#!/usr/bin/env python3
"""
Test radio button group consistency requirements
"""

import fitz
import shutil
from datetime import datetime

def test_radio_consistency():
    """Test if radio button groups need all widgets updated for consistency"""
    
    source_pdf = "pdf.pdf"
    field_name = "5"
    target_value = "/1"
    
    print("🔍 Testing Radio Button Group Consistency")
    print("=" * 60)
    
    # Test different consistency approaches
    approaches = [
        {
            "name": "only_select_target",
            "description": "Only update the target widget to selected, leave others unchanged",
            "function": update_only_select_target
        },
        {
            "name": "select_target_deselect_others",
            "description": "Update target to selected AND explicitly deselect others",
            "function": update_select_and_deselect
        },
        {
            "name": "deselect_all_then_select",
            "description": "First deselect all, then select target",
            "function": update_deselect_all_then_select
        }
    ]
    
    for approach in approaches:
        print(f"\n🧪 Testing: {approach['name']}")
        print(f"📄 Description: {approach['description']}")
        print("-" * 50)
        
        # Create test PDF
        timestamp = datetime.now().strftime("%H%M%S")
        test_pdf = f"test_pdf/radio_consistency_{approach['name']}_{timestamp}.pdf"
        shutil.copy2(source_pdf, test_pdf)
        
        # Apply the approach
        success = approach['function'](test_pdf, field_name, target_value)
        
        if success:
            print("✅ Update completed")
            print(f"📄 Test PDF: {test_pdf}")
            
            # Check final state
            check_final_state(test_pdf, field_name)
        else:
            print("❌ Update failed")

def update_only_select_target(pdf_path, field_name, target_value):
    """Only update the target widget to selected"""
    try:
        doc = fitz.open(pdf_path)
        target_on_state = str(target_value).lstrip("/")
        
        print(f"   🎯 Target on_state: '{target_on_state}'")
        
        # Only update the target widget
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widget_on_state = widget.on_state()
                    if str(widget_on_state) == target_on_state:
                        old_value = widget.field_value
                        widget.field_value = widget.on_state()
                        widget.update()
                        new_value = widget.field_value
                        print(f"   ✅ Updated target widget: '{old_value}' -> '{new_value}'")
                        break
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_select_and_deselect(pdf_path, field_name, target_value):
    """Update target to selected AND explicitly deselect others"""
    try:
        doc = fitz.open(pdf_path)
        target_on_state = str(target_value).lstrip("/")
        
        print(f"   🎯 Target on_state: '{target_on_state}'")
        
        # Update all widgets in the group
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widget_on_state = widget.on_state()
                    old_value = widget.field_value
                    
                    if str(widget_on_state) == target_on_state:
                        # Select this widget
                        widget.field_value = widget.on_state()
                        print(f"   ✅ Selected widget (on_state '{widget_on_state}')")
                    else:
                        # Deselect this widget
                        widget.field_value = False
                        print(f"   ⚪ Deselected widget (on_state '{widget_on_state}')")
                    
                    widget.update()
                    new_value = widget.field_value
                    print(f"      Value change: '{old_value}' -> '{new_value}'")
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_deselect_all_then_select(pdf_path, field_name, target_value):
    """First deselect all, then select target"""
    try:
        doc = fitz.open(pdf_path)
        target_on_state = str(target_value).lstrip("/")
        
        print(f"   🎯 Target on_state: '{target_on_state}'")
        
        # Step 1: Deselect all widgets
        print("   📋 Step 1: Deselecting all widgets")
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    old_value = widget.field_value
                    widget.field_value = False
                    widget.update()
                    new_value = widget.field_value
                    print(f"      Deselected widget (on_state '{widget.on_state()}'): '{old_value}' -> '{new_value}'")
        
        # Step 2: Select target widget
        print("   📋 Step 2: Selecting target widget")
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widget_on_state = widget.on_state()
                    if str(widget_on_state) == target_on_state:
                        old_value = widget.field_value
                        widget.field_value = widget.on_state()
                        widget.update()
                        new_value = widget.field_value
                        print(f"      Selected target widget: '{old_value}' -> '{new_value}'")
                        break
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_final_state(pdf_path, field_name):
    """Check the final state of the radio button group"""
    try:
        doc = fitz.open(pdf_path)
        
        print("   📋 Final state:")
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    print(f"      Widget (on_state '{widget.on_state()}'): value='{widget.field_value}'")
        
        doc.close()
        
    except Exception as e:
        print(f"   ❌ Error checking final state: {e}")

if __name__ == "__main__":
    test_radio_consistency() 