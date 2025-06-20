#!/usr/bin/env python3
"""
PDF Form Field Editor using PyMuPDF (fitz)
More reliable approach that doesn't corrupt form fields
"""

import sys
import os
import fitz  # PyMuPDF

def load_field_dictionary():
    """Load the field dictionary for human-readable names"""
    pdf_dict = {
        "1": {"name": "Antragsnummer", "type": "text"},
        "2a": {"name": "Antragsteller Name", "type": "text"},
        "2b": {"name": "Antragserstellungsdatum", "type": "text"},
        "2c": {"name": "Antragsteller Abteilung", "type": "text"},
        "2d": {"name": "Antragsteller Telefonnummer", "type": "text"},
        "3": {"name": "Benennung", "type": "text"},
        "4": {"name": "Fremdteilenummer", "type": "text"},
        "5": {"name": "Kennzeichnung des Bedarfs", "type": "btn", "values": {"Neubedarf": "0", "Bedarfsänderung": "1"}},
        "6": {"name": "Kennzeichnung des Produkts", "type": "btn", "values": {"Stoff": "0", "Teil": "1"}},
        "7": {"name": "REACh-Code", "type": "text"},
        "8": {"name": "Lieferant", "type": "text"},
        "9": {"name": "Hersteller", "type": "text"},
        "10": {"name": "Verwendungszweck, Anforderungsgrund, Prozessbeschreibung, Anwendungsform", "type": "text"},
        "11": {"name": "Triebwerksprogramm", "type": "text"},
        "12a": {"name": "Einsatzort / Standort", "type": "text"},
        "12b": {"name": "Bereich Teamleiter*innen", "type": "text"},
        "13": {"name": "Erzeugnisrelevanz", "type": "btn", "values": {"Ja": "0", "Nein": "1"}},
        "14": {"name": "Nutzung", "type": "btn", "values": {"kurzfristig": "0", "langfristig": "1"}},
        "15a": {"name": "Lagerhaltig?", "type": "btn", "values": {"Ja": "0", "Nein": "1"}},
        "15b": {"name": "Bestellung über SAP?", "type": "btn", "values": {"Ja": "0", "Nein": "1"}},
        "16": {"name": "Basismengeneinheit SAP", "type": "text"},
        "17a": {"name": "monatlicher Bedarf", "type": "text"},
        "17b": {"name": "Häufigkeit der Anwendung", "type": "text"},
        "17c": {"name": "Menge pro Anwendung", "type": "text"},
        "18a": {"name": "EU-Sicherheitsdatenblatt", "type": "btn", "values": {"Ja": "Yes", "Nein": "Off"}},
        "18b": {"name": "Technisches Datenblatt", "type": "btn", "values": {"Ja": "Yes", "Nein": "Off"}},
        "18c": {"name": "Gefährdungsbeurteilung", "type": "btn", "values": {"Ja": "Yes", "Nein": "Off"}},
        "18d": {"name": "Produktzulassung nach", "type": "btn", "values": {"Ja": "Yes", "Nein": "Off"}},
        "18e": {"name": "Produktzulassung nach Spezifikation", "type": "text"},
        "19": {"name": "Erläuterungen", "type": "text"},
        "20": {"name": "Verweis auf vergangene Anträge", "type": "text"},
        "21": {"name": "Wunschtermin für Produkteinsatz", "type": "text"},
    }
    return pdf_dict

def get_form_fields(doc):
    """Get all form fields from the PDF document"""
    fields = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        widgets = page.widgets()
        for widget in widgets:
            if widget.field_name:  # Only include named fields
                fields.append({
                    'name': widget.field_name,
                    'type': widget.field_type_string,
                    'value': widget.field_value,
                    'page': page_num + 1,
                    'widget': widget
                })
    return fields

def display_form_fields(fields, pdf_dict):
    """Display all form fields with their current values"""
    if not fields:
        print("No form fields found in PDF")
        return None
    
    print("\nAvailable Form Fields:")
    print("=" * 60)
    
    field_list = []
    display_index = 1
    
    for field in fields:
        field_name = field['name']
        field_type = field['type']
        current_value = field['value'] or "Empty"
        
        # Skip signature fields
        if field_type == 'Signature':
            continue
            
        # Get human-readable name
        display_name = field_name
        if field_name in pdf_dict:
            display_name = pdf_dict[field_name]["name"]
        
        print(f"{display_index:2d}. [{field_name}] {display_name}")
        print(f"    Type: {field_type} | Current: {current_value} | Page: {field['page']}")
        print()
        
        field_list.append(field)
        display_index += 1
    
    return field_list

def edit_text_field(field, display_name):
    """Edit a text field"""
    current_value = field['value'] or ""
    print(f"\nEditing Text Field: {display_name}")
    print(f"Current value: {current_value}")
    print("Enter new value (or press Enter to keep current):")
    
    new_value = input("> ")
    if new_value.strip():
        return new_value
    return current_value

