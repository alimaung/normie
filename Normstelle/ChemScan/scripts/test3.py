data = {
    'id': '004-2016', 
    'tkz': '01042757', 
    'ats': '\\\\Dehesdna-a009a\\projekte\\k-z\\ofs\\Dokumentenservice\\TeileundStoffe\\Antrag\\2016\\004-2016_01042757.pdf', 
    'sdb': '\\\\Dehesdna-a009a\\projekte\\k-z\\ofs\\Dokumentenservice\\TeileundStoffe\\Gefährdungsbeurteilung\\01042757_Mobil Jet Oil 387 FSE.pdf', 
    'loc': 'DW', 
    'ats_comment': 
    'AT&S_004-2016_01042757_DW', 
    'sdb_comment': 'ChemScan_004-2016_01042757_DW', 
    'exists': True, 
    'pdf': True, 
    'class': True
    }

strings = [
    "004-201..757.pdf 148.08 KB 03.03.2025, 14:15 AT&S_004-2016_01042757_DW",
    "0104275..FSE.pdf 147.39 KB 03.03.2025, 14:15 ChemScan_004-2016_01042757_DW",
    "027-201..419.pdf 83.91 KB 03.03.2025, 14:15 AT&S_027-2019_01043419_DW",
    "0104341..387.pdf 125.14 KB 03.03.2025, 14:15 ChemScan_027-2019_01043419_DW"
]

comment_entries = []
for string in strings:
    s1 = string.split(" ")
    comment = s1[5]
    comment_entries.append(comment)

print(comment_entries) # list with comments only

print(data)

for key in data:
    print(key[])
#
## iterate through the list and remove existing comments
#for entry in comment_entries:
#    print(entry)
#    for key in data:
#        print(key["ats"])

