#!/usr/bin/env python3
"""
Debug script to examine checkbox and radio button field types
"""

import fitz

def debug_all_field_types():
    """Debug the actual widget types for checkbox and radio button fields"""
    
    pdf_path = "pdf.pdf"
    checkbox_fields = ["18a", "18b", "18c", "18d", "23a3"]
    radio_fields = ["5", "6", "13", "14", "15a"]
    text_fields = ["1", "3", "4", "7", "9"]
    
    print("🔍 Debugging All Field Types")
    print("=" * 60)
    
    try:
        doc = fitz.open(pdf_path)
        
        # Test checkbox fields
        print("\n🔲 CHECKBOX FIELDS")
        print("=" * 40)
        for field_name in checkbox_fields:
            debug_field(doc, field_name, "checkbox")
        
        # Test radio button fields
        print("\n🔘 RADIO BUTTON FIELDS")
        print("=" * 40)
        for field_name in radio_fields:
            debug_field(doc, field_name, "radio")
        
        # Test text fields
        print("\n📝 TEXT FIELDS")
        print("=" * 40)
        for field_name in text_fields:
            debug_field(doc, field_name, "text")
        
        doc.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def debug_field(doc, field_name, expected_type):
    """Debug a single field"""
    print(f"\n📋 Field: {field_name} (expected: {expected_type})")
    
    widgets_found = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                widgets_found.append({
                    'page': page_num + 1,
                    'field_type': widget.field_type,
                    'field_type_string': widget.field_type_string,
                    'current_value': widget.field_value,
                    'on_state': widget.on_state() if hasattr(widget, 'on_state') else 'N/A'
                })
    
    if widgets_found:
        print(f"   ✅ Found {len(widgets_found)} widget(s)")
        for i, widget_info in enumerate(widgets_found):
            print(f"   Widget {i+1}:")
            print(f"     Page: {widget_info['page']}")
            print(f"     Type: {widget_info['field_type']}")
            print(f"     Type String: '{widget_info['field_type_string']}'")
            print(f"     Current Value: '{widget_info['current_value']}'")
            print(f"     On State: {widget_info['on_state']}")
        
        # Determine what our get_field_type function would return
        widget_count = len(widgets_found)
        widget_type_str = widgets_found[0]['field_type_string'].lower()
        
        if "checkbox" in widget_type_str:
            detected_type = "checkbox"
        elif "button" in widget_type_str:
            detected_type = "radio" if widget_count > 1 else "checkbox"
        elif "text" in widget_type_str:
            detected_type = "text"
        else:
            detected_type = "unknown"
        
        if detected_type == expected_type:
            print(f"   ✅ Detection: {detected_type} (CORRECT)")
        else:
            print(f"   ❌ Detection: {detected_type} (WRONG - expected {expected_type})")
    else:
        print(f"   ❌ No widgets found for field '{field_name}'")

if __name__ == "__main__":
    debug_all_field_types() 