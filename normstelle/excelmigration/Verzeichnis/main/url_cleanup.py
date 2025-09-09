#!/usr/bin/env python3
"""
URL Cleanup Script for Verzeichnis.json

This script fixes URLs in the Verzeichnis.json file by applying replacement rules
defined in the 'replace' file and ignoring URLs specified in the ignore lists.
"""

import json
import os
import re
from typing import Dict, List, Set, Tuple, Any

class URLCleaner:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.replacement_rules = []
        self.ignore_patterns = set()
        self.dead_urls = set()
        self.target_replacement = ""
        
        # Statistics
        self.stats = {
            'total_urls': 0,
            'fixed_urls': 0,
            'ignored_urls': 0,
            'unchanged_urls': 0,
            'error_urls': 0
        }
        
    def load_replacement_rules(self, replace_file: str = "replace"):
        """Load replacement rules from the replace file."""
        replace_path = os.path.join(self.base_dir, replace_file)
        
        try:
            with open(replace_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the replace file
            lines = content.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.lower() == 'replace:':
                    current_section = 'replace'
                elif line.lower() == 'with:':
                    current_section = 'with'
                elif line.lower() == 'ignore:':
                    current_section = 'ignore'
                elif line.startswith('+contents of:'):
                    # Load additional ignore file
                    ignore_file = line.split(':', 1)[1].strip()
                    self.load_ignore_file(ignore_file)
                elif current_section == 'replace':
                    # Add patterns to replace
                    self.replacement_rules.append(line)
                elif current_section == 'with':
                    # Set the target replacement
                    self.target_replacement = line
                elif current_section == 'ignore':
                    # Add patterns to ignore
                    self.ignore_patterns.add(line)
            
            print(f"Loaded {len(self.replacement_rules)} replacement rules")
            print(f"Target replacement: {self.target_replacement}")
            print(f"Loaded {len(self.ignore_patterns)} ignore patterns")
            
        except FileNotFoundError:
            print(f"Warning: Replace file '{replace_path}' not found")
        except Exception as e:
            print(f"Error loading replacement rules: {e}")
    
    def load_ignore_file(self, file_path: str):
        """Load URLs to ignore from a separate file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.dead_urls.add(line)
            print(f"Loaded {len(self.dead_urls)} dead URLs from {file_path}")
        except FileNotFoundError:
            print(f"Warning: Ignore file '{file_path}' not found")
        except Exception as e:
            print(f"Error loading ignore file: {e}")
    
    def should_ignore_url(self, url: str) -> bool:
        """Check if a URL should be ignored based on patterns and dead URL list."""
        if not url:
            return True
            
        # Check against ignore patterns
        for pattern in self.ignore_patterns:
            if pattern in url:
                return True
                
        # Check against dead URLs
        if url in self.dead_urls:
            return True
            
        # Check for HTTP/HTTPS URLs (should be ignored)
        if url.startswith(('http://', 'https://')):
            return True
            
        return False
    
    def fix_url(self, url: str) -> Tuple[str, bool]:
        """
        Fix a single URL based on replacement rules.
        Returns (fixed_url, was_changed)
        """
        if not url or self.should_ignore_url(url):
            return url, False
            
        original_url = url
        
        # Apply replacement rules
        for old_pattern in self.replacement_rules:
            if old_pattern in url:
                # Replace the old pattern with the new target
                url = url.replace(old_pattern, self.target_replacement)
                
        # Normalize path separators (convert forward slashes to backslashes for Windows paths)
        if url.startswith('\\\\'):
            url = url.replace('/', '\\')
            
        return url, url != original_url
    
    def process_url_object(self, obj: Any) -> bool:
        """
        Process a URL object (dict with 'url' field) and fix its URL.
        Returns True if the URL was changed.
        """
        if not isinstance(obj, dict) or 'url' not in obj:
            return False
            
        original_url = obj['url']
        if not original_url:
            return False
            
        self.stats['total_urls'] += 1
        
        if self.should_ignore_url(original_url):
            self.stats['ignored_urls'] += 1
            return False
            
        fixed_url, was_changed = self.fix_url(original_url)
        
        if was_changed:
            obj['url'] = fixed_url
            self.stats['fixed_urls'] += 1
            print(f"Fixed: {original_url[:80]}... -> {fixed_url[:80]}...")
            return True
        else:
            self.stats['unchanged_urls'] += 1
            return False
    
    def process_data_entry(self, entry: Dict) -> int:
        """
        Process a single data entry and fix all URLs within it.
        Returns the number of URLs that were changed.
        """
        changes = 0
        
        # Get hyperlink columns from metadata or use defaults
        hyperlink_columns = [
            "Antrag", "Datenblatt", "Produkt-zulassung", "SDB MSDS",
            "Gefährdungsprüfungeurteilung", "Gefährdungsprüfung", 
            "Sonstiges", "Schriftverkehr", "Änd. Historie"
        ]
        
        for column in hyperlink_columns:
            if column in entry and entry[column]:
                if self.process_url_object(entry[column]):
                    changes += 1
                    
        return changes
    
    def cleanup_json_file(self, input_file: str, output_file: str = None):
        """
        Clean up URLs in the JSON file.
        If output_file is None, creates a new cleaned file.
        """
        if output_file is None:
            # Create a new cleaned file instead of overwriting
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_cleaned.json"
            
        try:
            # Load JSON data
            print(f"Loading {input_file}...")
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Processing {len(data.get('data', []))} entries...")
            
            total_changes = 0
            
            # Process each data entry
            for i, entry in enumerate(data.get('data', [])):
                changes = self.process_data_entry(entry)
                total_changes += changes
                
                if (i + 1) % 100 == 0:
                    print(f"Processed {i + 1} entries...")
            
            # Update metadata
            if 'metadata' in data:
                data['metadata']['url_cleanup'] = {
                    'applied': True,
                    'total_changes': total_changes,
                    'statistics': self.stats.copy(),
                    'rules_applied': len(self.replacement_rules),
                    'target_replacement': self.target_replacement
                }
            
            # Save the cleaned data
            print(f"Saving cleaned data to {output_file}...")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Print statistics
            print("\n" + "="*50)
            print("URL CLEANUP COMPLETED")
            print("="*50)
            print(f"Total URLs processed: {self.stats['total_urls']}")
            print(f"URLs fixed: {self.stats['fixed_urls']}")
            print(f"URLs ignored: {self.stats['ignored_urls']}")
            print(f"URLs unchanged: {self.stats['unchanged_urls']}")
            print(f"Total changes made: {total_changes}")
            
            if self.stats['total_urls'] > 0:
                fix_rate = (self.stats['fixed_urls'] / self.stats['total_urls']) * 100
                print(f"Fix rate: {fix_rate:.2f}%")
                
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{input_file}': {e}")
        except Exception as e:
            print(f"Error processing file: {e}")


def main():
    """Main function to run the URL cleanup."""
    # Initialize cleaner
    cleaner = URLCleaner()
    
    # Load replacement rules
    cleaner.load_replacement_rules()
    
    # Define file paths
    input_file = "Verzeichnis.json"
    backup_file = "Verzeichnis_backup.json"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found in current directory")
        print("Make sure you're running this script from the correct directory")
        return
    
    # Create backup
    print(f"Creating backup: {backup_file}")
    import shutil
    shutil.copy2(input_file, backup_file)
    
    # Clean up URLs
    cleaner.cleanup_json_file(input_file)
    
    print(f"\nBackup saved as: {backup_file}")
    print("URL cleanup completed successfully!")


if __name__ == "__main__":
    main()
