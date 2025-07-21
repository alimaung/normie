#!/usr/bin/env python3
"""
TDS/PDS (Technical/Product Data Sheet) Detector
Detects Technical Data Sheets and Product Data Sheets based on common keywords and patterns
Less standardized than SDS but useful for document classification
"""

import os
import re
import json
from datetime import datetime
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
class TDSScore:
    """Container for TDS/PDS detection results"""
    total_score: int
    is_likely_tds: bool
    document_type: str  # "TDS", "PDS", "Technical Sheet", etc.
    confidence_level: str
    breakdown: Dict[str, int]
    detected_features: List[str]
    language_detected: str


class TDSDetector:
    """
    Detects Technical Data Sheets (TDS) and Product Data Sheets (PDS).
    
    Unlike SDS, these documents are not standardized, so detection relies on:
    - Common terminology and keywords
    - Technical specification patterns
    - Product information indicators
    - Format characteristics
    
    Scoring System (0-100):
    - 80-100: Very likely TDS/PDS
    - 60-79:  Likely TDS/PDS
    - 40-59:  Possibly TDS/PDS
    - 20-39:  Unlikely to be TDS/PDS
    - 0-19:   Definitely not TDS/PDS
    """
    
    def __init__(self):
        # German and English TDS/PDS keywords with confidence weights
        self.keywords = {
            # Primary document type indicators (high confidence)
            'document_type_primary': {
                # German
                'produktdatenblatt': 20,
                'technisches datenblatt': 20,
                'technische daten': 15,
                'technisches merkblatt': 18,
                'produktdetails': 12,
                'datenblatt': 15,
                'produktinformation': 12,
                'technische spezifikation': 15,
                'produktspezifikation': 15,
                'technische eigenschaften': 12,
                'leistungsdaten': 10,
                'kennwerte': 8,
                'produktmerkmale': 10,
                'anwendungshinweise': 8,
                'verarbeitungshinweise': 8,
                'technische beschreibung': 10,
                # English
                'technical data sheet': 20,
                'product data sheet': 20,
                'technical datasheet': 18,
                'product datasheet': 18,
                'technical specification': 15,
                'product specification': 15,
                'technical information': 12,
                'product information': 12,
                'technical properties': 10,
                'product properties': 10,
                'performance data': 10,
                'technical details': 12,
                'product details': 12,
                'application guide': 8,
                'processing guide': 8,
                'technical description': 10,
            },
            
            # Secondary indicators (medium confidence)
            'document_type_secondary': {
                # German
                'eigenschaften': 5,
                'anwendung': 4,
                'verarbeitung': 4,
                'spezifikation': 6,
                'kennwerte und eigenschaften': 8,
                'physikalische eigenschaften': 8,
                'chemische eigenschaften': 8,
                'mechanische eigenschaften': 8,
                'thermische eigenschaften': 6,
                'elektrische eigenschaften': 6,
                'produktbeschreibung': 6,
                'materialangaben': 6,
                'werkstoffdaten': 8,
                # English
                'properties': 5,
                'application': 4,
                'processing': 4,
                'specification': 6,
                'characteristics': 5,
                'physical properties': 8,
                'chemical properties': 8,
                'mechanical properties': 8,
                'thermal properties': 6,
                'electrical properties': 6,
                'material data': 8,
                'product description': 6,
                'material specifications': 8,
            },
            
            # Technical measurement indicators (medium confidence)
            'technical_measurements': {
                # German
                'dichte': 3,
                'viskosität': 3,
                'schmelzpunkt': 3,
                'glasübergangstemperatur': 4,
                'zugfestigkeit': 4,
                'biegefestigkeit': 4,
                'druckfestigkeit': 4,
                'härte': 3,
                'elastizitätsmodul': 4,
                'wärmeleitfähigkeit': 3,
                'temperaturbeständigkeit': 4,
                'lösemittelbeständigkeit': 4,
                'chemische beständigkeit': 4,
                # English
                'density': 3,
                'viscosity': 3,
                'melting point': 3,
                'glass transition temperature': 4,
                'tensile strength': 4,
                'flexural strength': 4,
                'compressive strength': 4,
                'hardness': 3,
                'elastic modulus': 4,
                'thermal conductivity': 3,
                'temperature resistance': 4,
                'chemical resistance': 4,
                'solvent resistance': 4,
            },
            
            # Format and structure indicators (lower confidence)
            'format_indicators': {
                # German
                'tabelle': 2,
                'werte': 2,
                'messverfahren': 3,
                'prüfverfahren': 3,
                'norm': 3,
                'standard': 3,
                'min.': 2,
                'max.': 2,
                'typ.': 2,
                'ca.': 1,
                # English
                'table': 2,
                'values': 2,
                'test method': 3,
                'testing procedure': 3,
                'standard': 3,
                'typical': 2,
                'minimum': 2,
                'maximum': 2,
                'approx': 1,
            },
            
            # Industry/application indicators (lower confidence)
            'industry_indicators': {
                # German
                'automotive': 2,
                'aerospace': 2,
                'elektronik': 2,
                'bauindustrie': 2,
                'medizintechnik': 2,
                'verpackung': 2,
                'beschichtung': 2,
                'klebstoff': 3,
                'dichtung': 2,
                'isolierung': 2,
                # English
                'automotive': 2,
                'aerospace': 2,
                'electronics': 2,
                'construction': 2,
                'medical': 2,
                'packaging': 2,
                'coating': 2,
                'adhesive': 3,
                'sealant': 2,
                'insulation': 2,
            }
        }
        
        # Negative indicators (subtract points if found - suggests other document types)
        self.negative_indicators = {
            # SDS-specific terms (strong negative indicators)
            'sicherheitsdatenblatt': -30,
            'safety data sheet': -30,
            'sds': -20,
            'msds': -20,
            '1907/2006 eg': -25,
            'reach': -15,
            'clp': -15,
            'ghs': -15,
            'gefahrenhinweis': -15,
            'hazard statement': -15,
            'sicherheitshinweis': -15,
            'precautionary statement': -15,
            'gefahrenpiktogramm': -15,
            'hazard pictogram': -15,
            'signalwort': -12,
            'signal word': -12,
            'erste hilfe': -12,
            'first aid': -12,
            'brandbekämpfung': -12,
            'firefighting': -12,
            'toxikologie': -15,
            'toxicological': -15,
            'entsorgung': -10,
            'disposal': -10,
            'transport information': -10,
            'transportangaben': -10,
            'cas-nr': -8,
            'cas number': -8,
            'eg-nr': -8,
            'ec number': -8,
            'h[0-9]{3}': -10,  # H-codes like H319
            'p[0-9]{3}': -10,  # P-codes like P101
            'euh[0-9]{3}': -10,  # EUH-codes
            # Document sections that indicate SDS
            '1. bezeichnung': -15,
            '2. gefahren': -15,
            '3. zusammensetzung': -15,
            '4. erste hilfe': -15,
            '1. identification': -15,
            '2. hazards': -15,
            '3. composition': -15,
            '4. first aid': -15,
            # Business documents
            'rechnung': -10,
            'invoice': -10,
            'vertrag': -10,
            'contract': -10,
            'bestellung': -8,
            'order': -8,
        }
        
        # Technical data patterns (regex)
        self.technical_patterns = [
            # Units and measurements
            r'\b\d+\s*(?:°C|K|°F)\b',  # Temperature
            r'\b\d+\s*(?:MPa|GPa|N/mm²|psi)\b',  # Pressure/Strength
            r'\b\d+\s*(?:g/cm³|kg/m³|g/ml)\b',  # Density
            r'\b\d+\s*(?:mPa·s|cP|Pa·s)\b',  # Viscosity
            r'\b\d+\s*(?:W/m·K|W/mK)\b',  # Thermal conductivity
            r'\b\d+\s*(?:%|Prozent)\b',  # Percentages
            r'\b\d+\s*(?:mm|cm|m|µm|nm)\b',  # Dimensions
            r'\b\d+\s*(?:min|h|s|d)\b',  # Time
            # Standards
            r'\b(?:DIN|ISO|ASTM|EN)\s*\d+\b',  # Standards
            r'\b(?:≥|≤|>|<|±)\s*\d+',  # Comparison operators
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
                
        # Fallback to other methods
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
            'eigenschaften', 'anwendung', 'verarbeitung', 'datenblatt',
            'technische', 'produkt', 'und', 'der', 'die', 'das', 'mit', 'für'
        ]
        
        english_indicators = [
            'properties', 'application', 'processing', 'datasheet',
            'technical', 'product', 'and', 'the', 'of', 'for', 'with', 'data'
        ]
        
        german_count = sum(1 for word in german_indicators if word in text_lower)
        english_count = sum(1 for word in english_indicators if word in text_lower)
        
        if german_count > english_count:
            return 'German'
        elif english_count > german_count:
            return 'English'
        else:
            return 'Mixed/Unknown'

    def is_likely_sds(self, text: str) -> bool:
        """Quick check to determine if document is likely an SDS (should be excluded from TDS detection)"""
        text_lower = text.lower()
        
        # Strong SDS indicators
        strong_sds_indicators = [
            'sicherheitsdatenblatt',
            'safety data sheet',
            '1907/2006 eg',
            'reach',
        ]
        
        # Check for strong indicators
        for indicator in strong_sds_indicators:
            if indicator in text_lower:
                return True
        
        # Check for SDS section structure (numbered sections 1-16)
        sds_sections = 0
        section_patterns = [
            r'\b1\.\s*bezeichnung',
            r'\b2\.\s*gefahren',
            r'\b3\.\s*zusammensetzung',
            r'\b4\.\s*erste\s*hilfe',
            r'\b1\.\s*identification',
            r'\b2\.\s*hazards',
            r'\b3\.\s*composition',
            r'\b4\.\s*first\s*aid',
        ]
        
        for pattern in section_patterns:
            if re.search(pattern, text_lower):
                sds_sections += 1
        
        # If we find 3 or more SDS sections, it's likely an SDS
        if sds_sections >= 3:
            return True
        
        return False

    def score_keywords(self, text: str) -> Tuple[int, List[str], str]:
        """Score based on keyword presence and determine document type"""
        text_lower = text.lower()
        total_score = 0
        found_features = []
        category_scores = {}
        
        # Score positive indicators
        for category, keywords in self.keywords.items():
            category_score = 0
            for keyword, points in keywords.items():
                if keyword in text_lower:
                    category_score += points
                    found_features.append(f"Keyword: {keyword} (+{points})")
            
            category_scores[category] = category_score
            total_score += category_score
        
        # Apply negative indicators
        negative_score = 0
        for keyword, penalty in self.negative_indicators.items():
            # Check if this is a regex pattern (contains special regex chars)
            if any(char in keyword for char in ['[', ']', '{', '}', '+', '*', '?', '^', '$']):
                # Use regex search for patterns
                if re.search(keyword, text_lower):
                    negative_score += penalty
                    found_features.append(f"Negative pattern: {keyword} ({penalty})")
            else:
                # Simple text search for regular keywords
                if keyword in text_lower:
                    negative_score += penalty
                    found_features.append(f"Negative: {keyword} ({penalty})")
        
        total_score += negative_score
        category_scores['negative_indicators'] = negative_score
        
        # Determine likely document type based on strongest indicators
        document_type = "Technical Document"
        if category_scores.get('document_type_primary', 0) > 0:
            # Find the highest scoring primary keyword to determine type
            primary_keywords = self.keywords['document_type_primary']
            best_keyword = None
            best_score = 0
            
            for keyword, points in primary_keywords.items():
                if keyword in text_lower and points > best_score:
                    best_score = points
                    best_keyword = keyword
            
            if best_keyword:
                if 'produktdaten' in best_keyword or 'product data' in best_keyword:
                    document_type = "Product Data Sheet (PDS)"
                elif 'technisch' in best_keyword or 'technical' in best_keyword:
                    document_type = "Technical Data Sheet (TDS)"
                elif 'merkblatt' in best_keyword:
                    document_type = "Technical Information Sheet"
                elif 'spezifikation' in best_keyword or 'specification' in best_keyword:
                    document_type = "Technical Specification"
        
        return total_score, found_features, document_type

    def score_technical_patterns(self, text: str) -> Tuple[int, List[str]]:
        """Score based on technical measurement patterns"""
        pattern_score = 0
        pattern_features = []
        
        for pattern in self.technical_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Award points based on number of matches (but cap it)
                points = min(len(matches) * 2, 10)
                pattern_score += points
                pattern_features.append(f"Technical pattern: {pattern} ({len(matches)} matches, +{points})")
        
        return pattern_score, pattern_features

    def score_structure_indicators(self, text: str) -> Tuple[int, List[str]]:
        """Score based on document structure typical for TDS/PDS"""
        structure_score = 0
        structure_features = []
        
        # Look for table-like structures
        lines = text.split('\n')
        table_indicators = 0
        
        for line in lines:
            line_clean = line.strip()
            # Look for lines with multiple numeric values (typical in spec tables)
            numeric_matches = re.findall(r'\b\d+(?:[.,]\d+)?\b', line_clean)
            if len(numeric_matches) >= 3:
                table_indicators += 1
        
        if table_indicators >= 5:
            structure_score += 15
            structure_features.append(f"Table-like structure: {table_indicators} rows with multiple values (+15)")
        elif table_indicators >= 2:
            structure_score += 8
            structure_features.append(f"Some tabular data: {table_indicators} rows (+8)")
        
        # Look for specification sections
        spec_patterns = [
            r'(?:eigenschaften|properties)[\s\S]{20,100}(?:\d+|wert|value)',
            r'(?:technische\s+daten|technical\s+data)[\s\S]{20,200}',
            r'(?:spezifikation|specification)[\s\S]{20,200}',
        ]
        
        for pattern in spec_patterns:
            if re.search(pattern, text.lower()):
                structure_score += 5
                structure_features.append(f"Specification section found (+5)")
                break
        
        return structure_score, structure_features

    def detect_tds(self, pdf_path: str) -> TDSScore:
        """
        Main detection method - analyzes PDF and returns TDS/PDS score
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            TDSScore object with detection results
        """
        if not os.path.exists(pdf_path):
            return TDSScore(
                total_score=0,
                is_likely_tds=False,
                document_type="Unknown",
                confidence_level="Error",
                breakdown={},
                detected_features=["File not found"],
                language_detected="Unknown"
            )
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return TDSScore(
                total_score=0,
                is_likely_tds=False,
                document_type="Unknown",
                confidence_level="Error",
                breakdown={},
                detected_features=["Could not extract text"],
                language_detected="Unknown"
            )
        
        # Detect language
        language = self.detect_language(text)
        
        # Check for SDS early
        if self.is_likely_sds(text):
            return TDSScore(
                total_score=0,
                is_likely_tds=False,
                document_type="SDS",
                confidence_level="Very Low",
                breakdown={},
                detected_features=["Identified as SDS"],
                language_detected=language
            )

        # Score different aspects
        keyword_score, keyword_features, document_type = self.score_keywords(text)
        pattern_score, pattern_features = self.score_technical_patterns(text)
        structure_score, structure_features = self.score_structure_indicators(text)
        
        # Calculate total score
        total_score = max(0, keyword_score + pattern_score + structure_score)
        
        # Determine confidence level and likelihood
        if total_score >= 80:
            confidence = "Very High"
            is_likely = True
        elif total_score >= 60:
            confidence = "High"
            is_likely = True
        elif total_score >= 40:
            confidence = "Medium"
            is_likely = True
        elif total_score >= 20:
            confidence = "Low"
            is_likely = False
        else:
            confidence = "Very Low"
            is_likely = False
        
        # Combine all features
        all_features = keyword_features + pattern_features + structure_features
        
        # Create breakdown
        breakdown = {
            'keywords': keyword_score,
            'technical_patterns': pattern_score,
            'structure': structure_score,
            'total': total_score
        }
        
        return TDSScore(
            total_score=total_score,
            is_likely_tds=is_likely,
            document_type=document_type,
            confidence_level=confidence,
            breakdown=breakdown,
            detected_features=all_features,
            language_detected=language
        )

    def batch_detect(self, pdf_directory: str) -> Dict[str, TDSScore]:
        """
        Detect TDS/PDS for all PDFs in a directory
        
        Args:
            pdf_directory: Directory containing PDF files
            
        Returns:
            Dictionary mapping filenames to TDSScore objects
        """
        results = {}
        
        if not os.path.exists(pdf_directory):
            return results
        
        for filename in os.listdir(pdf_directory):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, filename)
                results[filename] = self.detect_tds(pdf_path)
        
        return results


