#!/usr/bin/env python3
"""
Batch SDS Detection Script
Runs SDS detection on all PDFs in the sds folder and generates comprehensive reports
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add the current directory to path so we can import sds_detector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sds_detector import SDSDetector, SDSScore


def create_html_report(results: dict, output_dir: str):
    """Create an HTML report of the SDS detection results"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SDS Detection Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
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
            border-left: 4px solid #007bff;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .summary-card .number {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .file-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }
        .file-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: white;
        }
        .file-card.sds {
            border-left: 5px solid #28a745;
        }
        .file-card.non-sds {
            border-left: 5px solid #dc3545;
        }
        .file-card.uncertain {
            border-left: 5px solid #ffc107;
        }
        .file-name {
            font-weight: bold;
            margin-bottom: 10px;
            word-break: break-all;
        }
        .score {
            font-size: 1.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        .score.high { color: #28a745; }
        .score.medium { color: #ffc107; }
        .score.low { color: #dc3545; }
        .details {
            margin-top: 15px;
        }
        .details table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .details th, .details td {
            padding: 5px 10px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .details th {
            background: #f8f9fa;
            font-weight: bold;
        }
        .confidence {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .confidence.very-high { background: #d4edda; color: #155724; }
        .confidence.high { background: #d4edda; color: #155724; }
        .confidence.medium { background: #fff3cd; color: #856404; }
        .confidence.low { background: #f8d7da; color: #721c24; }
        .confidence.very-low { background: #f8d7da; color: #721c24; }
        .language {
            display: inline-block;
            padding: 2px 6px;
            background: #e9ecef;
            border-radius: 4px;
            font-size: 0.8em;
        }
        .features {
            margin-top: 10px;
            max-height: 100px;
            overflow-y: auto;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            font-size: 0.85em;
        }
        .timestamp {
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 SDS Detection Report</h1>
            <p>Analysis of PDF documents for Safety Data Sheet compliance</p>
        </div>
"""

    # Calculate summary statistics
    total_files = len(results)
    sds_files = sum(1 for r in results.values() if r.is_likely_sds)
    high_confidence = sum(1 for r in results.values() if r.total_score >= 70)
    avg_score = sum(r.total_score for r in results.values()) / total_files if total_files > 0 else 0

    html_content += f"""
        <div class="summary">
            <div class="summary-card">
                <h3>Total Files</h3>
                <div class="number">{total_files}</div>
            </div>
            <div class="summary-card">
                <h3>Likely SDS</h3>
                <div class="number">{sds_files}</div>
            </div>
            <div class="summary-card">
                <h3>High Confidence</h3>
                <div class="number">{high_confidence}</div>
            </div>
            <div class="summary-card">
                <h3>Average Score</h3>
                <div class="number">{avg_score:.1f}</div>
            </div>
        </div>
        
        <div class="file-grid">
"""

    # Sort files by score (highest first)
    sorted_results = sorted(results.items(), key=lambda x: x[1].total_score, reverse=True)

    for filename, result in sorted_results:
        # Determine card class based on score
        if result.total_score >= 70:
            card_class = "sds"
            score_class = "high"
        elif result.total_score >= 50:
            card_class = "uncertain"
            score_class = "medium"
        else:
            card_class = "non-sds"
            score_class = "low"

        confidence_class = result.confidence_level.lower().replace(' ', '-')

        html_content += f"""
            <div class="file-card {card_class}">
                <div class="file-name">{filename}</div>
                <div class="score {score_class}">{result.total_score}/100</div>
                <div>
                    <span class="confidence {confidence_class}">{result.confidence_level}</span>
                    <span class="language">{result.language_detected}</span>
                </div>
                
                <div class="details">
                    <table>
                        <tr><th>Category</th><th>Score</th></tr>
                        <tr><td>Keywords</td><td>{result.breakdown.get('keywords', 0)}</td></tr>
                        <tr><td>Structure</td><td>{result.breakdown.get('structure', 0)}</td></tr>
                        <tr><td>Format</td><td>{result.breakdown.get('format', 0)}</td></tr>
                    </table>
                </div>
                
                <div class="features">
                    <strong>Key Features:</strong><br>
"""

        # Show first 5 features
        for feature in result.detected_features[:5]:
            html_content += f"• {feature}<br>"
        
        if len(result.detected_features) > 5:
            html_content += f"... and {len(result.detected_features) - 5} more"

        html_content += """
                </div>
            </div>
"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_content += f"""
        </div>
        
        <div class="timestamp">
            Report generated on {timestamp}
        </div>
    </div>
</body>
</html>
"""

    # Save HTML report
    html_path = os.path.join(output_dir, "sds_detection_report.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path


def main():
    """Main batch processing function"""
    print("🔍 Starting SDS Batch Detection")
    print("=" * 50)
    
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
    
    # Initialize detector
    detector = SDSDetector()
    results = {}
    
    # Process each file
    for i, filename in enumerate(pdf_files, 1):
        pdf_path = os.path.join(sds_dir, filename)
        print(f"🔍 [{i}/{len(pdf_files)}] Processing: {filename}")
        
        try:
            result = detector.detect_sds(pdf_path)
            results[filename] = result
            
            # Show quick result
            status = "✅ SDS" if result.is_likely_sds else "❌ Non-SDS"
            print(f"    {status} - Score: {result.total_score}/100 ({result.confidence_level})")
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            # Create error result
            results[filename] = SDSScore(
                total_score=0,
                is_likely_sds=False,
                confidence_level="Error",
                breakdown={},
                detected_features=[f"Processing error: {str(e)}"],
                language_detected="Unknown"
            )
    
    print()
    print("📊 Processing Complete - Generating Reports")
    print("-" * 50)
    
    # Generate summary
    sds_files = [f for f, r in results.items() if r.is_likely_sds]
    non_sds_files = [f for f, r in results.items() if not r.is_likely_sds]
    
    print(f"✅ Likely SDS files: {len(sds_files)}")
    for filename in sorted(sds_files, key=lambda x: results[x].total_score, reverse=True):
        score = results[filename].total_score
        print(f"   📄 {filename}: {score}/100")
    
    print(f"\n❌ Non-SDS files: {len(non_sds_files)}")
    for filename in sorted(non_sds_files, key=lambda x: results[x].total_score, reverse=True):
        score = results[filename].total_score
        print(f"   📄 {filename}: {score}/100")
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(script_dir, f"sds_detection_results_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save detailed JSON results
    json_path = os.path.join(output_dir, "detailed_results.json")
    json_data = {}
    for filename, result in results.items():
        json_data[filename] = {
            'score': result.total_score,
            'is_sds': result.is_likely_sds,
            'confidence': result.confidence_level,
            'language': result.language_detected,
            'breakdown': result.breakdown,
            'features': result.detected_features
        }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    # Create CSV summary
    csv_path = os.path.join(output_dir, "summary.csv")
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("Filename,Score,Is_SDS,Confidence,Language,Keywords_Score,Structure_Score,Format_Score\n")
        for filename, result in sorted(results.items(), key=lambda x: x[1].total_score, reverse=True):
            f.write(f'"{filename}",{result.total_score},{result.is_likely_sds},"{result.confidence_level}",')
            f.write(f'"{result.language_detected}",{result.breakdown.get("keywords", 0)},')
            f.write(f'{result.breakdown.get("structure", 0)},{result.breakdown.get("format", 0)}\n')
    
    # Create HTML report
    html_path = create_html_report(results, output_dir)
    
    print(f"\n📁 Reports saved to: {output_dir}")
    print(f"   📄 JSON Details: {os.path.basename(json_path)}")
    print(f"   📊 CSV Summary: {os.path.basename(csv_path)}")
    print(f"   🌐 HTML Report: {os.path.basename(html_path)}")
    
    print(f"\n🎉 Batch processing complete!")
    print(f"   Total files processed: {len(results)}")
    print(f"   SDS detected: {len(sds_files)}")
    print(f"   Success rate: {len(sds_files)/len(results)*100:.1f}%")


if __name__ == "__main__":
    main() 