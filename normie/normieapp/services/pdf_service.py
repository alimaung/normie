import os
import json
import PyPDF2
import base64
import re
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import datetime
import tempfile
import shutil

"""
PDF Service Module - Enhanced with German Field Mapping

This module has been updated to implement the functionality from:
- pdf_fields.py: Proper field extraction and cleaning
- pdf_decode.py: German field mapping and value translation

Key Features:
1. PDF_FIELD_DICT integration for German field names and types
2. Button value translation (PDF values ↔ German display text)
3. Proper signature field handling and formatting
4. Natural field sorting (1, 2a, 2b, 3, ...)
5. Field validation and type checking

Updated Functions:
- extract_pdf_fields_pypdf2(): Now uses PDF_FIELD_DICT for field mapping
- save_pdf_changes(): Converts German values back to PDF values
- Added helper functions for value translation and validation

TODO: Replace PDF_FIELD_DICT placeholder with actual mapping from pdf_decode.py
"""

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

# PDF Field Dictionary - maps field IDs to German names, types, and values
# TODO: Replace this placeholder with the actual pdf_dict from pdf_decode.py
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

def get_field_name_from_dict(field_id):
    """
    Get the German field name from PDF_FIELD_DICT.
    Falls back to field_id if not found.
    """
    if field_id in PDF_FIELD_DICT:
        return PDF_FIELD_DICT[field_id]["name"]
    return field_id

def get_field_type_from_dict(field_id):
    """
    Get the field type from PDF_FIELD_DICT.
    Falls back to basic PDF type detection if not found.
    """
    if field_id in PDF_FIELD_DICT:
        return PDF_FIELD_DICT[field_id]["type"]
    return "text"  # Default fallback

def translate_button_value_to_display(field_id, pdf_value):
    """
    Convert PDF button values to German display text.
    Example: "/0" -> "Ja", "/1" -> "Nein"
    """
    if field_id in PDF_FIELD_DICT and "values" in PDF_FIELD_DICT[field_id]:
        values_map = PDF_FIELD_DICT[field_id]["values"]
        # Look for the display label that maps to this PDF value
        for display_label, mapped_pdf_value in values_map.items():
            if mapped_pdf_value == pdf_value:
                return display_label
    # Return the original value if no mapping found
    return str(pdf_value)

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

def clean_signature_field_data(field_data):
    """
    Clean signature field data for JSON serialization.
    Based on clean_signature_field from pdf_fields.py
    """
    if '/FT' in field_data and field_data['/FT'] == '/Sig' and '/V' in field_data:
        sig_value = field_data['/V']
        cleaned_sig = {}
        
        # Handle various signature components
        if '/ByteRange' in sig_value:
            cleaned_sig['ByteRange'] = sig_value['/ByteRange']
            
        if '/ContactInfo' in sig_value:
            cleaned_sig['ContactInfo'] = str(sig_value['/ContactInfo'])
            
        if '/Contents' in sig_value:
            # Convert binary content to base64
            binary_content = sig_value['/Contents']
            if isinstance(binary_content, (bytes, PyPDF2.generic.ByteStringObject)):
                cleaned_sig['Contents'] = base64.b64encode(binary_content).decode('utf-8')
            else:
                cleaned_sig['Contents'] = str(binary_content)

        if '/Filter' in sig_value:
            cleaned_sig['Filter'] = sig_value['/Filter']
        
        if '/Location' in sig_value:
            cleaned_sig['Location'] = sig_value['/Location']
        
        if '/M' in sig_value:
            cleaned_sig['M'] = sig_value['/M']
            
        if '/Name' in sig_value:
            cleaned_sig['Name'] = sig_value['/Name']
            
        if '/Reason' in sig_value:
            cleaned_sig['Reason'] = sig_value['/Reason']

        if '/App' in sig_value:
            cleaned_sig['App'] = sig_value['/App']
            
        if '/SubFilter' in sig_value:
            cleaned_sig['SubFilter'] = sig_value['/SubFilter']
                    
        # Return cleaned signature data
        return cleaned_sig
        
    return field_data