def main():
    """Command line interface for TDS/PDS detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Detect Technical/Product Data Sheets in PDF files')
    parser.add_argument('input', help='PDF file or directory to analyze')
    parser.add_argument('--output', '-o', help='Output JSON file for results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    detector = TDSDetector()
    
    if os.path.isfile(args.input):
        # Single file
        result = detector.detect_tds(args.input)
        
        print(f"\n📋 TDS/PDS Detection Results for: {args.input}")
        print("=" * 60)
        print(f"Score: {result.total_score}/100")
        print(f"Likely TDS/PDS: {result.is_likely_tds}")
        print(f"Document Type: {result.document_type}")
        print(f"Confidence: {result.confidence_level}")
        print(f"Language: {result.language_detected}")
        print(f"\nScore Breakdown:")
        for category, score in result.breakdown.items():
            print(f"  {category.replace('_', ' ').title()}: {score}")
        
        if args.verbose:
            print(f"\nDetected Features:")
            for feature in result.detected_features[:15]:  # Show first 15
                print(f"  - {feature}")
            if len(result.detected_features) > 15:
                print(f"  ... and {len(result.detected_features) - 15} more")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump({
                    'file': args.input,
                    'score': result.total_score,
                    'is_tds': result.is_likely_tds,
                    'document_type': result.document_type,
                    'confidence': result.confidence_level,
                    'language': result.language_detected,
                    'breakdown': result.breakdown,
                    'features': result.detected_features
                }, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to: {args.output}")
    
    elif os.path.isdir(args.input):
        # Directory
        results = detector.batch_detect(args.input)
        
        print(f"\n📋 Batch TDS/PDS Detection Results for: {args.input}")
        print("=" * 70)
        
        tds_files = []
        non_tds_files = []
        
        for filename, result in results.items():
            if result.is_likely_tds:
                tds_files.append((filename, result.total_score, result.document_type))
            else:
                non_tds_files.append((filename, result.total_score, result.document_type))
        
        print(f"\n✅ Likely TDS/PDS files ({len(tds_files)}):")
        for filename, score, doc_type in sorted(tds_files, key=lambda x: x[1], reverse=True):
            print(f"  📄 {filename}: {score}/100 ({doc_type})")
        
        print(f"\n❌ Non-TDS/PDS files ({len(non_tds_files)}):")
        for filename, score, doc_type in sorted(non_tds_files, key=lambda x: x[1], reverse=True):
            print(f"  📄 {filename}: {score}/100")
        
        if args.output:
            output_data = {}
            for filename, result in results.items():
                output_data[filename] = {
                    'score': result.total_score,
                    'is_tds': result.is_likely_tds,
                    'document_type': result.document_type,
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
