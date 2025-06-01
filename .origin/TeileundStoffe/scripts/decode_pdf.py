
import json
from datetime import datetime
import pytz


pdf_dict = {
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
        "name": "Erzeugnisrelevanz",
        "type": "btn",
        "values": {
            "Ja": "/0",
            "Nein": "/1"
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

with open('form_fields.json', 'r', encoding='utf-8') as f:
    form_fields = json.load(f)
    

for fieldnumber, field_data in form_fields.items():
    if "/FT" in field_data and field_data["/FT"] == "/Tx":
        if "/V" in field_data:
            text = field_data["/V"].strip().replace("\r", " ") # strip newlines and spaces and remove returns          
            description = pdf_dict[fieldnumber]["name"]
            print(f"{fieldnumber} {description}: {text}")
        if "/V" not in field_data: # Handle cases where text fields are empty
            description = pdf_dict[fieldnumber]["name"]
            print(f"\033[31m{fieldnumber} {description}: N/A\033[0m")

    if "/FT" in field_data and field_data["/FT"] == "/Btn":
        if "/V" in field_data:
            value = field_data["/V"]
            if fieldnumber in pdf_dict and "values" in pdf_dict[fieldnumber]: # Check if the field exists in the pdf_dict (to get the human-readable name)
                for label, state in pdf_dict[fieldnumber]["values"].items(): # Find the human-readable name using the value
                    if state == value:
                        description = pdf_dict[fieldnumber]["name"] # Get the description from the /TU field (if available)
                        print(f"{fieldnumber} {description}: {label} ({value})") # Print field description, value, and human-readable name
                        
    if "/FT" in field_data and field_data["/FT"] == "/Sig":
        if "/V" in field_data:
            value = field_data["/V"]
            signatory = value['Name']
            sign_date = value['M']
            
            # establish date and timezone parts
            date_str = sign_date[2:16]
            timezone_str = sign_date[16:].strip()

            # datetime format
            dt = datetime.strptime(date_str, '%Y%m%d%H%M%S')
           
            # german format
            german_date = dt.strftime('%d.%m.%Y, %H:%M:%S')
            common_format = dt.strftime('%Y.%m.%d, %H:%M:%S')
            
            print(f"{fieldnumber} "f"\033[33m{signatory}\033[0m", f"\033[31m{common_format} {timezone_str}\033[0m")