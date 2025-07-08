#!/usr/bin/env python3
"""
Inspect available values for checkbox and radio button fields
"""

import fitz
from pathlib import Path

def inspect_field_values():
    """Inspect the available values for form fields"""
    
    pdf_path = Path("pdf.pdf")
    doc = fitz.open(pdf_path)
    
    print("Inspecting form field values...")
    
    # Fields of interest
    target_fields = ["18a", "5", "13", "14", "15a", "15b"]  # Some checkboxes and radio buttons
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name in target_fields:
                print(f"\n{'='*50}")
                print(f"Field: {widget.field_name}")
                print(f"Type: {widget.field_type_string}")
                print(f"Current Value: {widget.field_value}")
                
                # Try to get choice options if available
                if hasattr(widget, 'choice_values'):
                    print(f"Choice Values: {widget.choice_values}")
                
                # Additional properties that exist
                print(f"Field Flags: {widget.field_flags}")
                if hasattr(widget, 'field_label'):
                    print(f"Field Label: {widget.field_label}")
                
                # List all available attributes
                print("Available attributes:")
                attrs = [attr for attr in dir(widget) if not attr.startswith('_')]
                for attr in attrs:
                    try:
                        value = getattr(widget, attr)
                        if not callable(value):
                            print(f"  {attr}: {value}")
                    except:
                        print(f"  {attr}: <unable to access>")
    
    doc.close()

if __name__ == "__main__":
    inspect_field_values() 