def format_signature_display(signature_data):
    """
    Format signature data for display.
    Based on signature formatting from pdf_decode.py
    """
    if isinstance(signature_data, dict):
        signatory = signature_data.get('Name', 'Unknown')
        sign_date = signature_data.get('M', '')
        
        if sign_date and len(sign_date) >= 16:
            try:
                # Parse date format from PDF signature
                date_str = sign_date[2:16]
                timezone_str = sign_date[16:].strip()
                
                # Convert to datetime
                dt = datetime.strptime(date_str, '%Y%m%d%H%M%S')
                
                # Format for display
                german_date = dt.strftime('%d.%m.%Y, %H:%M:%S')
                
                return f"{signatory} - {german_date} {timezone_str}"
            except ValueError:
                pass
        
        return f"{signatory} - {sign_date}"
    
    return str(signature_data)

def natural_sort_key(s):
    """
    Create a key for natural sorting that handles numbers properly.
    Splits string into list of numeric and non-numeric parts.
    """
    def convert(text):
        # Convert number strings to integers for proper sorting
        return int(text) if text.isdigit() else text.lower()
    
    # Split string into numeric and non-numeric parts
    parts = re.split('([0-9]+)', str(s))
    return [convert(c) for c in parts]

def clean_value(value):
    """
    Clean value for JSON serialization.
    Handles various PyPDF2 object types.
    """
    if value is None:
        return ""
    elif isinstance(value, (PyPDF2.generic.ByteStringObject, bytes)):
        try:
            # Try to decode as UTF-8 first
            return value.decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            # If that fails, encode as base64
            if isinstance(value, bytes):
                return base64.b64encode(value).decode('utf-8')
            else:
                return base64.b64encode(value.original_bytes).decode('utf-8')
    elif isinstance(value, PyPDF2.generic.TextStringObject):
        return str(value)
    elif isinstance(value, PyPDF2.generic.NameObject):
        return str(value)
    elif isinstance(value, (int, float, bool)):
        return value
    elif isinstance(value, (list, tuple)):
        return [clean_value(item) for item in value]
    elif isinstance(value, dict):
        return {str(k): clean_value(v) for k, v in value.items()}
    else:
        return str(value)

def extract_pdf_fields(pdf_path):
    """
    Extract form fields from a PDF file.
    Returns a list of field objects with id, name, type, and value.
    Uses PyPDF2 for extraction (to get proper field descriptions) but PyMuPDF for saving.
    """
    # Use PyPDF2 for extraction to get proper field descriptions from /TU
    return extract_pdf_fields_pypdf2(pdf_path)

def extract_pdf_fields_fitz(pdf_path):
    """
    Extract form fields using PyMuPDF (fitz).
    More reliable for complex PDFs.
    """
    fields = []
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_name:  # Only include named fields
                    # Get field value
                    field_value = widget.field_value or ""
                    
                    # Convert PyMuPDF field type to PyPDF2-like format for consistency
                    field_type = "/Tx"  # Default to text
                    if widget.field_type_string in ['CheckBox', 'RadioButton']:
                        field_type = "/Btn"
                    elif widget.field_type_string == 'Signature':
                        field_type = "/Sig"
                    
                    # For now, use field_name as display name
                    # In the future, we could add a mapping dictionary
                    field_name = widget.field_name
                    
                    fields.append({
                        'id': widget.field_name,
                        'name': field_name,
                        'type': field_type,
                        'value': str(field_value)
                    })
        
        doc.close()
        
        # Sort fields naturally
        fields.sort(key=lambda x: natural_sort_key(x['id']))
        
    except Exception as e:
        print(f"Error extracting fields with PyMuPDF: {e}")
        raise e
    
    return fields

