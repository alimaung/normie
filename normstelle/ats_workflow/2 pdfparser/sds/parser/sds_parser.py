#!/usr/bin/env python3
"""
German Safety Data Sheet (SDB/SDS) Parser

This script parses German safety data sheets in PDF format according to the 
EU REACH regulation 16-section structure. It supports both single file and 
batch processing modes with fuzzy string matching for header variations.

Author: Generated for normie project
Dependencies: PyMuPDF, rapidfuzz
"""

import argparse
import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF (fitz) is required. Install with: pip install PyMuPDF")
    sys.exit(1)

try:
    from rapidfuzz import fuzz, process
except ImportError:
    print("Error: rapidfuzz is required. Install with: pip install rapidfuzz")
    sys.exit(1)


@dataclass
class SDSSection:
    """Represents a section of an SDS document"""
    number: int
    title: str
    content: str
    found: bool = False


class SDSParser:
    """Parser for German Safety Data Sheets (Sicherheitsdatenblätter)"""
    
    # Standard 16 sections as per EU REACH regulation
    STANDARD_SECTIONS = {
        1: "Bezeichnung des Stoffs bzw. des Gemischs und des Unternehmens",
        2: "Mögliche Gefahren",
        3: "Zusammensetzung / Angaben zu Bestandteilen",
        4: "Erste-Hilfe-Maßnahmen",
        5: "Maßnahmen zur Brandbekämpfung",
        6: "Maßnahmen bei unbeabsichtigter Freisetzung",
        7: "Handhabung und Lagerung",
        8: "Begrenzung und Überwachung der Exposition / persönliche Schutzausrüstungen",
        9: "Physikalische und chemische Eigenschaften",
        10: "Stabilität und Reaktivität",
        11: "Toxikologische Angaben",
        12: "Umweltbezogene Angaben",
        13: "Hinweise zur Entsorgung",
        14: "Angaben zum Transport",
        15: "Rechtsvorschriften",
        16: "Sonstige Angaben"
    }
    
    def __init__(self, fuzzy_threshold: int = 60, debug: bool = False):
        """
        Initialize the SDS parser
        
        Args:
            fuzzy_threshold: Minimum similarity score for fuzzy matching (0-100)
            debug: Enable debug output
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.debug = debug
        
    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                text += page_text + "\n"
            
            doc.close()
            
            # Check if PDF contains extractable text
            if not text.strip():
                return None
                
            return text
            
        except Exception as e:
            if self.debug:
                print(f"Error extracting text from {pdf_path}: {e}")
            return None
    
    def normalize_section_header(self, header: str) -> str:
        """
        Normalize section header for better matching
        
        Args:
            header: Raw header text
            
        Returns:
            Normalized header text
        """
        # Remove extra whitespace and normalize case
        normalized = re.sub(r'\s+', ' ', header.strip())
        
        # Remove common punctuation variations
        normalized = re.sub(r'[:.–-]+\s*$', '', normalized)
        normalized = re.sub(r'^[:.–-]+\s*', '', normalized)
        
        return normalized
    
    def find_section_headers(self, text: str) -> List[Tuple[int, str, int]]:
        """
        Find section headers using fuzzy matching against expected section titles
        
        Args:
            text: Full text content
            
        Returns:
            List of tuples (section_number, header_text, position_in_text)
        """
        headers = []
        lines = text.split('\n')
        
        if self.debug:
            print(f"Searching through {len(lines)} lines for section titles...")
        
        # For each line, check if it could be a section header
        for line_idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Calculate the character position of this line in the full text
            char_position = len('\n'.join(lines[:line_idx]))
            
            # Try to match this line against all expected section titles
            best_match = None
            best_similarity = 0
            best_section_num = None
            best_method = ""
            
            for section_num, expected_title in self.STANDARD_SECTIONS.items():
                # Clean the line for comparison
                cleaned_line = self.normalize_section_header(line)
                
                # Remove common prefixes like "1.", "Abschnitt 1:", etc.
                cleaned_line = re.sub(r'^(?:\d{1,2}\.?\s*)?(?:abschnitt\s+\d{1,2}[\s.:–-]*)?\s*', '', cleaned_line, flags=re.IGNORECASE)
                
                # Calculate similarity using multiple methods
                similarity = fuzz.ratio(cleaned_line.lower(), expected_title.lower())
                partial_similarity = fuzz.partial_ratio(cleaned_line.lower(), expected_title.lower())
                token_sort_similarity = fuzz.token_sort_ratio(cleaned_line.lower(), expected_title.lower())
                
                # Prioritize token_sort_ratio as it handles word order differences best
                # Use the highest score, but give extra weight to token_sort for word order issues
                final_similarity = max(similarity, partial_similarity, token_sort_similarity)
                
                # Determine which method gave the best score
                method_used = "ratio"
                if final_similarity == partial_similarity:
                    method_used = "partial"
                if final_similarity == token_sort_similarity:
                    method_used = "token_sort"
                
                if final_similarity > best_similarity and final_similarity >= self.fuzzy_threshold:
                    best_similarity = final_similarity
                    best_match = line
                    best_section_num = section_num
                    best_method = method_used
                    
                if self.debug and final_similarity >= 50:  # Debug threshold lower than actual threshold
                    print(f"  Line: '{line[:50]}...' vs Section {section_num}: {final_similarity}% ({method_used})")
            
            # If we found a good match, add it
            if best_match and best_section_num:
                headers.append((best_section_num, best_match, char_position))
                if self.debug:
                    print(f"✅ Found section {best_section_num}: '{best_match}' (similarity: {best_similarity}%, method: {best_method})")
        
        # Sort by position in text and remove duplicates (keep the first occurrence)
        headers.sort(key=lambda x: x[2])
        
        # Remove duplicate section numbers (keep first occurrence)
        seen_sections = set()
        unique_headers = []
        for header in headers:
            if header[0] not in seen_sections:
                unique_headers.append(header)
                seen_sections.add(header[0])
        
        if self.debug:
            print(f"Final headers found: {[f'Section {h[0]}' for h in unique_headers]}")
        
        return unique_headers
    
    def extract_sections(self, text: str) -> Dict[int, SDSSection]:
        """
        Extract all sections from the text
        
        Args:
            text: Full text content
            
        Returns:
            Dictionary mapping section numbers to SDSSection objects
        """
        # Initialize all sections as not found
        sections = {}
        for num, title in self.STANDARD_SECTIONS.items():
            sections[num] = SDSSection(num, title, "", False)
        
        # Find all section headers
        headers = self.find_section_headers(text)
        
        if not headers:
            if self.debug:
                print("No section headers found in the document")
            return sections
        
        # Extract content for each found section
        for i, (section_num, header_text, start_pos) in enumerate(headers):
            # Determine end position (start of next section or end of document)
            if i < len(headers) - 1:
                end_pos = headers[i + 1][2]
            else:
                end_pos = len(text)
            
            # Extract section content
            section_text = text[start_pos:end_pos].strip()
            
            # Remove the header from the content
            lines = section_text.split('\n')
            if lines:
                # Remove the first line (which contains the header)
                content = '\n'.join(lines[1:]).strip()
            else:
                content = ""
            
            # Update the section
            sections[section_num].content = content
            sections[section_num].found = True
            
            if self.debug:
                print(f"Extracted section {section_num}: {len(content)} characters")
        
        return sections
    
    def parse_file(self, pdf_path: str) -> Dict[str, Union[bool, Dict, List]]:
        """
        Parse a single SDS PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing parsing results
        """
        result = {
            'file_path': pdf_path,
            'success': False,
            'error': None,
            'sections_found': 0,
            'missing_sections': [],
            'sections': {}
        }
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            result['error'] = f"File not found: {pdf_path}"
            return result
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        
        if text is None:
            result['error'] = "No text found — possibly a scanned PDF or extraction failed"
            return result
        
        if not text.strip():
            result['error'] = "PDF contains no extractable text"
            return result
        
        # Extract sections
        sections = self.extract_sections(text)
        
        # Count found sections and identify missing ones
        found_sections = [num for num, section in sections.items() if section.found]
        missing_sections = [num for num, section in sections.items() if not section.found]
        
        result['sections_found'] = len(found_sections)
        result['missing_sections'] = missing_sections
        result['sections'] = {
            num: {
                'title': section.title,
                'content': section.content,
                'found': section.found
            }
            for num, section in sections.items()
        }
        
        if len(found_sections) == 16:
            result['success'] = True
        else:
            result['error'] = f"Missing sections: {missing_sections}"
        
        return result
    
    def parse_batch(self, folder_path: str) -> List[Dict]:
        """
        Parse all PDF files in a folder
        
        Args:
            folder_path: Path to folder containing PDF files
            
        Returns:
            List of parsing results for each file
        """
        results = []
        
        if not os.path.exists(folder_path):
            return [{'error': f"Folder not found: {folder_path}"}]
        
        # Find all PDF files
        pdf_files = []
        for ext in ['*.pdf', '*.PDF']:
            pdf_files.extend(Path(folder_path).glob(ext))
        
        if not pdf_files:
            return [{'error': f"No PDF files found in: {folder_path}"}]
        
        print(f"Found {len(pdf_files)} PDF files to process...")
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            result = self.parse_file(str(pdf_file))
            results.append(result)
        
        return results


def print_results(results: Union[Dict, List[Dict]], verbose: bool = False):
    """
    Print parsing results in a readable format
    
    Args:
        results: Single result dict or list of result dicts
        verbose: Include section content in output
    """
    if isinstance(results, dict):
        results = [results]
    
    for result in results:
        print("\n" + "="*80)
        print(f"File: {result.get('file_path', 'Unknown')}")
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            continue
        
        sections_found = result.get('sections_found', 0)
        missing_sections = result.get('missing_sections', [])
        
        if result.get('success'):
            print(f"✅ Success: All 16 sections found")
        else:
            print(f"⚠️  Warning: {sections_found}/16 sections found")
            if missing_sections:
                print(f"Missing sections: {missing_sections}")
        
        if verbose and 'sections' in result:
            print("\nSections:")
            for num in range(1, 17):
                section = result['sections'].get(num, {})
                status = "✅" if section.get('found') else "❌"
                title = section.get('title', 'Unknown')
                content_length = len(section.get('content', ''))
                
                print(f"  {status} Section {num}: {title}")
                if verbose and section.get('found') and content_length > 0:
                    content = section.get('content', '')[:200]
                    if len(section.get('content', '')) > 200:
                        content += "..."
                    print(f"      Content ({content_length} chars): {content}")


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="Parse German Safety Data Sheets (SDS/SDB) from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a single file
  python sds_parser.py --single path/to/sds.pdf
  
  # Parse all PDFs in a folder
  python sds_parser.py --batch path/to/sds/folder
  
  # Parse with verbose output and custom fuzzy threshold
  python sds_parser.py --single sds.pdf --verbose --fuzzy-threshold 75
  
  # Export results to JSON
  python sds_parser.py --batch folder --output results.json
        """
    )
    
    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--single', 
        type=str, 
        help='Parse a single PDF file'
    )
    mode_group.add_argument(
        '--batch', 
        type=str, 
        help='Parse all PDF files in a folder'
    )
    
    # Optional arguments
    parser.add_argument(
        '--fuzzy-threshold', 
        type=int, 
        default=60,
        help='Fuzzy matching threshold for section headers (0-100, default: 60)'
    )
    parser.add_argument(
        '--verbose', '-v', 
        action='store_true',
        help='Show verbose output including section content previews'
    )
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug output'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output results to JSON file'
    )
    
    args = parser.parse_args()
    
    # Validate fuzzy threshold
    if not 0 <= args.fuzzy_threshold <= 100:
        print("Error: Fuzzy threshold must be between 0 and 100")
        sys.exit(1)
    
    # Create parser instance
    sds_parser = SDSParser(
        fuzzy_threshold=args.fuzzy_threshold,
        debug=args.debug
    )
    
    # Process files
    if args.single:
        print(f"Parsing single file: {args.single}")
        results = sds_parser.parse_file(args.single)
    else:  # batch mode
        print(f"Parsing batch folder: {args.batch}")
        results = sds_parser.parse_batch(args.batch)
    
    # Output results
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to: {args.output}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    # Print results to console
    print_results(results, verbose=args.verbose)
    
    # Summary for batch mode
    if isinstance(results, list) and len(results) > 1:
        successful = sum(1 for r in results if r.get('success'))
        total = len(results)
        print(f"\n📊 Summary: {successful}/{total} files successfully parsed")


if __name__ == "__main__":
    main()
