#!/usr/bin/env python3
"""
SDS Date Detector
Detects issue dates in Safety Data Sheets and checks for validity (max 2 years old)
Focuses on German SDS documents with comprehensive date pattern recognition
"""

import os
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from pathlib import Path

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    print("Warning: PyMuPDF not available. Text extraction will be limited.")


class DateMatch(NamedTuple):
    """Represents a found date with context"""
    date: datetime
    original_text: str
    context_phrase: str
    confidence: float
    line_number: Optional[int] = None


@dataclass
class SDSDateResult:
    """Container for SDS date detection results"""
    filename: str
    primary_issue_date: Optional[datetime]
    all_dates_found: List[DateMatch]
    is_valid: bool
    days_until_expiry: Optional[int]
    expiry_date: Optional[datetime]
    validity_status: str
    confidence_score: float
    detection_notes: List[str]


class SDSDateDetector:
    """
    Detects and validates dates in Safety Data Sheets.
    
    Validity Rules:
    - SDS must not be older than 2 years (730 days)
    - Issue date is determined by highest confidence match
    - Multiple date formats supported (DD.MM.YYYY, DD/MM/YYYY, etc.)
    """
    
    def __init__(self):
        # German date indicator phrases with confidence weights
        self.date_indicators = {
            # Primary issue date indicators (high confidence)
            'primary_indicators': {
                'ausfertigungsdatum': 1.0,
                'ausgabedatum': 0.95,
                'erstelldatum': 0.9,
                'datum der erstellung': 0.9,
                'datum der ausgabe': 0.95,
                'dokumentdatum': 0.85,
                'sdb erstellt am': 1.0,
                'sicherheitsdatenblatt vom': 0.95,
                'datum sicherheitsdatenblatt': 0.95,
                'erste fassung': 0.8,
            },
            
            # Revision indicators (medium-high confidence) 
            'revision_indicators': {
                'überarbeitet am': 0.8,
                'geändert am': 0.75,
                'letzte änderung': 0.75,
                'überarbeitung vom': 0.8,
                'änderungsdatum': 0.75,
                'rev. datum': 0.7,
                'revision': 0.65,
                'sdb geändert am': 0.8,
                'revidiert am': 0.75,
                'nachgeführt am': 0.75,
                'letzte fassung': 0.7,
                'neufassung': 0.8,
                'neuausgabe': 0.85,
            },
            
            # Version indicators (medium confidence)
            'version_indicators': {
                'version vom': 0.6,
                'stand vom': 0.65,
                'stand': 0.5,
                'versionierung': 0.55,
                'fassung vom': 0.65,
            },
            
            # General indicators (lower confidence)
            'general_indicators': {
                'datum': 0.3,
                'gültig ab': 0.4,
                'gültig seit': 0.4,
                'in kraft seit': 0.4,
                'veröffentlichung am': 0.5,
                'veröffentlicht am': 0.5,
                'bearbeitungsdatum': 0.45,
                'redaktionsschluss': 0.4,
            },
            
            # Abbreviations (context-dependent confidence)
            'abbreviations': {
                'erst.': 0.7,
                'ausg.': 0.8,
                'geänd.': 0.6,
                'überarb.': 0.6,
                'aktual. am': 0.6,
                'akt.': 0.5,
                'upd.': 0.5,
                'änd.': 0.6,
                'bearb. am': 0.5,
                'v.': 0.3,  # Very common, low confidence alone
            }
        }
        
        # Date format patterns (DD.MM.YYYY, DD/MM/YYYY, etc.)
        self.date_patterns = [
            # European formats (most common in German SDS)
            (r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b', '%d.%m.%Y'),
            (r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', '%d/%m/%Y'),
            (r'\b(\d{1,2})-(\d{1,2})-(\d{4})\b', '%d-%m-%Y'),
            
            # ISO format
            (r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b', '%Y-%m-%d'),
            
            # With leading zeros
            (r'\b(\d{2})\.(\d{2})\.(\d{4})\b', '%d.%m.%Y'),
            (r'\b(\d{2})/(\d{2})/(\d{4})\b', '%d/%m/%Y'),
            
            # Space separated
            (r'\b(\d{1,2})\s+(\d{1,2})\s+(\d{4})\b', '%d %m %Y'),
            
            # Month names (German)
            (r'\b(\d{1,2})\.?\s*(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s*(\d{4})\b', '%d %B %Y'),
            (r'\b(\d{1,2})\.?\s*(Jan|Feb|Mär|Apr|Mai|Jun|Jul|Aug|Sep|Okt|Nov|Dez)\.?\s*(\d{4})\b', '%d %b %Y'),
        ]
        
        # Compile all indicator patterns for efficient matching
        self.all_indicators = {}
        for category, indicators in self.date_indicators.items():
            self.all_indicators.update(indicators)

    def extract_text_from_pdf(self, pdf_path: str) -> Optional[List[str]]:
        """Extract text from PDF and return as list of lines"""
        if not os.path.exists(pdf_path):
            return None
            
        lines = []
        
        if FITZ_AVAILABLE:
            try:
                doc = fitz.open(pdf_path)
                for page in doc:
                    page_text = page.get_text()
                    lines.extend(page_text.split('\n'))
                doc.close()
                return lines
            except Exception as e:
                print(f"PyMuPDF extraction failed: {e}")
                
        # Fallback to other methods
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    lines.extend(page_text.split('\n'))
            return lines
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")
            
        return None

    def find_dates_in_text(self, text_lines: List[str]) -> List[DateMatch]:
        """Find all dates with their context indicators"""
        found_dates = []
        
        for line_num, line in enumerate(text_lines):
            line_lower = line.lower().strip()
            if not line_lower:
                continue
            
            # Look for date indicator phrases
            best_indicator = None
            best_confidence = 0.0
            
            for indicator, confidence in self.all_indicators.items():
                if indicator in line_lower:
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_indicator = indicator
            
            # If we found an indicator, look for dates in this line and nearby lines
            if best_indicator:
                # Check current line and next 2 lines for dates
                search_lines = text_lines[line_num:line_num+3]
                for search_line in search_lines:
                    dates_in_line = self._extract_dates_from_line(search_line)
                    for date_obj, original_text in dates_in_line:
                        found_dates.append(DateMatch(
                            date=date_obj,
                            original_text=original_text,
                            context_phrase=best_indicator,
                            confidence=best_confidence,
                            line_number=line_num
                        ))
            
            # Also look for standalone dates without specific indicators
            # but with lower confidence
            dates_in_line = self._extract_dates_from_line(line)
            for date_obj, original_text in dates_in_line:
                # Only add if we haven't found this date already
                if not any(d.date == date_obj and d.original_text == original_text 
                          for d in found_dates):
                    found_dates.append(DateMatch(
                        date=date_obj,
                        original_text=original_text,
                        context_phrase="standalone_date",
                        confidence=0.2,
                        line_number=line_num
                    ))
        
        return found_dates

    def _extract_dates_from_line(self, line: str) -> List[Tuple[datetime, str]]:
        """Extract all valid dates from a single line"""
        dates = []
        
        for pattern, date_format in self.date_patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                try:
                    # Handle different pattern groups
                    if 'Januar' in date_format or '%B' in date_format:
                        # Month name format - need special handling
                        date_obj = self._parse_month_name_date(match.group(0))
                    else:
                        date_obj = datetime.strptime(match.group(0), date_format)
                    
                    # Validate date is reasonable (between 1990 and 2030)
                    if 1990 <= date_obj.year <= 2030:
                        dates.append((date_obj, match.group(0)))
                        
                except ValueError:
                    continue
        
        return dates

    def _parse_month_name_date(self, date_str: str) -> datetime:
        """Parse dates with German month names"""
        german_months = {
            'januar': 'January', 'jan': 'Jan',
            'februar': 'February', 'feb': 'Feb',
            'märz': 'March', 'mär': 'Mar',
            'april': 'April', 'apr': 'Apr',
            'mai': 'May',
            'juni': 'June', 'jun': 'Jun',
            'juli': 'July', 'jul': 'Jul',
            'august': 'August', 'aug': 'Aug',
            'september': 'September', 'sep': 'Sep',
            'oktober': 'October', 'okt': 'Oct',
            'november': 'November', 'nov': 'Nov',
            'dezember': 'December', 'dez': 'Dec'
        }
        
        date_str_lower = date_str.lower()
        for german, english in german_months.items():
            if german in date_str_lower:
                english_date = date_str_lower.replace(german, english)
                # Try different formats
                for fmt in ['%d %B %Y', '%d %b %Y', '%d. %B %Y', '%d. %b %Y']:
                    try:
                        return datetime.strptime(english_date, fmt)
                    except ValueError:
                        continue
        
        raise ValueError(f"Could not parse German date: {date_str}")

    def determine_primary_date(self, dates: List[DateMatch]) -> Optional[DateMatch]:
        """Determine the most likely issue date from found dates"""
        if not dates:
            return None
        
        # Sort by confidence score (highest first)
        sorted_dates = sorted(dates, key=lambda x: x.confidence, reverse=True)
        
        # Filter to only high-confidence primary indicators
        primary_dates = [d for d in sorted_dates if d.confidence >= 0.8]
        
        if primary_dates:
            return primary_dates[0]
        
        # If no high-confidence dates, take the highest confidence overall
        return sorted_dates[0]

    def validate_date(self, issue_date: datetime) -> Tuple[bool, int, datetime, str]:
        """
        Validate if the SDS is still current (within 2 years)
        
        Returns:
            (is_valid, days_until_expiry, expiry_date, status_message)
        """
        if not issue_date:
            return False, 0, None, "No issue date found"
        
        now = datetime.now()
        expiry_date = issue_date + timedelta(days=730)  # 2 years = 730 days
        days_until_expiry = (expiry_date - now).days
        
        if days_until_expiry > 0:
            if days_until_expiry <= 30:
                status = f"Expires soon (in {days_until_expiry} days)"
            elif days_until_expiry <= 90:
                status = f"Valid ({days_until_expiry} days remaining)"
            else:
                status = f"Valid ({days_until_expiry} days remaining)"
            return True, days_until_expiry, expiry_date, status
        else:
            days_expired = abs(days_until_expiry)
            status = f"EXPIRED ({days_expired} days ago)"
            return False, days_until_expiry, expiry_date, status

    def detect_dates(self, pdf_path: str) -> SDSDateResult:
        """
        Main method to detect and validate SDS dates
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            SDSDateResult with all findings
        """
        filename = os.path.basename(pdf_path)
        
        # Initialize result with defaults
        result = SDSDateResult(
            filename=filename,
            primary_issue_date=None,
            all_dates_found=[],
            is_valid=False,
            days_until_expiry=None,
            expiry_date=None,
            validity_status="No dates found",
            confidence_score=0.0,
            detection_notes=[]
        )
        
        if not os.path.exists(pdf_path):
            result.detection_notes.append("File not found")
            return result
        
        # Extract text
        text_lines = self.extract_text_from_pdf(pdf_path)
        if not text_lines:
            result.detection_notes.append("Could not extract text from PDF")
            return result
        
        # Find all dates
        all_dates = self.find_dates_in_text(text_lines)
        result.all_dates_found = all_dates
        result.detection_notes.append(f"Found {len(all_dates)} potential dates")
        
        if not all_dates:
            result.detection_notes.append("No dates found in document")
            return result
        
        # Determine primary issue date
        primary_date_match = self.determine_primary_date(all_dates)
        if primary_date_match:
            result.primary_issue_date = primary_date_match.date
            result.confidence_score = primary_date_match.confidence
            result.detection_notes.append(
                f"Primary date: {primary_date_match.date.strftime('%d.%m.%Y')} "
                f"(from '{primary_date_match.context_phrase}', confidence: {primary_date_match.confidence:.2f})"
            )
            
            # Validate the date
            is_valid, days_until_expiry, expiry_date, status = self.validate_date(primary_date_match.date)
            result.is_valid = is_valid
            result.days_until_expiry = days_until_expiry
            result.expiry_date = expiry_date
            result.validity_status = status
            
        else:
            result.detection_notes.append("Could not determine primary issue date")
        
        return result

    def batch_detect_dates(self, pdf_directory: str) -> Dict[str, SDSDateResult]:
        """
        Detect dates for all PDFs in a directory
        
        Args:
            pdf_directory: Directory containing PDF files
            
        Returns:
            Dictionary mapping filenames to SDSDateResult objects
        """
        results = {}
        
        if not os.path.exists(pdf_directory):
            return results
        
        for filename in os.listdir(pdf_directory):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, filename)
                results[filename] = self.detect_dates(pdf_path)
        
        return results


def create_date_report_html(results: Dict[str, SDSDateResult], output_dir: str) -> str:
    """Create an HTML report for date detection results"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SDS Date Validation Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .summary-card.valid { border-left: 4px solid #28a745; }
        .summary-card.expired { border-left: 4px solid #dc3545; }
        .summary-card.expiring { border-left: 4px solid #ffc107; }
        .summary-card.unknown { border-left: 4px solid #6c757d; }
        .file-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 20px;
        }
        .file-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: white;
        }
        .file-card.valid { border-left: 5px solid #28a745; }
        .file-card.expired { border-left: 5px solid #dc3545; }
        .file-card.expiring { border-left: 5px solid #ffc107; }
        .file-card.no-date { border-left: 5px solid #6c757d; }
        .file-name {
            font-weight: bold;
            margin-bottom: 10px;
            word-break: break-all;
        }
        .status {
            font-weight: bold;
            margin: 10px 0;
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
        }
        .status.valid { background: #d4edda; color: #155724; }
        .status.expired { background: #f8d7da; color: #721c24; }
        .status.expiring { background: #fff3cd; color: #856404; }
        .status.no-date { background: #e2e3e5; color: #495057; }
        .details {
            margin-top: 15px;
            font-size: 0.9em;
        }
        .date-info {
            margin: 5px 0;
        }
        .confidence {
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8em;
        }
        .notes {
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 0.85em;
        }
        .number {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📅 SDS Date Validation Report</h1>
            <p>Analysis of Safety Data Sheet validity based on issue dates</p>
        </div>
"""

    # Calculate statistics
    total_files = len(results)
    valid_files = sum(1 for r in results.values() if r.is_valid)
    expired_files = sum(1 for r in results.values() if r.primary_issue_date and not r.is_valid)
    expiring_soon = sum(1 for r in results.values() if r.days_until_expiry and 0 < r.days_until_expiry <= 90)
    no_date_files = sum(1 for r in results.values() if not r.primary_issue_date)

    html_content += f"""
        <div class="summary">
            <div class="summary-card valid">
                <h3>Valid SDS</h3>
                <div class="number">{valid_files}</div>
            </div>
            <div class="summary-card expired">
                <h3>Expired SDS</h3>
                <div class="number">{expired_files}</div>
            </div>
            <div class="summary-card expiring">
                <h3>Expiring Soon</h3>
                <div class="number">{expiring_soon}</div>
            </div>
            <div class="summary-card unknown">
                <h3>No Date Found</h3>
                <div class="number">{no_date_files}</div>
            </div>
        </div>
        
        <div class="file-list">
"""

    # Sort files by validity status and days until expiry
    def sort_key(item):
        filename, result = item
        if not result.primary_issue_date:
            return (3, 0)  # No date - last
        elif not result.is_valid:
            return (2, result.days_until_expiry or 0)  # Expired
        elif result.days_until_expiry and result.days_until_expiry <= 90:
            return (1, result.days_until_expiry)  # Expiring soon
        else:
            return (0, -(result.days_until_expiry or 0))  # Valid (newest first)

    sorted_results = sorted(results.items(), key=sort_key)

    for filename, result in sorted_results:
        # Determine card class
        if not result.primary_issue_date:
            card_class = "no-date"
            status_class = "no-date"
        elif not result.is_valid:
            card_class = "expired"
            status_class = "expired"
        elif result.days_until_expiry and result.days_until_expiry <= 90:
            card_class = "expiring"
            status_class = "expiring"
        else:
            card_class = "valid"
            status_class = "valid"

        html_content += f"""
            <div class="file-card {card_class}">
                <div class="file-name">{filename}</div>
                <div class="status {status_class}">{result.validity_status}</div>
                
                <div class="details">
"""

        if result.primary_issue_date:
            html_content += f"""
                    <div class="date-info">
                        <strong>Issue Date:</strong> {result.primary_issue_date.strftime('%d.%m.%Y')}
                    </div>
"""
            if result.expiry_date:
                html_content += f"""
                    <div class="date-info">
                        <strong>Expires:</strong> {result.expiry_date.strftime('%d.%m.%Y')}
                    </div>
"""
            html_content += f"""
                    <div class="date-info">
                        <span class="confidence">Confidence: {result.confidence_score:.2f}</span>
                    </div>
"""

        if result.detection_notes:
            html_content += f"""
                    <div class="notes">
                        <strong>Detection Notes:</strong><br>
"""
            for note in result.detection_notes:
                html_content += f"• {note}<br>"
            html_content += "</div>"

        html_content += """
                </div>
            </div>
"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_content += f"""
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; color: #666; font-size: 0.9em;">
            Report generated on {timestamp}
        </div>
    </div>
</body>
</html>
"""

    # Save HTML report
    html_path = os.path.join(output_dir, "sds_date_validation_report.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path


def main():
    """Command line interface for SDS date detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Detect and validate dates in Safety Data Sheet PDFs')
    parser.add_argument('input', help='PDF file or directory to analyze')
    parser.add_argument('--output', '-o', help='Output directory for reports')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    detector = SDSDateDetector()
    
    if os.path.isfile(args.input):
        # Single file
        result = detector.detect_dates(args.input)
        
        print(f"\n📅 SDS Date Detection Results for: {args.input}")
        print("=" * 60)
        print(f"Filename: {result.filename}")
        print(f"Status: {result.validity_status}")
        
        if result.primary_issue_date:
            print(f"Issue Date: {result.primary_issue_date.strftime('%d.%m.%Y')}")
            print(f"Confidence: {result.confidence_score:.2f}")
            if result.expiry_date:
                print(f"Expires: {result.expiry_date.strftime('%d.%m.%Y')}")
        
        if args.verbose:
            print(f"\nAll dates found ({len(result.all_dates_found)}):")
            for date_match in result.all_dates_found:
                print(f"  {date_match.date.strftime('%d.%m.%Y')} - {date_match.context_phrase} (conf: {date_match.confidence:.2f})")
            
            print(f"\nDetection Notes:")
            for note in result.detection_notes:
                print(f"  • {note}")
        
        if args.output:
            os.makedirs(args.output, exist_ok=True)
            json_path = os.path.join(args.output, "date_results.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'filename': result.filename,
                    'primary_issue_date': result.primary_issue_date.isoformat() if result.primary_issue_date else None,
                    'is_valid': result.is_valid,
                    'days_until_expiry': result.days_until_expiry,
                    'validity_status': result.validity_status,
                    'confidence_score': result.confidence_score,
                    'detection_notes': result.detection_notes
                }, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to: {json_path}")
    
    elif os.path.isdir(args.input):
        # Directory
        results = detector.batch_detect_dates(args.input)
        
        print(f"\n📅 Batch SDS Date Detection Results for: {args.input}")
        print("=" * 70)
        
        # Categorize results
        valid_files = [(f, r) for f, r in results.items() if r.is_valid]
        expired_files = [(f, r) for f, r in results.items() if r.primary_issue_date and not r.is_valid]
        no_date_files = [(f, r) for f, r in results.items() if not r.primary_issue_date]
        
        print(f"\n✅ Valid SDS ({len(valid_files)}):")
        for filename, result in sorted(valid_files, key=lambda x: x[1].days_until_expiry or 0):
            print(f"  📄 {filename}: {result.validity_status}")
        
        print(f"\n❌ Expired SDS ({len(expired_files)}):")
        for filename, result in sorted(expired_files, key=lambda x: x[1].days_until_expiry or 0, reverse=True):
            print(f"  📄 {filename}: {result.validity_status}")
        
        print(f"\n❓ No Date Found ({len(no_date_files)}):")
        for filename, result in no_date_files:
            print(f"  📄 {filename}")
        
        if args.output:
            os.makedirs(args.output, exist_ok=True)
            
            # Create detailed JSON
            json_data = {}
            for filename, result in results.items():
                json_data[filename] = {
                    'primary_issue_date': result.primary_issue_date.isoformat() if result.primary_issue_date else None,
                    'is_valid': result.is_valid,
                    'days_until_expiry': result.days_until_expiry,
                    'validity_status': result.validity_status,
                    'confidence_score': result.confidence_score,
                    'detection_notes': result.detection_notes
                }
            
            json_path = os.path.join(args.output, "date_results.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            # Create HTML report
            html_path = create_date_report_html(results, args.output)
            
            print(f"\n📁 Reports saved to: {args.output}")
            print(f"   📄 JSON Results: {os.path.basename(json_path)}")
            print(f"   🌐 HTML Report: {os.path.basename(html_path)}")
    
    else:
        print(f"Error: {args.input} is not a valid file or directory")


if __name__ == "__main__":
    main() 