#!/usr/bin/env python3
"""
Main URL Processing Pipeline

This script chains together the URL cleanup and extraction processes:
1. Cleans URLs in Verzeichnis.json using url_cleanup.py
2. Extracts URLs from both original and cleaned versions using url_extract.py
3. Provides comparison and analysis between the two versions
"""

import os
import sys
import json, shutil
import subprocess
from datetime import datetime
from typing import List, Dict, Set

# Import the modules directly
from url_cleanup import URLCleaner
from url_extract import extract_urls

class URLProcessingPipeline:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            'cleanup_stats': {},
            'original_urls': [],
            'cleaned_urls': [],
            'comparison': {}
        }
    
    def run_cleanup(self, input_file: str = "Verzeichnis.json") -> str:
        """
        Run the URL cleanup process.
        Returns the path to the cleaned file.
        """
        print("="*60)
        print("STEP 1: CLEANING URLs")
        print("="*60)
        
        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found!")
            return None
        
        # Initialize and run URL cleaner
        cleaner = URLCleaner()
        cleaner.load_replacement_rules()
        
        # Create backup
        backup_file = f"Verzeichnis_backup_{self.timestamp}.json"
        print(f"Creating backup: {backup_file}")
        import shutil
        shutil.copy2(input_file, backup_file)
        
        # Clean URLs - this will create a new cleaned file
        cleaned_file = f"Verzeichnis_cleaned_{self.timestamp}.json"
        cleaner.cleanup_json_file(input_file, cleaned_file)
        
        # Store cleanup statistics
        self.results['cleanup_stats'] = cleaner.stats.copy()
        
        print(f"\nCleanup completed. Files created:")
        print(f"  - Backup: {backup_file}")
        print(f"  - Cleaned: {cleaned_file}")
        
        return cleaned_file
    
    def extract_urls_from_files(self, original_file: str, cleaned_file: str):
        """
        Extract URLs from both original and cleaned files.
        """
        print("\n" + "="*60)
        print("STEP 2: EXTRACTING URLs")
        print("="*60)
        
        # Extract URLs from original file
        print(f"\nExtracting URLs from original file: {original_file}")
        original_urls_file = f"urls_original_{self.timestamp}.txt"
        self.results['original_urls'] = extract_urls(
            extract_all=False, 
            output_file=original_urls_file
        )
        
        # Extract URLs from cleaned file
        if cleaned_file and os.path.exists(cleaned_file):
            print(f"\nExtracting URLs from cleaned file: {cleaned_file}")
            cleaned_urls_file = f"urls_cleaned_{self.timestamp}.txt"
            
            # Temporarily modify the extract_urls function to work with different file
            original_json_file = 'Verzeichnis.json'
            temp_json_file = 'Verzeichnis_temp.json'
            
            # Backup original, copy cleaned file to expected location
            if os.path.exists(original_json_file):
                shutil.copy2(original_json_file, temp_json_file)
            shutil.copy2(cleaned_file, original_json_file)
            
            try:
                self.results['cleaned_urls'] = extract_urls(
                    extract_all=False,
                    output_file=cleaned_urls_file
                )
            finally:
                # Restore original file
                if os.path.exists(temp_json_file):
                    shutil.copy2(temp_json_file, original_json_file)
                    os.remove(temp_json_file)
        
        print(f"\nURL extraction completed. Files created:")
        print(f"  - Original URLs: {original_urls_file}")
        if cleaned_file:
            print(f"  - Cleaned URLs: {cleaned_urls_file}")
    
    def compare_urls(self):
        """
        Compare original and cleaned URLs to analyze the changes.
        """
        print("\n" + "="*60)
        print("STEP 3: COMPARING URLs")
        print("="*60)
        
        original_set = set(self.results['original_urls'])
        cleaned_set = set(self.results['cleaned_urls'])
        
        # Find differences
        urls_removed = original_set - cleaned_set
        urls_added = cleaned_set - original_set
        urls_unchanged = original_set & cleaned_set
        
        # Count changes by pattern
        pattern_changes = {}
        for orig_url in urls_removed:
            for cleaned_url in urls_added:
                # Simple heuristic: if URLs have similar endings, they might be related
                orig_end = orig_url.split('\\')[-1] if '\\' in orig_url else orig_url.split('/')[-1]
                cleaned_end = cleaned_url.split('\\')[-1] if '\\' in cleaned_url else cleaned_url.split('/')[-1]
                
                if orig_end == cleaned_end:
                    pattern_changes[orig_url] = cleaned_url
                    break
        
        # Store comparison results
        self.results['comparison'] = {
            'total_original': len(original_set),
            'total_cleaned': len(cleaned_set),
            'unchanged_count': len(urls_unchanged),
            'removed_count': len(urls_removed),
            'added_count': len(urls_added),
            'pattern_changes_count': len(pattern_changes),
            'urls_removed': list(urls_removed)[:10],  # Sample of removed URLs
            'urls_added': list(urls_added)[:10],      # Sample of added URLs
            'pattern_changes': dict(list(pattern_changes.items())[:10])  # Sample of changes
        }
        
        # Print comparison results
        print(f"Original URLs count: {len(original_set):,}")
        print(f"Cleaned URLs count: {len(cleaned_set):,}")
        print(f"Unchanged URLs: {len(urls_unchanged):,}")
        print(f"URLs removed: {len(urls_removed):,}")
        print(f"URLs added: {len(urls_added):,}")
        print(f"Pattern-based changes detected: {len(pattern_changes):,}")
        
        if pattern_changes:
            print(f"\nSample URL changes:")
            for i, (orig, cleaned) in enumerate(list(pattern_changes.items())[:5], 1):
                print(f"  {i}. {orig[:60]}...")
                print(f"     -> {cleaned[:60]}...")
        
        # Calculate success rate
        if len(original_set) > 0:
            change_rate = (len(pattern_changes) / len(original_set)) * 100
            print(f"\nEstimated fix rate: {change_rate:.1f}%")
    
    def generate_report(self):
        """
        Generate a comprehensive report of the entire process.
        """
        print("\n" + "="*60)
        print("FINAL REPORT")
        print("="*60)
        
        report_file = f"url_processing_report_{self.timestamp}.json"
        
        # Add timestamp and summary to results
        self.results['timestamp'] = self.timestamp
        self.results['summary'] = {
            'total_urls_processed': self.results['cleanup_stats'].get('total_urls', 0),
            'urls_fixed': self.results['cleanup_stats'].get('fixed_urls', 0),
            'urls_ignored': self.results['cleanup_stats'].get('ignored_urls', 0),
            'fix_rate_percentage': (
                (self.results['cleanup_stats'].get('fixed_urls', 0) / 
                 self.results['cleanup_stats'].get('total_urls', 1)) * 100
            ) if self.results['cleanup_stats'].get('total_urls', 0) > 0 else 0
        }
        
        # Save detailed report
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"Detailed report saved to: {report_file}")
        
        # Print summary
        summary = self.results['summary']
        print(f"\nPROCESS SUMMARY:")
        print(f"  Total URLs processed: {summary['total_urls_processed']:,}")
        print(f"  URLs successfully fixed: {summary['urls_fixed']:,}")
        print(f"  URLs ignored: {summary['urls_ignored']:,}")
        print(f"  Overall fix rate: {summary['fix_rate_percentage']:.1f}%")
        
        cleanup_stats = self.results['cleanup_stats']
        if cleanup_stats.get('total_urls', 0) > 0:
            print(f"\nDETAILED STATISTICS:")
            print(f"  Fixed: {cleanup_stats.get('fixed_urls', 0):,}")
            print(f"  Ignored: {cleanup_stats.get('ignored_urls', 0):,}")
            print(f"  Unchanged: {cleanup_stats.get('unchanged_urls', 0):,}")
    
    def run_full_pipeline(self, input_file: str = "Verzeichnis.json"):
        """
        Run the complete URL processing pipeline.
        """
        print("URL PROCESSING PIPELINE")
        print("=======================")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Processing file: {input_file}")
        
        try:
            # Step 1: Clean URLs
            cleaned_file = self.run_cleanup(input_file)
            
            # Step 2: Extract URLs from both versions
            self.extract_urls_from_files(input_file, cleaned_file)
            
            # Step 3: Compare results
            if self.results['original_urls'] and self.results['cleaned_urls']:
                self.compare_urls()
            
            # Step 4: Generate report
            self.generate_report()
            
            print(f"\n{'='*60}")
            print("PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"\nError in pipeline: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function to run the URL processing pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run complete URL processing pipeline')
    parser.add_argument('--input', '-i', default='Verzeichnis.json',
                        help='Input JSON file (default: Verzeichnis.json)')
    parser.add_argument('--cleanup-only', action='store_true',
                        help='Run only the URL cleanup step')
    parser.add_argument('--extract-only', action='store_true',
                        help='Run only the URL extraction step')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found!")
        print("Make sure you're in the correct directory and the file exists.")
        sys.exit(1)
    
    # Initialize pipeline
    pipeline = URLProcessingPipeline()
    
    if args.cleanup_only:
        pipeline.run_cleanup(args.input)
    elif args.extract_only:
        # Just extract from existing files
        pipeline.extract_urls_from_files(args.input, "Verzeichnis_cleaned.json")
    else:
        # Run full pipeline
        pipeline.run_full_pipeline(args.input)


if __name__ == "__main__":
    main()







