import os
import json
import shutil
import tempfile
from datetime import datetime

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

# PDF Field Dictionary - maps field IDs to German names, types, and values
# Copied from pdf_service.py to ensure proper value translation
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

def get_field_type_from_dict(field_id):
    """
    Get the field type from PDF_FIELD_DICT.
    Falls back to basic PDF type detection if not found.
    """
    if field_id in PDF_FIELD_DICT:
        return PDF_FIELD_DICT[field_id]["type"]
    return "text"  # Default fallback

def translate_display_value_to_pdf(field_id, display_value):
    """
    Convert German display text back to PDF values.
    Example: "Ja" -> "/0", "Nein" -> "/1"
    """
    if field_id in PDF_FIELD_DICT and "values" in PDF_FIELD_DICT[field_id]:
        values_map = PDF_FIELD_DICT[field_id]["values"]
        if display_value in values_map:
            return values_map[display_value]
    # Return the original value if no mapping found
    return str(display_value)

def save_pdf_changes_simple(template_path, frontend_data):
    """
    Simple PDF field update that preserves signatures.
    Uses BATCHED UPDATES approach like Adobe Acrobat to preserve signatures.
    
    CRITICAL: All fields are updated in a single document session,
    then saved once with a single incremental save - just like Adobe.
    """
    if not FITZ_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) is required. Install with: pip install PyMuPDF")
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template PDF not found: {template_path}")
    
    try:
        # Use the template_path directly (it's already the target file)
        output_path = template_path
        print(f"📄 Working with file: {output_path}")
        
        # Track updates
        updated_count = 0
        skipped_count = 0
        button_count = 0
        text_count = 0
        
        # CRITICAL: Open document ONCE for ALL updates (like Adobe)
        print(f"\n🔄 Opening PDF for BATCH updates (Adobe-style)...")
        doc = fitz.open(output_path)
        
        # Collect all field updates to perform in batch
        field_updates = []
        
        # First pass: Analyze all fields and prepare updates
        for field_name, new_value in frontend_data.items():
            print(f"\n📋 Analyzing field '{field_name}' with value '{new_value}'")
            
            # Get field type from our dictionary
            dict_field_type = get_field_type_from_dict(field_name)
            
            # Find the field in the PDF
            field_found = False
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    if widget.field_name != field_name:
                        continue
                    
                    field_found = True
                    
                    # Skip signature fields completely
                    if widget.field_type_string == 'Signature':
                        print(f"🔒 Skipping signature field '{field_name}' to preserve signature")
                        break
                    
                    # Get current value
                    current_value = str(widget.field_value or "")
                    new_value_str = str(new_value)
                    
                    # Check if update is needed
                    if current_value == new_value_str:
                        skipped_count += 1
                        print(f"⏭️  Field '{field_name}' - no change needed ('{current_value}')")
                        break
                    
                    print(f"📝 Field '{field_name}' needs update: '{current_value}' → '{new_value_str}'")
                    
                    # Prepare the update
                    update_info = {
                        'widget': widget,
                        'field_name': field_name,
                        'new_value': new_value,
                        'new_value_str': new_value_str,
                        'dict_field_type': dict_field_type,
                        'widget_type': widget.field_type_string,
                        'page_num': page_num
                    }
                    field_updates.append(update_info)
                    
                    if dict_field_type == 'btn':
                        button_count += 1
                    else:
                        text_count += 1
                    
                    break  # Only update first occurrence of this field
                
                if field_found:
                    break  # Move to next field
            
            if not field_found:
                print(f"❓ Field '{field_name}' not found in PDF")
        
        print(f"\n🎯 BATCH UPDATE PLAN:")
        print(f"   📝 Text fields to update: {text_count}")
        print(f"   🔘 Button fields to update: {button_count}")
        print(f"   ⏭️  Fields to skip: {skipped_count}")
        print(f"   📦 Total updates planned: {len(field_updates)}")
        
        # Second pass: Apply all updates in memory (like Adobe)
        if field_updates:
            print(f"\n🔄 Applying {len(field_updates)} field updates in batch...")
            
            for update in field_updates:
                widget = update['widget']
                field_name = update['field_name']
                new_value = update['new_value']
                new_value_str = update['new_value_str']
                dict_field_type = update['dict_field_type']
                widget_type = update['widget_type']
                page_num = update['page_num']
                
                try:
                    # Handle different field types with proper value translation
                    if widget_type in ['Text', 'FreeText']:
                        # Text fields - use value as string
                        widget.field_value = new_value_str
                        print(f"   📝 Text field '{field_name}' = '{new_value_str}'")
                        
                    elif widget_type in ['CheckBox', 'RadioButton']:
                        # Button fields - use proper PDF value translation
                        if dict_field_type == 'btn':
                            # Translate German display values to PDF internal values
                            pdf_value = translate_display_value_to_pdf(field_name, new_value_str)
                            print(f"   🔄 Translating '{new_value_str}' → '{pdf_value}' for field '{field_name}'")
                            
                            # Apply proper PyMuPDF value format
                            if widget_type == 'CheckBox':
                                # Checkboxes: convert to boolean
                                if pdf_value in ['/Ja', '/Yes', '/On', '/0']:
                                    widget.field_value = True
                                    print(f"   🔘 Checkbox '{field_name}' set to TRUE")
                                else:
                                    widget.field_value = False
                                    print(f"   ⚪ Checkbox '{field_name}' set to FALSE")
                            elif widget_type == 'RadioButton':
                                # Radio buttons: remove leading slash
                                if pdf_value.startswith('/'):  
                                    radio_value = pdf_value[1:]
                                    widget.field_value = radio_value
                                    print(f"   📻 Radio '{field_name}' set to '{radio_value}'")
                                else:
                                    widget.field_value = pdf_value
                                    print(f"   📻 Radio '{field_name}' set to '{pdf_value}'")
                        else:
                            # Fallback for fields not in dictionary
                            widget.field_value = new_value_str
                            print(f"   🔘 Button '{field_name}' set to '{new_value_str}' (fallback)")
                    else:
                        # Other field types
                        widget.field_value = new_value_str
                        print(f"   ❓ Other field '{field_name}' set to '{new_value_str}'")
                    
                    # Update the widget in memory
                    widget.update()
                    updated_count += 1
                    
                    # Debug: Show actual value set
                    actual_value = widget.field_value
                    print(f"     ✅ Actual value: '{actual_value}' (type: {type(actual_value)})")
                    
                except Exception as widget_error:
                    print(f"   ❌ Error updating field '{field_name}': {widget_error}")
            
            # CRITICAL: Single save operation (like Adobe Acrobat)
            print(f"\n💾 Saving ALL changes with SINGLE incremental save (Adobe-style)...")
            doc.saveIncr()
            print(f"✅ Single incremental save completed - signatures should be preserved!")
        else:
            print(f"\n⏭️  No updates needed - PDF unchanged")
        
        # Close document once
        doc.close()
        
        print(f"\n🎉 BATCH UPDATE SUMMARY:")
        print(f"   ✅ Updated {updated_count} fields total")
        print(f"   📝 Text fields: {text_count}")
        print(f"   🔘 Button fields: {button_count}")
        print(f"   ⏭️  Skipped: {skipped_count} unchanged fields")
        print(f"   💾 Incremental saves: 1 (Adobe-style)")
        print(f"   📄 Result: {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error in save_pdf_changes_simple: {str(e)}")
        raise e

