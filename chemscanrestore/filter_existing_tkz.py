import json
import os
from pathlib import Path

def filter_existing_tkz(verzeichnis_path, results_path, output_path=None):
    """
    Filter Verzeichnis_teilenummer_links.json to only include entries that exist in chemscan_tkz_results.json
    
    Args:
        verzeichnis_path (str): Path to Verzeichnis_teilenummer_links.json
        results_path (str): Path to chemscan_tkz_results.json
        output_path (str, optional): Path for output JSON file
    
    Returns:
        dict: Filtered data as dictionary
    """
    # Load the JSON files
    print(f"Loading Verzeichnis file: {verzeichnis_path}")
    with open(verzeichnis_path, 'r', encoding='utf-8') as f:
        verzeichnis_data = json.load(f)
    
    print(f"Loading ChemScan results file: {results_path}")
    with open(results_path, 'r', encoding='utf-8') as f:
        results_data = json.load(f)
    
    # Create a set of TKZs that exist in ChemScan
    existing_tkzs = set()
    for result in results_data['results']:
        if result.get('exists', False):
            # Clean up TKZ (remove any whitespace, convert to string)
            tkz = str(result['tkz']).strip()
            existing_tkzs.add(tkz)
    
    print(f"Found {len(existing_tkzs)} existing TKZs in ChemScan results")
    
    # Filter the Verzeichnis entries
    filtered_entries = []
    for entry in verzeichnis_data['teilenummer_links']:
        # Get the TKZ and clean it up
        tkz = entry.get('Teile-nummer')
        if not isinstance(tkz, str):
            tkz = str(tkz)
        
        # Remove any newlines or extra spaces (some entries might have multiple TKZs)
        tkz = tkz.strip().split('\n')[0]
        
        # Check if this TKZ exists in ChemScan
        if tkz in existing_tkzs:
            # Keep the entry as is without adding ChemScan details
            filtered_entries.append(entry)
    
    # Create the filtered data structure
    filtered_data = {
        "metadata": {
            "original_total_entries": len(verzeichnis_data['teilenummer_links']),
            "filtered_total_entries": len(filtered_entries),
            "filter_criteria": "Exists in ChemScan database",
            "original_verzeichnis_file": os.path.basename(verzeichnis_path),
            "original_results_file": os.path.basename(results_path)
        },
        "teilenummer_links": filtered_entries
    }
    
    # Determine output file path
    if output_path is None:
        script_dir = Path(__file__).parent
        output_path = script_dir / "existing_teilenummer_links.json"
    
    # Write to JSON file
    print(f"Writing filtered data to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully created filtered JSON file with {len(filtered_entries)} entries")
    print(f"Output file: {output_path}")
    
    return filtered_data

def main():
    """Main function to filter TKZ entries"""
    # Get the directory of this script
    script_dir = Path(__file__).parent
    verzeichnis_path = script_dir / "Verzeichnis_teilenummer_links.json"
    results_path = script_dir / "chemscan_tkz_results.json"
    
    if not verzeichnis_path.exists():
        print(f"Error: Verzeichnis file not found at {verzeichnis_path}")
        return
    
    if not results_path.exists():
        print(f"Error: ChemScan results file not found at {results_path}")
        return
    
    try:
        # Filter the entries
        filtered_data = filter_existing_tkz(str(verzeichnis_path), str(results_path))
        
        # Print summary
        print("\n" + "="*60)
        print("FILTERING SUMMARY")
        print("="*60)
        print(f"Original entries: {filtered_data['metadata']['original_total_entries']}")
        print(f"Filtered entries: {filtered_data['metadata']['filtered_total_entries']}")
        print(f"Filter criteria: {filtered_data['metadata']['filter_criteria']}")
        
        # Show sample data
        if filtered_data['teilenummer_links']:
            print(f"\nFirst filtered entry sample:")
            first_entry = filtered_data['teilenummer_links'][0]
            for key, value in first_entry.items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"Failed to filter data: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 