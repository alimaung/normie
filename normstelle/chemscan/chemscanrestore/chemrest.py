import json
import os
import sys

# Add parent directory to path to import CS_Control_V4
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from .CS import CS_Control_V4

def upload_specific_ats(tkz_list=None):
    """
    Upload specific ATS files to ChemScan based on TKZ numbers
    
    Args:
        tkz_list (list): List of TKZ numbers to upload, or None to prompt user
    """
    # Load the JSON data
    json_path = os.path.join(os.path.dirname(__file__), 'Verzeichnis_teilenummer_links.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # If no TKZ list provided, ask user for input
    if not tkz_list:
        input_tkz = input("Enter TKZ number(s) separated by commas: ")
        tkz_list = [tkz.strip() for tkz in input_tkz.split(',')]
    
    # Filter data for the specified TKZ numbers
    filtered_items = []
    for item in data['teilenummer_links']:
        if str(item['Teile-nummer']).strip() in tkz_list:
            filtered_items.append(item)
    
    if not filtered_items:
        print(f"No matching TKZ numbers found in the data.")
        return
    
    # Format data for CS_Control_V4
    upload_data = []
    for item in filtered_items:
        # Format the data as expected by CS_Control_V4
        entry = {
            "id": item['Antrag-nummer'].replace("/", "-"),
            "tkz": str(item['Teile-nummer']),
            "ats": item['File_URL'],
            "sdb": "",  # No SDB in this case
            "loc": item['Location'],
            "ats_comment": item['Comment'],
            "sdb_comment": "",
            "exists": None,
            "pdf": None,
            "class": None
        }
        upload_data.append(entry)
        print(f"Prepared for upload: TKZ {entry['tkz']} - {entry['ats']}")
    
    # Confirm before uploading
    confirm = input(f"Ready to upload {len(upload_data)} files. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Upload cancelled.")
        return
    
    # Call CS_Control_V4.main with the data
    try:
        CS_Control_V4.main(upload_data)
        print("Upload process completed.")
    except Exception as e:
        print(f"Error during upload: {e}")

if __name__ == "__main__":
    upload_specific_ats()