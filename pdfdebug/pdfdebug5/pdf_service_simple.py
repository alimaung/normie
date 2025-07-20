#!/usr/bin/env python3
"""
PDF Service Simple - Working Radio Button Method with Signature Preservation
Based on successful test_field_5.py and test_comprehensive_fields.py implementation
"""

import fitz
import json
import shutil
import os
from datetime import datetime

PDF_FIELD_DICT = {
    "1": {
        "name": "Antragsnummer",
        "type": "text",
    },
    "2a": {
        "name": "Antragsteller Name",
        "type": "text",
    },
    "2b": {
        "name": "Antragserstellungsdatum",
        "type": "text",
    },
    "2c": {
        "name": "Antragsteller Abteilung",
        "type": "text",
    },
    "2d": {
        "name": "Antragsteller Telefonnummer",
        "type": "text",
    },
    "3": {
        "name": "Benennung",
        "type": "text",
    },
    "4": {
        "name": "Fremdteilenummer",
        "type": "text",
    },
    "5": {
        "name": "Kennzeichnung des Bedarfs",
        "type": "btn",
        "values": {
            "Neubedarf": "/0",
            "Bedarfsänderung": "/1"
        },
    },
    "6": {
        "name": "Kennzeichnung des Produkts",
        "type": "btn",
        "values": {
            "Stoff": "/0",
            "Teil": "/1"
        },
    },
    "7": {
        "name": "REACh-Code",
        "type": "text",
    },
    "8": {
        "name": "Lieferant",
        "type": "text",
    },
    "9": {
        "name": "Hersteller",
        "type": "text",
    },
    "10": {
        "name": "Verwendungszweck, Anforderungsgrund, Prozessbeschreibung, Anwendungsform",
        "type": "text",
    },
    "11": {
        "name": "Triebwerksprogramm",
        "type": "text",
    },
    "12a": {
        "name": "Einsatzort / Standort",
        "type": "text",
    },
    "12b": {
        "name": "Bereich Teamleiter*innen",
        "type": "text",
    },
    "13": {
        "name": "Erzeugnisrelevant, besteht Kontakt mit Luftfahrtteilen?",
        "type": "btn",
        "values": {
            "Ja (Produktzulassung ist erforderlich)": "/0",
            "Nein (Produktzulassung ist nicht erforderlich)": "/1"
        },
    },
    "14": {
        "name": "Nutzung",
        "type": "btn",
        "values": {
            "kurzfristig": "/0",
            "langfristig": "/1"
        },
    },
    "15a": {
        "name": "Lagerhaltig?",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1"
        },
    },
    "15b": {
        "name": "Bestellung über SAP?",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1"
        },
    },
    "16": {
        "name": "Basismengeneinheit SAP",
        "type": "text",
    },
    "17a": {
        "name": "monatlicher Bedarf",
        "type": "text",
    },
    "17b": {
        "name": "Häufigkeit der Anwendung",
        "type": "text",
    },
    "17c": {
        "name": "Menge pro Anwendung",
        "type": "text",
    },
    "18a": {
        "name": "EU-Sicherheitsdatenblatt",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "18b": {
        "name": "Technisches Datenblatt",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "18c": {
        "name": "Gefährdungsbeurteilung",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "18d": {
        "name": "Produktzulassung nach",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "18e": {
        "name": "Produktzulassung nach Spezifikation",
        "type": "text",
    },
    "19": {
        "name": "Erläuterungen",
        "type": "text",
    },
    "20": {
        "name": "Verweis auf vergangene Anträge",
        "type": "text",
    },
    "21": {
        "name": "Wunschtermin für Produkteinsatz",
        "type": "text",
    },
    "22a": {
        "name": "ChemScan durch",
        "type": "text",
    },
    "22a1": {
        "name": "ChemScan Datum",
        "type": "text",
    },
    "22a2": {
        "name": "ChemScan durchgeführt",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1"
        },
    },
    "22b": {
        "name": "ChemScan durch",
        "type": "text",
    },
    "22b1": {
        "name": "ChemScan Datum",
        "type": "text",
    },
    "22b2": {
        "name": "ChemScan durchgeführt",
        "type": "btn",
        "values": {
            "Ja": "/1",
            "Nein": "/0"
        },
    },
    "23a1": {
        "name": "ChemVV",
        "type": "text",
    },
    "23a2": {
        "name": "Sonstige",
        "type": "text",
    },
    "23a3": {
        "name": "KMR (TRGS 905)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23a4": {
        "name": "ArbMedVV",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23a5": {
        "name": "SVHC / REACh XIV",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23a6": {
        "name": "ChemVV",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23a7": {
        "name": "AGW (TRGS 900)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23a8": {
        "name": "ODIN",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23a9": {
        "name": "REACh XVII",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23a10": {
        "name": "Sonstige",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23a11": {
        "name": "BGW (TRGS 903)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23a12": {
        "name": "ERB (Bek 910)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23a13": {
        "name": "Ex-Schutz",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23a14": {
        "name": "Physikalische Gefahr",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23b1": {
        "name": "ChemVV",
        "type": "text",
    },
    "23b2": {
        "name": "Sonstige",
        "type": "text",
    },
    "23b3": {
        "name": "KMR (TRGS 905)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23b4": {
        "name": "ArbMedVV",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23b5": {
        "name": "SVHC / REACh XIV",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23b6": {
        "name": "ChemVV",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23b7": {
        "name": "AGW (TRGS 900)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23b8": {
        "name": "ODIN",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23b9": {
        "name": "REACh XVII",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23b10": {
        "name": "Sonstige",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23b11": {
        "name": "BGW (TRGS 903)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23b12": {
        "name": "ERB (Bek 910)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23b13": {
        "name": "Ex-Schutz",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "23b14": {
        "name": "Physikalische Gefahr",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24a1": {
        "name": "AWSV - WGK =",
        "type": "text",
    },
    "24a2": {
        "name": "ADR - UN Nr. =",
        "type": "text",
    },
    "24a3": {
        "name": "TRGS 510- Lagerkl. =",
        "type": "text",
    },
    "24a4": {
        "name": "SVHC PBT",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24a5": {
        "name": "AWSV - WGK =",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24a6": {
        "name": "ADR - UN Nr. =",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24a7": {
        "name": "TRGS 510- Lagerkl. =",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24a8": {
        "name": "SVHC vPvB",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24a9": {
        "name": "2.BImSchV (KMR Kat1)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24a10": {
        "name": "12.BImSchV (H1, H2, P8)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24a11": {
        "name": "31.BImSchV (VOC)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24b1": {
        "name": "AWSV - WGK =",
        "type": "text",
    },
    "24b2": {
        "name": "ADR - UN Nr. =",
        "type": "text",
    },
    "24b3": {
        "name": "TRGS 510- Lagerkl. =",
        "type": "text",
    },
    "24b4": {
        "name": "SVHC PBT",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24b5": {
        "name": "AWSV - WGK =",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24b6": {
        "name": "ADR - UN Nr. =",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24b7": {
        "name": "TRGS 510- Lagerkl. =",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24b8": {
        "name": "SVHC vPvB",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24b9": {
        "name": "2.BImSchV (KMR Kat1)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24b10": {
        "name": "12.BImSchV (H1, H2, P8)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "24b11": {
        "name": "31.BImSchV (VOC)",
        "type": "btn",
        "values": {
            "Ja": "/Ja",
            "Nein": "/Off"
        },
    },
    "25a": {
        "name": "Umweltschutz Name",
        "type": "text",
    },
    "25b": {
        "name": "Umweltschutz Unterschrift",
        "type": "sig",
    },
    "25c": {
        "name": "Datum der Umweltschutz Prüfung",
        "type": "text",
    },
    "26": {
        "name": "Ergebnis der Prüfung für Umweltschutz",
        "type": "btn",
        "values": {
            "Genehmigt": "/0",
            "Nicht genehmigt": "/1",
            "Genehmigt mit Einschränkung": "/2"
        },
    },
    "27": {
        "name": "BImSch-Genehmigung erfoderlich?",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1"
        },
    },
    "28": {
        "name": "AwSV Anlage erforderlich?",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1"
        },
    },
    "29": {
        "name": "Beteiligung Umweltschutz bei Gefährdungsbeurteilung erforderlich?",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1"
        },
    },
    "30": {
        "name": "Zusammenlagerung zu beachten?",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1"
        },
    },
    "31": {
        "name": "Erläuterungen - Erläuterungen zur Freigabe und Hinweise für den Wareneingang.",
        "type": "text",
    },
    "32a": {
        "name": "Arbeits- & Gesundheitschutz Name",
        "type": "text",
    },
    "32b": {
        "name": "Arbeits- & Gesundheitschutz Unterschrift",
        "type": "sig",
    },
    "32c": {
        "name": "Datum der Arbeits- & Gesundheitschutz Prüfung",
        "type": "text",
    },
    "33": {
        "name": "Ergebnis der Prüfung für Arbeits- & Gesundheitsschutz",
        "type": "btn",
        "values": {
            "Genehmigt": "/2",
            "Nicht genehmigt": "/1",
            "Genehmigt mit Einschränkung": "/0"
        },
    },
    "34": {
        "name": "Produkt ist HS&E-relevant?",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1"
        },
    },
    "35": {
        "name": "Information an Lager erforderlich?",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1"
        },
    },
    "36": {
        "name": "Gefahrstoffspezifische Gefährdungsbeurteilung erforderlich?",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1"
        },
    },
    "37": {
        "name": "Betriebsanweisung erforderlich?",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1"
        },
    },
    "38": {
        "name": "Erläuterungen - Erläuterungen zur Freigabe und Hinweise für den Wareneingang.",
        "type": "text",
    },
    "39": {
        "name": "Produkt und Lieferantenzulassung",
        "type": "btn",
        "values": {
            "erforderlich und nicht vorhanden": "/0",
            "erforderlich und vorhanden": "/1",
            "nicht erforderlich": "/2",
            "nicht möglich": "/3",
        },
    },
    "39a": {
        "name": "nicht möglich / Ablehnung Grund:",
        "type": "text",
    },
    "40a": {
        "name": "Fertigungslabor Name",
        "type": "text",
    },
    "40b": {
        "name": "Fertigungslabor Unterschrift",
        "type": "sig",
    },
    "40c": {
        "name": "Datum der Fertigungslabor Prüfung",
        "type": "text",
    },
    "41": {
        "name": "Haltbarkeit bei Bestellung",
        "type": "btn",
        "values": {
            "Ablauf zu max. 1/4": "/0",
            "Mindesthaltbarkeit": "/1",
            "keine Einschränkung": "/2",
        },
    },
    "41a": {
        "name": "Tagen",
        "type": "text",
    },
    "42": {
        "name": "Zertifikat (nach DIN EN 10204)",
        "type": "btn",
        "values": {
            "2.1": "/0",
            "3.1": "/1",
            "Andere": "/2",
            "nicht erforderlich": "/3",
        },
    },
    "42a": {
        "name": "Andere Zertifikat",
        "type": "text",
    },
    "43": {
        "name": "MLC104-Eintrag erforderlich?",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1",
            "bereits eingetragen": "/2",
        },
    },
    "44": {
        "name": "OMat-Eintrag erforderlich?",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1",
            "bereits eingetragen": "/2",
        },
    },
    "44a": {
        "name": "OMat Nr.",
        "type": "text",
    },
    "45": {
        "name": "Produktzulassung nach:",
        "type": "text",
    },
    "46": {
        "name": "Lieferantenanforderung / Produktzulassungsforderungen",
        "type": "text",
    },
    "47a": {
        "name": "Fertigungslabor Name",
        "type": "text",
    },
    "47b": {
        "name": "Fertigungslabor Unterschrift",
        "type": "sig",
    },
    "47c": {
        "name": "Datum der Fertigungslabor Prüfung",
        "type": "text",
    },
    "48": {
        "name": "Zertifikat (nach DIN EN 10204)",
        "type": "btn",
        "values": {
            "2.1": "/0",
            "3.1": "/1",
            "Andere": "/2",
            "nicht erforderlich": "/3",
        },
    },
    "48a": {
        "name": "Andere Zertifikat",
        "type": "text",
    },
    "49": {
        "name": "Lieferantenanforderung / Produktzulassungsforderungen",
        "type": "text",
    },
    "50a": {
        "name": "Normenstelle Name",
        "type": "text",
    },
    "50b": {
        "name": "Normenstelle Unterschrift",
        "type": "sig",
    },
    "50c": {
        "name": "Normenstelle Datum",
        "type": "text",
    },
    "51": {
        "name": "Teilenummer",
        "type": "text",
    },
    "52": {
        "name": "Erläuterungen bzw. Änderungen",
        "type": "text",
    },
}

def update_pdf_fields(pdf_path, field_updates, output_path=None):
    """
    Update PDF form fields with proper radio button handling and signature preservation
    
    Args:
        pdf_path: Path to the source PDF file
        field_updates: Dictionary of field updates {field_name: new_value}
        output_path: Optional output path (defaults to overwriting source)
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    # Use source path as output if not specified
    if output_path is None:
        output_path = pdf_path
    
    print(f"🔄 Updating PDF fields...")
    print(f"📄 Source: {pdf_path}")
    print(f"📄 Output: {output_path}")
    print(f"🔧 Fields to update: {list(field_updates.keys())}")
    
    try:
        # Open PDF document - single session for signature preservation
        doc = fitz.open(pdf_path)
        
        # Track successful updates
        successful_updates = []
        failed_updates = []
        
        # Process each field update
        for field_name, new_value in field_updates.items():
            print(f"\n🔧 Processing field '{field_name}' -> '{new_value}'")
            
            # Skip signature fields completely
            if is_signature_field(doc, field_name):
                print(f"   ⚠️  Skipping signature field '{field_name}'")
                continue
            
            # Determine field type and handle accordingly
            field_type = get_field_type(doc, field_name)
            
            try:
                if field_type == "radio":
                    success = handle_radio_button_field(doc, field_name, new_value)
                elif field_type == "checkbox":
                    success = handle_checkbox_field(doc, field_name, new_value)
                elif field_type == "text":
                    success = handle_text_field(doc, field_name, new_value)
                else:
                    print(f"   ❌ Unknown field type: {field_type}")
                    success = False
                
                if success:
                    successful_updates.append(field_name)
                    print(f"   ✅ Successfully updated field '{field_name}'")
                else:
                    failed_updates.append(field_name)
                    print(f"   ❌ Failed to update field '{field_name}'")
                    
            except Exception as e:
                print(f"   ❌ Error updating field '{field_name}': {e}")
                failed_updates.append(field_name)
        
        # Save with incremental save for signature preservation
        print(f"\n💾 Saving PDF...")
        if output_path != pdf_path:
            # If different output path, save normally first
            doc.save(output_path)
        else:
            # If same path, use incremental save
            doc.saveIncr()
        
        doc.close()
        
        # Report results
        print(f"\n📊 Update Summary:")
        print(f"   ✅ Successful: {len(successful_updates)} fields")
        print(f"   ❌ Failed: {len(failed_updates)} fields")
        
        if successful_updates:
            print(f"   ✅ Updated fields: {', '.join(successful_updates)}")
        
        if failed_updates:
            print(f"   ❌ Failed fields: {', '.join(failed_updates)}")
        
        return len(failed_updates) == 0
        
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return False

def handle_radio_button_field(doc, field_name, new_value):
    """
    Handle radio button fields using the working on_state() method
    Based on successful test_comprehensive_fields.py implementation
    """
    print(f"   🔘 Handling radio button field '{field_name}'")
    
    # Find all widgets for this field
    field_widgets = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                try:
                    on_state = widget.on_state()
                    field_widgets.append({
                        'page_num': page_num,
                        'on_state': on_state,
                        'current_value': widget.field_value,
                        'field_type': widget.field_type_string
                    })
                    print(f"   📊 Found widget on page {page_num + 1}, on_state: {on_state}, current: {widget.field_value}")
                except Exception as e:
                    print(f"   ❌ Error getting widget info: {e}")
    
    if not field_widgets:
        print(f"   ❌ No widgets found for field '{field_name}'")
        return False
    
    print(f"   ✅ Found {len(field_widgets)} widget(s) for field '{field_name}'")
    
    # Convert new_value to target on_state
    # Handle both "/0" format and direct "0" format
    target_on_state = str(new_value).lstrip("/")
    print(f"   🎯 Looking for widget with on_state '{target_on_state}'")
    
    # Set the correct radio button - get fresh widget references
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    try:
                        widget_on_state = widget.on_state()
                        if str(widget_on_state) == target_on_state:
                            # Set this widget to its on_state (selected)
                            widget.field_value = widget.on_state()
                            print(f"   ✅ Setting widget (on_state '{widget_on_state}') to selected")
                        else:
                            # Set other widgets to False (deselected)
                            widget.field_value = False
                            print(f"   ✅ Setting widget (on_state '{widget_on_state}') to off")
                        widget.update()
                    except Exception as e:
                        print(f"   ❌ Error setting widget: {e}")
                        return False
        
        # Verify the final values
        print(f"   📊 Final values:")
        for page_num in range(len(doc)):
            page = doc[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    try:
                        final_value = widget.field_value
                        on_state = widget.on_state()
                        print(f"   📊 Widget (on_state '{on_state}'): '{final_value}'")
                    except Exception as e:
                        print(f"   ❌ Error reading final value: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to set radio button: {e}")
        return False

def handle_checkbox_field(doc, field_name, new_value):
    """
    Handle checkbox fields using the working on_state() method
    Based on successful test_comprehensive_fields.py implementation
    """
    print(f"   ☑️  Handling checkbox field '{field_name}'")
    
    # Convert new_value to boolean
    target_checked = bool(new_value)
    if isinstance(new_value, str):
        target_checked = new_value.lower() in ['true', '1', 'yes', 'on', 'checked']
    
    print(f"   🎯 Setting checkbox to: {'checked' if target_checked else 'unchecked'}")
    
    # Find and process checkbox widgets
    field_found = False
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                field_found = True
                print(f"   ✅ Found checkbox '{field_name}' on page {page_num + 1}")
                print(f"   📊 Field type: {widget.field_type_string}")
                print(f"   📊 Current value: {widget.field_value}")
                
                try:
                    if target_checked:
                        # Check the checkbox - try on_state() first, fallback to True
                        try:
                            on_state = widget.on_state()
                            widget.field_value = on_state
                            print(f"   ✅ Setting checkbox to checked (on_state: {on_state})")
                        except:
                            widget.field_value = True
                            print(f"   ✅ Setting checkbox to checked (True)")
                    else:
                        # Uncheck the checkbox
                        widget.field_value = False
                        print(f"   ✅ Setting checkbox to unchecked (False)")
                    
                    widget.update()
                    
                    # Verify the value was set
                    new_value_check = widget.field_value
                    print(f"   📊 Result after setting: '{new_value_check}'")
                    
                    return True
                    
                except Exception as e:
                    print(f"   ❌ Failed to set checkbox: {e}")
                    return False
    
    if not field_found:
        print(f"   ❌ Checkbox field '{field_name}' not found")
        return False
    
    return True

def handle_text_field(doc, field_name, new_value):
    """Handle text fields - simple value assignment"""
    print(f"   📝 Handling text field '{field_name}'")
    
    field_found = False
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                field_found = True
                print(f"   ✅ Found text field '{field_name}' on page {page_num + 1}")
                print(f"   📊 Current value: '{widget.field_value}'")
                
                try:
                    widget.field_value = str(new_value)
                    widget.update()
                    print(f"   ✅ Set text field to: '{new_value}'")
                    return True
                except Exception as e:
                    print(f"   ❌ Failed to set text field: {e}")
                    return False
    
    if not field_found:
        print(f"   ❌ Text field '{field_name}' not found")
        return False
    
    return True

def get_field_type(doc, field_name):
    """
    Determine field type by examining widgets
    Returns: 'radio', 'checkbox', 'text', or 'unknown'
    """
    
    # Examine actual widgets to determine type
    widget_count = 0
    widget_type_str = None
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                widget_count += 1
                widget_type_str = widget.field_type_string.lower()
    
    if widget_count == 0:
        return "unknown"
    
    # Handle different widget types
    if "checkbox" in widget_type_str:
        return "checkbox"
    elif "button" in widget_type_str:
        # If multiple widgets exist, it's a radio button group
        if widget_count > 1:
            return "radio"
        else:
            return "checkbox"
    elif "text" in widget_type_str:
        return "text"
    else:
        return "unknown"

def is_signature_field(doc, field_name):
    """Check if a field is a signature field"""
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                field_type_str = widget.field_type_string.lower()
                return "signature" in field_type_str
    return False

def main():
    """Test the PDF service with sample data"""
    
    # Test configuration
    test_pdf = "pdf.pdf"
    
    if not os.path.exists(test_pdf):
        print(f"❌ Test PDF not found: {test_pdf}")
        return
    
    # Sample field updates
    field_updates = {
        "5": "/1",      # Radio button - Bedarfsänderung
        "18a": True,    # Checkbox - checked
        "26": "/2",     # Multi-option radio - Genehmigt mit Einschränkung
        "1": "Test Text Value"  # Text field
    }
    
    # Create backup
    backup_path = f"pdf_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    shutil.copy2(test_pdf, backup_path)
    print(f"📋 Created backup: {backup_path}")
    
    # Update PDF fields
    success = update_pdf_fields(test_pdf, field_updates)
    
    if success:
        print(f"\n✅ PDF update completed successfully!")
        print(f"📄 Updated PDF: {test_pdf}")
        print(f"📋 Backup available: {backup_path}")
    else:
        print(f"\n❌ PDF update failed!")
        print(f"📋 Original preserved in: {backup_path}")

if __name__ == "__main__":
    main() 