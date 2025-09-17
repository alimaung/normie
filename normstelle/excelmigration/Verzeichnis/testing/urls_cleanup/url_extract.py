# URL Extraction Tool for Verzeichnis.json
# 
# Usage:
#   python url_extract.py               # Extract unique URLs only (default)
#   python url_extract.py --all         # Extract all URLs including duplicates
#   python url_extract.py -a            # Short form for --all
#   python url_extract.py -o myfile.txt # Specify custom output file
#
# Reads Verzeichnis.json and extracts all URLs from 'url' keys
# Outputs to urls.txt by default or custom file with -o flag

import json
import os
import argparse

def extract_urls(extract_all=False, output_file='urls.txt'):
    """Extract URLs from Verzeichnis.json and save to file
    
    Args:
        extract_all (bool): If True, extract all URLs including duplicates. If False, extract only unique URLs.
        output_file (str): Name of the output file.
    """
    
    # Path to the JSON file
    json_file = 'Verzeichnis.json'
    
    # Check if JSON file exists
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found!")
        return
    
    print(f"Reading {json_file}...")
    
    # Read and parse JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract URLs
    if extract_all:
        urls = []  # Use list to keep all URLs including duplicates
    else:
        urls = set()  # Use set to automatically handle uniqueness
    
    # Handle different JSON structures
    if isinstance(data, list):
        # If data is a list of objects
        for item in data:
            if isinstance(item, dict) and 'url' in item and item['url'] is not None:
                if extract_all:
                    urls.append(item['url'])
                else:
                    urls.add(item['url'])
    elif isinstance(data, dict):
        # If data is a single object or nested structure
        def extract_urls_recursive(obj):
            if isinstance(obj, dict):
                if 'url' in obj and obj['url'] is not None:
                    if extract_all:
                        urls.append(obj['url'])
                    else:
                        urls.add(obj['url'])
                for value in obj.values():
                    extract_urls_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_urls_recursive(item)
        
        extract_urls_recursive(data)
    
    # Process URLs based on extraction mode
    if extract_all:
        # Keep all URLs, just filter out None values and sort
        final_urls = sorted([url for url in urls if url is not None])
        print(f"Found {len(final_urls)} total URLs (including duplicates)")
    else:
        # Convert set to sorted list for consistent output
        final_urls = sorted([url for url in urls if url is not None])
        print(f"Found {len(final_urls)} unique URLs")
    
    # Write URLs to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in final_urls:
            f.write(url + '\n')
    
    print(f"URLs saved to {output_file}")
    return final_urls

def main():
    """Main function with command-line argument parsing"""
    parser = argparse.ArgumentParser(description='Extract URLs from Verzeichnis.json')
    parser.add_argument('--all', '-a', action='store_true', 
                        help='Extract all URLs including duplicates (default: extract unique URLs only)')
    parser.add_argument('--output', '-o', default='urls.txt',
                        help='Output file name (default: urls.txt)')
    
    args = parser.parse_args()
    
    # Extract URLs based on arguments
    extract_urls(extract_all=args.all, output_file=args.output)

if __name__ == "__main__":
    main()