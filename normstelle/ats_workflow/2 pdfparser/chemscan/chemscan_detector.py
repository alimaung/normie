#!/usr/bin/env python3
"""
ChemScan Detector
Detects ChemScan hazardous substance assessment reports (Stellungnahme/Gefahrstoffprüfung)
These are bespoke German documents with a very specific structure for chemical risk assessment
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
class ChemScanScore:
    """Container for ChemScan detection results"""
    total_score: int
    is_likely_chemscan: bool
    document_type: str
    confidence_level: str
    breakdown: Dict[str, int]
    detected_features: List[str]
    language_detected: str


class ChemScanDetector:
    """
    Detects ChemScan hazardous substance assessment reports.
    
    These are highly specific German documents with a standardized structure for
    evaluating chemical substances against regulatory requirements (TRGS, REACH, etc.).
    
    Scoring System (0-100):
    - 85-100: Very likely ChemScan report
    - 70-84:  Likely ChemScan report
    - 50-69:  Possibly ChemScan-related
    - 30-49:  Unlikely to be ChemScan
    - 0-29:   Definitely not ChemScan
    """
    
    def __init__(self):
        # ChemScan-specific keywords with high confidence weights
        self.keywords = {
            # Primary ChemScan indicators (very specific to this document type)
            'chemscan_primary': {
                'gefährdungsbeurteilung': 25,
                'rechtsprüfung gefahrstoffe': 25,
                'chemscan prüfung produktsicherheit': 25,
                'chemscan prüfung arbeitsschutz': 25,
                'ergebnis chemscan prüfung': 20,
                'stellungnahme zum sdb': 15,
                'katalogprüfung': 15,
                'prüfmatrix': 15,
                'bewertungskriterium': 12,
                'treffer': 8,  # Common in the tabular results
                'arbeitsmedizinisch relevante informationen': 10,
            },
            
            # German regulatory framework terms (specific combinations)
            'regulatory_framework': {
                'trgs 900': 8,  # Arbeitsplatzgrenzwerte
                'trgs 903': 8,  # Biologische Grenzwerte
                'trgs 905': 8,  # KMR-Stoffe
                'trgs 906': 8,  # Krebserzeugende Tätigkeiten
                'trgs 907': 8,  # Sensibilisierende Stoffe
                'trgs 910': 8,  # Akzeptanz- und Toleranzkonzentrationen
                'trgs510': 6,   # Lagerklasse
                'arbmedvv': 6,  # Arbeitsmedizinische Vorsorge
                'odin': 6,      # Organisationsdienst für nachgehende Untersuchungen
                'awsv': 5,      # Wassergefährdungsklasse
                'bimschv': 5,   # Bundesimmissionsschutzverordnung
                'elektrostoffv': 5,  # ROHS
                'rohs - elektrostoffv': 8,
            },
            
            # ChemScan assessment language (specific phrasing)
            'assessment_language': {
                'keine bedenken': 10,
                'der stoff kann verwendet werden': 10,
                'stoff unterliegt keinem weiterverwendungsverbot': 10,
                'gefährdungsbeurteilung': 8,
                'ordnungsgemäßen gebrauch der psa': 8,
                'gbu erstellen': 8,
                'lagerklasse vorhanden': 6,
                'prüfen und ggf. beachten': 6,
                'arbeits- und umweltschutz': 6,
                'produktsicherheit': 5,
                'arbeits- und gesundheitsschutz': 6,
            },
            
            # Document structure indicators
            'structure_indicators': {
                'grunddaten': 6,
                'verwendete menge': 5,
                'tkz-nr': 8,  # Very specific identifier
                'standort': 4,
                'fazit': 5,
                'übersicht': 4,
                'auswertung': 4,
                'begründung': 4,
                'verantwortlich': 4,
                'pflegedatum': 6,
                'überarbeitungsdatum': 5,
            },
            
            # Specific assessment categories (unique structure)
            'assessment_categories': {
                'physikalische gefährdungen': 5,
                'gesundheitliche gefährdungen': 5,
                'rechtliche vorgaben': 5,
                'generelle gefährdungen': 6,
                'substances of very high concern': 4,  # SVHC in this context
                'zulassungspflichtige stoffe': 5,
                'stoffe die einer beschränkung unterliegen': 6,
                'verzeichnis krebserzeugender': 6,
                'sensibilisierende stoffe': 5,
            }
        }
        
        # Negative indicators (reduce score if found - indicates other document types)
        self.negative_indicators = {
            # Pure SDS indicators (not assessment reports)
            'erste hilfe': -5,
            'brandbekämpfung': -5,
            'exposition controls': -5,
            'physical and chemical properties': -8,
            'stability and reactivity': -8,
            'transport information': -5,
            'disposal considerations': -5,
            # TDS/PDS indicators
            'produktdatenblatt': -8,
            'technical data sheet': -8,
            'technische spezifikation': -6,
            # Business documents
            'rechnung': -10,
            'invoice': -10,
            'vertrag': -8,
            'contract': -8,
        }
        
        # ChemScan-specific patterns (regex)
        self.chemscan_patterns = [
            r'TKZ-Nr\.:\s*\d+',  # TKZ number format
            r'Treffer:\s*\d+',   # Assessment results format
            r'LK:\s*\d+',        # Lagerklasse format
            r'\d+\s*l\s*pro\s*anwendung',  # Usage amount format
            r'M\.Sc\.\s+[\w\s-]+',  # Responsible person format
            r'SDB\s+(?:Überarbeitungsdatum|Pflegedatum)',  # SDB date references
            r'Ergebnis:\s*\d+',  # Result numbering
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
        """Detect primary language - ChemScan reports are primarily German"""
        text_lower = text.lower()
        
        # ChemScan documents are German regulatory reports
        german_indicators = [
            'rechtsprüfung', 'gefahrstoffe', 'arbeitsschutz', 'produktsicherheit',
            'gefährdungsbeurteilung', 'trgs', 'arbeitsplatzgrenzwerte'
        ]
        
        german_count = sum(1 for word in german_indicators if word in text_lower)
        
        # ChemScan reports should be primarily German
        if german_count >= 2:
            return 'German'
        else:
            return 'Mixed/Unknown'

    def score_keywords(self, text: str) -> Tuple[int, List[str]]:
        """Score based on ChemScan-specific keyword presence"""
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
                    found_features.append(f"ChemScan keyword: {keyword} (+{points})")
            
            category_scores[category] = category_score
            total_score += category_score
        
        # Apply negative indicators
        negative_score = 0
        for keyword, penalty in self.negative_indicators.items():
            if keyword in text_lower:
                negative_score += penalty
                found_features.append(f"Negative indicator: {keyword} ({penalty})")
        
        total_score += negative_score
        category_scores['negative_indicators'] = negative_score
        
        return total_score, found_features

    def score_patterns(self, text: str) -> Tuple[int, List[str]]:
        """Score based on ChemScan-specific patterns"""
        pattern_score = 0
        pattern_features = []
        
        for pattern in self.chemscan_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Award points based on pattern matches
                points = min(len(matches) * 3, 12)  # Cap at 12 points per pattern
                pattern_score += points
                pattern_features.append(f"ChemScan pattern: {pattern} ({len(matches)} matches, +{points})")
        
        return pattern_score, pattern_features

    def score_structure(self, text: str) -> Tuple[int, List[str]]:
        """Score based on ChemScan document structure"""
        structure_score = 0
        structure_features = []
        
        # Look for the characteristic assessment table structure
        lines = text.split('\n')
        assessment_rows = 0
        
        # Count lines that look like assessment results (keyword + number + ja/nein)
        for line in lines:
            line_clean = line.strip().lower()
            # Look for patterns like "trgs 900" followed by "0" and "nein"
            if any(trgs in line_clean for trgs in ['trgs', 'arbmedvv', 'odin', 'reach']):
                if re.search(r'\b\d+\b.*\b(?:ja|nein)\b', line_clean):
                    assessment_rows += 1
        
        if assessment_rows >= 10:
            structure_score += 20
            structure_features.append(f"Strong assessment structure: {assessment_rows} assessment rows (+20)")
        elif assessment_rows >= 5:
            structure_score += 12
            structure_features.append(f"Moderate assessment structure: {assessment_rows} assessment rows (+12)")
        elif assessment_rows >= 2:
            structure_score += 6
            structure_features.append(f"Some assessment structure: {assessment_rows} assessment rows (+6)")
        
        # Look for the characteristic section structure
        sections_found = 0
        section_patterns = [
            r'1\)\s*gefahrstoffinformationen',
            r'2\)\s*arbeitsmedizinisch\s*relevante',
            r'3\)\s*physikalische\s*gefährdungen',
            r'4\)\s*generelle\s*gefährdungen',
            r'5\)\s*rechtliche\s*vorgaben',
        ]
        
        for pattern in section_patterns:
            if re.search(pattern, text.lower()):
                sections_found += 1
        
        if sections_found >= 4:
            structure_score += 15
            structure_features.append(f"Complete section structure: {sections_found}/5 sections (+15)")
        elif sections_found >= 2:
            structure_score += 8
            structure_features.append(f"Partial section structure: {sections_found}/5 sections (+8)")
        
        return structure_score, structure_features

    def detect_chemscan(self, pdf_path: str) -> ChemScanScore:
        """
        Main detection method - analyzes PDF and returns ChemScan score
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ChemScanScore object with detection results
        """
        if not os.path.exists(pdf_path):
            return ChemScanScore(
                total_score=0,
                is_likely_chemscan=False,
                document_type="Unknown",
                confidence_level="Error",
                breakdown={},
                detected_features=["File not found"],
                language_detected="Unknown"
            )
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return ChemScanScore(
                total_score=0,
                is_likely_chemscan=False,
                document_type="Unknown",
                confidence_level="Error",
                breakdown={},
                detected_features=["Could not extract text"],
                language_detected="Unknown"
            )
        
        # Detect language
        language = self.detect_language(text)
        
        # Score different aspects
        keyword_score, keyword_features = self.score_keywords(text)
        pattern_score, pattern_features = self.score_patterns(text)
        structure_score, structure_features = self.score_structure(text)
        
        # Calculate total score
        total_score = max(0, keyword_score + pattern_score + structure_score)
        
        # Determine document type and confidence
        document_type = "Chemical Assessment Report"
        if total_score >= 50:
            # Check for specific ChemScan indicators to refine type
            text_lower = text.lower()
            if 'chemscan prüfung' in text_lower:
                document_type = "ChemScan Assessment Report"
            elif 'rechtsprüfung gefahrstoffe' in text_lower:
                document_type = "German Hazardous Substance Legal Review"
            elif 'stellungnahme' in text_lower:
                document_type = "Chemical Substance Statement"
        
        # Determine confidence level and likelihood
        if total_score >= 85:
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
        all_features = keyword_features + pattern_features + structure_features
        
        # Create breakdown
        breakdown = {
            'keywords': keyword_score,
            'patterns': pattern_score,
            'structure': structure_score,
            'total': total_score
        }
        
        return ChemScanScore(
            total_score=total_score,
            is_likely_chemscan=is_likely,
            document_type=document_type,
            confidence_level=confidence,
            breakdown=breakdown,
            detected_features=all_features,
            language_detected=language
        )

    def batch_detect(self, pdf_directory: str) -> Dict[str, ChemScanScore]:
        """
        Detect ChemScan reports for all PDFs in a directory
        
        Args:
            pdf_directory: Directory containing PDF files
            
        Returns:
            Dictionary mapping filenames to ChemScanScore objects
        """
        results = {}
        
        if not os.path.exists(pdf_directory):
            return results
        
        for filename in os.listdir(pdf_directory):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, filename)
                results[filename] = self.detect_chemscan(pdf_path)
        
        return results


def main():
    """Command line interface for ChemScan detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Detect ChemScan hazardous substance assessment reports in PDF files')
    parser.add_argument('input', help='PDF file or directory to analyze')
    parser.add_argument('--output', '-o', help='Output JSON file for results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    detector = ChemScanDetector()
    
    if os.path.isfile(args.input):
        # Single file
        result = detector.detect_chemscan(args.input)
        
        print(f"\n🧪 ChemScan Detection Results for: {args.input}")
        print("=" * 70)
        print(f"Score: {result.total_score}/100")
        print(f"Likely ChemScan: {result.is_likely_chemscan}")
        print(f"Document Type: {result.document_type}")
        print(f"Confidence: {result.confidence_level}")
        print(f"Language: {result.language_detected}")
        print(f"\nScore Breakdown:")
        for category, score in result.breakdown.items():
            print(f"  {category.replace('_', ' ').title()}: {score}")
        
        if args.verbose:
            print(f"\nDetected Features:")
            for feature in result.detected_features[:20]:  # Show first 20
                print(f"  - {feature}")
            if len(result.detected_features) > 20:
                print(f"  ... and {len(result.detected_features) - 20} more")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump({
                    'file': args.input,
                    'score': result.total_score,
                    'is_chemscan': result.is_likely_chemscan,
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
        
        print(f"\n🧪 Batch ChemScan Detection Results for: {args.input}")
        print("=" * 80)
        
        chemscan_files = []
        non_chemscan_files = []
        
        for filename, result in results.items():
            if result.is_likely_chemscan:
                chemscan_files.append((filename, result.total_score, result.document_type))
            else:
                non_chemscan_files.append((filename, result.total_score, result.document_type))
        
        print(f"\n✅ Likely ChemScan files ({len(chemscan_files)}):")
        for filename, score, doc_type in sorted(chemscan_files, key=lambda x: x[1], reverse=True):
            print(f"  🧪 {filename}: {score}/100 ({doc_type})")
        
        print(f"\n❌ Non-ChemScan files ({len(non_chemscan_files)}):")
        for filename, score, doc_type in sorted(non_chemscan_files, key=lambda x: x[1], reverse=True):
            print(f"  📄 {filename}: {score}/100")
        
        if args.output:
            output_data = {}
            for filename, result in results.items():
                output_data[filename] = {
                    'score': result.total_score,
                    'is_chemscan': result.is_likely_chemscan,
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
