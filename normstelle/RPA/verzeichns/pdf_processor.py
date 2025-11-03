"""
PDF Processing Module for CMSR Automation

Extracts form fields from PDF files in memory and processes them for Excel writing.
Uses the existing pdf_fields.py module for extraction, then processes data in memory.
"""

import sys
from pathlib import Path

# Add the pdfparser directory to path to import pdf_fields
pdfparser_path = Path(__file__).parent.parent / "pdfparser" / "pdf"
sys.path.insert(0, str(pdfparser_path))

from pdf_fields import extract_form_fields

# PDF field definitions (from pdf_decode.py)
pdf_dict = {
    "1": {"name": "Antragsnummer", "type": "text"},
    "2a": {"name": "Antragsteller Name", "type": "text"},
    "2b": {"name": "Antragserstellungsdatum", "type": "text"},
    "2c": {"name": "Antragsteller Abteilung", "type": "text"},
    "2d": {"name": "Antragsteller Telefonnummer", "type": "text"},
    "3": {"name": "Benennung", "type": "text"},
    "4": {"name": "Fremdteilenummer", "type": "text"},
    "5": {"name": "Kennzeichnung des Bedarfs", "type": "btn", "values": {"Neubedarf": "/0", "Bedarfsänderung": "/1"}},
    "6": {"name": "Kennzeichnung des Produkts", "type": "btn", "values": {"Stoff": "/0", "Teil": "/1"}},
    "7": {"name": "REACh-Code", "type": "text"},
    "8": {"name": "Lieferant", "type": "text"},
    "9": {"name": "Hersteller", "type": "text"},
    "10": {"name": "Verwendungszweck, Anforderungsgrund, Prozessbeschreibung, Anwendungsform", "type": "text"},
    "11": {"name": "Triebwerksprogramm", "type": "text"},
    "12a": {"name": "Einsatzort / Standort", "type": "text"},
    "12b": {"name": "Bereich Teamleiter*innen", "type": "text"},
    "13": {"name": "Erzeugnisrelevanz", "type": "btn", "values": {"Ja": "/0", "Nein": "/1"}},
    "14": {"name": "Nutzung", "type": "btn", "values": {"kurzfristig": "/0", "langfristig": "/1"}},
    "15a": {"name": "Lagerhaltig?", "type": "btn", "values": {"Ja": "/0", "Nein": "/1"}},
    "15b": {"name": "Bestellung über SAP?", "type": "btn", "values": {"Ja": "/0", "Nein": "/1"}},
    "16": {"name": "Basismengeneinheit SAP", "type": "text"},
    "17a": {"name": "monatlicher Bedarf", "type": "text"},
    "17b": {"name": "Häufigkeit der Anwendung", "type": "text"},
    "17c": {"name": "Menge pro Anwendung", "type": "text"},
    "18a": {"name": "EU-Sicherheitsdatenblatt", "type": "btn", "values": {"Ja": "/Ja", "Nein": "/Off"}},
    "18b": {"name": "Technisches Datenblatt", "type": "btn", "values": {"Ja": "/Ja", "Nein": "/Off"}},
    "18c": {"name": "Gefährdungsbeurteilung", "type": "btn", "values": {"Ja": "/Ja", "Nein": "/Off"}},
    "18d": {"name": "Produktzulassung nach", "type": "btn", "values": {"Ja": "/Ja", "Nein": "/Off"}},
    "18e": {"name": "Produktzulassung nach Spezifikation", "type": "text"},
    "19": {"name": "Erläuterungen", "type": "text"},
    "20": {"name": "Verweis auf vergangene Anträge", "type": "text"},
    "21": {"name": "Wunschtermin für Produkteinsatz", "type": "text"}
}

def extract_pdf_fields_memory(pdf_path):
    """
    Extract form fields from PDF using pdf_fields.py and return processed data in memory.
    Returns dict with field values ready for Excel processing.
    """
    print(f"Processing PDF: {pdf_path}")
    
    # Use existing pdf_fields.py to extract form fields (returns dict, no JSON file created)
    form_fields = extract_form_fields(pdf_path, None)  # Pass None to avoid writing JSON file
    
    if not form_fields:
        print("No form fields found in PDF")
        return None
    
    print(f"Found {len(form_fields)} form fields")
    
    extracted_data = {}
    
    # Process each field and extract values
    for field_name, field_data in form_fields.items():
        field_value = extract_field_value(field_name, field_data)
        
        if field_value is not None:
            extracted_data[field_name] = field_value
            
            # Debug output
            if field_name in pdf_dict:
                field_desc = pdf_dict[field_name]["name"]
                print(f"  {field_name} ({field_desc}): {field_value}")
    
    return extracted_data

def extract_field_value(field_name, field_data):
    """
    Extract the actual value from a PDF field based on its type.
    """
    # Text fields
    if "/FT" in field_data and field_data["/FT"] == "/Tx":
        if "/V" in field_data:
            text = field_data["/V"].strip().replace("\r", " ")
            return text if text else None
        return None
    
    # Button fields (checkboxes, radio buttons)
    if "/FT" in field_data and field_data["/FT"] == "/Btn":
        if "/V" in field_data:
            value = field_data["/V"]
            
            # Try to get human-readable value from definitions
            if field_name in pdf_dict and "values" in pdf_dict[field_name]:
                for label, state in pdf_dict[field_name]["values"].items():
                    if state == value:
                        return label
            
            # Return raw value if no mapping found
            return value
        return None
    
    # Signature fields
    if "/FT" in field_data and field_data["/FT"] == "/Sig":
        if "/V" in field_data:
            return "SIGNED"
        return "NOT_SIGNED"
    
    return None

def validate_neubedarf(extracted_data):
    """
    Validate that this is a 'Neubedarf' (new requirement) request.
    Returns True if valid, False otherwise.
    """
    bedarf_field = extracted_data.get("5")  # Field 5: Kennzeichnung des Bedarfs
    
    if bedarf_field == "Neubedarf":
        print("✓ Validated: This is a Neubedarf (new requirement)")
        return True
    elif bedarf_field == "Bedarfsänderung":
        print("✗ Error: This is a Bedarfsänderung (requirement change) - not supported yet")
        return False
    else:
        print(f"✗ Error: Unknown requirement type: {bedarf_field}")
        return False

def process_pdf_for_excel(pdf_path):
    """
    Main function to process PDF and return data ready for Excel writing.
    """
    # Extract fields from PDF
    extracted_data = extract_pdf_fields_memory(pdf_path)
    
    if not extracted_data:
        return None
    
    # Validate this is a Neubedarf
    if not validate_neubedarf(extracted_data):
        return None
    
    print(f"Successfully processed PDF with {len(extracted_data)} fields")
    return extracted_data

# Test function
if __name__ == "__main__":
    test_pdf = Path(__file__).parent.parent / "pdfparser" / "Antrag T&S Huby Swab Wattestäbchen.pdf"
    
    if test_pdf.exists():
        result = process_pdf_for_excel(test_pdf)
        if result:
            print(f"\nExtracted {len(result)} fields successfully")
            # Print some key fields for verification
            key_fields = ["1", "2a", "3", "5", "13"]
            for field in key_fields:
                if field in result:
                    print(f"Key field {field}: {result[field]}")
    else:
        print(f"Test PDF not found at: {test_pdf}")