def extract_pdf_fields_pypdf2(pdf_path):
    """
    Extract form fields using PyPDF2 with proper German field mapping.
    Now uses PDF_FIELD_DICT for field names, types, and value translation.
    """
    fields = []
    
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Check if the PDF has form fields
        if reader.get_fields():
            # Get all form fields
            form_fields = reader.get_fields()
            
            # Process each field with natural sorting
            field_ids = sorted(form_fields.keys(), key=natural_sort_key)
            for field_id in field_ids:
                field = form_fields[field_id]
                
                # Remove /Kids entries that can cause issues
                if '/Kids' in field:
                    del field['/Kids']
                
                # Get basic field type from PDF
                pdf_field_type = field.get('/FT', 'Unknown')
                
                # Get field value and clean it for JSON serialization
                raw_value = field.get('/V', '')
                field_value = clean_value(raw_value)
                
                # Use PDF_FIELD_DICT for field metadata
                field_name = get_field_name_from_dict(field_id)
                field_type = get_field_type_from_dict(field_id)
                
                # Handle different field types properly
                if pdf_field_type == '/Tx':  # Text field
                    # For text fields, just use the cleaned value
                    processed_value = field_value
                    
                elif pdf_field_type == '/Btn':  # Button field
                    # For button fields, translate PDF values to German display text
                    if field_value:
                        processed_value = translate_button_value_to_display(field_id, field_value)
                    else:
                        processed_value = ""
                    
                elif pdf_field_type == '/Sig':  # Signature field
                    # For signature fields, clean and format the data
                    if field_value:
                        cleaned_sig = clean_signature_field_data(field)
                        if cleaned_sig != field:
                            # If signature was cleaned, format it for display
                            processed_value = format_signature_display(cleaned_sig)
                        else:
                            processed_value = "Digital Signature Present"
                    else:
                        processed_value = ""
                        
                else:
                    # Default handling for unknown field types
                    processed_value = field_value
                
                # Validate field exists in our dictionary
                if field_id not in PDF_FIELD_DICT:
                    print(f"Warning: Field '{field_id}' not found in PDF_FIELD_DICT")
                
                # Add field to result with proper type mapping
                fields.append({
                    'id': field_id,
                    'name': field_name,
                    'type': f"/{pdf_field_type[1:]}" if pdf_field_type.startswith('/') else f"/{pdf_field_type}",  # Keep PDF format for compatibility
                    'value': processed_value,
                    'dict_type': field_type,  # Add the dictionary type for reference
                    'raw_value': field_value,  # Keep raw value for debugging
                })
    
    return fields

