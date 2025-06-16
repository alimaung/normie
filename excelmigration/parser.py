# read from verzeichnis.json
# extract all unique values from "data":"Benennung"
# {
#  "metadata": {
#    ...
#  },
#  "data": [
#    {
#      ...
#      "Benennung": "HAERTER",

import json

with open('verzeichnis.json', 'r') as file:
    data = json.load(file)

# extract all unique values from "data":"Bearbeiter" (filtering out None values)
benennungen = set()
for item in data['data']:
    bearbeiter = item.get('Antragsteller')
    if bearbeiter is not None:  # Only add non-None values
        benennungen.add(bearbeiter)

# save as txt file
with open('Antragsteller.txt', 'w') as file:
    for benennung in benennungen:
        file.write(benennung + '\n')


# read from abteilungen.txt
with open('Antragsteller.txt', 'r') as file:
    benennungen = file.readlines()

# print the unique values
print(benennungen)
