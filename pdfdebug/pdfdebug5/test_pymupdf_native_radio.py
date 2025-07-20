#!/usr/bin/env python3
"""
Test PyMuPDF's native field update methods for radio buttons
"""

import fitz
import shutil
import os
from datetime import datetime

def test_native_radio_update():
    """Test using PyMuPDF's native field update methods"""
    
    source_pdf = "pdf.pdf"
    
    if not os.path.exists(source_pdf):
        print(f"❌ Source PDF not found: {source_pdf}")
        return
    
    print("🔍 Testing PyMuPDF Native Radio Button Update")
    print("=" * 60)
    
    # Create test PDF
    timestamp = datetime.now().strftime("%H%M%S")
    test_pdf = f"test_pdf/radio_native_method_{timestamp}.pdf"
    shutil.copy2(source_pdf, test_pdf)
    
    try:
        doc = fitz.open(test_pdf)
        
        # Test field - radio button field 5
        field_name = "5"
        new_value = "/1"
        
        print(f"🔄 Testing native update for field '{field_name}' -> '{new_value}'")
        
        # Method 1: Try using set_field_value (if it exists)
        try:
            # This might not exist in all PyMuPDF versions
            success = doc.set_field_value(field_name, new_value)
            print(f"   📋 set_field_value result: {success}")
        except AttributeError:
            print("   ⚠️  set_field_value method not available")
        except Exception as e:
            print(f"   ❌ set_field_value error: {e}")
        
        # Method 2: Try using form field methods
        try:
            # Get form fields
            form_fields = doc.get_form_fields()
            if form_fields:
                print(f"   📋 Found {len(form_fields)} form fields")
                
                # Find our field
                target_field = None
                for field in form_fields:
                    if field.get('name') == field_name:
                        target_field = field
                        break
                
                if target_field:
                    print(f"   ✅ Found target field: {target_field}")
                else:
                    print(f"   ❌ Field '{field_name}' not found in form fields")
            else:
                print("   ⚠️  No form fields found")
        except AttributeError:
            print("   ⚠️  get_form_fields method not available")
        except Exception as e:
            print(f"   ❌ get_form_fields error: {e}")
        
        # Method 3: Try direct field update without widget manipulation
        try:
            target_on_state = str(new_value).lstrip("/")
            print(f"   🎯 Target on_state: '{target_on_state}'")
            
            # Find the field and update it more directly
            field_widgets = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                for widget in page.widgets():
                    if widget.field_name == field_name:
                        field_widgets.append({
                            'widget': widget,
                            'on_state': widget.on_state(),
                            'current_value': widget.field_value
                        })
            
            print(f"   📋 Found {len(field_widgets)} widgets for field '{field_name}'")
            
            # Update using a more direct approach
            for widget_info in field_widgets:
                widget = widget_info['widget']
                widget_on_state = widget_info['on_state']
                
                if str(widget_on_state) == target_on_state:
                    # This should be selected
                    widget.field_value = widget_on_state
                    print(f"   ✅ Set widget (on_state '{widget_on_state}') to selected")
                else:
                    # This should be deselected  
                    widget.field_value = False
                    print(f"   ⚪ Set widget (on_state '{widget_on_state}') to deselected")
            
            # Update all widgets at once without individual update() calls
            for widget_info in field_widgets:
                widget_info['widget'].update()
            
            print("   ✅ Native-style update completed")
            
        except Exception as e:
            print(f"   ❌ Direct field update error: {e}")
        
        # Save and close
        doc.saveIncr()
        doc.close()
        
        print(f"✅ Test completed successfully")
        print(f"📄 Test PDF: {test_pdf}")
        print("   📋 Please check signature validity in Adobe Acrobat")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_native_radio_update() 