def edit_button_field(field, display_name, pdf_dict):
    """Edit a button/checkbox field"""
    field_name = field['name']
    current_value = field['value'] or ""
    
    print(f"\nEditing Button Field: {display_name}")
    print(f"Current value: {current_value}")
    
    if field_name in pdf_dict and "values" in pdf_dict[field_name]:
        options = pdf_dict[field_name]["values"]
        print("Available options:")
        for i, (label, value) in enumerate(options.items(), 1):
            current_marker = " (current)" if str(value) == str(current_value) else ""
            print(f"{i}. {label} -> {value}{current_marker}")
        
        print("Select option number (or press Enter to keep current):")
        choice = input("> ")
        
        if choice.strip().isdigit():
            choice_num = int(choice.strip())
            if 1 <= choice_num <= len(options):
                selected_value = list(options.values())[choice_num - 1]
                return selected_value
    else:
        # For fields without predefined options, allow manual input
        print("Enter new value (or press Enter to keep current):")
        new_value = input("> ")
        if new_value.strip():
            return new_value
    
    return current_value

def update_pdf_fields(doc, field_updates):
    """Update PDF form fields using PyMuPDF"""
    updated_count = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        widgets = page.widgets()
        
        for widget in widgets:
            if widget.field_name in field_updates:
                new_value = field_updates[widget.field_name]
                try:
                    # Update the widget value
                    widget.field_value = new_value
                    widget.update()
                    print(f"Updated field '{widget.field_name}' to '{new_value}' on page {page_num + 1}")
                    updated_count += 1
                except Exception as e:
                    print(f"Error updating field '{widget.field_name}': {e}")
    
    return updated_count

def main():
    if len(sys.argv) < 2:
        print("PDF Form Field Editor using PyMuPDF")
        print("Usage: python pdf_edit_fitz.py <input_pdf> [output_pdf]")
        print("Example: python pdf_edit_fitz.py document.pdf edited_document.pdf")
        print("\nNote: Requires PyMuPDF - install with: pip install PyMuPDF")
        return
    
    input_pdf_path = sys.argv[1]
    output_pdf_path = sys.argv[2] if len(sys.argv) > 2 else "edited_" + os.path.basename(input_pdf_path)
    
    if not os.path.exists(input_pdf_path):
        print(f"Error: PDF file not found: {input_pdf_path}")
        return
    
    try:
        # Open PDF document
        doc = fitz.open(input_pdf_path)
        pdf_dict = load_field_dictionary()
        
        print(f"Loaded PDF: {input_pdf_path}")
        print(f"Pages: {len(doc)}")
        
        # Get all form fields
        all_fields = get_form_fields(doc)
        field_updates = {}
        
        while True:
            # Display form fields
            field_list = display_form_fields(all_fields, pdf_dict)
            if not field_list:
                break
            
            print("Options:")
            print("- Enter field number to edit")
            print("- Type 'save' to save changes and exit")
            print("- Type 'quit' to exit without saving")
            
            choice = input("\nYour choice: ").strip().lower()
            
            if choice == 'save':
                if field_updates:
                    print(f"\nSaving {len(field_updates)} field updates...")
                    updated_count = update_pdf_fields(doc, field_updates)
                    
                    if updated_count > 0:
                        # Save the document
                        doc.save(output_pdf_path)
                        print(f"Successfully updated {updated_count} fields")
                        print(f"PDF saved to: {output_pdf_path}")
                    else:
                        print("No fields were updated.")
                else:
                    print("No changes to save.")
                break
                
            elif choice == 'quit':
                print("Exiting without saving changes.")
                break
                
            elif choice.isdigit():
                field_num = int(choice)
                if 1 <= field_num <= len(field_list):
                    field = field_list[field_num - 1]
                    field_name = field['name']
                    field_type = field['type']
                    
                    # Get display name
                    display_name = field_name
                    if field_name in pdf_dict:
                        display_name = pdf_dict[field_name]["name"]
                    
                    # Edit based on field type
                    if field_type in ['Text', 'FreeText']:
                        new_value = edit_text_field(field, display_name)
                        if new_value != (field['value'] or ""):
                            field_updates[field_name] = new_value
                            print(f"Field '{field_name}' updated!")
                    elif field_type in ['CheckBox', 'RadioButton', 'Button']:
                        new_value = edit_button_field(field, display_name, pdf_dict)
                        if str(new_value) != str(field['value'] or ""):
                            field_updates[field_name] = new_value
                            print(f"Field '{field_name}' updated!")
                    else:
                        print(f"Field type '{field_type}' not fully supported yet.")
                        # Still allow manual editing
                        print("Enter new value (or press Enter to skip):")
                        new_value = input("> ")
                        if new_value.strip():
                            field_updates[field_name] = new_value
                            print(f"Field '{field_name}' updated!")
                else:
                    print("Invalid field number.")
            else:
                print("Invalid choice. Please try again.")
        
        # Close the document
        doc.close()
        
    except ImportError:
        print("Error: PyMuPDF not installed. Install with: pip install PyMuPDF")
    except Exception as e:
        print(f"Error processing PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 