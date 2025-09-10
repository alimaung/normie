#!/usr/bin/env python3
"""
Quick script to create the compressed JSON file manually.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'normie.settings')
django.setup()

from normieapp.services.directory_service import get_directory_service

def main():
    """Create compressed JSON file."""
    service = get_directory_service()
    
    # Get file paths
    data_dir = Path("normieapp/static/normieapp/data")
    input_file = data_dir / "Verzeichnis.json"
    output_file = data_dir / "Verzeichnis_compressed.json"
    
    if not input_file.exists():
        print(f"❌ Source file not found: {input_file}")
        return 1
    
    try:
        print(f"📂 Creating compressed JSON...")
        print(f"   Input:  {input_file}")
        print(f"   Output: {output_file}")
        
        size_info = service.optimize_json(str(input_file), str(output_file))
        
        print(f"✅ Compression complete!")
        print(f"   Original: {size_info['original_mb']:.1f}MB")
        print(f"   Compressed: {size_info['compressed_mb']:.1f}MB")
        print(f"   Savings: {size_info['savings_percent']:.1f}%")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