def remove_appearance_streams_from_pdf(pdf_path):
    """
    Remove appearance streams (/AP) from PDF text form fields to prevent text clipping.
    This forces PDF viewers to regenerate appearance streams with proper text layout.
    Preserves appearance streams for checkboxes, radio buttons, and signatures.
    
    Args:
        pdf_path: Path to the PDF file to fix
    
    Returns:
        bool: True if changes were made, False otherwise
    """
    try:
        # Read the PDF data
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        print(f"Removing appearance streams from text fields to fix text clipping...")
        
        # Find all form field objects with appearance streams - use a broader pattern first
        # Look for objects with /Type/Annot, /Subtype/Widget, and /AP
        form_field_ap_pattern = rb'/Type\s*/Annot[^>]*?/Subtype\s*/Widget[^>]*?/AP\s*(?:<<[^>]*>>|\d+\s+\d+\s+R)'
        
        matches = list(re.finditer(form_field_ap_pattern, pdf_data, re.DOTALL))
        
        if not matches:
            print("No form field appearance streams found")
            return False
        
        print(f"Found {len(matches)} form field objects with appearance streams")
        
        modified_data = pdf_data
        total_changes = 0
        text_fields_processed = 0
        other_fields_skipped = 0
        
        # Process each match to check if it's a text field and remove /AP entries
        for match in reversed(matches):  # Process in reverse to maintain positions
            # Find the object boundaries
            obj_start = pdf_data.rfind(b' obj', 0, match.start())
            if obj_start == -1:
                continue
                
            # Find the actual start of the object number
            obj_start = pdf_data.rfind(b'\n', 0, obj_start) + 1
            if obj_start == 0:
                obj_start = pdf_data.rfind(b'\r', 0, obj_start) + 1
            
            # Find the end of the object
            obj_end = pdf_data.find(b'endobj', match.end())
            if obj_end == -1:
                continue
            obj_end += len(b'endobj')
            
            # Extract the object data
            obj_data = pdf_data[obj_start:obj_end]
            
            try:
                obj_text = obj_data.decode('latin-1', errors='replace')
            except:
                continue
            
            # Check if this object has /AP entries
            if '/AP' not in obj_text:
                continue
            
            # Determine field type and decide whether to remove appearance streams
            is_text_field = '/FT/Tx' in obj_text
            is_button_field = '/FT/Btn' in obj_text
            is_signature_field = ('/Lock' in obj_text or '/SigFlags' in obj_text or 
                                'Signature' in obj_text or '/Type/Sig' in obj_text)
            
            # Only remove appearance streams from text fields
            if is_text_field and not is_signature_field:
                print(f"Processing text field object...")
                
                # Remove /AP entries using multiple patterns
                obj_text_modified = obj_text
                
                # Pattern 1: /AP<<...>> (nested dictionary) - more flexible matching
                ap_dict_pattern = r'/AP\s*<<(?:[^<>]|<<[^<>]*>>)*>>'
                obj_text_modified = re.sub(ap_dict_pattern, '', obj_text_modified, flags=re.DOTALL)
                
                # Pattern 2: /AP <reference> (object reference)
                ap_ref_pattern = r'/AP\s+\d+\s+\d+\s+R'
                obj_text_modified = re.sub(ap_ref_pattern, '', obj_text_modified)
                
                # Pattern 3: Remove any remaining /AP entries
                ap_simple_pattern = r'/AP[^\s/]*'
                obj_text_modified = re.sub(ap_simple_pattern, '', obj_text_modified)
                
                # Clean up any double spaces
                obj_text_modified = re.sub(r'\s+', ' ', obj_text_modified)
                
                if obj_text_modified != obj_text:
                    # Convert back to bytes and replace in the PDF data
                    try:
                        modified_obj_data = obj_text_modified.encode('latin-1')
                        modified_data = modified_data[:obj_start] + modified_obj_data + modified_data[obj_end:]
                        total_changes += 1
                        text_fields_processed += 1
                        print(f"  ✅ Removed appearance streams (size change: {len(obj_data)} -> {len(modified_obj_data)} bytes)")
                    except Exception as e:
                        print(f"  ❌ Error encoding modified object: {e}")
                else:
                    print(f"  ℹ️ No /AP entries found to remove")
            
            elif is_button_field:
                print(f"Skipping button field (checkbox/radio) - preserving appearance streams")
                other_fields_skipped += 1
            elif is_signature_field:
                print(f"Skipping signature field - preserving appearance streams")
                other_fields_skipped += 1
            else:
                print(f"Skipping unknown field type - preserving appearance streams")
                other_fields_skipped += 1
        
        if total_changes > 0:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_path = temp_file.name
            temp_file.close()
            
            try:
                # Write the modified data to temp file
                with open(temp_path, 'wb') as f:
                    f.write(modified_data)
                
                # Replace the original file
                shutil.move(temp_path, pdf_path)
                
                print(f"Successfully removed appearance streams from {text_fields_processed} text field objects")
                print(f"Preserved appearance streams for {other_fields_skipped} non-text field objects")
                return True
                
            except Exception as e:
                # Clean up temp file if it exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                print(f"Error saving modified PDF: {e}")
                return False
        else:
            print(f"No text field appearance streams were removed")
            print(f"Analyzed {text_fields_processed + other_fields_skipped} form field objects")
            return False
            
    except Exception as e:
        print(f"Error removing appearance streams: {e}")
        return False

def refresh_pdf_fields_for_adobe(pdf_path):
    """
    Refresh PDF fields for better Adobe Acrobat compatibility.
    Uses the field refresh technique from refresh_text_fields.py to force Adobe
    to regenerate appearance streams without removing them completely.
    """
    try:
        print(f"Refreshing PDF fields in: {pdf_path}")
        doc = fitz.open(pdf_path)
        
        fields_refreshed = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_name and widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                    try:
                        # Get original value
                        original_value = str(widget.field_value or '')
                        
                        if original_value.strip():  # Only refresh fields with content
                            # Use the "newline refresh" technique: add newline, then remove it
                            # This forces Adobe to regenerate the appearance without data loss
                            temp_value = original_value + "\n"
                            widget.field_value = temp_value
                            widget.update()
                            
                            # Restore original value
                            widget.field_value = original_value
                            widget.update()
                            
                            fields_refreshed += 1
                            print(f"  ✅ Refreshed field: {widget.field_name}")
                    
                    except Exception as widget_error:
                        print(f"  ⚠️ Could not refresh field {widget.field_name}: {widget_error}")
        
        if fields_refreshed > 0:
            # Save with incremental update
            doc.saveIncr()
            print(f"✅ Successfully refreshed {fields_refreshed} text fields")
        else:
            print("ℹ️ No text fields found to refresh")
            
        doc.close()
        return True
        
    except Exception as e:
        print(f"❌ Error refreshing PDF fields: {e}")
        return False

