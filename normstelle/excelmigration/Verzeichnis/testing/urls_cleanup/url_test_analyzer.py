#!/usr/bin/env python3
"""
URL Test Analyzer for Verzeichnis.json

This script analyzes the URLs in Verzeichnis.json to determine:
- How many URLs were fixed by the cleanup process
- Success rates including and excluding ignored URLs
- Detailed statistics and breakdown of URL types
"""

import json
import os
import re
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any

class URLAnalyzer:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.ignore_patterns = set()
        self.dead_urls = set()
        self.replacement_rules = []
        self.target_replacement = ""
        
    def load_rules_and_ignores(self, replace_file: str = "replace"):
        """Load replacement rules and ignore patterns."""
        replace_path = os.path.join(self.base_dir, replace_file)
        
        try:
            with open(replace_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
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
                    ignore_file = line.split(':', 1)[1].strip()
                    self.load_ignore_file(ignore_file)
                elif current_section == 'replace':
                    self.replacement_rules.append(line)
                elif current_section == 'with':
                    self.target_replacement = line
                elif current_section == 'ignore':
                    self.ignore_patterns.add(line)
                    
        except FileNotFoundError:
            print(f"Warning: Replace file '{replace_path}' not found")
        except Exception as e:
            print(f"Error loading rules: {e}")
    
    def load_ignore_file(self, file_path: str):
        """Load URLs to ignore from a separate file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.dead_urls.add(line)
        except FileNotFoundError:
            print(f"Warning: Ignore file '{file_path}' not found")
        except Exception as e:
            print(f"Error loading ignore file: {e}")
    
    def categorize_url(self, url: str) -> str:
        """Categorize a URL into different types."""
        if not url:
            return "empty"
            
        # Check if URL should be ignored
        if self.should_ignore_url(url):
            return "ignored"
            
        # Check if URL uses old patterns that should be replaced
        for old_pattern in self.replacement_rules:
            if old_pattern in url:
                return "needs_fixing"
                
        # Check if URL already uses the new pattern
        if self.target_replacement and self.target_replacement.rstrip('\\') in url:
            return "already_fixed"
            
        # Check URL types
        if url.startswith(('http://', 'https://')):
            return "web_url"
        elif url.startswith('\\\\'):
            return "network_path"
        elif url.startswith(('../', '..\\')):
            return "relative_path"
        elif ':' in url and url[1:3] == ':\\':
            return "absolute_path"
        else:
            return "other"
    
    def should_ignore_url(self, url: str) -> bool:
        """Check if a URL should be ignored."""
        if not url:
            return True
            
        # Check against ignore patterns
        for pattern in self.ignore_patterns:
            if pattern in url:
                return True
                
        # Check against dead URLs
        if url in self.dead_urls:
            return True
            
        return False
    
    def extract_urls_from_entry(self, entry: Dict) -> List[Tuple[str, str]]:
        """Extract all URLs from a data entry. Returns list of (column, url) tuples."""
        urls = []
        
        hyperlink_columns = [
            "Antrag", "Datenblatt", "Produkt-zulassung", "SDB MSDS",
            "Gefährdungsprüfungeurteilung", "Gefährdungsprüfung", 
            "Sonstiges", "Schriftverkehr", "Änd. Historie"
        ]
        
        for column in hyperlink_columns:
            if column in entry and entry[column]:
                if isinstance(entry[column], dict) and 'url' in entry[column]:
                    url = entry[column]['url']
                    if url:
                        urls.append((column, url))
                        
        return urls
    
    def analyze_json_file(self, file_path: str) -> Dict:
        """Analyze URLs in a JSON file and return statistics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{file_path}': {e}")
            return {}
        
        stats = {
            'total_entries': len(data.get('data', [])),
            'total_urls': 0,
            'url_categories': defaultdict(int),
            'column_stats': defaultdict(int),
            'url_examples': defaultdict(list)
        }
        
        # Analyze each entry
        for entry in data.get('data', []):
            urls = self.extract_urls_from_entry(entry)
            stats['total_urls'] += len(urls)
            
            for column, url in urls:
                category = self.categorize_url(url)
                stats['url_categories'][category] += 1
                stats['column_stats'][column] += 1
                
                # Store examples (limit to 3 per category)
                if len(stats['url_examples'][category]) < 3:
                    stats['url_examples'][category].append(url)
        
        return stats
    
    def calculate_success_rates(self, stats: Dict) -> Dict:
        """Calculate success rates and percentages."""
        total_urls = stats['total_urls']
        if total_urls == 0:
            return {'error': 'No URLs found'}
        
        categories = stats['url_categories']
        
        # URLs that can potentially be fixed (excluding ignored ones)
        fixable_urls = total_urls - categories.get('ignored', 0) - categories.get('empty', 0)
        
        # URLs that were successfully processed
        fixed_urls = categories.get('already_fixed', 0)
        needs_fixing = categories.get('needs_fixing', 0)
        
        results = {
            'total_urls': total_urls,
            'fixable_urls': fixable_urls,
            'ignored_urls': categories.get('ignored', 0),
            'empty_urls': categories.get('empty', 0),
            'fixed_urls': fixed_urls,
            'needs_fixing': needs_fixing,
            'web_urls': categories.get('web_url', 0),
            'other_urls': categories.get('other', 0) + categories.get('network_path', 0) + categories.get('relative_path', 0) + categories.get('absolute_path', 0)
        }
        
        # Calculate percentages
        if total_urls > 0:
            results['fix_rate_total'] = (fixed_urls / total_urls) * 100
            results['ignore_rate_total'] = (results['ignored_urls'] / total_urls) * 100
        
        if fixable_urls > 0:
            results['fix_rate_fixable'] = (fixed_urls / fixable_urls) * 100
            results['remaining_rate_fixable'] = (needs_fixing / fixable_urls) * 100
        
        return results
    
    def print_detailed_report(self, stats: Dict, title: str):
        """Print a detailed analysis report."""
        print(f"\n{'='*60}")
        print(f"{title.center(60)}")
        print(f"{'='*60}")
        
        if 'error' in stats:
            print(f"Error: {stats['error']}")
            return
        
        # Basic statistics
        print(f"Total entries: {stats['total_entries']:,}")
        print(f"Total URLs found: {stats['total_urls']:,}")
        
        # URL categories breakdown
        print(f"\nURL Categories:")
        print(f"-" * 40)
        for category, count in sorted(stats['url_categories'].items()):
            percentage = (count / stats['total_urls']) * 100 if stats['total_urls'] > 0 else 0
            print(f"{category.replace('_', ' ').title():<20}: {count:>6,} ({percentage:>5.1f}%)")
        
        # Column statistics
        print(f"\nURLs by Column:")
        print(f"-" * 40)
        for column, count in sorted(stats['column_stats'].items()):
            percentage = (count / stats['total_urls']) * 100 if stats['total_urls'] > 0 else 0
            print(f"{column:<25}: {count:>6,} ({percentage:>5.1f}%)")
        
        # Examples
        print(f"\nURL Examples by Category:")
        print(f"-" * 40)
        for category, examples in stats['url_examples'].items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for i, example in enumerate(examples, 1):
                # Truncate long URLs
                display_url = example[:80] + "..." if len(example) > 80 else example
                print(f"  {i}. {display_url}")
    
    def compare_before_after(self, before_stats: Dict, after_stats: Dict):
        """Compare statistics before and after cleanup."""
        print(f"\n{'='*60}")
        print(f"BEFORE vs AFTER COMPARISON".center(60))
        print(f"{'='*60}")
        
        before_results = self.calculate_success_rates(before_stats)
        after_results = self.calculate_success_rates(after_stats)
        
        if 'error' in before_results or 'error' in after_results:
            print("Error in calculating results")
            return
        
        print(f"{'Metric':<30} {'Before':<12} {'After':<12} {'Change':<12}")
        print(f"-" * 66)
        
        metrics = [
            ('Total URLs', 'total_urls'),
            ('Fixed URLs', 'fixed_urls'),
            ('URLs Needing Fix', 'needs_fixing'),
            ('Ignored URLs', 'ignored_urls'),
            ('Fix Rate (Total)', 'fix_rate_total'),
            ('Fix Rate (Fixable)', 'fix_rate_fixable')
        ]
        
        for label, key in metrics:
            before_val = before_results.get(key, 0)
            after_val = after_results.get(key, 0)
            
            if 'rate' in key:
                change = after_val - before_val
                print(f"{label:<30} {before_val:>8.1f}%  {after_val:>8.1f}%  {change:>+8.1f}%")
            else:
                change = after_val - before_val
                print(f"{label:<30} {before_val:>8,}    {after_val:>8,}    {change:>+8,}")
        
        print(f"\n{'SUCCESS SUMMARY':<30}")
        print(f"-" * 40)
        if after_results.get('fixable_urls', 0) > 0:
            success_rate = after_results.get('fix_rate_fixable', 0)
            print(f"Overall success rate (excl. ignored): {success_rate:.1f}%")
        
        if after_results.get('total_urls', 0) > 0:
            total_rate = after_results.get('fix_rate_total', 0)
            print(f"Overall success rate (incl. ignored): {total_rate:.1f}%")


def main():
    """Main function to run the URL analysis."""
    analyzer = URLAnalyzer()
    
    # Load rules and ignore patterns
    analyzer.load_rules_and_ignores()
    
    # Define file paths
    current_file = "Verzeichnis.json"
    backup_file = "Verzeichnis_backup.json"
    
    print("URL Analysis Report")
    print("==================")
    
    # Analyze current file
    if os.path.exists(current_file):
        print(f"\nAnalyzing current file: {current_file}")
        current_stats = analyzer.analyze_json_file(current_file)
        analyzer.print_detailed_report(current_stats, "CURRENT FILE ANALYSIS")
        
        current_results = analyzer.calculate_success_rates(current_stats)
        if 'error' not in current_results:
            print(f"\nCURRENT SUCCESS RATES:")
            print(f"Fix rate (including ignored): {current_results.get('fix_rate_total', 0):.1f}%")
            print(f"Fix rate (excluding ignored): {current_results.get('fix_rate_fixable', 0):.1f}%")
    else:
        print(f"Current file '{current_file}' not found")
        current_stats = {}
    
    # Analyze backup file if it exists
    if os.path.exists(backup_file):
        print(f"\nAnalyzing backup file: {backup_file}")
        backup_stats = analyzer.analyze_json_file(backup_file)
        analyzer.print_detailed_report(backup_stats, "BACKUP FILE ANALYSIS (BEFORE CLEANUP)")
        
        # Compare before and after if both exist
        if current_stats and backup_stats:
            analyzer.compare_before_after(backup_stats, current_stats)
    else:
        print(f"\nBackup file '{backup_file}' not found")
        print("Run the cleanup script first to create a backup for comparison")
    
    print(f"\n{'='*60}")
    print("Analysis completed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()



