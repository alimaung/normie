#!/usr/bin/env python3
"""
Download missing files for the Kanbanize OpenAPI offline site
"""

import requests
import os
from pathlib import Path

def download_missing_files():
    """Download the files that weren't captured by the mirror script."""
    base_url = 'https://demo.kanbanize.com'
    
    files_to_download = [
        ('/openapi/json', 'openapi/openapi.json'),
        ('/application-v1110/resources/images/favicon.ico', 'openapi/favicon.ico')
    ]
    
    for url_path, local_path in files_to_download:
        try:
            url = base_url + url_path
            print(f'Downloading: {url}')
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Create directory if it doesn't exist
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            if local_path.endswith('.json'):
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
            else:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
            
            print(f'Saved: {local_path}')
            
        except Exception as e:
            print(f'Error downloading {url}: {e}')

if __name__ == "__main__":
    download_missing_files()
    print("\nMissing files download complete!")
    print("You can now open openapi/openapi.html in your browser.")

