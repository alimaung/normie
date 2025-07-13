#!/usr/bin/env python3
"""
Fuzzy Link Finder - Find potential matches for broken links using fuzzy string matching
Searches the directory index to find files that might be the same as broken links
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import unquote
import re
from difflib import SequenceMatcher
from collections import defaultdict

class FuzzyLinkFinder:
    def __init__(self, verification_report_path, directory_index_path, verbose=True):
        """
        Initialize the fuzzy link finder
        
        Args:
            verification_report_path (str): Path to the link verification report JSON
            directory_index_path (str): Path to the directory index JSON
            verbose (bool): Enable verbose logging
        """
        self.verification_report_path = verification_report_path
        self.directory_index_path = directory_index_path
        self.verbose = verbose
        
        # Data storage
        self.verification_report = None
        self.directory_structure = None
        self.all_files = []  # List of all files with their full paths
        self.broken_links = []
        
        # Results
        self.fuzzy_matches = []
        
    def log(self, message, level="INFO"):
        """Verbose logging with timestamp"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] [{level}] {message}")
    
    def load_data(self):
        """Load verification report and directory index"""
        self.log("Loading link verification report...")
        try:
            with open(self.verification_report_path, 'r', encoding='utf-8') as f:
                self.verification_report = json.load(f)
            
            # Extract broken links
            self.broken_links = [
                link for link in self.verification_report.get('broken_link_details', [])
                if link['status'] == 'broken'  # Only actual broken links, not invalid format
            ]
            self.log(f"Found {len(self.broken_links)} broken links to analyze")
            
        except Exception as e:
            self.log(f"Error loading verification report: {e}", "ERROR")
            return False
        
        self.log("Loading directory index...")
        try:
            with open(self.directory_index_path, 'r', encoding='utf-8') as f:
                directory_data = json.load(f)
                self.directory_structure = directory_data.get('structure', {})
            self.log(f"Loaded directory structure")
        except Exception as e:
            self.log(f"Error loading directory index: {e}", "ERROR")
            return False
        
        # Build comprehensive file list
        self.build_file_list()
        return True
    
    def build_file_list(self):
        """Build a comprehensive list of all files with their paths"""
        self.log("Building comprehensive file list...")
        
        def extract_files(structure, current_path=""):
            """Recursively extract all file paths"""
            for item_name, item_data in structure.items():
                if isinstance(item_data, dict):
                    # This is a directory
                    new_path = os.path.join(current_path, item_name) if current_path else item_name
                    
                    # Add files in this directory
                    for file_name in item_data.get('files', []):
                        file_path = os.path.join(new_path, file_name)
                        self.all_files.append({
                            'full_path': file_path.replace('/', '\\'),
                            'filename': file_name,
                            'directory': new_path.replace('/', '\\'),
                            'extension': os.path.splitext(file_name)[1].lower()
                        })
                    
                    # Recursively process subdirectories
                    for subdir_name, subdir_data in item_data.get('subdirs', {}).items():
                        extract_files({subdir_name: subdir_data}, new_path)
        
        extract_files(self.directory_structure)
        self.log(f"Built file list with {len(self.all_files)} files")
    
    def similarity_score(self, str1, str2):
        """Calculate similarity score between two strings"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def extract_filename_from_broken_link(self, broken_link):
        """Extract the expected filename from a broken link"""
        normalized_path = broken_link.get('normalized_path', '')
        if not normalized_path:
            return None
        
        # Extract just the filename part
        filename = os.path.basename(normalized_path)
        return filename
    
    def find_fuzzy_matches(self, min_similarity=0.6, max_matches_per_link=5):
        """Find fuzzy matches for broken links"""
        self.log(f"Starting fuzzy search with minimum similarity {min_similarity}")
        
        total_broken = len(self.broken_links)
        processed = 0
        
        for broken_link in self.broken_links:
            expected_filename = self.extract_filename_from_broken_link(broken_link)
            if not expected_filename:
                continue
            
            # Get expected file extension
            expected_ext = os.path.splitext(expected_filename)[1].lower()
            
            # Find potential matches
            matches = []
            
            for file_info in self.all_files:
                # Only compare files with same extension
                if file_info['extension'] != expected_ext:
                    continue
                
                # Calculate similarity scores
                filename_similarity = self.similarity_score(expected_filename, file_info['filename'])
                
                # Also check similarity without path prefixes (just the core filename)
                expected_core = self.extract_core_filename(expected_filename)
                actual_core = self.extract_core_filename(file_info['filename'])
                core_similarity = self.similarity_score(expected_core, actual_core)
                
                # Use the higher of the two similarities
                best_similarity = max(filename_similarity, core_similarity)
                
                if best_similarity >= min_similarity:
                    matches.append({
                        'file_info': file_info,
                        'filename_similarity': filename_similarity,
                        'core_similarity': core_similarity,
                        'best_similarity': best_similarity
                    })
            
            # Sort by similarity and take top matches
            matches.sort(key=lambda x: x['best_similarity'], reverse=True)
            top_matches = matches[:max_matches_per_link]
            
            if top_matches:
                self.fuzzy_matches.append({
                    'broken_link': broken_link,
                    'expected_filename': expected_filename,
                    'matches': top_matches
                })
            
            processed += 1
            if processed % 50 == 0:
                self.log(f"Processed {processed}/{total_broken} broken links")
        
        self.log(f"Fuzzy search completed! Found potential matches for {len(self.fuzzy_matches)} broken links")
    
    def extract_core_filename(self, filename):
        """Extract core filename by removing common prefixes/suffixes"""
        # Remove file extension
        core = os.path.splitext(filename)[0]
        
        # Remove common patterns like dates, numbers, etc.
        # Remove leading numbers and dashes
        core = re.sub(r'^[\d\-_]+', '', core)
        
        # Remove trailing numbers and dashes
        core = re.sub(r'[\d\-_]+$', '', core)
        
        # Remove multiple spaces
        core = re.sub(r'\s+', ' ', core).strip()
        
        return core
    
    def generate_report(self):
        """Generate a comprehensive fuzzy match report"""
        self.log("Generating fuzzy match report...")
        
        # Statistics
        total_broken = len(self.broken_links)
        links_with_matches = len(self.fuzzy_matches)
        total_potential_matches = sum(len(match['matches']) for match in self.fuzzy_matches)
        
        # Group by similarity ranges
        similarity_ranges = {
            'high_confidence': [],  # 0.8+
            'medium_confidence': [],  # 0.6-0.8
            'low_confidence': []  # <0.6
        }
        
        for fuzzy_match in self.fuzzy_matches:
            best_match = fuzzy_match['matches'][0] if fuzzy_match['matches'] else None
            if best_match:
                similarity = best_match['best_similarity']
                if similarity >= 0.8:
                    similarity_ranges['high_confidence'].append(fuzzy_match)
                elif similarity >= 0.6:
                    similarity_ranges['medium_confidence'].append(fuzzy_match)
                else:
                    similarity_ranges['low_confidence'].append(fuzzy_match)
        
        # Group by file type
        by_extension = defaultdict(list)
        for fuzzy_match in self.fuzzy_matches:
            expected_filename = fuzzy_match['expected_filename']
            ext = os.path.splitext(expected_filename)[1].lower()
            by_extension[ext].append(fuzzy_match)
        
        report = {
            'fuzzy_search_summary': {
                'scan_timestamp': datetime.now().isoformat(),
                'verification_report': self.verification_report_path,
                'directory_index': self.directory_index_path,
                'total_broken_links': total_broken,
                'links_with_potential_matches': links_with_matches,
                'total_potential_matches': total_potential_matches,
                'match_rate_percentage': round((links_with_matches / total_broken * 100), 2) if total_broken > 0 else 0
            },
            'confidence_breakdown': {
                'high_confidence_matches': len(similarity_ranges['high_confidence']),
                'medium_confidence_matches': len(similarity_ranges['medium_confidence']),
                'low_confidence_matches': len(similarity_ranges['low_confidence'])
            },
            'matches_by_file_type': {ext: len(matches) for ext, matches in by_extension.items()},
            'high_confidence_matches': similarity_ranges['high_confidence'][:20],  # Top 20
            'medium_confidence_matches': similarity_ranges['medium_confidence'][:20],  # Top 20
            'all_fuzzy_matches': self.fuzzy_matches[:100]  # Limit to first 100 for file size
        }
        
        return report
    
    def save_report(self, output_file="fuzzy_link_matches.json"):
        """Save fuzzy match report to JSON file"""
        self.log(f"Saving fuzzy match report to {output_file}")
        
        try:
            report = self.generate_report()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(output_file)
            self.log(f"Report saved successfully! File size: {file_size:,} bytes")
            return output_file
            
        except Exception as e:
            self.log(f"Error saving report: {e}", "ERROR")
            return None
    
    def print_summary(self):
        """Print a summary of fuzzy match results"""
        total_broken = len(self.broken_links)
        links_with_matches = len(self.fuzzy_matches)
        
        print("\n" + "="*60)
        print("FUZZY LINK SEARCH SUMMARY")
        print("="*60)
        print(f"Total Broken Links Analyzed: {total_broken:,}")
        print(f"Links with Potential Matches: {links_with_matches:,}")
        print(f"Match Rate: {(links_with_matches/total_broken*100):.1f}%" if total_broken > 0 else "N/A")
        
        if links_with_matches > 0:
            # Show some examples
            print(f"\nTop fuzzy matches:")
            for i, fuzzy_match in enumerate(self.fuzzy_matches[:5]):
                broken_link = fuzzy_match['broken_link']
                best_match = fuzzy_match['matches'][0] if fuzzy_match['matches'] else None
                
                print(f"\n{i+1}. Expected: {fuzzy_match['expected_filename']}")
                print(f"   Row: {broken_link['row_info']['antrag_nummer']} - {broken_link['row_info']['column']}")
                if best_match:
                    print(f"   Best Match: {best_match['file_info']['filename']}")
                    print(f"   Similarity: {best_match['best_similarity']:.3f}")
                    print(f"   Location: {best_match['file_info']['directory']}")

def main():
    """Main function"""
    # File paths
    verification_report = "link_verification_report.json"
    directory_index = "directory_index.json"
    
    print("Fuzzy Link Finder v1.0")
    print("=" * 50)
    print(f"Verification report: {verification_report}")
    print(f"Directory index: {directory_index}")
    print("=" * 50)
    
    # Check if files exist
    if not os.path.exists(verification_report):
        print(f"ERROR: Verification report not found: {verification_report}")
        sys.exit(1)
    
    if not os.path.exists(directory_index):
        print(f"ERROR: Directory index file not found: {directory_index}")
        sys.exit(1)
    
    # Create finder and run
    finder = FuzzyLinkFinder(verification_report, directory_index, verbose=True)
    
    if not finder.load_data():
        print("Failed to load data files")
        sys.exit(1)
    
    # Run fuzzy search with different similarity thresholds
    finder.find_fuzzy_matches(min_similarity=0.6, max_matches_per_link=5)
    
    # Save report and print summary
    report_file = finder.save_report()
    finder.print_summary()
    
    if report_file:
        print(f"\nDetailed fuzzy match report saved to: {report_file}")
    
    print("\nFuzzy search completed!")

if __name__ == "__main__":
    main() 