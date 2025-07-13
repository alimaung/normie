#!/usr/bin/env python3
"""
Generate test PDFs for signature validation testing
"""

import fitz
import shutil
from datetime import datetime
import os

def generate_signature_test_pdfs():
    """Generate all test PDFs for signature validation testing"""
    
    source_pdf = "pdf.pdf"
    
    if not os.path.exists(source_pdf):
        print(f"❌ Source PDF not found: {source_pdf}")
        return
    
    print("🔍 Generating Signature Test PDFs")
    print("=" * 60)
    
    # Test approaches
    approaches = [
        {
            "name": "text_field_baseline",
            "description": "Text field update (baseline - should keep signature 'unknown')",
            "function": update_text_field
        },
        {
            "name": "checkbox_baseline", 
            "description": "Checkbox update (baseline - should keep signature 'unknown')",
            "function": update_checkbox_field
        },
        {
            "name": "radio_current_method",
            "description": "Radio button - current method (all widgets updated)",
            "function": update_radio_current_method
        },
        {
            "name": "radio_only_select_target",
            "description": "Radio button - only select target widget",
            "function": update_radio_only_select_target
        },
        {
            "name": "radio_deselect_all_then_select",
            "description": "Radio button - deselect all then select target",
            "function": update_radio_deselect_all_then_select
        }
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for approach in approaches:
        print(f"\n🧪 Generating: {approach['name']}")
        print(f"📄 Description: {approach['description']}")
        print("-" * 50)
        
        # Create test PDF
        test_pdf = f"test_pdf/signature_test_{approach['name']}_{timestamp}.pdf"
        shutil.copy2(source_pdf, test_pdf)
        
        # Apply the approach
        success = approach['function'](test_pdf)
        
        if success:
            print(f"✅ Generated: {test_pdf}")
        else:
            print(f"❌ Failed to generate: {test_pdf}")
    
    print(f"\n🎉 All test PDFs generated!")
    print(f"📋 Please test these PDFs in Adobe Acrobat to check signature validity:")
    print(f"   - Text and checkbox updates should show 'unknown' signature")
    print(f"   - Radio button updates may show 'invalid' signature")
    print(f"   - Look for any radio button method that preserves signature validity")

def update_text_field(pdf_path):
    """Update a text field (baseline test)"""
    try:
        doc = fitz.open(pdf_path)
        
        # Update text field 1
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == "1":
                    widget.field_value = "SIGNATURE-TEST-TEXT"
                    widget.update()
                    print(f"   ✅ Updated text field: {widget.field_name}")
                    break
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_checkbox_field(pdf_path):
    """Update a checkbox field (baseline test)"""
    try:
        doc = fitz.open(pdf_path)
        
        # Update checkbox field 18a
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == "18a":
                    widget.field_value = widget.on_state()
                    widget.update()
                    print(f"   ✅ Updated checkbox field: {widget.field_name}")
                    break
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_radio_current_method(pdf_path):
    """Update radio button using current method"""
    try:
        doc = fitz.open(pdf_path)
        
        field_name = "5"
        target_value = "/1"
        target_on_state = str(target_value).lstrip("/")
        
        # Current method: Update all widgets
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
                    widget.update()
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_radio_only_select_target(pdf_path):
    """Update radio button - only select target widget"""
    try:
        doc = fitz.open(pdf_path)
        
        field_name = "5"
        target_value = "/1"
        target_on_state = str(target_value).lstrip("/")
        
        # Only update the target widget
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widget_on_state = widget.on_state()
                    if str(widget_on_state) == target_on_state:
                        widget.field_value = widget.on_state()
                        widget.update()
                        print(f"   ✅ Selected target widget (on_state '{widget_on_state}')")
                        break
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_radio_deselect_all_then_select(pdf_path):
    """Update radio button - deselect all then select target"""
    try:
        doc = fitz.open(pdf_path)
        
        field_name = "5"
        target_value = "/1"
        target_on_state = str(target_value).lstrip("/")
        
        # Step 1: Deselect all widgets
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widget.field_value = False
                    widget.update()
        
        # Step 2: Select target widget
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widget_on_state = widget.on_state()
                    if str(widget_on_state) == target_on_state:
                        widget.field_value = widget.on_state()
                        widget.update()
                        print(f"   ✅ Selected target widget (on_state '{widget_on_state}')")
                        break
        
        doc.saveIncr()
        doc.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    generate_signature_test_pdfs() 