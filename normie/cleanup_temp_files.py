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
    
    total_cleaned = 0
    
    print(f"🧹 Cleaning temp directory: {temp_dir}")
    
    for pattern in patterns:
        for temp_file in temp_dir.glob(pattern):
            try:
                temp_file.unlink()
                print(f"   ✅ Deleted: {temp_file.name}")
                total_cleaned += 1
            except Exception as e:
                print(f"   ⚠️  Could not delete {temp_file.name}: {e}")
    
    if total_cleaned == 0:
        print("   ✨ No temp files found (already clean)")
    else:
        print(f"   🎉 Cleaned up {total_cleaned} temp files")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