def save_pdf_changes(template_path, fields):
    """
    Save changes back to the original PDF file.
    Uses PyMuPDF for reliable form field updates and removes appearance streams to prevent clipping.
    Now properly converts German display values back to PDF values and handles combined fields.
    """
    # Use PyMuPDF approach directly - it's more reliable for preserving appearances
    if not FITZ_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) is required as fallback for PDF form editing. Install with: pip install PyMuPDF")
    
    try:
        # Open the PDF document with PyMuPDF
        doc = fitz.open(template_path)
        
        # Create a dictionary of field updates with proper value conversion
        field_updates = {}
        for field in fields:
            field_id = field.get('id', '')
            field_value = field.get('value', '')
            dict_type = field.get('dict_type', 'text')
            
            if field_id:
                # Convert German display values back to PDF values for button fields
                if dict_type == 'btn' and field_value:
                    # Handle the new German "Ja"/"Nein" format
                    if field_value in ['Ja', 'ja', 'Yes', 'yes', 'True', 'true', '1', 1, True]:
                        # Find the PDF value for "checked" state
                        pdf_value = translate_display_value_to_pdf(field_id, 'Ja')
                        if not pdf_value:  # Fallback if translation fails
                            # Check if this field uses /Ja format or /0 format
                            field_def = PDF_FIELD_DICT.get(field_id, {})
                            values = field_def.get('values', {})
                            if '/Ja' in values.values():
                                pdf_value = '/Ja'
                            else:
                                pdf_value = '/0'
                        field_updates[field_id] = pdf_value
                    elif field_value in ['Nein', 'nein', 'No', 'no', 'False', 'false', '0', 0, False]:
                        # Find the PDF value for "unchecked" state
                        pdf_value = translate_display_value_to_pdf(field_id, 'Nein')
                        if not pdf_value:  # Fallback if translation fails
                            # Check if this field uses /Off format or /1 format
                            field_def = PDF_FIELD_DICT.get(field_id, {})
                            values = field_def.get('values', {})
                            if '/Off' in values.values():
                                pdf_value = '/Off'
                            else:
                                pdf_value = '/1'
                        field_updates[field_id] = pdf_value
                    else:
                        # Try direct translation for other values (radio buttons)
                        pdf_value = translate_display_value_to_pdf(field_id, field_value)
                        # If translation returns the same value, it means no mapping was found
                        # For radio buttons, we should still save the translated value
                        if pdf_value != field_value:
                            field_updates[field_id] = pdf_value
                        else:
                            # Check if this is a valid display value that should be translated
                            field_def = PDF_FIELD_DICT.get(field_id, {})
                            values = field_def.get('values', {})
                            if field_value in values:
                                # This is a valid German display text, use its PDF value
                                field_updates[field_id] = values[field_value]
                            else:
                                # Fallback to original value
                                field_updates[field_id] = field_value
                else:
                    # For text and signature fields, use the value as-is
                    field_updates[field_id] = str(field_value)
        
        # Update form fields using PyMuPDF
        updated_count = 0
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_name in field_updates:
                    # Skip signature fields - don't update them
                    if widget.field_type_string == 'Signature':
                        print(f"Skipping signature field '{widget.field_name}' - preserving original")
                        continue
                        
                    new_value = field_updates[widget.field_name]
                    field_dict_type = get_field_type_from_dict(widget.field_name)
                    
                    try:
                        # Handle different field types based on both PyMuPDF type and our dictionary type
                        if widget.field_type_string in ['Text', 'FreeText']:
                            widget.field_value = new_value
                        elif widget.field_type_string in ['CheckBox', 'RadioButton']:
                            # For radio buttons, use the PDF value directly 
                            # For checkboxes, convert to boolean
                            if widget.field_type_string == 'RadioButton':
                                # Radio buttons need the exact PDF value
                                widget.field_value = new_value
                            else:
                                # Checkboxes need boolean values
                                if field_dict_type == 'btn':
                                    # Check for "checked" values in various formats
                                    checked_values = ['/0', '/Yes', '/Ja', 'True', 'true', '1', True, 1]
                                    if new_value in checked_values:
                                        widget.field_value = True
                                    else:
                                        widget.field_value = False
                                else:
                                    # Fallback to original logic
                                    if new_value in ['/0', '/Yes', '/Ja', 'True', 'true', '1', True, 1]:
                                        widget.field_value = True
                                    else:
                                        widget.field_value = False
                        else:
                            # Default handling for other field types
                            widget.field_value = new_value
                        
                        widget.update()
                        updated_count += 1
                        print(f"Updated field '{widget.field_name}' to '{new_value}' on page {page_num + 1}")
                    except Exception as widget_error:
                        print(f"Error updating field '{widget.field_name}': {widget_error}")
        
        # Save the document using incremental save for better compatibility
        
        try:
            # Use incremental save to avoid warnings and preserve compatibility
            doc.saveIncr()
            doc.close()
            
            # Don't use temporary file for incremental save
            print("✅ PDF saved using incremental save method")
            
            # IMPORTANT: Apply the more effective text clipping fix
            # Remove appearance streams from text fields to prevent clipping
            print("🔧 Removing appearance streams from text fields to fix clipping...")
            remove_appearance_streams_from_pdf(template_path)
            
        except Exception as save_error:
            # Close document on error
            doc.close()
            raise save_error
        
        print(f"Successfully updated {updated_count} fields in {template_path}")
        return template_path
        
    except Exception as e:
        print(f"Error saving PDF changes: {str(e)}")
        raise e

