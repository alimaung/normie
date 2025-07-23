#!/usr/bin/env python3
"""
Comprehensive SDS Analysis Batch Script
Runs both SDS detection and date validation on all PDFs in the sds folder
Generates combined reports with both detection and validity information
Includes detection for scanned documents with no extractable text
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

# Add the current directory to path so we can import our detectors
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sds_detector import SDSDetector, SDSScore
from sds_date_detector import SDSDateDetector, SDSDateResult

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    print("Warning: PyMuPDF not available. Text extraction will be limited.")


def detect_scanned_document(pdf_path: str) -> tuple[bool, str, int]:
    """
    Detect if a PDF is likely a scanned document with no extractable text
    
    Returns:
        tuple: (is_scanned, reason, char_count)
            - is_scanned: True if document appears to be scanned
            - reason: Description of why it's considered scanned
            - char_count: Number of extractable characters found
    """
    if not os.path.exists(pdf_path):
        return True, "File not found", 0
    
    text = ""
    char_count = 0
    
    # Try to extract text using available methods
    if FITZ_AVAILABLE:
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                page_text = page.get_text()
                text += page_text
            doc.close()
        except Exception as e:
            return True, f"Text extraction failed: {str(e)}", 0
    else:
        # Fallback to PyPDF2
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            return True, f"Text extraction failed: {str(e)}", 0
    
    # Count actual characters (excluding whitespace)
    char_count = len(re.sub(r'\s+', '', text))
    
    # Determine if it's likely scanned based on text content
    if char_count == 0:
        return True, "No extractable text found", 0
    elif char_count < 50:
        return True, f"Very little text found ({char_count} chars)", char_count
    elif char_count < 200:
        # Check if text looks like OCR artifacts or random characters
        # Look for patterns that suggest poor OCR or scanning
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        words = clean_text.split()
        
        if len(words) < 20:
            return True, f"Insufficient meaningful text ({len(words)} words, {char_count} chars)", char_count
        
        # Check for excessive single characters or very short "words"
        single_chars = sum(1 for word in words if len(word) == 1)
        if single_chars > len(words) * 0.5:  # More than 50% single characters
            return True, f"Text appears to be OCR artifacts ({single_chars}/{len(words)} single chars)", char_count
    
    # If we have substantial text, it's probably not scanned
    return False, f"Sufficient text content ({char_count} chars)", char_count


def create_enhanced_sds_score(pdf_path: str, sds_detector: SDSDetector) -> SDSScore:
    """
    Create an SDS score with scanned document detection
    """
    # First check if it's a scanned document
    is_scanned, scan_reason, char_count = detect_scanned_document(pdf_path)
    
    if is_scanned:
        # Create a special result for scanned documents
        return SDSScore(
            total_score=0,
            is_likely_sds=None,  # Use None to indicate "unknown" rather than False
            confidence_level="Unknown (Scanned)",
            breakdown={"scanned_detection": 0, "char_count": char_count},
            detected_features=[f"Scanned document: {scan_reason}"],
            language_detected="Unknown (Scanned)"
        )
    
    # If not scanned, proceed with normal SDS detection
    try:
        return sds_detector.detect_sds(pdf_path)
    except Exception as e:
        return SDSScore(
            total_score=0,
            is_likely_sds=False,
            confidence_level="Error",
            breakdown={},
            detected_features=[f"Processing error: {str(e)}"],
            language_detected="Unknown"
        )


def create_combined_html_report(sds_results: dict, date_results: dict, output_dir: str) -> str:
    """Create a comprehensive HTML report combining SDS detection and date validation"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive SDS Analysis Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1600px;
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .summary-card.good { border-left: 4px solid #28a745; }
        .summary-card.warning { border-left: 4px solid #ffc107; }
        .summary-card.bad { border-left: 4px solid #dc3545; }
        .summary-card.info { border-left: 4px solid #007bff; }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .summary-card .number {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .file-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
            gap: 20px;
        }
        .file-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: white;
        }
        .file-card.valid-sds-valid-date { border-left: 5px solid #28a745; }
        .file-card.valid-sds-expired { border-left: 5px solid #fd7e14; }
        .file-card.valid-sds-no-date { border-left: 5px solid #ffc107; }
        .file-card.invalid-sds { border-left: 5px solid #dc3545; }
        .file-card.scanned-document { border-left: 5px solid #6c757d; }
        .file-name {
            font-weight: bold;
            margin-bottom: 15px;
            word-break: break-all;
            font-size: 1.1em;
        }
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }
        .status-section {
            padding: 10px;
            border-radius: 6px;
            background: #f8f9fa;
        }
        .status-section h4 {
            margin: 0 0 8px 0;
            font-size: 0.9em;
            color: #495057;
            text-transform: uppercase;
        }
        .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 5px;
        }
        .status-badge.sds-valid { background: #d4edda; color: #155724; }
        .status-badge.sds-invalid { background: #f8d7da; color: #721c24; }
        .status-badge.sds-scanned { background: #e2e3e5; color: #495057; }
        .status-badge.date-valid { background: #d4edda; color: #155724; }
        .status-badge.date-expired { background: #f8d7da; color: #721c24; }
        .status-badge.date-expiring { background: #fff3cd; color: #856404; }
        .status-badge.date-unknown { background: #e2e3e5; color: #495057; }
        .details {
            font-size: 0.85em;
            line-height: 1.4;
        }
        .score {
            font-size: 1.2em;
            font-weight: bold;
            margin: 5px 0;
        }
        .score.high { color: #28a745; }
        .score.medium { color: #ffc107; }
        .score.low { color: #dc3545; }
        .priority-high {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .priority-medium {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #dee2e6;
        }
        .tab {
            padding: 10px 20px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-bottom: none;
            cursor: pointer;
            margin-right: 5px;
        }
        .tab.active {
            background: white;
            border-bottom: 1px solid white;
            margin-bottom: -1px;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
    <script>
        function showTab(tabName) {
            // Hide all tab contents
            var contents = document.querySelectorAll('.tab-content');
            contents.forEach(function(content) {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            var tabs = document.querySelectorAll('.tab');
            tabs.forEach(function(tab) {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍📅 Comprehensive SDS Analysis Report</h1>
            <p>Combined Safety Data Sheet detection and validity analysis</p>
        </div>
"""

    # Calculate combined statistics
    total_files = len(sds_results)
    valid_sds = sum(1 for r in sds_results.values() if r.is_likely_sds is True)
    scanned_docs = sum(1 for r in sds_results.values() if r.is_likely_sds is None)
    valid_dates = sum(1 for r in date_results.values() if r.is_valid)
    expired_dates = sum(1 for r in date_results.values() if r.primary_issue_date and not r.is_valid)
    
    # Critical issues (SDS with expired dates)
    critical_issues = 0
    action_needed = 0
    good_status = 0
    
    for filename in sds_results:
        sds_result = sds_results[filename]
        date_result = date_results.get(filename)
        
        if sds_result.is_likely_sds is True:  # Only count valid SDS files
            if date_result and date_result.primary_issue_date and not date_result.is_valid:
                critical_issues += 1
            elif date_result and date_result.days_until_expiry and 0 < date_result.days_until_expiry <= 90:
                action_needed += 1
            elif date_result and date_result.is_valid:
                good_status += 1

    html_content += f"""
        <div class="summary">
            <div class="summary-card info">
                <h3>Total Files</h3>
                <div class="number">{total_files}</div>
            </div>
            <div class="summary-card good">
                <h3>Valid SDS & Current</h3>
                <div class="number">{good_status}</div>
            </div>
            <div class="summary-card warning">
                <h3>Action Needed</h3>
                <div class="number">{action_needed}</div>
            </div>
            <div class="summary-card bad">
                <h3>Critical Issues</h3>
                <div class="number">{critical_issues}</div>
            </div>
            <div class="summary-card info">
                <h3>Scanned/Unknown</h3>
                <div class="number">{scanned_docs}</div>
            </div>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('overview')">Overview</div>
            <div class="tab" onclick="showTab('critical')">Critical Issues</div>
            <div class="tab" onclick="showTab('action-needed')">Action Needed</div>
            <div class="tab" onclick="showTab('all-files')">All Files</div>
        </div>
"""

    # Create different views
    def create_file_card(filename, sds_result, date_result):
        # Determine overall status
        if sds_result.is_likely_sds is None:  # Scanned document
            card_class = "scanned-document"
            priority_level = "unknown"
        elif not sds_result.is_likely_sds:
            card_class = "invalid-sds"
            priority_level = "low"
        elif date_result and date_result.primary_issue_date and not date_result.is_valid:
            card_class = "valid-sds-expired"
            priority_level = "high"
        elif date_result and date_result.days_until_expiry and 0 < date_result.days_until_expiry <= 90:
            card_class = "valid-sds-valid-date"
            priority_level = "medium"
        elif date_result and date_result.is_valid:
            card_class = "valid-sds-valid-date"
            priority_level = "low"
        else:
            card_class = "valid-sds-no-date"
            priority_level = "medium"

        score_class = "high" if sds_result.total_score >= 70 else "medium" if sds_result.total_score >= 50 else "low"
        
        card_html = f"""
            <div class="file-card {card_class}">
                <div class="file-name">{filename}</div>
                
                <div class="status-grid">
                    <div class="status-section">
                        <h4>SDS Detection</h4>
                        <div class="status-badge {'sds-valid' if sds_result.is_likely_sds is True else 'sds-scanned' if sds_result.is_likely_sds is None else 'sds-invalid'}">
                            {'✅ Valid SDS' if sds_result.is_likely_sds is True else '❓ Scanned/Unknown' if sds_result.is_likely_sds is None else '❌ Not SDS'}
                        </div>
                        <div class="score {score_class}">{sds_result.total_score}/100</div>
                        <div class="details">
                            Confidence: {sds_result.confidence_level}<br>
                            Language: {sds_result.language_detected}
                        </div>
                    </div>
                    
                    <div class="status-section">
                        <h4>Date Validation</h4>
"""
        
        if date_result and date_result.primary_issue_date:
            if date_result.is_valid:
                if date_result.days_until_expiry <= 90:
                    badge_class = "date-expiring"
                    badge_text = "⚠️ Expiring Soon"
                else:
                    badge_class = "date-valid"
                    badge_text = "✅ Valid"
            else:
                badge_class = "date-expired"
                badge_text = "❌ Expired"
            
            card_html += f"""
                        <div class="status-badge {badge_class}">{badge_text}</div>
                        <div class="details">
                            Issue: {date_result.primary_issue_date.strftime('%d.%m.%Y')}<br>
                            Status: {date_result.validity_status}<br>
                            Confidence: {date_result.confidence_score:.2f}
                        </div>
"""
        else:
            card_html += """
                        <div class="status-badge date-unknown">❓ No Date Found</div>
                        <div class="details">Could not detect issue date</div>
"""

        card_html += "</div></div>"

        # Add priority notices
        if priority_level == "high":
            card_html += """
                <div class="priority-high">
                    <strong>🚨 URGENT:</strong> This SDS has expired and needs immediate replacement!
                </div>
"""
        elif priority_level == "medium" and date_result and date_result.days_until_expiry and 0 < date_result.days_until_expiry <= 90:
            card_html += f"""
                <div class="priority-medium">
                    <strong>⚠️ ACTION NEEDED:</strong> This SDS expires in {date_result.days_until_expiry} days. Plan for renewal.
                </div>
"""

        card_html += "</div>"
        return card_html, priority_level

    # Overview tab
    html_content += """
        <div id="overview" class="tab-content active">
            <h2>📊 Analysis Summary</h2>
            <div class="file-list">
"""

    # Show top issues first
    all_files = []
    for filename in sds_results:
        sds_result = sds_results[filename]
        date_result = date_results.get(filename)
        card_html, priority = create_file_card(filename, sds_result, date_result)
        all_files.append((filename, card_html, priority, sds_result, date_result))

    # Sort by priority (high -> medium -> low -> unknown)
    priority_order = {"high": 0, "medium": 1, "low": 2, "unknown": 3}
    all_files.sort(key=lambda x: (priority_order[x[2]], x[0]))

    # Show first 10 files in overview
    for filename, card_html, priority, sds_result, date_result in all_files[:10]:
        html_content += card_html

    html_content += """
            </div>
        </div>
"""

    # Critical Issues tab
    critical_files = [f for f in all_files if f[2] == "high"]
    html_content += f"""
        <div id="critical" class="tab-content">
            <h2>🚨 Critical Issues ({len(critical_files)})</h2>
            <p>These SDS files are expired and require immediate attention:</p>
            <div class="file-list">
"""
    for filename, card_html, priority, sds_result, date_result in critical_files:
        html_content += card_html
    html_content += """
            </div>
        </div>
"""

    # Action Needed tab
    action_files = [f for f in all_files if f[2] == "medium"]
    html_content += f"""
        <div id="action-needed" class="tab-content">
            <h2>⚠️ Action Needed ({len(action_files)})</h2>
            <p>These files need attention soon (expiring within 90 days or missing dates):</p>
            <div class="file-list">
"""
    for filename, card_html, priority, sds_result, date_result in action_files:
        html_content += card_html
    html_content += """
            </div>
        </div>
"""

    # All Files tab
    html_content += f"""
        <div id="all-files" class="tab-content">
            <h2>📋 All Files ({len(all_files)})</h2>
            <div class="file-list">
"""
    for filename, card_html, priority, sds_result, date_result in all_files:
        html_content += card_html
    html_content += """
            </div>
        </div>
"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_content += f"""
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; color: #666; font-size: 0.9em;">
            Report generated on {timestamp}
        </div>
    </div>
</body>
</html>
"""

    # Save HTML report
    html_path = os.path.join(output_dir, "comprehensive_sds_analysis.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path


def main():
    """Main comprehensive analysis function"""
    print("🔍📅 Starting Comprehensive SDS Analysis")
    print("=" * 60)
    
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sds_dir = os.path.join(script_dir, "sds")
    
    if not os.path.exists(sds_dir):
        print(f"❌ Error: SDS directory not found: {sds_dir}")
        return
    
    # Find all PDF files
    pdf_files = [f for f in os.listdir(sds_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ No PDF files found in: {sds_dir}")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files in: {sds_dir}")
    print()
    
    # Initialize detectors
    sds_detector = SDSDetector()
    date_detector = SDSDateDetector()
    
    sds_results = {}
    date_results = {}
    
    # Process each file
    for i, filename in enumerate(pdf_files, 1):
        pdf_path = os.path.join(sds_dir, filename)
        print(f"🔍 [{i}/{len(pdf_files)}] Analyzing: {filename}")
        
        try:
            # SDS Detection
            sds_result = create_enhanced_sds_score(pdf_path, sds_detector)
            sds_results[filename] = sds_result
            
            # Date Detection
            date_result = date_detector.detect_dates(pdf_path)
            date_results[filename] = date_result
            
            # Show quick summary with language and scanned status
            if sds_result.is_likely_sds is None:  # Scanned document
                sds_status = "❓ Unknown (Scanned)"
                lang_info = "🔍 Scanned"
            elif sds_result.is_likely_sds:
                sds_status = "✅ SDS"
                lang_info = f"🌐 {sds_result.language_detected}"
            else:
                sds_status = "❌ Non-SDS"
                lang_info = f"🌐 {sds_result.language_detected}"
            
            date_status = date_result.validity_status if date_result.primary_issue_date else "No date"
            
            print(f"    {sds_status} ({sds_result.total_score}/100) | {lang_info} | 📅 {date_status}")
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            # Create error results
            sds_results[filename] = SDSScore(
                total_score=0,
                is_likely_sds=False,
                confidence_level="Error",
                breakdown={},
                detected_features=[f"Processing error: {str(e)}"],
                language_detected="Unknown"
            )
            date_results[filename] = SDSDateResult(
                filename=filename,
                primary_issue_date=None,
                all_dates_found=[],
                is_valid=False,
                days_until_expiry=None,
                expiry_date=None,
                validity_status="Processing error",
                confidence_score=0.0,
                detection_notes=[f"Error: {str(e)}"]
            )
    
    print()
    print("📊 Analysis Complete - Generating Comprehensive Report")
    print("-" * 60)
    
    # Generate combined statistics
    valid_sds = [f for f, r in sds_results.items() if r.is_likely_sds is True]
    invalid_sds = [f for f, r in sds_results.items() if r.is_likely_sds is False]
    scanned_docs = [f for f, r in sds_results.items() if r.is_likely_sds is None]
    valid_dates = [f for f, r in date_results.items() if r.is_valid]
    expired_dates = [f for f, r in date_results.items() if r.primary_issue_date and not r.is_valid]
    
    # Language breakdown
    language_counts = {}
    for filename, result in sds_results.items():
        lang = result.language_detected
        language_counts[lang] = language_counts.get(lang, 0) + 1
    
    # Critical analysis (only for valid SDS files)
    critical_issues = []
    action_needed = []
    
    for filename in valid_sds:
        date_result = date_results.get(filename)
        if date_result and date_result.primary_issue_date and not date_result.is_valid:
            critical_issues.append(filename)
        elif date_result and date_result.days_until_expiry and 0 < date_result.days_until_expiry <= 90:
            action_needed.append(filename)
    
    print(f"📋 Analysis Summary:")
    print(f"   Total files: {len(pdf_files)}")
    print(f"   ✅ Valid SDS: {len(valid_sds)}")
    print(f"   ❌ Non-SDS: {len(invalid_sds)}")
    print(f"   ❓ Scanned/Unknown: {len(scanned_docs)}")
    print(f"   📅 Valid dates: {len(valid_dates)}")
    print(f"   🚨 Critical issues (expired SDS): {len(critical_issues)}")
    print(f"   ⚠️  Action needed (expiring soon): {len(action_needed)}")
    
    if language_counts:
        print(f"\n🌐 Language Breakdown:")
        for lang, count in sorted(language_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {lang}: {count} files")
    
    if critical_issues:
        print(f"\n🚨 CRITICAL - Expired SDS files:")
        for filename in critical_issues:
            date_result = date_results[filename]
            print(f"   📄 {filename}: Expired {abs(date_result.days_until_expiry)} days ago")
    
    if action_needed:
        print(f"\n⚠️  ACTION NEEDED - Expiring soon:")
        for filename in action_needed:
            date_result = date_results[filename]
            print(f"   📄 {filename}: Expires in {date_result.days_until_expiry} days")
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(script_dir, f"comprehensive_sds_analysis_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save combined JSON results
    combined_data = {}
    for filename in sds_results:
        sds_result = sds_results[filename]
        date_result = date_results.get(filename)
        
        combined_data[filename] = {
            'sds_detection': {
                'score': sds_result.total_score,
                'is_sds': sds_result.is_likely_sds,  # Can be True, False, or None (scanned)
                'confidence': sds_result.confidence_level,
                'language': sds_result.language_detected,
                'breakdown': sds_result.breakdown,
                'is_scanned': sds_result.is_likely_sds is None
            },
            'date_validation': {
                'primary_issue_date': date_result.primary_issue_date.isoformat() if date_result and date_result.primary_issue_date else None,
                'is_valid': date_result.is_valid if date_result else False,
                'days_until_expiry': date_result.days_until_expiry if date_result else None,
                'validity_status': date_result.validity_status if date_result else "No analysis",
                'confidence_score': date_result.confidence_score if date_result else 0.0
            }
        }
    
    json_path = os.path.join(output_dir, "comprehensive_analysis.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    
    # Create comprehensive HTML report
    html_path = create_combined_html_report(sds_results, date_results, output_dir)
    
    # Create CSV summary
    csv_path = os.path.join(output_dir, "comprehensive_summary.csv")
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("Filename,SDS_Score,Is_SDS,Is_Scanned,Language,SDS_Confidence,Issue_Date,Date_Valid,Days_Until_Expiry,Status\n")
        for filename in sorted(sds_results.keys()):
            sds_result = sds_results[filename]
            date_result = date_results.get(filename)
            
            issue_date_str = date_result.primary_issue_date.strftime('%d.%m.%Y') if date_result and date_result.primary_issue_date else ""
            is_scanned = sds_result.is_likely_sds is None
            
            f.write(f'"{filename}",{sds_result.total_score},{sds_result.is_likely_sds},{is_scanned},')
            f.write(f'"{sds_result.language_detected}","{sds_result.confidence_level}","{issue_date_str}",')
            f.write(f'{date_result.is_valid if date_result else False},')
            f.write(f'{date_result.days_until_expiry if date_result else ""},')
            f.write(f'"{date_result.validity_status if date_result else "No analysis"}"\n')
    
    print(f"\n📁 Comprehensive reports saved to: {output_dir}")
    print(f"   🌐 HTML Report: {os.path.basename(html_path)}")
    print(f"   📄 JSON Data: {os.path.basename(json_path)}")
    print(f"   📊 CSV Summary: {os.path.basename(csv_path)}")
    
    print(f"\n🎉 Comprehensive analysis complete!")
    if critical_issues:
        print(f"⚠️  WARNING: {len(critical_issues)} SDS files have expired and need immediate replacement!")
    if action_needed:
        print(f"📅 NOTE: {len(action_needed)} SDS files will expire within 90 days.")


if __name__ == "__main__":
    main() 