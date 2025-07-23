#!/usr/bin/env python3
"""
Chemical Identifier Extractor for Safety Data Sheets
Extracts CAS numbers, EC numbers, and REACH registration numbers from SDS documents
Focuses on Section 3 (Composition/Information on Ingredients) with proper identifier separation
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, NamedTuple, Set
from dataclasses import dataclass
from pathlib import Path

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    print("Warning: PyMuPDF not available. Text extraction will be limited.")


class ChemicalIdentifier(NamedTuple):
    """Represents a found chemical identifier with context"""
    identifier_type: str  # 'CAS', 'EC', 'REACH'
    number: str
    context_phrase: str
    substance_name: Optional[str]
    concentration: Optional[str]
    confidence: float
    line_number: Optional[int] = None
    section: Optional[str] = None


@dataclass
class ChemicalExtractionResult:
    """Container for chemical identifier extraction results"""
    filename: str
    cas_numbers: List[ChemicalIdentifier]
    ec_numbers: List[ChemicalIdentifier]
    reach_numbers: List[ChemicalIdentifier]
    all_identifiers: List[ChemicalIdentifier]
    unique_cas_count: int
    unique_ec_count: int
    unique_reach_count: int
    section_3_found: bool
    extraction_confidence: float
    extraction_notes: List[str]
    detected_substances: List[str]


class ChemicalExtractor:
    """
    Extracts chemical identifiers (CAS, EC, REACH) from Safety Data Sheets.
    
    Features:
    - Focuses on Section 3 (Composition/Information on Ingredients)
    - Separates CAS, EC, and REACH numbers properly
    - Recognizes context indicators and proper layouts
    - Validates identifier formats
    - Attempts to identify substance names and concentrations
    """
    
    def __init__(self):
        # Chemical identifier patterns - using official formats
        self.identifier_patterns = {
            'CAS': [
                r'\b(\d{1,7}-\d{2}-\d)\b',          # Official CAS format: NNNNN-NN-N
                r'\b(\d{1,7}\s*-\s*\d{2}\s*-\s*\d)\b',  # With optional spaces
            ],
            'EC': [
                r'\b(?:EC|EG)?\s*(\d{3}-\d{3}-\d)\b',    # Official EC/EG format: NNN-NNN-R
                r'\b(?:EC|EG)?\s*(\d{3}\s*-\s*\d{3}\s*-\s*\d)\b',  # With optional spaces
            ],
            'REACH': [
                r'\b(\d{2}-\d{8,10}-\d{2}-\d{4})\b',    # Official REACH format: NN-NNNNNNNNNN-NN-NNNN
                r'\b(\d{2}\s*-\s*\d{8,10}\s*-\s*\d{2}\s*-\s*\d{4})\b',  # With optional spaces
            ]
        }
        
        # Context indicators for each identifier type
        self.context_indicators = {
            'CAS': {
                'cas-nr': 1.0,
                'cas-nummer': 1.0,
                'cas number': 1.0,
                'cas no': 0.95,
                'cas#': 0.9,
                'cas :': 0.95,
                'cas:': 1.0,
                'registry number': 0.8,
                'chemical abstracts service': 0.85,
            },
            'EC': {
                'ec-nr': 1.0,
                'ec-nummer': 1.0,
                'ec number': 1.0,
                'ec no': 0.95,
                'ec#': 0.9,
                'ec :': 0.95,
                'ec:': 1.0,
                'einecs': 0.9,
                'elincs': 0.9,
            },
            'REACH': {
                'reach-nr': 1.0,
                'reach number': 1.0,
                'reach no': 0.95,
                'reach :': 0.95,
                'reach:': 1.0,
                'registrierungsnummer': 0.9,
                'registration number': 0.9,
                'reg. nr': 0.8,
                'reg nr': 0.8,
            }
        }
        
        # General indicators (apply to all types with lower confidence)
        self.general_indicators = {
            'zusammensetzung': 0.6,
            'composition': 0.6,
            'information on ingredients': 0.6,
            'angaben zu den bestandteilen': 0.6,
            'ingredients': 0.5,
            'bestandteile': 0.5,
            'components': 0.5,
            'substances': 0.4,
            'stoffe': 0.4,
        }
        
        # Section 3 patterns (German and English)
        self.section_3_patterns = [
            r'\b3\.\s*zusammensetzung.*?bestandteile',
            r'\b3\.\s*composition.*?ingredients',
            r'\b3\.\s*angaben.*?bestandteile',
            r'\b3\.\s*information.*?ingredients',
            r'\bsektion\s*3',
            r'\bsection\s*3',
            r'\babschnitt\s*3',
        ]
        
        # Concentration patterns
        self.concentration_patterns = [
            r'(\d+(?:[.,]\d+)?)\s*%',
            r'(\d+(?:[.,]\d+)?)\s*prozent',
            r'(\d+(?:[.,]\d+)?)\s*gewichtsprozent',
            r'(\d+(?:[.,]\d+)?)\s*vol[.-]?%',
            r'(\d+(?:[.,]\d+)?)\s*gew[.-]?%',
            r'(\d+(?:[.,]\d+)?)\s*w/w',
            r'(\d+(?:[.,]\d+)?)\s*v/v',
            r'(\d+(?:[.,]\d+)?)\s*weight\s*%',
            r'(\d+(?:[.,]\d+)?)\s*volume\s*%',
            r'<\s*(\d+(?:[.,]\d+)?)\s*%',
            r'>\s*(\d+(?:[.,]\d+)?)\s*%',
            r'(\d+(?:[.,]\d+)?)\s*-\s*(\d+(?:[.,]\d+)?)\s*%',
        ]

    def extract_text_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract text from PDF and return as list of lines"""
        text_lines = []
        
        if FITZ_AVAILABLE:
            try:
                doc = fitz.open(pdf_path)
                for page in doc:
                    page_text = page.get_text()
                    text_lines.extend(page_text.split('\n'))
                doc.close()
            except Exception as e:
                print(f"Error extracting text with PyMuPDF: {e}")
                return []
        else:
            # Fallback to PyPDF2
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        text_lines.extend(page_text.split('\n'))
            except Exception as e:
                print(f"Error extracting text with PyPDF2: {e}")
                return []
        
        return [line.strip() for line in text_lines if line.strip()]

    def validate_identifier(self, identifier_type: str, number: str) -> bool:
        """Validate identifier format and check digit where applicable"""
        clean_number = re.sub(r'[^\d-]', '', number)
        
        if identifier_type == 'CAS':
            return self._validate_cas_number(clean_number)
        elif identifier_type == 'EC':
            return self._validate_ec_number(clean_number)
        elif identifier_type == 'REACH':
            return self._validate_reach_number(clean_number)
        
        return False

    def _validate_cas_number(self, cas_number: str) -> bool:
        """Validate CAS number using check digit algorithm"""
        if not re.match(r'^\d{1,7}-\d{2}-\d$', cas_number):
            return False
        
        parts = cas_number.split('-')
        if len(parts) != 3:
            return False
        
        # Calculate check digit using CAS algorithm
        digits_str = parts[0] + parts[1]
        check_digit = int(parts[2])
        
        total = 0
        for i, digit in enumerate(reversed(digits_str)):
            total += int(digit) * (i + 1)
        
        calculated_check = total % 10
        return calculated_check == check_digit

    def _validate_ec_number(self, ec_number: str) -> bool:
        """Validate EC number format (NNN-NNN-R)"""
        return bool(re.match(r'^\d{3}-\d{3}-\d$', ec_number))

    def _validate_reach_number(self, reach_number: str) -> bool:
        """Validate REACH registration number format (NN-NNNNNNNNNN-NN-NNNN)"""
        return bool(re.match(r'^\d{2}-\d{8,10}-\d{2}-\d{4}$', reach_number))

    def find_section_3_boundaries(self, text_lines: List[str]) -> Tuple[Optional[int], Optional[int]]:
        """Find the start and end lines of Section 3"""
        start_line = None
        end_line = None
        
        for i, line in enumerate(text_lines):
            line_lower = line.lower().strip()
            
            if start_line is None:
                for pattern in self.section_3_patterns:
                    if re.search(pattern, line_lower):
                        start_line = i
                        break
            elif start_line is not None and end_line is None:
                if re.search(r'\b4\.\s*erste.*?hilfe', line_lower) or \
                   re.search(r'\b4\.\s*first.*?aid', line_lower):
                    end_line = i
                    break
        
        if start_line is not None and end_line is None:
            end_line = len(text_lines)
        
        return start_line, end_line

    def parse_identifier_block(self, lines: List[str], start_idx: int) -> List[ChemicalIdentifier]:
        """
        Parse a block of lines that contains chemical identifiers.
        This handles proper layouts like:
        CAS:   69011-36-5   
        EC:    500-241-6   
        REACH: 01-21199763-62-32
        """
        found_identifiers = []
        
        # Look at current line and next few lines for identifier patterns
        for line_offset in range(min(5, len(lines) - start_idx)):
            line = lines[start_idx + line_offset]
            line_lower = line.lower().strip()
            
            if not line_lower:
                continue
            
            # Check for each identifier type
            for identifier_type in ['CAS', 'EC', 'REACH']:
                # Look for context indicators first
                context_confidence = 0.0
                context_phrase = None
                
                for indicator, confidence in self.context_indicators[identifier_type].items():
                    if indicator in line_lower:
                        if confidence > context_confidence:
                            context_confidence = confidence
                            context_phrase = indicator
                
                # If we found a context indicator, look for numbers in this line
                if context_phrase:
                    for pattern in self.identifier_patterns[identifier_type]:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            # For EC numbers, extract the actual number (group 1 if EC prefix, else full match)
                            if identifier_type == 'EC' and match.groups():
                                number = match.group(1) if match.group(1) else match.group(0)
                            else:
                                number = match.group(1) if match.groups() else match.group(0)
                            
                            # Clean up any remaining spaces
                            number = re.sub(r'\s+', '', number)
                            
                            if self.validate_identifier(identifier_type, number):
                                # Try to extract substance name and concentration from nearby context
                                substance_name = self._extract_substance_name_from_block(lines, start_idx, line_offset)
                                concentration = self._extract_concentration_from_block(lines, start_idx, line_offset)
                                
                                found_identifiers.append(ChemicalIdentifier(
                                    identifier_type=identifier_type,
                                    number=number,
                                    context_phrase=context_phrase,
                                    substance_name=substance_name,
                                    concentration=concentration,
                                    confidence=context_confidence,
                                    line_number=start_idx + line_offset,
                                    section="Section 3"
                                ))
        
        return found_identifiers

    def find_identifiers_in_text(self, text_lines: List[str], focus_section_3: bool = True) -> List[ChemicalIdentifier]:
        """Find all chemical identifiers with proper context separation"""
        found_identifiers = []
        
        # First, try to find Section 3 boundaries
        section_3_start, section_3_end = self.find_section_3_boundaries(text_lines)
        
        if focus_section_3 and section_3_start is not None:
            search_lines = text_lines[section_3_start:section_3_end]
            line_offset = section_3_start
            search_section = "Section 3"
        else:
            search_lines = text_lines
            line_offset = 0
            search_section = "Full Document"
        
        i = 0
        while i < len(search_lines):
            line = search_lines[i]
            line_lower = line.lower().strip()
            
            if not line_lower:
                i += 1
                continue
            
            # Check if this line contains any identifier context
            has_identifier_context = False
            for identifier_type in ['CAS', 'EC', 'REACH']:
                for indicator in self.context_indicators[identifier_type]:
                    if indicator in line_lower:
                        has_identifier_context = True
                        break
                if has_identifier_context:
                    break
            
            if has_identifier_context:
                # Parse this block of lines for identifiers
                block_identifiers = self.parse_identifier_block(search_lines, i)
                for identifier in block_identifiers:
                    # Adjust line number for global context
                    identifier = identifier._replace(line_number=identifier.line_number + line_offset)
                    found_identifiers.append(identifier)
                
                # Skip ahead a few lines to avoid re-processing the same block
                i += 3
            else:
                # Look for standalone numbers with general context
                for identifier_type in ['CAS', 'EC', 'REACH']:
                    for pattern in self.identifier_patterns[identifier_type]:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            # Handle number extraction consistently
                            if identifier_type == 'EC' and match.groups():
                                number = match.group(1) if match.group(1) else match.group(0)
                            else:
                                number = match.group(1) if match.groups() else match.group(0)
                            
                            # Clean up any remaining spaces
                            number = re.sub(r'\s+', '', number)
                            
                            if self.validate_identifier(identifier_type, number):
                                # Lower confidence for standalone numbers
                                confidence = 0.5 if search_section == "Section 3" else 0.3
                                
                                substance_name = self._extract_substance_name_from_line(line)
                                concentration = self._extract_concentration_from_line(line)
                                
                                found_identifiers.append(ChemicalIdentifier(
                                    identifier_type=identifier_type,
                                    number=number,
                                    context_phrase="standalone_pattern",
                                    substance_name=substance_name,
                                    concentration=concentration,
                                    confidence=confidence,
                                    line_number=i + line_offset,
                                    section=search_section
                                ))
                i += 1
        
        return found_identifiers

    def _extract_substance_name_from_block(self, lines: List[str], start_idx: int, current_offset: int) -> Optional[str]:
        """Extract substance name from a block of lines around the identifier"""
        # Look in surrounding lines for substance names
        search_range = range(max(0, start_idx + current_offset - 2), 
                           min(len(lines), start_idx + current_offset + 3))
        
        for idx in search_range:
            line = lines[idx]
            # Look for patterns that suggest substance names
            # Remove common non-substance words
            clean_line = re.sub(r'\b(cas|ec|reach|nr|number|nummer|:\s*\d+|\d+-\d+-\d)\b', '', line, flags=re.IGNORECASE)
            clean_line = clean_line.strip(' :-')
            
            if len(clean_line) > 3 and not re.match(r'^\d+', clean_line):
                # Simple heuristic for chemical names
                if re.search(r'[a-zA-Z]{3,}', clean_line):
                    return clean_line[:50]  # Limit length
        
        return None

    def _extract_concentration_from_block(self, lines: List[str], start_idx: int, current_offset: int) -> Optional[str]:
        """Extract concentration from a block of lines around the identifier"""
        search_range = range(max(0, start_idx + current_offset - 1), 
                           min(len(lines), start_idx + current_offset + 2))
        
        for idx in search_range:
            line = lines[idx]
            for pattern in self.concentration_patterns:
                matches = re.findall(pattern, line)
                if matches:
                    if isinstance(matches[0], tuple):
                        return f"{matches[0][0]}-{matches[0][1]}%"
                    else:
                        return f"{matches[0]}%"
        
        return None

    def _extract_substance_name_from_line(self, line: str) -> Optional[str]:
        """Extract substance name from a single line"""
        # Remove identifiers and common words
        clean_line = re.sub(r'\b(\d+-\d+-\d|\d+-\d+-\d+|cas|ec|reach|nr|number|nummer)\b', '', line, flags=re.IGNORECASE)
        clean_line = clean_line.strip(' :-')
        
        if len(clean_line) > 3 and re.search(r'[a-zA-Z]{3,}', clean_line):
            return clean_line[:50]
        
        return None

    def _extract_concentration_from_line(self, line: str) -> Optional[str]:
        """Extract concentration from a single line"""
        for pattern in self.concentration_patterns:
            matches = re.findall(pattern, line)
            if matches:
                if isinstance(matches[0], tuple):
                    return f"{matches[0][0]}-{matches[0][1]}%"
                else:
                    return f"{matches[0]}%"
        return None

    def extract_chemical_identifiers(self, pdf_path: str) -> ChemicalExtractionResult:
        """
        Main method to extract chemical identifiers from SDS PDF
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            ChemicalExtractionResult with all findings
        """
        filename = os.path.basename(pdf_path)
        
        # Initialize result with defaults
        result = ChemicalExtractionResult(
            filename=filename,
            cas_numbers=[],
            ec_numbers=[],
            reach_numbers=[],
            all_identifiers=[],
            unique_cas_count=0,
            unique_ec_count=0,
            unique_reach_count=0,
            section_3_found=False,
            extraction_confidence=0.0,
            extraction_notes=[],
            detected_substances=[]
        )
        
        if not os.path.exists(pdf_path):
            result.extraction_notes.append("File not found")
            return result
        
        # Extract text
        text_lines = self.extract_text_from_pdf(pdf_path)
        if not text_lines:
            result.extraction_notes.append("Could not extract text from PDF")
            return result
        
        # Check if Section 3 exists
        section_3_start, section_3_end = self.find_section_3_boundaries(text_lines)
        result.section_3_found = section_3_start is not None
        
        if result.section_3_found:
            result.extraction_notes.append(f"Found Section 3 at lines {section_3_start}-{section_3_end}")
        else:
            result.extraction_notes.append("Section 3 not clearly identified, searching entire document")
        
        # Find all identifiers
        all_identifiers = self.find_identifiers_in_text(text_lines, focus_section_3=True)
        result.all_identifiers = all_identifiers
        
        # Separate by type
        result.cas_numbers = [i for i in all_identifiers if i.identifier_type == 'CAS']
        result.ec_numbers = [i for i in all_identifiers if i.identifier_type == 'EC']
        result.reach_numbers = [i for i in all_identifiers if i.identifier_type == 'REACH']
        
        # Calculate unique counts
        result.unique_cas_count = len(set(i.number for i in result.cas_numbers))
        result.unique_ec_count = len(set(i.number for i in result.ec_numbers))
        result.unique_reach_count = len(set(i.number for i in result.reach_numbers))
        
        # Extract substance names
        substance_names = [i.substance_name for i in all_identifiers if i.substance_name]
        result.detected_substances = list(set(substance_names))
        
        # Calculate overall confidence
        if all_identifiers:
            avg_confidence = sum(i.confidence for i in all_identifiers) / len(all_identifiers)
            result.extraction_confidence = avg_confidence
            result.extraction_notes.append(
                f"Found {len(result.cas_numbers)} CAS, {len(result.ec_numbers)} EC, "
                f"{len(result.reach_numbers)} REACH numbers"
            )
        else:
            result.extraction_confidence = 0.0
            result.extraction_notes.append("No chemical identifiers found")
        
        return result

    def batch_extract_identifiers(self, pdf_directory: str) -> Dict[str, ChemicalExtractionResult]:
        """Extract chemical identifiers for all PDFs in a directory"""
        results = {}
        
        if not os.path.exists(pdf_directory):
            return results
        
        for filename in os.listdir(pdf_directory):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, filename)
                results[filename] = self.extract_chemical_identifiers(pdf_path)
        
        return results