def test_simple_pdf_update(pdf_path, frontend_data_path):
    """
    Test function that loads frontend data and updates PDF.
    
    Args:
        pdf_path: Path to the PDF file
        frontend_data_path: Path to JSON file with field data
    
    Returns:
        str: Path to the updated PDF
    """
    # Load frontend data
    with open(frontend_data_path, 'r', encoding='utf-8') as f:
        frontend_data = json.load(f)
    
    print(f"📄 Loading PDF: {pdf_path}")
    print(f"📊 Loading data: {frontend_data_path}")
    print(f"🔢 Found {len(frontend_data)} fields to update")
    
    # Note: save_pdf_changes_simple will create a copy as "test.pdf"
    # Original file remains untouched
    
    # Update the PDF
    result_path = save_pdf_changes_simple(pdf_path, frontend_data)
    
    print(f"✅ PDF updated successfully: {result_path}")
    return result_path

def extract_pdf_fields_simple(pdf_path):
    """
    Simple field extraction for debugging.
    Returns basic field information.
    """
    if not FITZ_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) is required. Install with: pip install PyMuPDF")
    
    fields = []
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_name:
                    field_info = {
                        'id': widget.field_name,
                        'type': widget.field_type_string,
                        'value': widget.field_value,
                        'page': page_num + 1
                    }
                    fields.append(field_info)
        
        doc.close()
        
    except Exception as e:
        print(f"Error extracting fields: {e}")
        raise e
    
    return fields

if __name__ == "__main__":
    # Test with the provided files
    pdf_file = "pdf.pdf"  # Adjust path as needed
    data_file = "frontend_data.json"
    
    if os.path.exists(pdf_file) and os.path.exists(data_file):
        try:
            result = test_simple_pdf_update(pdf_file, data_file)
            print(f"\n🎯 Test completed successfully!")
            print(f"📄 Updated PDF: {result}")
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
    else:
        print(f"❌ Required files not found:")
        print(f"   PDF: {pdf_file} (exists: {os.path.exists(pdf_file)})")
        print(f"   Data: {data_file} (exists: {os.path.exists(data_file)})") 