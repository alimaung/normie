#!/usr/bin/env python3
"""
Test different radio button update methods to find signature-friendly approach
"""

import fitz
import shutil
import os
from datetime import datetime

def test_radio_update_methods():
    """Test different approaches to radio button updates"""
    
    source_pdf = "pdf.pdf"
    
    if not os.path.exists(source_pdf):
        print(f"❌ Source PDF not found: {source_pdf}")
        return
    
    
    
    
    
    
    print("🔍 Testing Radio Button Update Methods")
    print("=" * 60)
    
    # Test different approaches
    test_methods = [
        {
            "name": "current_method",
            "description": "Current method: Update all widgets with immediate update() calls",
            "function": update_radio_current
        },
        {
            "name": "single_widget_only",
            "description": "Only update the selected widget, leave others unchanged",
            "function": update_radio_single_widget
        },
        {
            "name": "batch_update",
            "description": "Set all values first, then call update() on all at once",
            "function": update_radio_batch
        },
        {
            "name": "minimal_touch",
            "description": "Only touch widgets that actually need to change",
            "function": update_radio_minimal_touch
        }
    ]
    
    test_field = "5"  # Simple radio button field
    test_value = "/1"  # Switch to option 1
    
    for method in test_methods:
        print(f"\n🧪 Testing: {method['name']}")
        print(f"📄 Description: {method['description']}")
        print("-" * 50)
        
        # Create test PDF
        timestamp = datetime.now().strftime("%H%M%S")
        test_pdf = f"test_pdf/radio_method_{method['name']}_{timestamp}.pdf"
        shutil.copy2(source_pdf, test_pdf)
        
        # Test the method
        success = method['function'](test_pdf, test_field, test_value)
        
        if success:
            print("✅ Update completed successfully")
            print(f"📄 Test PDF: {test_pdf}")
            print("   📋 Please check signature validity in Adobe Acrobat")
        else:
            print("❌ Update failed")

def update_radio_current(pdf_path, field_name, new_value):
    """Current method: Update all widgets with immediate update() calls"""
    try:
        doc = fitz.open(pdf_path)
        
        target_on_state = str(new_value).lstrip("/")
        print(f"   🎯 Target on_state: '{target_on_state}'")
        
        # Current approach: Update all widgets immediately
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widget_on_state = widget.on_state()
                    if str(widget_on_state) == target_on_state:
                        widget.field_value = widget.on_state()
                        print(f"   ✅ Selected widget (on_state '{widget_on_state}')")
                    else:
                        widget.field_value = False
                        print(f"   ⚪ Deselected widget (on_state '{widget_on_state}')")
                    widget.update()  # Immediate update
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_radio_single_widget(pdf_path, field_name, new_value):
    """Only update the selected widget, leave others unchanged"""
    try:
        doc = fitz.open(pdf_path)
        
        target_on_state = str(new_value).lstrip("/")
        print(f"   🎯 Target on_state: '{target_on_state}'")
        
        # Only update the widget that should be selected
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widget_on_state = widget.on_state()
                    if str(widget_on_state) == target_on_state:
                        widget.field_value = widget.on_state()
                        widget.update()
                        print(f"   ✅ Selected widget (on_state '{widget_on_state}')")
                        break
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_radio_batch(pdf_path, field_name, new_value):
    """Set all values first, then call update() on all at once"""
    try:
        doc = fitz.open(pdf_path)
        
        target_on_state = str(new_value).lstrip("/")
        print(f"   🎯 Target on_state: '{target_on_state}'")
        
        # Collect all widgets first
        widgets_to_update = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widgets_to_update.append(widget)
        
        # Set all values first
        for widget in widgets_to_update:
            widget_on_state = widget.on_state()
            if str(widget_on_state) == target_on_state:
                widget.field_value = widget.on_state()
                print(f"   ✅ Set widget (on_state '{widget_on_state}') to selected")
            else:
                widget.field_value = False
                print(f"   ⚪ Set widget (on_state '{widget_on_state}') to deselected")
        
        # Then update all at once
        for widget in widgets_to_update:
            widget.update()
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_radio_minimal_touch(pdf_path, field_name, new_value):
    """Only touch widgets that actually need to change"""
    try:
        doc = fitz.open(pdf_path)
        
        target_on_state = str(new_value).lstrip("/")
        print(f"   🎯 Target on_state: '{target_on_state}'")
        
        # First, check current state
        widgets_info = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widgets_info.append({
                        'widget': widget,
                        'on_state': widget.on_state(),
                        'current_value': widget.field_value
                    })
        
        # Only update widgets that need to change
        changes_made = 0
        for info in widgets_info:
            widget = info['widget']
            widget_on_state = info['on_state']
            current_value = info['current_value']
            
            if str(widget_on_state) == target_on_state:
                # This should be selected
                expected_value = widget.on_state()
                if str(current_value) != str(expected_value):
                    widget.field_value = expected_value
                    widget.update()
                    changes_made += 1
                    print(f"   ✅ Selected widget (on_state '{widget_on_state}') - CHANGED")
                else:
                    print(f"   ✅ Widget (on_state '{widget_on_state}') already selected - NO CHANGE")
            else:
                # This should be deselected
                if str(current_value) != 'False' and str(current_value) != 'Off':
                    widget.field_value = False
                    widget.update()
                    changes_made += 1
                    print(f"   ⚪ Deselected widget (on_state '{widget_on_state}') - CHANGED")
                else:
                    print(f"   ⚪ Widget (on_state '{widget_on_state}') already deselected - NO CHANGE")
        
        print(f"   📊 Total changes made: {changes_made}")
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_radio_update_methods() 