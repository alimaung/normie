import requests
import json
import time
import os

# Load the JSON file with Teile-nummer entries
json_file_path = os.path.join(os.path.dirname(__file__), 'Verzeichnis_teilenummer_links.json')
with open(json_file_path, 'r', encoding='utf-8') as f:
    tkz_data = json.load(f)

# Set up the session with cookies
cookies = {
    "BAPRM": "K2REVVBEczZEWksxdGtvMXM2M2IrQmduWFp0bVpYS2VJVHN2eFFodWt0S1plTmJEb0N4TXRrYTQ5K2VIa3Zhallqb09JdVZHSER4OVdzNXlJU0phQXc9PTpBT2VVS3pud0d5cEtqZmxsN2dqb3hLRWp1MHlXMTRua2xYM1NSWkc2ZDN5SnlCT1htR1pxcC9MS3FRYVZidFBtUDUwMFE4K0IzdHNXVXdybHpod0dzQT09",
    "BAPID": "881b6ef489d246a5da0c52895d0a1d79",
    "https-_csrf": "jxN4VAAoOcPDQ1pC6DSUMnOFH9VQxG6fMvXwZ_FXqsc"
}

# Set up headers
headers = {
    "authority": "app.chemscan.de",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache, no-store",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "x-csrf-header": "jxN4VAAoOcPDQ1pC6DSUMnOFH9VQxG6fMvXwZ_FXqsc",
    "x-requested-with": "XMLHttpRequest"
}

# Create a list to store results
results = []

# Function to check if a TKZ exists in ChemScan
def check_tkz_exists(tkz):
    # Update referer with current TKZ
    headers["referer"] = f"https://app.chemscan.de/cadaster/organization/?grid%5Buub-hazard-substance-organization-with-actions-grid%5D=i%3D1%26p%3D25%26f%255BinternalName%255D%255Bvalue%255D%3D{tkz}%26f%255BinternalName%255D%255Btype%255D%3D1%26c%3Dactive1.hsSds1.hsHa1.hsWaterHazardClass1.internalName1.name1.alternativeName1.manufacturerName1.symbolSigns1.catalogRRates1.substanceName1.hazardSubstanceAssessmentBU1.responsibleUserGroup1.hsNumber0.additionalInfo10.additionalInfo20.catalogWarehouseClass0.catalogUnNumber0.hsForm0.hsBoilingPoint0.hsFlamePoint0.sdsRequested0.sdsPrinted0.hsVocAmount0%26v%3D__all__%26a%3Dgrid%26g%255BoriginalRoute%255D%3Duub_cadaster_organization_index"
    
    # Construct the URL with the TKZ
    url = f"https://app.chemscan.de/datagrid/uub-hazard-substance-organization-with-actions-grid?uub-hazard-substance-organization-with-actions-grid%5BoriginalRoute%5D=uub_cadaster_organization_index&appearanceType=grid&uub-hazard-substance-organization-with-actions-grid%5B_pager%5D%5B_page%5D=1&uub-hazard-substance-organization-with-actions-grid%5B_pager%5D%5B_per_page%5D=25&uub-hazard-substance-organization-with-actions-grid%5B_parameters%5D%5Bview%5D=__all__&uub-hazard-substance-organization-with-actions-grid%5B_appearance%5D%5B_type%5D=grid&uub-hazard-substance-organization-with-actions-grid%5B_filter%5D%5BinternalName%5D%5Bvalue%5D={tkz}&uub-hazard-substance-organization-with-actions-grid%5B_filter%5D%5BinternalName%5D%5Btype%5D=1&uub-hazard-substance-organization-with-actions-grid%5B_columns%5D=active1.hsSds1.hsHa1.hsWaterHazardClass1.internalName1.name1.alternativeName1.manufacturerName1.symbolSigns1.catalogRRates1.substanceName1.hazardSubstanceAssessmentBU1.responsibleUserGroup1.hsNumber0.additionalInfo10.additionalInfo20.catalogWarehouseClass0.catalogUnNumber0.hsForm0.hsBoilingPoint0.hsFlamePoint0.sdsRequested0.sdsPrinted0.hsVocAmount0"

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        response_json = response.json()
        
        # Check if the TKZ exists (if data array is not empty)
        exists = len(response_json.get("data", [])) > 0
        total_records = response_json.get("options", {}).get("totalRecords", 0)
        
        result = {
            "tkz": tkz,
            "exists": exists,
            "total_records": total_records
        }
        
        if exists:
            # Get the first record
            record = response_json["data"][0]
            result["name"] = record.get("name", "N/A")
            result["manufacturer"] = record.get("manufacturerName", "N/A")
            result["symbol_signs"] = record.get("symbolSigns", "N/A")
            result["hazard_codes"] = record.get("catalogRRates", "N/A")
        
        return result
    
    except Exception as e:
        print(f"Error checking TKZ {tkz}: {e}")
        return {
            "tkz": tkz,
            "exists": False,
            "error": str(e)
        }

# Process each Teile-nummer in the JSON file
print(f"Found {len(tkz_data['teilenummer_links'])} entries in the JSON file")
print("Starting to check each TKZ in ChemScan...")

for i, entry in enumerate(tkz_data['teilenummer_links']):
    tkz = entry.get('Teile-nummer')
    
    # Skip if TKZ is not a string (some might be numbers or other types)
    if not isinstance(tkz, str):
        tkz = str(tkz)
    
    # Remove any newlines or extra spaces (some entries might have multiple TKZs)
    tkz = tkz.strip().split('\n')[0]
    
    print(f"[{i+1}/{len(tkz_data['teilenummer_links'])}] Checking TKZ: {tkz}")
    
    result = check_tkz_exists(tkz)
    results.append(result)
    
    # Print the result
    if result["exists"]:
        print(f"  ✓ Found in ChemScan: {result.get('name', 'N/A')}")
    else:
        print(f"  ✗ Not found in ChemScan")
    
    # Add a small delay to avoid overwhelming the server
    time.sleep(1)

# Save results to a JSON file
output_file = os.path.join(os.path.dirname(__file__), 'chemscan_tkz_results.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        "metadata": {
            "total_checked": len(results),
            "total_found": sum(1 for r in results if r["exists"]),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "results": results
    }, f, indent=2)

# Print summary
found_count = sum(1 for r in results if r["exists"])
print("\nSummary:")
print(f"Total TKZs checked: {len(results)}")
print(f"TKZs found in ChemScan: {found_count}")
print(f"TKZs not found in ChemScan: {len(results) - found_count}")
print(f"Results saved to: {output_file}")
