
import os 
import CS_Control_V4 as c4

def filter():
    data = [
        [
            '049/2024', 
            '01044138', 
            'Ja', 
            'nein', 
            'CHEMIKALIE', 
            'Schwefelsäure 37% (Produktnummer: 17900014)', 
            '', 
            '2024-04-04 00:00:00+00:00', 
            '2024-06-10 00:00:00+00:00', 
            'A&T-ME', 
            'DW', 
            'Schrepffer, M.', 
            'pdf | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Antrag\\2024\\049-2024_01044138_Freigabe.pdf', 
            'pdf | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Datenblatt\\049-2024_01044138_DE_Schwefelsäure__37%_TI.pdf', 
            'msg | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Schriftverkehr\\049-2024_01044138_CHEMIKALIE Schwefelsäure 37% (Produktnummer 17900014).msg', 
            'pdf | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Sicherheitsdatenblatt\\049-2024_01044138_DE_Schwefelsäure_SDS.pdf', 
            '', 
            'pdf | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Gefährdungsbeurteilung\\049-2024_01044138_Schwefelsäure 37%_ChemScan.pdf', 
            'msg | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Schriftverkehr\\AW049-2024_01044138_CHEMIKALIE Schwefelsäure 37% (Produktnummer 17900014)_Ergaenzung Feld 19.msg', 
            'msg | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Schriftverkehr\\049-2024_01044138_Antrag.msg', 
            'msg | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Schriftverkehr\\049-2024_01044138_WG AfTS 0492024 (TKZ 01044138) - CHEMIKALIE Schwefelsäure 37%_Laborfreigabe.msg', 
            '', 
            '', 
            'Hohe Priorität.Nachfolgeprodukt für TKZ01041062 (Antrag 013/2010), da dieses nicht mehr lieferbar ist. Nachweis bezüglich Kontakt mit Luftfahrtbauteilen siehe Statement vom Hersteller in Email vom Antragsteller (Schriftverkehr).04.04.2024 an ChemScan08.04..2024: ChemScan Bewertung erhalten und Antrag zur Ergänzung von Feld 19 an Antragsteller weitergeleitet. Info am selben Tag ergänzt (siehe \'Sonstiges\').Bitte beachten: In Abwesenheit von Karsten Bartz (Urlaub) Antrag am 08.04.2024 zuerst zur Bewertung an HS&E DW gesendet. Nach Erhalt der Freigabe an Karsten Bartz weiterleiten.22.04.2024: E-Mail an Antragsteller mit der Bitte um ein TDS vom Hersteller für die Bewertung seitens Labor. TDS nachgeliefert und verlinkt.10.06.2024: Laborfreigabe erhalten, ist aber, laut Prozess, nicht notwendig, da kein Kontakt mit Luftfahrtteilen besteht (siehe Email unter \'Historie\').13.09.2024: Antwort auf Anrage auf fehlerhaften Eintrag im Antrag bezgl. der angegebenen Menge pro Anwendung (200ml oder 90KG) unter der Spalte O "Produktzulassung" verlinkt. Es soll nichts im Antrag korriegiert werden lt. Antragsteller.', 
            '', 
            '', 
            ''
        ], 
        [
            '096/2024', 
            '01044201',
            'Ja', 
            'nein', 
            'CHEMIKALIE', 
            'H2O_Schwefelsäure 37%, für Vacudest, Abwasseraufbereitung (Produktnummer: 17900014)', 
            '', 
            '2024-08-22 00:00:00+00:00', 
            '2024-08-28 00:00:00+00:00', 
            'A&T-ME', 
            'DW', 
            'Halavin, W.', 
            'pdf | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Antrag\\2024\\096-2024_01044201_Freigabe.pdf', 
            'pdf | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Datenblatt\\049-2024_01044138_DE_Schwefelsäure__37%_TI.pdf', 
            '', 
            'pdf | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Sicherheitsdatenblatt\\049-2024_01044138_DE_Schwefelsäure_SDS.pdf', 
            '', 
            'pdf | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Gefährdungsbeurteilung\\049-2024_01044138_Schwefelsäure 37%_ChemScan.pdf', 
            '', 
            'msg | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Schriftverkehr\\049-2024_01044138_Antrag.msg', 
            'pdf | \\\\dehesdna-a009a\\projekte\\k-z\\Ofs\\Dokumentenservice\\TeileundStoffe\\Antrag\\2024\\049-2024_01044138_Freigabe.pdf', 
            '', 
            '', 
            'Hinweis vom Antragsteller: Produkt bereits zugelassen, TKZ 01044138, 049/2024, Antrag nur ein Update zur Basismenge 75 kg, Hintergrund, wie beim Antrag 049/2024: Nachfolgeprodukt für TKZ 01041062, da dieses nicht mehr lieferbar ist. Nachweis bezüglich Kontakt mit Luftfahrtbauteilen "siehe Statement vom Hersteller in meiner Mail."  (siehe Schriftverkehr)Antrag in neue Vorlage übertragen. Da laut Prozess das SDB noch verwendbar ist (Version 3.0 vom 07.03.2023), werden sowohl SDB als auch ChemScan Bewertung und TDB für diesen Antrag erneut verwendet und hier entsprechend verlinkt. Vom Antragsteller erhaltene TDB & SDB der Fa Brenntag sind bei diesem Antrag nicht relevant.', 
            '', 
            '', 
            ''
        ]
    ]

    proc_data = []

    for row in data:
        ats = row[12].split("|")[1].replace("\\\\dehesdna-a009a\\projekte", "P:").strip()
        sdb = row[17].split("|")[1].replace("\\\\dehesdna-a009a\\projekte", "P:").strip()


        tkz = row[1]
        id = row[0].replace("/", "-")
        loc = row[10]

        ats_comment = "AT&S_" + id + "_" + tkz + "_" + loc
        sdb_comment = "ChemScan_" + id + "_" + tkz + "_" + loc

        dict = {}
        dict["id"] = id
        dict["tkz"] = tkz
        dict["ats"] = ats
        dict["sdb"] = sdb
        dict["loc"] = loc
        dict["ats_comment"] = ats_comment
        dict["sdb_comment"] = sdb_comment
        dict["exists"] = None
        dict["pdf"] = None
        dict["class"] = None

        proc_data.append(dict)

    print(proc_data)
    #return proc_data
    c4.main(proc_data)

filter()