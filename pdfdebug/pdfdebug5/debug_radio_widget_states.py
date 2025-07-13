#!/usr/bin/env python3
"""
Debug why some radio button update methods aren't applying changes
"""

import fitz
import shutil
from datetime import datetime

def debug_radio_widget_states():
    """Debug the current state of radio button widgets"""
    
    source_pdf = "pdf.pdf"
    field_name = "5"
    target_value = "/1"
    
    print("🔍 Debugging Radio Button Widget States")
    print("=" * 60)
    
    # Create test PDF
    timestamp = datetime.now().strftime("%H%M%S")
    test_pdf = f"test_pdf/radio_debug_{timestamp}.pdf"
    shutil.copy2(source_pdf, test_pdf)
    
    try:
        doc = fitz.open(test_pdf)
        
        print(f"📋 Analyzing field '{field_name}' with target value '{target_value}'")
        target_on_state = str(target_value).lstrip("/")
        
        # Get current state
        print(f"\n🔍 BEFORE UPDATE:")
        widgets_before = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widget_info = {
                        'page': page_num + 1,
                        'on_state': widget.on_state(),
                        'current_value': widget.field_value,
                        'widget': widget
                    }
                    widgets_before.append(widget_info)
                    print(f"   Widget on page {widget_info['page']}: on_state='{widget_info['on_state']}', current_value='{widget_info['current_value']}'")
        
        # Test the single widget approach with detailed debugging
        print(f"\n🔧 TESTING SINGLE WIDGET APPROACH:")
        print(f"   Target on_state: '{target_on_state}'")
        
        widget_found = False
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widget_on_state = widget.on_state()
                    print(f"   Checking widget: on_state='{widget_on_state}', target='{target_on_state}'")
                    
                    if str(widget_on_state) == target_on_state:
                        print(f"   ✅ Found target widget!")
                        print(f"      Current value: '{widget.field_value}'")
                        print(f"      Expected value: '{widget.on_state()}'")
                        
                        # Try to update it
                        try:
                            old_value = widget.field_value
                            widget.field_value = widget.on_state()
                            widget.update()
                            new_value = widget.field_value
                            
                            print(f"      Update result: '{old_value}' -> '{new_value}'")
                            widget_found = True
                            break
                        except Exception as e:
                            print(f"      ❌ Update failed: {e}")
            
            if widget_found:
                break
        
        if not widget_found:
            print(f"   ❌ No widget found with on_state '{target_on_state}'")
        
        # Check state after update
        print(f"\n🔍 AFTER UPDATE:")
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    print(f"   Widget on page {page_num + 1}: on_state='{widget.on_state()}', current_value='{widget.field_value}'")
        
        # Test if the issue is with radio button group behavior
        print(f"\n🔧 TESTING RADIO GROUP BEHAVIOR:")
        print("   Attempting to update all widgets in group...")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widget_on_state = widget.on_state()
                    old_value = widget.field_value
                    
                    if str(widget_on_state) == target_on_state:
                        # This should be selected
                        widget.field_value = widget.on_state()
                        print(f"   ✅ Set widget (on_state '{widget_on_state}') to selected")
                    else:
                        # This should be deselected
                        widget.field_value = False
                        print(f"   ⚪ Set widget (on_state '{widget_on_state}') to deselected")
                    
                    widget.update()
                    new_value = widget.field_value
                    print(f"      Value change: '{old_value}' -> '{new_value}'")
        
        # Final state check
        print(f"\n🔍 FINAL STATE:")
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    print(f"   Widget on page {page_num + 1}: on_state='{widget.on_state()}', current_value='{widget.field_value}'")
        
        doc.saveIncr()
        doc.close()
        
        print(f"\n✅ Debug completed")
        print(f"📄 Test PDF: {test_pdf}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_radio_widget_states() 