def generate_filled_pdf(template_path, fields, output_path=None, overwrite_original=False):
    """
    Generate a filled PDF form using the provided template and field values.
    
    Args:
        template_path: Path to the PDF template
        fields: List of field dictionaries with id, value, type
        output_path: Optional output path. If None, creates a temporary file
        overwrite_original: If True, saves changes back to the template_path
    """
    # If overwrite_original is True, save to the original file
    if overwrite_original:
        output_path = template_path
    
    # If no output path is provided, create a temporary file
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        output_path = temp_file.name
        temp_file.close()
    
    try:
        # Create a copy of the template
        with open(template_path, 'rb') as template_file:
            reader = PyPDF2.PdfReader(template_file)
            writer = PyPDF2.PdfWriter()
            
            # Add all pages from the template
            for page_num in range(len(reader.pages)):
                writer.add_page(reader.pages[page_num])
            
            # Prepare field values in a dictionary format for PyPDF2
            form_values = {}
            
            # Update form fields
            for i, field in enumerate(fields):
                try:
                    field_id = field.get('id', '')
                    field_value = field.get('value', '')
                    field_type = field.get('type', '/Tx')
                    
                    print(f"Processing field {i}: id={field_id}, type={field_type}, value={field_value}")
                    
                    # Skip empty field IDs
                    if not field_id:
                        continue
                    
                    # Handle different field types
                    if field_type == '/Btn':
                        # Button fields (checkboxes, radio buttons)
                        if field_value in ['/0', '/Yes', True, 'true', 'True']:
                            form_values[field_id] = '/0'
                        else:
                            form_values[field_id] = '/1'
                    elif field_type == '/Tx':
                        # Text fields
                        form_values[field_id] = str(field_value)
                    else:
                        # Default handling for other field types
                        form_values[field_id] = str(field_value)
                except Exception as field_error:
                    print(f"Error processing field {i}: {str(field_error)}")
                    print(f"Field data: {field}")
            
            # Update all form fields at once
            if form_values:
                try:
                    # Try to update all fields at once
                    writer.update_page_form_field_values(writer.pages[0], form_values)
                except Exception as e:
                    print(f"Error updating all fields at once: {str(e)}")
                    # Fall back to updating fields one by one
                    for field_id, field_value in form_values.items():
                        try:
                            writer.update_page_form_field_values(writer.pages[0], {field_id: field_value})
                        except Exception as field_e:
                            print(f"Error updating field {field_id}: {str(field_e)}")
            
            # Write the output PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        
        return output_path
    except Exception as e:
        # Log the error details for debugging
        print(f"Error in generate_filled_pdf: {str(e)}")
        print(f"Fields type: {type(fields)}")
        if not isinstance(fields, list):
            print(f"Fields is not a list: {fields}")
        else:
            print(f"Number of fields: {len(fields)}")
            for i, field in enumerate(fields):
                print(f"Field {i}: {type(field)} - {field}")
        raise e

