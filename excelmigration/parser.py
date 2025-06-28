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

# extract all unique values from "data":"Einsatzort" (filtering out None values)
benennungen = set()
for item in data['data']:
    einsatzort = item.get('Einsatzort')
    if einsatzort is not None:  # Only add non-None values
        benennungen.add(einsatzort.strip().strip())

# save as txt file
with open('Einsatzort.txt', 'w') as file:
    for benennung in benennungen:
        file.write(benennung + '\n')


# read from abteilungen.txt
with open('Einsatzort.txt', 'r') as file:
    benennungen = file.readlines()

# print the unique values
print(benennungen)
