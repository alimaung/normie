#!/usr/bin/env python3
"""
Comprehensive CAS Number Extraction Batch Script
Extracts CAS numbers from all SDS PDFs focusing on Section 3 (Composition/Information on Ingredients)
Generates detailed reports with substance identification and confidence scoring
Includes detection for scanned documents and validation of CAS number formats
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

# Add the current directory to path so we can import our detector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cas_extractor import CASExtractor, CASExtractionResult, CASMatch


def create_cas_html_report(cas_results: dict, output_dir: str) -> str:
    """Create a comprehensive HTML report for CAS number extraction"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive CAS Number Extraction Report</title>
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
        .file-card.high-cas { border-left: 5px solid #28a745; }
        .file-card.medium-cas { border-left: 5px solid #ffc107; }
        .file-card.low-cas { border-left: 5px solid #fd7e14; }
        .file-card.no-cas { border-left: 5px solid #dc3545; }
        .file-card.no-section3 { border-left: 5px solid #6c757d; }
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
        .status-badge.cas-found { background: #d4edda; color: #155724; }
        .status-badge.cas-none { background: #f8d7da; color: #721c24; }
        .status-badge.section3-found { background: #d4edda; color: #155724; }
        .status-badge.section3-missing { background: #f8d7da; color: #721c24; }
        .status-badge.confidence-high { background: #d4edda; color: #155724; }
        .status-badge.confidence-medium { background: #fff3cd; color: #856404; }
        .status-badge.confidence-low { background: #f8d7da; color: #721c24; }
        .details {
            font-size: 0.85em;
            line-height: 1.4;
        }
        .cas-list {
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .cas-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            padding: 5px;
            background: white;
            border-radius: 3px;
            font-size: 0.9em;
        }
        .cas-number {
            font-weight: bold;
            color: #007bff;
        }
        .cas-substance {
            color: #28a745;
        }
        .cas-concentration {
            color: #fd7e14;
        }
        .confidence {
            font-size: 1.2em;
            font-weight: bold;
            margin: 5px 0;
        }
        .confidence.high { color: #28a745; }
        .confidence.medium { color: #ffc107; }
        .confidence.low { color: #dc3545; }
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
        .cas-frequency {
            background: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .substance-list {
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .substance-item {
            margin-bottom: 3px;
            font-size: 0.9em;
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
            <h1>🧪📋 Comprehensive CAS Number Extraction Report</h1>
            <p>Chemical Abstracts Service Registry Numbers found in Safety Data Sheets</p>
        </div>
"""

    # Calculate statistics
    total_files = len(cas_results)
    files_with_cas = sum(1 for r in cas_results.values() if r.cas_numbers)
    files_with_section3 = sum(1 for r in cas_results.values() if r.section_3_found)
    total_cas_instances = sum(len(r.cas_numbers) for r in cas_results.values())
    total_unique_cas = len(set(match.cas_number for result in cas_results.values() for match in result.cas_numbers))
    
    # Confidence levels
    high_confidence_files = sum(1 for r in cas_results.values() if r.extraction_confidence >= 0.8)
    medium_confidence_files = sum(1 for r in cas_results.values() if 0.5 <= r.extraction_confidence < 0.8)
    low_confidence_files = sum(1 for r in cas_results.values() if 0 < r.extraction_confidence < 0.5)
    no_cas_files = sum(1 for r in cas_results.values() if r.extraction_confidence == 0)

    html_content += f"""
        <div class="summary">
            <div class="summary-card info">
                <h3>Total Files</h3>
                <div class="number">{total_files}</div>
            </div>
            <div class="summary-card good">
                <h3>Files with CAS</h3>
                <div class="number">{files_with_cas}</div>
            </div>
            <div class="summary-card info">
                <h3>CAS Instances</h3>
                <div class="number">{total_cas_instances}</div>
            </div>
            <div class="summary-card good">
                <h3>Unique CAS Numbers</h3>
                <div class="number">{total_unique_cas}</div>
            </div>
            <div class="summary-card warning">
                <h3>Section 3 Found</h3>
                <div class="number">{files_with_section3}</div>
            </div>
            <div class="summary-card good">
                <h3>High Confidence</h3>
                <div class="number">{high_confidence_files}</div>
            </div>
        </div>
"""

    # CAS frequency analysis
    cas_counter = Counter()
    substance_counter = Counter()
    for result in cas_results.values():
        for match in result.cas_numbers:
            cas_counter[match.cas_number] += 1
            if match.substance_name:
                substance_counter[match.substance_name] += 1

    # Create tabs
    html_content += """
        <div class="tabs">
            <div class="tab active" onclick="showTab('overview')">Overview</div>
            <div class="tab" onclick="showTab('cas-frequency')">CAS Frequency</div>
            <div class="tab" onclick="showTab('high-confidence')">High Confidence</div>
            <div class="tab" onclick="showTab('all-files')">All Files</div>
        </div>
"""

    def create_file_card(filename, result):
        # Determine card class based on results
        if not result.cas_numbers:
            if not result.section_3_found:
                card_class = "no-section3"
                status_class = "No Section 3"
            else:
                card_class = "no-cas"
                status_class = "No CAS Found"
        elif result.extraction_confidence >= 0.8:
            card_class = "high-cas"
            status_class = "High Confidence"
        elif result.extraction_confidence >= 0.5:
            card_class = "medium-cas"
            status_class = "Medium Confidence"
        else:
            card_class = "low-cas"
            status_class = "Low Confidence"

        confidence_class = "high" if result.extraction_confidence >= 0.8 else "medium" if result.extraction_confidence >= 0.5 else "low"
        
        card_html = f"""
            <div class="file-card {card_class}">
                <div class="file-name">{filename}</div>
                
                <div class="status-grid">
                    <div class="status-section">
                        <h4>CAS Extraction</h4>
                        <div class="status-badge {'cas-found' if result.cas_numbers else 'cas-none'}">
                            {'✅' if result.cas_numbers else '❌'} {len(result.cas_numbers)} CAS ({result.unique_cas_count} unique)
                        </div>
                        <div class="confidence {confidence_class}">{result.extraction_confidence:.2f}</div>
                        <div class="details">
                            Status: {status_class}
                        </div>
                    </div>
                    
                    <div class="status-section">
                        <h4>Document Structure</h4>
                        <div class="status-badge {'section3-found' if result.section_3_found else 'section3-missing'}">
                            {'✅ Section 3 Found' if result.section_3_found else '❌ Section 3 Missing'}
                        </div>
                        <div class="details">
                            Substances: {len(result.detected_substances)}<br>
                            Notes: {len(result.extraction_notes)}
                        </div>
                    </div>
                </div>
"""
        
        # Add CAS numbers if found
        if result.cas_numbers:
            card_html += """
                <div class="cas-list">
                    <strong>🧪 CAS Numbers Found:</strong>
"""
            for match in result.cas_numbers:
                substance_info = f"<span class='cas-substance'>{match.substance_name}</span>" if match.substance_name else ""
                concentration_info = f"<span class='cas-concentration'>{match.concentration}</span>" if match.concentration else ""
                
                card_html += f"""
                    <div class="cas-item">
                        <span class="cas-number">{match.cas_number}</span>
                        <span>{substance_info} {concentration_info}</span>
                    </div>
"""
            card_html += "</div>"
        
        # Add detected substances if any
        if result.detected_substances:
            card_html += """
                <div class="substance-list">
                    <strong>🔬 Detected Substances:</strong><br>
"""
            for substance in result.detected_substances:
                card_html += f"<div class='substance-item'>• {substance}</div>"
            card_html += "</div>"

        card_html += "</div>"
        return card_html

    # Overview tab
    html_content += """
        <div id="overview" class="tab-content active">
            <h2>📊 Extraction Overview</h2>
            <div class="file-list">
"""

    # Show files sorted by confidence and CAS count
    all_files = [(filename, result) for filename, result in cas_results.items()]
    all_files.sort(key=lambda x: (len(x[1].cas_numbers), x[1].extraction_confidence), reverse=True)

    # Show first 15 files in overview
    for filename, result in all_files[:15]:
        card_html = create_file_card(filename, result)
        html_content += card_html

    html_content += """
            </div>
        </div>
"""

    # CAS Frequency tab
    html_content += f"""
        <div id="cas-frequency" class="tab-content">
            <h2>📈 CAS Number Frequency Analysis</h2>
            
            <div class="cas-frequency">
                <h3>🧪 Most Common CAS Numbers</h3>
"""
    
    for cas_number, count in cas_counter.most_common(20):
        html_content += f"""
                <div class="cas-item">
                    <span class="cas-number">{cas_number}</span>
                    <span>Found in {count} file{'s' if count > 1 else ''}</span>
                </div>
"""
    
    html_content += """
            </div>
            
            <div class="cas-frequency">
                <h3>🔬 Most Common Substances</h3>
"""
    
    for substance, count in substance_counter.most_common(15):
        html_content += f"""
                <div class="substance-item">• <strong>{substance}</strong> - {count} occurrence{'s' if count > 1 else ''}</div>
"""
    
    html_content += """
            </div>
        </div>
"""

    # High Confidence tab
    high_confidence_files = [f for f in all_files if f[1].extraction_confidence >= 0.8 or len(f[1].cas_numbers) > 0]
    html_content += f"""
        <div id="high-confidence" class="tab-content">
            <h2>✅ High Confidence Results ({len(high_confidence_files)})</h2>
            <p>Files with successful CAS number extraction:</p>
            <div class="file-list">
"""
    for filename, result in high_confidence_files:
        card_html = create_file_card(filename, result)
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
    for filename, result in all_files:
        card_html = create_file_card(filename, result)
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
    html_path = os.path.join(output_dir, "cas_extraction_analysis.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path


def main():
    """Main comprehensive CAS extraction function"""
    print("🧪📋 Starting Comprehensive CAS Number Extraction")
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
    
    # Initialize CAS extractor
    cas_extractor = CASExtractor()
    
    cas_results = {}
    
    # Process each file
    for i, filename in enumerate(pdf_files, 1):
        pdf_path = os.path.join(sds_dir, filename)
        print(f"🧪 [{i}/{len(pdf_files)}] Extracting from: {filename}")
        
        try:
            # CAS Extraction
            cas_result = cas_extractor.extract_cas_numbers(pdf_path)
            cas_results[filename] = cas_result
            
            # Show quick summary
            section3_status = "✅ Section 3" if cas_result.section_3_found else "❌ No Section 3"
            cas_status = f"🧪 {len(cas_result.cas_numbers)} CAS ({cas_result.unique_cas_count} unique)" if cas_result.cas_numbers else "❌ No CAS"
            confidence_status = f"📊 {cas_result.extraction_confidence:.2f}"
            
            print(f"    {section3_status} | {cas_status} | {confidence_status}")
            
            # Show CAS numbers found
            if cas_result.cas_numbers:
                for match in cas_result.cas_numbers[:3]:  # Show first 3
                    substance_info = f" ({match.substance_name})" if match.substance_name else ""
                    concentration_info = f" - {match.concentration}" if match.concentration else ""
                    print(f"      • {match.cas_number}{substance_info}{concentration_info}")
                if len(cas_result.cas_numbers) > 3:
                    print(f"      ... and {len(cas_result.cas_numbers) - 3} more")
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            # Create error result
            cas_results[filename] = CASExtractionResult(
                filename=filename,
                cas_numbers=[],
                unique_cas_count=0,
                section_3_found=False,
                extraction_confidence=0.0,
                extraction_notes=[f"Processing error: {str(e)}"],
                detected_substances=[]
            )
    
    print()
    print("📊 Extraction Complete - Generating Comprehensive Report")
    print("-" * 60)
    
    # Generate comprehensive statistics
    files_with_cas = [f for f, r in cas_results.items() if r.cas_numbers]
    files_without_cas = [f for f, r in cas_results.items() if not r.cas_numbers]
    files_with_section3 = [f for f, r in cas_results.items() if r.section_3_found]
    
    # CAS analysis
    all_cas_matches = []
    unique_cas_numbers = set()
    all_substances = set()
    
    for result in cas_results.values():
        all_cas_matches.extend(result.cas_numbers)
        unique_cas_numbers.update(match.cas_number for match in result.cas_numbers)
        all_substances.update(result.detected_substances)
    
    # Most common CAS numbers
    cas_frequency = Counter(match.cas_number for match in all_cas_matches)
    substance_frequency = Counter(match.substance_name for match in all_cas_matches if match.substance_name)
    
    print(f"📋 Extraction Summary:")
    print(f"   Total files: {len(pdf_files)}")
    print(f"   ✅ Files with CAS numbers: {len(files_with_cas)}")
    print(f"   ❌ Files without CAS numbers: {len(files_without_cas)}")
    print(f"   📄 Files with Section 3: {len(files_with_section3)}")
    print(f"   🧪 Total CAS instances: {len(all_cas_matches)}")
    print(f"   🔬 Unique CAS numbers: {len(unique_cas_numbers)}")
    print(f"   ⚗️  Detected substances: {len(all_substances)}")
    
    if cas_frequency:
        print(f"\n🧪 Most Common CAS Numbers:")
        for cas_number, count in cas_frequency.most_common(10):
            print(f"   {cas_number}: {count} occurrence{'s' if count > 1 else ''}")
    
    if substance_frequency:
        print(f"\n🔬 Most Common Substances:")
        for substance, count in substance_frequency.most_common(5):
            print(f"   {substance}: {count} occurrence{'s' if count > 1 else ''}")
    
    # Files with most CAS numbers
    files_by_cas_count = sorted(
        [(f, r) for f, r in cas_results.items() if r.cas_numbers],
        key=lambda x: len(x[1].cas_numbers),
        reverse=True
    )
    
    if files_by_cas_count:
        print(f"\n🏆 Files with Most CAS Numbers:")
        for filename, result in files_by_cas_count[:5]:
            print(f"   📄 {filename}: {len(result.cas_numbers)} CAS numbers")
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(script_dir, f"cas_extraction_analysis_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save JSON results
    json_data = {}
    for filename, result in cas_results.items():
        json_data[filename] = {
            'cas_numbers': [
                {
                    'cas_number': match.cas_number,
                    'substance_name': match.substance_name,
                    'concentration': match.concentration,
                    'confidence': match.confidence,
                    'context_phrase': match.context_phrase,
                    'line_number': match.line_number,
                    'section': match.section
                } for match in result.cas_numbers
            ],
            'unique_cas_count': result.unique_cas_count,
            'section_3_found': result.section_3_found,
            'extraction_confidence': result.extraction_confidence,
            'extraction_notes': result.extraction_notes,
            'detected_substances': result.detected_substances
        }
    
    json_path = os.path.join(output_dir, "cas_extraction_results.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    # Create HTML report
    html_path = create_cas_html_report(cas_results, output_dir)
    
    # Create CSV summary
    csv_path = os.path.join(output_dir, "cas_extraction_summary.csv")
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("Filename,CAS_Count,Unique_CAS_Count,Section_3_Found,Extraction_Confidence,Detected_Substances,CAS_Numbers\n")
        for filename in sorted(cas_results.keys()):
            result = cas_results[filename]
            cas_numbers_str = "; ".join([match.cas_number for match in result.cas_numbers])
            substances_str = "; ".join(result.detected_substances)
            
            f.write(f'"{filename}",{len(result.cas_numbers)},{result.unique_cas_count},')
            f.write(f'{result.section_3_found},{result.extraction_confidence:.3f},')
            f.write(f'"{substances_str}","{cas_numbers_str}"\n')
    
    # Create detailed CAS registry
    registry_path = os.path.join(output_dir, "cas_registry.csv")
    with open(registry_path, 'w', encoding='utf-8') as f:
        f.write("CAS_Number,Substance_Name,Concentration,Confidence,Context,Filename,Line_Number,Section\n")
        for filename, result in cas_results.items():
            for match in result.cas_numbers:
                f.write(f'"{match.cas_number}","{match.substance_name or ""}",')
                f.write(f'"{match.concentration or ""}",{match.confidence:.3f},')
                f.write(f'"{match.context_phrase}","{filename}",')
                f.write(f'{match.line_number or ""},"{match.section or ""}"\n')
    
    print(f"\n📁 Comprehensive reports saved to: {output_dir}")
    print(f"   🌐 HTML Report: {os.path.basename(html_path)}")
    print(f"   📄 JSON Data: {os.path.basename(json_path)}")
    print(f"   📊 CSV Summary: {os.path.basename(csv_path)}")
    print(f"   🧪 CAS Registry: {os.path.basename(registry_path)}")
    
    print(f"\n🎉 CAS extraction analysis complete!")
    if files_with_cas:
        print(f"✅ Successfully extracted CAS numbers from {len(files_with_cas)}/{len(pdf_files)} files")
        print(f"🧪 Total unique CAS numbers found: {len(unique_cas_numbers)}")
    else:
        print(f"⚠️  No CAS numbers found in any files. Check Section 3 detection and PDF text extraction.")


if __name__ == "__main__":
    main() 