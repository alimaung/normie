#!/usr/bin/env python3
"""
Simple script to repair corrupted JSON files in the mail directory.
Fixes common issues like missing commas and incomplete structures.
"""

import json
import os
import re
from pathlib import Path

def repair_json_file(file_path):
    """Repair a single JSON file."""
    print(f"Checking {file_path}...")
    
    try:
        # Try to read normally first
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"  ✓ {file_path} is already valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ⚠ {file_path} is corrupted: {e}")
        
        # Read raw content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Save backup
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  → Created backup: {backup_path}")
        
        # Apply repairs
        original_content = content
        
        # Fix missing commas before closing brackets/braces
        content = re.sub(r'(["\d\]\}])\s*\n\s*([}\]])', r'\1,\n\2', content)
        
        # Remove trailing commas before closing brackets/braces
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        # Fix incomplete objects
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces > close_braces:
            content += '}' * (open_braces - close_braces)
            print(f"  → Added {open_braces - close_braces} closing braces")
        
        # Fix incomplete arrays
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        if open_brackets > close_brackets:
            content += ']' * (open_brackets - close_brackets)
            print(f"  → Added {open_brackets - close_brackets} closing brackets")
        
        # Try to parse repaired content
        try:
            json.loads(content)
            
            # Write repaired content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✓ Repaired {file_path}")
            return True
            
        except json.JSONDecodeError as e2:
            print(f"  ✗ Could not repair {file_path}: {e2}")
            
            # Restore original
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            return False
    
    except Exception as e:
        print(f"  ✗ Error reading {file_path}: {e}")
        return False

def main():
    """Main function to repair all JSON files in the current directory."""
    print("JSON File Repair Tool")
    print("====================")
    
    # Find all JSON files
    json_files = list(Path('.').glob('emails_*.json'))
    
    if not json_files:
        print("No email JSON files found in current directory.")
        return
    
    print(f"Found {len(json_files)} email JSON files:")
    for f in json_files:
        print(f"  - {f}")
    print()
    
    repaired_count = 0
    failed_count = 0
    
    for json_file in json_files:
        if repair_json_file(json_file):
            if "repaired" in str(json_file):
                repaired_count += 1
        else:
            failed_count += 1
    
    print()
    print(f"Repair completed:")
    print(f"  ✓ {repaired_count} files repaired")
    print(f"  ✗ {failed_count} files failed")
    
    if repaired_count > 0:
        print("\nBackup files created with .backup extension")

if __name__ == '__main__':
    main() 