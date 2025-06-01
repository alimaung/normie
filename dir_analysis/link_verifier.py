#!/usr/bin/env python3
"""
Link Verifier - Verify hyperlinks against actual directory structure
Checks if files referenced in Excel hyperlinks actually exist in the directory
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import unquote
import re

class LinkVerifier:
    def __init__(self, excel_json_path, directory_index_path, verbose=True):
        """
        Initialize the link verifier
        
        Args:
            excel_json_path (str): Path to the Excel extraction JSON
            directory_index_path (str): Path to the directory index JSON
            verbose (bool): Enable verbose logging
        """
        self.excel_json_path = excel_json_path
        self.directory_index_path = directory_index_path
        self.verbose = verbose
        
        # Load data
        self.excel_data = None
        self.directory_structure = None
        self.file_index = set()  # Set of all files for fast lookup
        
        # Results
        self.verification_results = {
            'total_links': 0,
            'valid_links': 0,
            'broken_links': 0,
            'invalid_format': 0,
            'broken_link_details': [],
            'statistics': {}
        }
        
    def log(self, message, level="INFO"):
        """Verbose logging with timestamp"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] [{level}] {message}")
    
    def load_data(self):
        """Load Excel data and directory index"""
        self.log("Loading Excel extraction data...")
        try:
            with open(self.excel_json_path, 'r', encoding='utf-8') as f:
                self.excel_data = json.load(f)
            self.log(f"Loaded {len(self.excel_data.get('data', []))} Excel records")
        except Exception as e:
            self.log(f"Error loading Excel data: {e}", "ERROR")
            return False
        
        self.log("Loading directory index...")
        try:
            with open(self.directory_index_path, 'r', encoding='utf-8') as f:
                directory_data = json.load(f)
                self.directory_structure = directory_data.get('structure', {})
            self.log(f"Loaded directory structure with {directory_data.get('metadata', {}).get('total_files', 0)} files")
        except Exception as e:
            self.log(f"Error loading directory index: {e}", "ERROR")
            return False
        
        # Build file index for fast lookup
        self.build_file_index()
        return True
    
    def build_file_index(self):
        """Build a set of all file paths for fast lookup"""
        self.log("Building file index for fast lookup...")
        
        def extract_files(structure, current_path=""):
            """Recursively extract all file paths"""
            for item_name, item_data in structure.items():
                if isinstance(item_data, dict):
                    # This is a directory
                    new_path = os.path.join(current_path, item_name) if current_path else item_name
                    
                    # Add files in this directory
                    for file_name in item_data.get('files', []):
                        file_path = os.path.join(new_path, file_name)
                        # Normalize path separators and case
                        normalized_path = file_path.replace('/', '\\').lower()
                        self.file_index.add(normalized_path)
                    
                    # Recursively process subdirectories
                    for subdir_name, subdir_data in item_data.get('subdirs', {}).items():
                        extract_files({subdir_name: subdir_data}, new_path)
        
        extract_files(self.directory_structure)
        self.log(f"Built file index with {len(self.file_index)} files")
    
    def normalize_url_to_path(self, url):
        """
        Convert a file URL to a relative path that can be checked against the directory index
        
        Args:
            url (str): File URL from Excel hyperlink
            
        Returns:
            tuple: (normalized_path, is_valid_format)
        """
        if not url:
            return None, False
        
        try:
            # Handle different URL formats
            if url.startswith("file:///"):
                # Remove file:/// prefix
                path_part = url[8:]
                
                # Handle network paths (\\server\share)
                if path_part.startswith("\\\\"):
                    # Extract the path after the server/share
                    # Expected format: \\Dehesdna-a009a\projekte\k-z\ofs\Dokumentenservice\TeileundStoffe\...
                    base_pattern = r"\\\\Dehesdna-a009a\\projekte\\k-z\\ofs\\Dokumentenservice\\TeileundStoffe\\?"
                    match = re.search(base_pattern, path_part, re.IGNORECASE)
                    
                    if match:
                        # Extract everything after the base path
                        relative_path = path_part[match.end():]
                        if relative_path:
                            # URL decode and normalize
                            decoded_path = unquote(relative_path)
                            normalized_path = decoded_path.replace('/', '\\').lower()
                            return f"teileundstoffe\\{normalized_path}", True
                        else:
                            # Root directory reference
                            return "teileundstoffe", True
                    else:
                        return None, False
                else:
                    # Local path format
                    decoded_path = unquote(path_part)
                    normalized_path = decoded_path.replace('/', '\\').lower()
                    return f"teileundstoffe\\{normalized_path}", True
            
            elif url.startswith("\\\\"):
                # Direct network path
                base_pattern = r"\\\\Dehesdna-a009a\\projekte\\k-z\\ofs\\Dokumentenservice\\TeileundStoffe\\?"
                match = re.search(base_pattern, url, re.IGNORECASE)
                
                if match:
                    relative_path = url[match.end():]
                    if relative_path:
                        normalized_path = relative_path.replace('/', '\\').lower()
                        return f"teileundstoffe\\{normalized_path}", True
                    else:
                        return "teileundstoffe", True
                else:
                    return None, False
            
            else:
                # Unknown format
                return None, False
                
        except Exception as e:
            self.log(f"Error normalizing URL '{url}': {e}", "WARNING")
            return None, False
    
    def verify_link(self, url, row_info):
        """
        Verify if a single link exists in the directory structure
        
        Args:
            url (str): URL to verify
            row_info (dict): Information about the row containing this link
            
        Returns:
            dict: Verification result
        """
        normalized_path, is_valid_format = self.normalize_url_to_path(url)
        
        if not is_valid_format:
            return {
                'status': 'invalid_format',
                'url': url,
                'normalized_path': None,
                'exists': False,
                'row_info': row_info
            }
        
        if not normalized_path:
            return {
                'status': 'invalid_format',
                'url': url,
                'normalized_path': None,
                'exists': False,
                'row_info': row_info
            }
        
        # Check if file exists in our index
        exists = normalized_path in self.file_index
        
        return {
            'status': 'valid' if exists else 'broken',
            'url': url,
            'normalized_path': normalized_path,
            'exists': exists,
            'row_info': row_info
        }
    
    def verify_all_links(self):
        """Verify all hyperlinks in the Excel data"""
        self.log("Starting link verification...")
        
        if not self.excel_data or not self.directory_structure:
            self.log("Data not loaded properly", "ERROR")
            return False
        
        # Hyperlink columns to check
        hyperlink_columns = [
            'Antrag', 'Datenblatt', 'Produkt-zulassung', 'SDB MSDS',
            'Gefährdungsprüfungeurteilung', 'Gefährdungsprüfung',
            'Sonstiges', 'Schriftverkehr', 'Änd. Historie'
        ]
        
        total_rows = len(self.excel_data.get('data', []))
        processed_rows = 0
        
        for row_idx, row in enumerate(self.excel_data.get('data', [])):
            # Create row info for context
            row_info = {
                'row_index': row_idx,
                'antrag_nummer': row.get('Antrag-nummer', 'Unknown'),
                'teile_nummer': row.get('Teile-nummer', 'Unknown'),
                'benennung': row.get('Benennung', 'Unknown')
            }
            
            # Check each hyperlink column
            for column in hyperlink_columns:
                if column in row and row[column]:
                    cell_data = row[column]
                    
                    # Check if this is a hyperlink object
                    if isinstance(cell_data, dict) and 'url' in cell_data:
                        url = cell_data['url']
                        if url:  # Skip None/empty URLs
                            self.verification_results['total_links'] += 1
                            
                            # Add column info to row context
                            row_info_with_column = row_info.copy()
                            row_info_with_column['column'] = column
                            row_info_with_column['display_text'] = cell_data.get('display_text', '')
                            
                            # Verify the link
                            result = self.verify_link(url, row_info_with_column)
                            
                            # Update statistics
                            if result['status'] == 'valid':
                                self.verification_results['valid_links'] += 1
                            elif result['status'] == 'broken':
                                self.verification_results['broken_links'] += 1
                                self.verification_results['broken_link_details'].append(result)
                            elif result['status'] == 'invalid_format':
                                self.verification_results['invalid_format'] += 1
                                self.verification_results['broken_link_details'].append(result)
            
            processed_rows += 1
            
            # Progress logging
            if processed_rows % 500 == 0:
                self.log(f"Processed {processed_rows:,}/{total_rows:,} rows "
                        f"({processed_rows/total_rows*100:.1f}%) - "
                        f"Found {self.verification_results['total_links']} links so far")
        
        self.log(f"Link verification completed!")
        self.log(f"Total links found: {self.verification_results['total_links']}")
        self.log(f"Valid links: {self.verification_results['valid_links']}")
        self.log(f"Broken links: {self.verification_results['broken_links']}")
        self.log(f"Invalid format: {self.verification_results['invalid_format']}")
        
        return True
    
    def generate_report(self):
        """Generate a comprehensive verification report"""
        self.log("Generating verification report...")
        
        # Calculate statistics
        total = self.verification_results['total_links']
        valid_pct = (self.verification_results['valid_links'] / total * 100) if total > 0 else 0
        broken_pct = (self.verification_results['broken_links'] / total * 100) if total > 0 else 0
        invalid_pct = (self.verification_results['invalid_format'] / total * 100) if total > 0 else 0
        
        # Group broken links by type
        broken_by_column = {}
        broken_by_year = {}
        
        for broken_link in self.verification_results['broken_link_details']:
            column = broken_link['row_info'].get('column', 'Unknown')
            broken_by_column[column] = broken_by_column.get(column, 0) + 1
            
            # Extract year from Antrag-nummer if possible
            antrag = broken_link['row_info'].get('antrag_nummer', '')
            year_match = re.search(r'(\d{4})', str(antrag))
            year = year_match.group(1) if year_match else 'Unknown'
            broken_by_year[year] = broken_by_year.get(year, 0) + 1
        
        report = {
            'verification_summary': {
                'scan_timestamp': datetime.now().isoformat(),
                'excel_file': self.excel_json_path,
                'directory_index': self.directory_index_path,
                'total_links_checked': total,
                'valid_links': self.verification_results['valid_links'],
                'broken_links': self.verification_results['broken_links'],
                'invalid_format_links': self.verification_results['invalid_format'],
                'validity_percentage': round(valid_pct, 2),
                'broken_percentage': round(broken_pct, 2),
                'invalid_percentage': round(invalid_pct, 2)
            },
            'broken_links_by_column': broken_by_column,
            'broken_links_by_year': broken_by_year,
            'broken_link_details': self.verification_results['broken_link_details'][:100],  # Limit to first 100
            'sample_broken_links': self.verification_results['broken_link_details'][:10]  # First 10 for quick review
        }
        
        return report
    
    def save_report(self, output_file="link_verification_report.json"):
        """Save verification report to JSON file"""
        self.log(f"Saving verification report to {output_file}")
        
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
        """Print a summary of verification results"""
        total = self.verification_results['total_links']
        if total == 0:
            print("No links found to verify.")
            return
        
        valid = self.verification_results['valid_links']
        broken = self.verification_results['broken_links']
        invalid = self.verification_results['invalid_format']
        
        print("\n" + "="*60)
        print("LINK VERIFICATION SUMMARY")
        print("="*60)
        print(f"Total Links Checked: {total:,}")
        print(f"Valid Links: {valid:,} ({valid/total*100:.1f}%)")
        print(f"Broken Links: {broken:,} ({broken/total*100:.1f}%)")
        print(f"Invalid Format: {invalid:,} ({invalid/total*100:.1f}%)")
        
        if broken > 0:
            print(f"\nFirst few broken links:")
            for i, broken_link in enumerate(self.verification_results['broken_link_details'][:5]):
                row_info = broken_link['row_info']
                print(f"  {i+1}. {row_info['antrag_nummer']} - {row_info['column']}")
                print(f"     URL: {broken_link['url'][:80]}...")
                print(f"     Expected: {broken_link['normalized_path']}")

def main():
    """Main function"""
    # File paths
    excel_json = "../excelmigration/Verzeichnis.json"
    directory_index = "directory_index.json"
    
    print("Link Verifier v1.0")
    print("=" * 50)
    print(f"Excel data: {excel_json}")
    print(f"Directory index: {directory_index}")
    print("=" * 50)
    
    # Check if files exist
    if not os.path.exists(excel_json):
        print(f"ERROR: Excel JSON file not found: {excel_json}")
        sys.exit(1)
    
    if not os.path.exists(directory_index):
        print(f"ERROR: Directory index file not found: {directory_index}")
        sys.exit(1)
    
    # Create verifier and run
    verifier = LinkVerifier(excel_json, directory_index, verbose=True)
    
    if not verifier.load_data():
        print("Failed to load data files")
        sys.exit(1)
    
    if not verifier.verify_all_links():
        print("Link verification failed")
        sys.exit(1)
    
    # Save report and print summary
    report_file = verifier.save_report()
    verifier.print_summary()
    
    if report_file:
        print(f"\nDetailed report saved to: {report_file}")
    
    print("\nVerification completed!")

if __name__ == "__main__":
    main() 