def get_pdf_field_mapping(pdf_path):
    """
    Extract field IDs and their types from a PDF form.
    Useful for creating field mappings.
    """
    mapping = {}
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        form_fields = reader.get_fields()
        
        for field_id, field in form_fields.items():
            field_type = field.get('/FT', 'Unknown')
            mapping[field_id] = {
                'type': str(field_type),
                'name': field_id  # Default name is the ID
            }
    
    return mapping

def get_field_type_and_value(field):
    """
    Get the type and value of a PDF form field.
    """
    field_type = None
    field_value = None
    
    if '/FT' in field:
        field_type = field['/FT']
        
        if field_type == '/Tx' and '/V' in field:  # Text field
            field_value = field['/V']
        elif field_type == '/Btn' and '/V' in field:  # Button/checkbox/radio
            field_value = field['/V']
        elif field_type == '/Sig' and '/V' in field:  # Signature
            if '/Name' in field['/V']:
                field_value = field['/V']['Name']
            else:
                field_value = "Signature"
    
    return field_type, field_value

def validate_field_value(field_id, value):
    """
    Validate field values against PDF_FIELD_DICT definitions.
    Returns True if valid, False otherwise.
    """
    if field_id not in PDF_FIELD_DICT:
        return False
    
    field_def = PDF_FIELD_DICT[field_id]
    field_type = field_def.get('type', 'text')
    
    if field_type == 'btn' and 'values' in field_def:
        # For button fields, check if the value is in the allowed values
        allowed_values = list(field_def['values'].keys()) + list(field_def['values'].values())
        return value in allowed_values
    
    # For text and sig fields, any value is acceptable
    return True

def get_field_metadata():
    """
    Return the metadata for PDF form fields.
    Now uses the PDF_FIELD_DICT instead of hardcoded values.
    """
    # Return a copy of the PDF_FIELD_DICT for external use
    return PDF_FIELD_DICT.copy()

def get_field_options(field_id):
    """
    Get field options for button fields from PDF_FIELD_DICT.
    Returns a list of (display_text, pdf_value) tuples.
    """
    if field_id not in PDF_FIELD_DICT:
        return []
    
    field_def = PDF_FIELD_DICT[field_id]
    if field_def.get('type') != 'btn' or 'values' not in field_def:
        return []
    
    # Return list of (display_text, pdf_value) tuples
    return list(field_def['values'].items())

def get_fields_by_type(field_type):
    """
    Get all fields of a specific type from PDF_FIELD_DICT.
    Useful for grouping fields in the UI.
    """
    fields_of_type = []
    for field_id, field_def in PDF_FIELD_DICT.items():
        if field_def.get('type') == field_type:
            fields_of_type.append({
                'id': field_id,
                'name': field_def['name'],
                'type': field_type,
                'values': field_def.get('values', {})
            })
    return fields_of_type

def fill_pdf_form(template_path, form_data):
    """
    Fill a PDF form with provided data.
    Returns a BytesIO object containing the filled PDF.
    """
    # This is a placeholder - actual PDF form filling is complex
    # For a real implementation, you might need to use a library like pdftk or a PDF API service
    
    # For now, we'll just create a simple PDF with the form data
    buffer = BytesIO()
    
    # Create the PDF
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica", 12)
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Form Data")
    c.setFont("Helvetica", 12)
    
    # Add form data
    y = 750
    for field_id, value in form_data.items():
        metadata = get_field_metadata().get(field_id, {})
        field_name = metadata.get("name", field_id)
        
        c.drawString(50, y, f"{field_name} ({field_id}): {value}")
        y -= 20
        
        if y < 50:  # Start a new page if we run out of space
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 800
    
    c.save()
    buffer.seek(0)
    return buffer

