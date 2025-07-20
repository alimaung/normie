#!/usr/bin/env python3
"""
Find Outlook data files and explore direct access options.
"""

import os
import glob
from pathlib import Path

def find_outlook_files():
    """Find PST and OST files."""
    print("Searching for Outlook data files...")
    
    search_paths = [
        os.path.expanduser("~\\AppData\\Local\\Microsoft\\Outlook\\"),
        os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Outlook\\"),
        os.path.expanduser("~\\Documents\\Outlook Files\\"),
    ]
    
    found_files = []
    
    for search_path in search_paths:
        for ext in ['*.pst', '*.ost']:
            try:
                pattern = os.path.join(search_path, ext)
                files = glob.glob(pattern)
                found_files.extend(files)
            except:
                pass
    
    return found_files

# Run this to see what files you have
files = find_outlook_files()
for f in files:
    print(f"Found: {f}")
    print(f"Size: {os.path.getsize(f) / (1024*1024):.1f} MB")