#!/usr/bin/env python3
"""
Quick script to clean up any leftover temporary files that might be causing COM conflicts.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'normie.settings')
django.setup()

from django.conf import settings

def main():
    """Clean up temporary files."""
    temp_dir = Path(settings.BASE_DIR) / "normieapp" / "static" / "normieapp" / "temp"
    
    if not temp_dir.exists():
        print(f"❌ Temp directory not found: {temp_dir}")
        return 1
    
    # Patterns to clean up
    patterns = [
        "Verzeichnis_current.xlsb",    # Current XLSB file (new fixed name)
        "Verzeichnis_current.xlsx",    # Current XLSX file (new fixed name)
        "Verzeichnis_*.xlsb",          # Legacy timestamped XLSB files
        "Verzeichnis_*.xlsx",          # Legacy timestamped XLSX files  
        "Verzeichnis.xlsb",            # Legacy fixed name
        "Verzeichnis.xlsx",            # Legacy fixed name
        "Verzeichnis_original_temp.json",
        "Verzeichnis_temp.json"
    ]
    
    # Legacy testing files to clean up (now removed from production)
    data_dir = Path(settings.BASE_DIR) / "normieapp" / "static" / "normieapp" / "data"
    legacy_patterns = [
        "Verzeichnis_original.json",      # Original extracted data
        "Verzeichnis_original.json.backup", # Backup of original
        "urls_original.txt",              # URL list from original  
        "urls_cleaned.txt"                # URL list from cleaned
    ]
    
    total_cleaned = 0
    
    print(f"🧹 Cleaning temp directory: {temp_dir}")
    
    # Clean temp files
    for pattern in patterns:
        for temp_file in temp_dir.glob(pattern):
            try:
                temp_file.unlink()
                print(f"   ✅ Deleted temp: {temp_file.name}")
                total_cleaned += 1
            except Exception as e:
                print(f"   ⚠️  Could not delete {temp_file.name}: {e}")
    
    print(f"🧹 Cleaning legacy testing files: {data_dir}")
    
    # Clean legacy testing files from data directory
    for pattern in legacy_patterns:
        legacy_file = data_dir / pattern
        if legacy_file.exists():
            try:
                legacy_file.unlink()
                print(f"   ✅ Deleted legacy: {legacy_file.name}")
                total_cleaned += 1
            except Exception as e:
                print(f"   ⚠️  Could not delete {legacy_file.name}: {e}")
    
    if total_cleaned == 0:
        print("   ✨ No files to clean (already clean)")
    else:
        print(f"   🎉 Cleaned up {total_cleaned} files total")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

