import csv
import os 


with open('filtered_data.csv', 'r', encoding='utf-8') as c:
    data = csv.reader(c, delimiter='\t')  # Use tab delimiter if needed
    
    #headers = next(data)
    #header_dict = {index: header for index, header in enumerate(headers)}
    #print(header_dict)  # Print the dictionary
    
    head_dict = {
        0: 'Antrag-nummer', 
        1: 'Teile-nummer', 
        2: 'Freigabe', 
        3: 'relevant für Luftfahrtteile', 
        4: 'Benennung', 
        5: 'Produktname / Normkurzbezeichnung', 
        6: 'Produktzulassungs-spezifikation', 
        7: 'Eingang', 
        8: 'Abschluss', 
        9: 'Abteilung', 
        10: 'Einsatzort', 
        11: 'Antragsteller', 
        12: 'Antrag', 
        13: 'Datenblatt', 
        14: 'Produkt-zulassung', 
        15: 'SDB MSDS', 
        16: 'Gefährdungsprüfungbeurteilung', 
        17: 'Gefährdungsprüfung', 
        18: 'Sonstiges', 
        19: 'Schriftverkehr', 
        20: 'Änd. Historie', 
        21: 'Datum', 
        22: 'Bearbeiter', 
        23: 'Bemerkung (289 offene Anträge)'
    }
    
    # Specify the column indices to fetch (e.g., column 1, 3, and 5)
    columns_to_fetch = [16]

    for index, row in enumerate(data):
        # Skip the header row (index 0) by checking the index
        if index == 0:
            continue

        # Fetch the specific columns based on the indices
        selected_columns = [row[i] for i in columns_to_fetch if i < len(row)]
        
        if selected_columns:
            # If you need to extract the part after 'ChemScan\\'
            for link in selected_columns:
                # Assuming the link is a string like 'pdf | ChemScan\\...'
                if '|' in link:
                    filepath = link.split('|')[1].strip(" ")  # Extract the part after 'ChemScan\\'
                    filename = filepath.split('\\')[1]
                    #folder = filepath.split('\\')[0]
                    #print(folder, filename)
                else:
                    print(link)  # If no 'ChemScan\\' part is found, print the link as it is
        
        cd = os.getcwd()
        file_path = os.path.join(cd, filename)
        os.startfile(file_path)