# Backward compatibility - keep old class name as alias
CASExtractor = ChemicalExtractor
CASExtractionResult = ChemicalExtractionResult
CASMatch = ChemicalIdentifier


def main():
    """Command line interface for chemical identifier extraction"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract chemical identifiers (CAS, EC, REACH) from Safety Data Sheet PDFs')
    parser.add_argument('input', help='PDF file or directory to analyze')
    parser.add_argument('--output', '-o', help='Output directory for reports')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--section3-only', action='store_true', help='Focus only on Section 3')
    
    args = parser.parse_args()
    
    extractor = ChemicalExtractor()
    
    if os.path.isfile(args.input):
        # Single file
        result = extractor.extract_chemical_identifiers(args.input)
        
        print(f"\n🧪 Chemical Identifier Extraction Results for: {args.input}")
        print("=" * 60)
        print(f"Filename: {result.filename}")
        print(f"Section 3 Found: {'✅' if result.section_3_found else '❌'}")
        print(f"Extraction Confidence: {result.extraction_confidence:.2f}")
        
        print(f"\n📊 Summary:")
        print(f"  🧪 CAS Numbers: {len(result.cas_numbers)} ({result.unique_cas_count} unique)")
        print(f"  🏷️  EC Numbers: {len(result.ec_numbers)} ({result.unique_ec_count} unique)")
        print(f"  📋 REACH Numbers: {len(result.reach_numbers)} ({result.unique_reach_count} unique)")
        
        if result.cas_numbers:
            print(f"\n🧪 CAS Numbers:")
            for i, identifier in enumerate(result.cas_numbers, 1):
                substance_info = f" ({identifier.substance_name})" if identifier.substance_name else ""
                concentration_info = f" - {identifier.concentration}" if identifier.concentration else ""
                print(f"  {i}. {identifier.number}{substance_info}{concentration_info}")
                if args.verbose:
                    print(f"      Context: {identifier.context_phrase} (confidence: {identifier.confidence:.2f})")
        
        if result.ec_numbers:
            print(f"\n🏷️ EC Numbers:")
            for i, identifier in enumerate(result.ec_numbers, 1):
                substance_info = f" ({identifier.substance_name})" if identifier.substance_name else ""
                concentration_info = f" - {identifier.concentration}" if identifier.concentration else ""
                print(f"  {i}. {identifier.number}{substance_info}{concentration_info}")
                if args.verbose:
                    print(f"      Context: {identifier.context_phrase} (confidence: {identifier.confidence:.2f})")
        
        if result.reach_numbers:
            print(f"\n📋 REACH Numbers:")
            for i, identifier in enumerate(result.reach_numbers, 1):
                substance_info = f" ({identifier.substance_name})" if identifier.substance_name else ""
                print(f"  {i}. {identifier.number}{substance_info}")
                if args.verbose:
                    print(f"      Context: {identifier.context_phrase} (confidence: {identifier.confidence:.2f})")
        
        if result.detected_substances:
            print(f"\n🔬 Detected Substances:")
            for substance in result.detected_substances:
                print(f"  • {substance}")
        
        if args.verbose and result.extraction_notes:
            print(f"\n📝 Extraction Notes:")
            for note in result.extraction_notes:
                print(f"  • {note}")
    
    else:
        # Directory - batch processing
        results = extractor.batch_extract_identifiers(args.input)
        
        print(f"\n🧪 Batch Chemical Identifier Extraction Results")
        print("=" * 60)
        print(f"Directory: {args.input}")
        print(f"Files processed: {len(results)}")
        
        total_cas = sum(len(result.cas_numbers) for result in results.values())
        total_ec = sum(len(result.ec_numbers) for result in results.values())
        total_reach = sum(len(result.reach_numbers) for result in results.values())
        unique_cas = len(set(i.number for result in results.values() for i in result.cas_numbers))
        unique_ec = len(set(i.number for result in results.values() for i in result.ec_numbers))
        unique_reach = len(set(i.number for result in results.values() for i in result.reach_numbers))
        
        print(f"🧪 CAS Numbers: {total_cas} ({unique_cas} unique)")
        print(f"🏷️ EC Numbers: {total_ec} ({unique_ec} unique)")
        print(f"📋 REACH Numbers: {total_reach} ({unique_reach} unique)")


if __name__ == "__main__":
    main() 