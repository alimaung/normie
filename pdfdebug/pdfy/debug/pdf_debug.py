#!/usr/bin/env python3
"""
PDF Debug Script - Raw Structure Analysis

This script analyzes the raw bytes of a PDF file to understand its structure
and help debug parsing issues.
"""

import os
import re
from typing import List, Dict, Any


def analyze_pdf_structure(pdf_path: str):
    """Analyze the raw structure of a PDF file."""
    print(f"🔍 PDF Debug Analysis")
    print(f"📄 File: {pdf_path}")
    print("=" * 60)
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    print(f"📊 File size: {len(pdf_data):,} bytes")
    
    # 1. Check PDF header
    print(f"\n1. PDF HEADER:")
    print(f"   First 20 bytes: {pdf_data[:20]}")
    print(f"   As text: {pdf_data[:20].decode('ascii', errors='ignore')}")
    
    # 2. Check PDF footer/trailer area
    print(f"\n2. PDF FOOTER/TRAILER AREA:")
    footer_size = min(1000, len(pdf_data))
    footer_data = pdf_data[-footer_size:]
    print(f"   Last {footer_size} bytes:")
    print(f"   Raw: {footer_data}")
    print(f"   As text: {footer_data.decode('ascii', errors='ignore')}")
    
    # 3. Look for key PDF keywords
    print(f"\n3. PDF KEYWORDS SEARCH:")
    keywords = [
        b'%%EOF',
        b'startxref',
        b'trailer',
        b'xref',
        b'obj',
        b'endobj',
        b'AcroForm',
        b'/FT',
        b'/T',
        b'/Root'
    ]
    
    for keyword in keywords:
        matches = list(re.finditer(re.escape(keyword), pdf_data))
        print(f"   '{keyword.decode()}': {len(matches)} occurrences")
        
        if matches:
            # Show first and last occurrence
            first_match = matches[0]
            last_match = matches[-1]
            
            print(f"      First at byte {first_match.start()}")
            if len(matches) > 1:
                print(f"      Last at byte {last_match.start()}")
            
            # Show context around last match for important keywords
            if keyword in [b'%%EOF', b'startxref', b'trailer']:
                start = max(0, last_match.start() - 50)
                end = min(len(pdf_data), last_match.end() + 50)
                context = pdf_data[start:end]
                print(f"      Context: {context.decode('ascii', errors='ignore')}")
    
    # 4. Look for trailer patterns
    print(f"\n4. TRAILER PATTERN ANALYSIS:")
    
    # Pattern 1: Standard trailer
    pattern1 = rb'trailer\s*<<.*?>>\s*startxref\s*\d+\s*%%EOF'
    matches1 = list(re.finditer(pattern1, pdf_data, re.DOTALL))
    print(f"   Standard trailer pattern: {len(matches1)} matches")
    
    # Pattern 2: Just startxref + number + EOF
    pattern2 = rb'startxref\s*(\d+)\s*%%EOF'
    matches2 = list(re.finditer(pattern2, pdf_data))
    print(f"   StartXRef pattern: {len(matches2)} matches")
    
    if matches2:
        for i, match in enumerate(matches2):
            offset = int(match.group(1))
            print(f"      Match {i+1}: XRef offset = {offset}")
    
    # Pattern 3: trailer keyword
    pattern3 = rb'trailer\s*<<'
    matches3 = list(re.finditer(pattern3, pdf_data))
    print(f"   Trailer keyword: {len(matches3)} matches")
    
    # 5. Manual trailer search
    print(f"\n5. MANUAL TRAILER SEARCH:")
    
    # Find all %%EOF
    eof_matches = list(re.finditer(rb'%%EOF', pdf_data))
    print(f"   Found {len(eof_matches)} %%EOF markers")
    
    for i, eof_match in enumerate(eof_matches):
        print(f"\n   %%EOF #{i+1} at byte {eof_match.start()}:")
        
        # Look backwards for startxref
        search_start = max(0, eof_match.start() - 200)
        search_area = pdf_data[search_start:eof_match.start()]
        
        startxref_match = re.search(rb'startxref\s*(\d+)', search_area)
        if startxref_match:
            xref_offset = int(startxref_match.group(1))
            print(f"      Found startxref: {xref_offset}")
            
            # Look for trailer before startxref
            trailer_search = pdf_data[search_start:search_start + startxref_match.start()]
            trailer_match = re.search(rb'trailer\s*<<', trailer_search)
            if trailer_match:
                print(f"      Found trailer keyword")
                
                # Extract trailer content
                trailer_start = search_start + trailer_match.start()
                trailer_end = search_start + startxref_match.start()
                trailer_content = pdf_data[trailer_start:trailer_end]
                print(f"      Trailer content: {trailer_content.decode('ascii', errors='ignore')}")
            else:
                print(f"      No trailer keyword found")
        else:
            print(f"      No startxref found before this %%EOF")
    
    # 6. XRef table analysis
    print(f"\n6. XREF TABLE ANALYSIS:")
    
    # Find all xref keywords
    xref_matches = list(re.finditer(rb'xref\s*\n', pdf_data))
    print(f"   Found {len(xref_matches)} xref tables")
    
    for i, xref_match in enumerate(xref_matches):
        print(f"\n   XRef #{i+1} at byte {xref_match.start()}:")
        
        # Show some content after xref
        content_start = xref_match.end()
        content_end = min(len(pdf_data), content_start + 200)
        content = pdf_data[content_start:content_end]
        
        print(f"      Content after xref: {content.decode('ascii', errors='ignore')}")
    
    # 7. Object scanning
    print(f"\n7. OBJECT SCANNING:")
    
    obj_pattern = rb'(\d+)\s+(\d+)\s+obj\b'
    obj_matches = list(re.finditer(obj_pattern, pdf_data))
    print(f"   Found {len(obj_matches)} objects")
    
    if obj_matches:
        # Show first few objects
        for i, match in enumerate(obj_matches[:5]):
            obj_num = int(match.group(1))
            gen_num = int(match.group(2))
            print(f"      Object {obj_num} gen {gen_num} at byte {match.start()}")
        
        if len(obj_matches) > 5:
            print(f"      ... and {len(obj_matches) - 5} more objects")
    
    # 8. Form field scanning
    print(f"\n8. FORM FIELD SCANNING:")
    
    # Look for AcroForm references
    acroform_matches = list(re.finditer(rb'/AcroForm\s+(\d+)\s+\d+\s+R', pdf_data))
    print(f"   AcroForm references: {len(acroform_matches)}")
    
    for match in acroform_matches:
        acroform_ref = int(match.group(1))
        print(f"      AcroForm object: {acroform_ref}")
    
    # Look for field type indicators
    field_indicators = [
        (b'/FT/Tx', 'Text fields'),
        (b'/FT/Btn', 'Button fields'),
        (b'/FT/Ch', 'Choice fields'),
        (b'/FT/Sig', 'Signature fields'),
        (b'/T(', 'Field names'),
        (b'/V(', 'Field values')
    ]
    
    for indicator, description in field_indicators:
        matches = list(re.finditer(re.escape(indicator), pdf_data))
        print(f"   {description}: {len(matches)} occurrences")
        
        if matches and len(matches) <= 5:
            for match in matches:
                # Show context
                start = max(0, match.start() - 20)
                end = min(len(pdf_data), match.end() + 20)
                context = pdf_data[start:end]
                print(f"      Context: {context.decode('ascii', errors='ignore')}")
    
    print(f"\n{'='*60}")
    print("🔍 Debug analysis complete!")
    print("💡 Use this information to fix the PDF parser")


def main():
    """Main function."""
    pdf_file = "pdf.pdf"
    
    if len(os.sys.argv) > 1:
        pdf_file = os.sys.argv[1]
    
    analyze_pdf_structure(pdf_file)


if __name__ == "__main__":
    main() 