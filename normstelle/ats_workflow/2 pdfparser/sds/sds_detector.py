#!/usr/bin/env python3
"""
SDS (Safety Data Sheet) Detector
Scores PDF documents on likelihood of being a Safety Data Sheet (0-100)
Primarily German with English support
"""

import os
import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    print("Warning: PyMuPDF not available. Text extraction will be limited.")


@dataclass
class SDSScore:
    """Container for SDS detection results"""
    total_score: int
    is_likely_sds: bool
    confidence_level: str
    breakdown: Dict[str, int]
    detected_features: List[str]
    language_detected: str
    

class SDSDetector:
    """
    Detects Safety Data Sheets and provides confidence scoring.
    
    Scoring System (0-100):
    - 90-100: Almost certainly an SDS
    - 70-89:  Very likely an SDS
    - 50-69:  Possibly an SDS
    - 30-49:  Unlikely to be an SDS
    - 0-29:   Definitely not an SDS
    """
    
    def __init__(self):
        # German SDS keywords and patterns
        self.german_keywords = {
            # Document type indicators (25 points max)
            'document_type': {
                'sicherheitsdatenblatt': 15,
                'safety data sheet': 12,
                'sds': 10,
                'msds': 8,
                'material safety data sheet': 12,
                '1907/2006 eg': 10,
                'reach': 8,
                'clp': 5,
            },
            
            # Section headers (30 points max)
            'section_headers': {
                'bezeichnung des stoffs': 5,
                'mögliche gefahren': 5,
                'zusammensetzung': 5,
                'erste hilfe': 5,
                'brandbekämpfung': 5,
                'unbeabsichtigter freisetzung': 4,
                'handhabung und lagerung': 5,
                'expositionsbegrenzung': 4,
                'physikalische eigenschaften': 4,
                'stabilität und reaktivität': 4,
                'toxikologie': 5,
                'umweltbezogene angaben': 4,
                'entsorgung': 4,
                'transportangaben': 4,
                'vorschriften': 4,
                'weitere angaben': 3,
                # English equivalents
                'identification': 4,
                'hazards identification': 5,
                'composition': 5,
                'first aid measures': 5,
                'firefighting measures': 4,
                'accidental release': 4,
                'handling and storage': 4,
                'exposure controls': 4,
                'physical and chemical properties': 4,
                'stability and reactivity': 4,
                'toxicological information': 5,
                'ecological information': 4,
                'disposal considerations': 4,
                'transport information': 4,
                'regulatory information': 4,
            },
            
            # Chemical/Safety indicators (20 points max)
            'chemical_safety': {
                'cas-nr': 3,
                'cas number': 3,
                'eg-nr': 2,
                'ec number': 2,
                'ghs': 5,
                'pictogramm': 3,
                'pictogram': 3,
                'signalwort': 3,
                'signal word': 3,
                'gefahrenhinweis': 3,
                'hazard statement': 3,
                'sicherheitshinweis': 3,
                'precautionary statement': 3,
                'achtung': 2,
                'gefahr': 2,
                'warning': 2,
                'danger': 2,
            },
            
            # Product/Company info (15 points max)
            'product_info': {
                'produktname': 3,
                'product name': 3,
                'handelsname': 2,
                'trade name': 2,
                'hersteller': 2,
                'manufacturer': 2,
                'lieferant': 2,
                'supplier': 2,
                'notfall-telefon': 3,
                'emergency telephone': 3,
                'notfallnummer': 3,
                'emergency number': 3,
            },
            
            # Regulatory codes (10 points max)
            'regulatory_codes': {
                'h[0-9]{3}': 2,  # H-codes (H319, H315, etc.)
                'p[0-9]{3}': 2,  # P-codes (P101, P264, etc.)
                'euh[0-9]{3}': 2,  # EUH-codes
                'r[0-9]{2}': 1,   # Old R-phrases
                's[0-9]{2}': 1,   # Old S-phrases
            }
        }
        
        # Numbered section patterns
        self.section_patterns = [
            r'\b1\.\s*bezeichnung',  # German
            r'\b2\.\s*(?:mögliche\s*)?gefahren',
            r'\b3\.\s*zusammensetzung',
            r'\b4\.\s*erste\s*hilfe',
            r'\b5\.\s*(?:maßnahmen\s*bei\s*)?brand',
            r'\b6\.\s*(?:maßnahmen\s*bei\s*)?unbeabsichtigter',
            r'\b7\.\s*(?:lagerung\s*und\s*)?handhabung',
            r'\b8\.\s*exposition',
            r'\b9\.\s*physikalische',
            r'\b10\.\s*stabilität',
            r'\b11\.\s*(?:angaben\s*zur\s*)?toxikologie',
            r'\b12\.\s*umwelt',
            r'\b13\.\s*(?:hinweise\s*zur\s*)?entsorgung',
            r'\b14\.\s*(?:angaben\s*zum\s*)?transport',
            r'\b15\.\s*vorschriften',
            r'\b16\.\s*weitere\s*angaben',
            # English
            r'\b1\.\s*identification',
            r'\b2\.\s*hazards?\s*identification',
            r'\b3\.\s*composition',
            r'\b4\.\s*first\s*aid',
            r'\b5\.\s*fire\s*fighting',
            r'\b6\.\s*accidental\s*release',
            r'\b7\.\s*handling\s*and\s*storage',
            r'\b8\.\s*exposure\s*controls',
            r'\b9\.\s*physical\s*and\s*chemical',
            r'\b10\.\s*stability',
            r'\b11\.\s*toxicological',
            r'\b12\.\s*ecological',
            r'\b13\.\s*disposal',
            r'\b14\.\s*transport',
            r'\b15\.\s*regulatory',
            r'\b16\.\s*other',
        ]

    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Extract text from PDF using available libraries"""
        if not os.path.exists(pdf_path):
            return None
            
        text = ""
        
        if FITZ_AVAILABLE:
            try:
                doc = fitz.open(pdf_path)
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            except Exception as e:
                print(f"PyMuPDF extraction failed: {e}")
                
        # Fallback to other methods if needed
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")
            
        return None

    def detect_language(self, text: str) -> str:
        """Detect primary language of the document"""
        text_lower = text.lower()
        
        german_indicators = [
            'sicherheitsdatenblatt', 'bezeichnung', 'gefahren', 'zusammensetzung',
            'erste hilfe', 'handhabung', 'lagerung', 'entsorgung', 'und', 'der', 'die', 'das'
        ]
        
        english_indicators = [
            'safety data sheet', 'identification', 'hazards', 'composition',
            'first aid', 'handling', 'storage', 'disposal', 'and', 'the', 'of', 'for'
        ]
        
        german_count = sum(1 for word in german_indicators if word in text_lower)
        english_count = sum(1 for word in english_indicators if word in text_lower)
        
        if german_count > english_count:
            return 'German'
        elif english_count > german_count:
            return 'English'
        else:
            return 'Mixed/Unknown'

    def score_keywords(self, text: str) -> Tuple[int, List[str]]:
        """Score based on keyword presence"""
        text_lower = text.lower()
        total_score = 0
        found_features = []
        category_scores = {}
        
        for category, keywords in self.german_keywords.items():
            category_score = 0
            category_max = 25 if category == 'document_type' else \
                          30 if category == 'section_headers' else \
                          20 if category == 'chemical_safety' else \
                          15 if category == 'product_info' else 10
            
            for keyword, points in keywords.items():
                if category == 'regulatory_codes':
                    # Use regex for code patterns
                    if re.search(keyword, text_lower):
                        category_score += points
                        found_features.append(f"Regulatory pattern: {keyword}")
                else:
                    # Simple text search for other keywords
                    if keyword in text_lower:
                        category_score += points
                        found_features.append(f"Keyword: {keyword}")
            
            # Cap category score at maximum
            category_score = min(category_score, category_max)
            category_scores[category] = category_score
            total_score += category_score
            
        return total_score, found_features

    def score_structure(self, text: str) -> Tuple[int, List[str]]:
        """Score based on document structure (numbered sections)"""
        text_lower = text.lower()
        found_sections = []
        structural_features = []
        
        # Look for numbered sections
        for pattern in self.section_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                found_sections.extend(matches)
                structural_features.append(f"Section pattern: {pattern}")
        
        # Score based on number of sections found
        section_count = len(set(found_sections))  # Remove duplicates
        
        if section_count >= 12:  # Most sections found
            structure_score = 30
            structural_features.append(f"Complete structure: {section_count}/16 sections")
        elif section_count >= 8:  # Many sections
            structure_score = 25
            structural_features.append(f"Good structure: {section_count}/16 sections")
        elif section_count >= 5:  # Some sections
            structure_score = 15
            structural_features.append(f"Partial structure: {section_count}/16 sections")
        elif section_count >= 3:  # Few sections
            structure_score = 8
            structural_features.append(f"Minimal structure: {section_count}/16 sections")
        else:  # Very few or no sections
            structure_score = 0
            
        return structure_score, structural_features

    def score_format_indicators(self, text: str) -> Tuple[int, List[str]]:
        """Score based on format indicators specific to SDS"""
        text_lower = text.lower()
        format_score = 0
        format_features = []
        
        # Page numbering patterns
        page_patterns = [
            r'seite\s+\d+\s+von\s+\d+',  # German: "Seite X von Y"
            r'page\s+\d+\s+of\s+\d+',    # English: "Page X of Y"
        ]
        
        for pattern in page_patterns:
            if re.search(pattern, text_lower):
                format_score += 5
                format_features.append(f"Page numbering: {pattern}")
                break
        
        # Date patterns
        date_patterns = [
            r'ausfertigungsdatum',  # German issue date
            r'überarbeitet\s*am',   # German revision date
            r'version\s*:?\s*\d+',  # Version number
            r'revision\s*:?\s*\d+', # Revision number
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, text_lower):
                format_score += 3
                format_features.append(f"Date indicator: {pattern}")
        
        # Contact information patterns
        contact_patterns = [
            r'tel\.?\s*:?\s*[\+\d\s\-\(\)]+',     # Phone numbers
            r'fax\.?\s*:?\s*[\+\d\s\-\(\)]+',     # Fax numbers
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+',  # Email addresses
        ]
        
        for pattern in contact_patterns:
            if re.search(pattern, text_lower):
                format_score += 2
                format_features.append(f"Contact info: {pattern}")
        
        # Cap format score
        format_score = min(format_score, 15)
        
        return format_score, format_features

    def detect_sds(self, pdf_path: str) -> SDSScore:
        """
        Main detection method - analyzes PDF and returns SDS score
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            SDSScore object with detection results
        """
        if not os.path.exists(pdf_path):
            return SDSScore(
                total_score=0,
                is_likely_sds=False,
                confidence_level="Error",
                breakdown={},
                detected_features=["File not found"],
                language_detected="Unknown"
            )
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return SDSScore(
                total_score=0,
                is_likely_sds=False,
                confidence_level="Error",
                breakdown={},
                detected_features=["Could not extract text"],
                language_detected="Unknown"
            )
        
        # Detect language
        language = self.detect_language(text)
        
        # Score different aspects
        keyword_score, keyword_features = self.score_keywords(text)
        structure_score, structure_features = self.score_structure(text)
        format_score, format_features = self.score_format_indicators(text)
        
        # Calculate total score
        total_score = keyword_score + structure_score + format_score
        
        # Determine confidence level
        if total_score >= 90:
            confidence = "Very High"
            is_likely = True
        elif total_score >= 70:
            confidence = "High"
            is_likely = True
        elif total_score >= 50:
            confidence = "Medium"
            is_likely = True
        elif total_score >= 30:
            confidence = "Low"
            is_likely = False
        else:
            confidence = "Very Low"
            is_likely = False
        
        # Combine all features
        all_features = keyword_features + structure_features + format_features
        
        # Create breakdown
        breakdown = {
            'keywords': keyword_score,
            'structure': structure_score,
            'format': format_score,
            'total': total_score
        }
        
        return SDSScore(
            total_score=total_score,
            is_likely_sds=is_likely,
            confidence_level=confidence,
            breakdown=breakdown,
            detected_features=all_features,
            language_detected=language
        )

    def batch_detect(self, pdf_directory: str) -> Dict[str, SDSScore]:
        """
        Detect SDS for all PDFs in a directory
        
        Args:
            pdf_directory: Directory containing PDF files
            
        Returns:
            Dictionary mapping filenames to SDSScore objects
        """
        results = {}
        
        if not os.path.exists(pdf_directory):
            return results
        
        for filename in os.listdir(pdf_directory):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, filename)
                results[filename] = self.detect_sds(pdf_path)
        
        return results


def main():
    """Command line interface for SDS detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Detect Safety Data Sheets in PDF files')
    parser.add_argument('input', help='PDF file or directory to analyze')
    parser.add_argument('--output', '-o', help='Output JSON file for results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    detector = SDSDetector()
    
    if os.path.isfile(args.input):
        # Single file
        result = detector.detect_sds(args.input)
        
        print(f"\nSDS Detection Results for: {args.input}")
        print("=" * 50)
        print(f"Score: {result.total_score}/100")
        print(f"Likely SDS: {result.is_likely_sds}")
        print(f"Confidence: {result.confidence_level}")
        print(f"Language: {result.language_detected}")
        print(f"\nScore Breakdown:")
        for category, score in result.breakdown.items():
            print(f"  {category.capitalize()}: {score}")
        
        if args.verbose:
            print(f"\nDetected Features:")
            for feature in result.detected_features[:10]:  # Show first 10
                print(f"  - {feature}")
            if len(result.detected_features) > 10:
                print(f"  ... and {len(result.detected_features) - 10} more")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump({
                    'file': args.input,
                    'score': result.total_score,
                    'is_sds': result.is_likely_sds,
                    'confidence': result.confidence_level,
                    'language': result.language_detected,
                    'breakdown': result.breakdown,
                    'features': result.detected_features
                }, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to: {args.output}")
    
    elif os.path.isdir(args.input):
        # Directory
        results = detector.batch_detect(args.input)
        
        print(f"\nBatch SDS Detection Results for: {args.input}")
        print("=" * 60)
        
        sds_files = []
        non_sds_files = []
        
        for filename, result in results.items():
            if result.is_likely_sds:
                sds_files.append((filename, result.total_score))
            else:
                non_sds_files.append((filename, result.total_score))
        
        print(f"\nLikely SDS files ({len(sds_files)}):")
        for filename, score in sorted(sds_files, key=lambda x: x[1], reverse=True):
            print(f"  {filename}: {score}/100")
        
        print(f"\nNon-SDS files ({len(non_sds_files)}):")
        for filename, score in sorted(non_sds_files, key=lambda x: x[1], reverse=True):
            print(f"  {filename}: {score}/100")
        
        if args.output:
            output_data = {}
            for filename, result in results.items():
                output_data[filename] = {
                    'score': result.total_score,
                    'is_sds': result.is_likely_sds,
                    'confidence': result.confidence_level,
                    'language': result.language_detected,
                    'breakdown': result.breakdown
                }
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to: {args.output}")
    
    else:
        print(f"Error: {args.input} is not a valid file or directory")


if __name__ == "__main__":
    main() 