def get_signature_details(pdf_path):
    """
    Extract detailed signature information from PDF using PyMuPDF.
    Returns a dictionary with signature details for each signature field.
    """
    signature_details = {}
    
    if not FITZ_AVAILABLE:
        return signature_details
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_name and widget.field_type_string == 'Signature':
                    sig_info = {
                        'field_name': widget.field_name,
                        'page': page_num + 1,
                        'signed': False,
                        'signer_name': '',
                        'sign_date': '',
                        'reason': '',
                        'location': '',
                        'contact_info': ''
                    }
                    
                    # Check if signature is actually signed
                    if widget.field_value:
                        sig_info['signed'] = True
                        
                        # Try to extract signature details
                        try:
                            # Get signature annotation if available
                            annots = page.annots()
                            for annot in annots:
                                if annot.type[1] == 'Widget' and hasattr(annot, 'widget'):
                                    if annot.widget.field_name == widget.field_name:
                                        # Try to get signature dictionary
                                        sig_dict = annot.get_signature()
                                        if sig_dict:
                                            sig_info['signer_name'] = sig_dict.get('name', '')
                                            sig_info['sign_date'] = sig_dict.get('date', '')
                                            sig_info['reason'] = sig_dict.get('reason', '')
                                            sig_info['location'] = sig_dict.get('location', '')
                                            sig_info['contact_info'] = sig_dict.get('contact_info', '')
                        except Exception as sig_error:
                            print(f"Could not extract signature details for {widget.field_name}: {sig_error}")
                    
                    signature_details[widget.field_name] = sig_info
        
        doc.close()
        
    except Exception as e:
        print(f"Error extracting signature details: {e}")
    
    return signature_details

def save_pdf_changes_pypdf2_fixed(template_path, fields):
    """
    Save changes using PyPDF2 with appearance dictionary fix to prevent text clipping.
    This approach removes the Normal appearance that causes text clipping issues.
    """
    try:
        # Create a temporary file for the updated PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_path = temp_file.name
        temp_file.close()
        
        # Create a copy of the template
        with open(template_path, 'rb') as template_file:
            reader = PyPDF2.PdfReader(template_file)
            writer = PyPDF2.PdfWriter()
            
            # Add all pages from the template
            for page_num in range(len(reader.pages)):
                writer.add_page(reader.pages[page_num])
            
            # Prepare field values in a dictionary format for PyPDF2
            form_values = {}
            
            # Update form fields
            for field in fields:
                field_id = field.get('id', '')
                field_value = field.get('value', '')
                field_type = field.get('type', '/Tx')
                
                # Skip empty field IDs
                if not field_id:
                    continue
                
                # Handle different field types
                if field_type == '/Btn':
                    # Button fields (checkboxes, radio buttons)
                    if field_value in ['/0', '/Yes', True, 'true', 'True']:
                        form_values[field_id] = '/0'
                    else:
                        form_values[field_id] = '/1'
                elif field_type == '/Tx':
                    # Text fields
                    form_values[field_id] = str(field_value)
                else:
                    # Default handling for other field types
                    form_values[field_id] = str(field_value)
            
            # Update all form fields at once
            if form_values:
                for page in writer.pages:
                    try:
                        writer.update_page_form_field_values(page, form_values)
                        
                        # Alternative approach: Set need_appearances flag to let PDF viewer handle rendering
                        # This tells the PDF viewer to generate appearances dynamically
                        if hasattr(writer, '_root_object') and writer._root_object:
                            acro_form = writer._root_object.get('/AcroForm')
                            if acro_form:
                                acro_form_obj = acro_form.get_object()
                                # Set NeedAppearances to True - this tells PDF viewers to generate appearances
                                acro_form_obj[PyPDF2.generic.NameObject('/NeedAppearances')] = PyPDF2.generic.BooleanObject(True)
                                print("Set NeedAppearances flag to True")
                    except Exception as page_error:
                        print(f"Error updating page: {page_error}")
            
            # Write the output PDF
            with open(temp_path, 'wb') as output_file:
                writer.write(output_file)
        
        # Replace original file with updated version
        shutil.move(temp_path, template_path)
        
        print(f"Successfully updated fields using PyPDF2 with appearance fix")
        return template_path
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"Error in PyPDF2 save with appearance fix: {str(e)}")
        raise e
