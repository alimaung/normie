#!/usr/bin/env python3
"""
PDF Structure Analyzer - Verifies true incremental saves
This script analyzes the binary structure of PDF files to determine if 
incremental saves are truly appending content after the original EOF.
"""

import os
import sys
import re
from typing import List, Dict, Tuple

class PDFStructureAnalyzer:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.file_size = os.path.getsize(pdf_path)
        self.pdf_data = None
        self.load_pdf_data()
    
    def load_pdf_data(self):
        """Load the entire PDF file into memory for analysis."""
        try:
            with open(self.pdf_path, 'rb') as f:
                self.pdf_data = f.read()
            print(f"✅ Loaded PDF: {os.path.basename(self.pdf_path)} ({self.file_size:,} bytes)")
        except Exception as e:
            print(f"❌ Error loading PDF: {e}")
            self.pdf_data = None
    
    def find_pdf_header(self) -> Tuple[int, str]:
        """Find the PDF header (%PDF-x.x)."""
        if not self.pdf_data:
            return -1, ""
        
        # Look for PDF header pattern
        header_pattern = rb'%PDF-(\d+\.\d+)'
        match = re.search(header_pattern, self.pdf_data)
        
        if match:
            position = match.start()
            version = match.group(1).decode('ascii')
            return position, version
        return -1, ""
    
    def find_eof_markers(self) -> List[Tuple[int, str]]:
        """Find all %%EOF markers in the PDF."""
        if not self.pdf_data:
            return []
        
        eof_markers = []
        pattern = rb'%%EOF'
        
        start = 0
        while True:
            pos = self.pdf_data.find(pattern, start)
            if pos == -1:
                break
            
            # Get some context around the EOF marker
            context_start = max(0, pos - 20)
            context_end = min(len(self.pdf_data), pos + 30)
            context = self.pdf_data[context_start:context_end]
            
            eof_markers.append((pos, context.decode('latin-1', errors='replace')))
            start = pos + len(pattern)
        
        return eof_markers
    
    def find_xref_tables(self) -> List[Tuple[int, str]]:
        """Find all xref table locations."""
        if not self.pdf_data:
            return []
        
        xref_tables = []
        pattern = rb'xref\s*\n'
        
        start = 0
        while True:
            match = re.search(pattern, self.pdf_data[start:])
            if not match:
                break
            
            pos = start + match.start()
            
            # Get the xref table header (first few lines)
            lines_start = pos
            lines_end = min(len(self.pdf_data), pos + 100)
            header = self.pdf_data[lines_start:lines_end].decode('latin-1', errors='replace')
            
            xref_tables.append((pos, header.split('\n')[0:3]))
            start = pos + len(match.group())
        
        return xref_tables
    
    def find_trailer_objects(self) -> List[Tuple[int, str]]:
        """Find all trailer objects."""
        if not self.pdf_data:
            return []
        
        trailers = []
        pattern = rb'trailer\s*\n'
        
        start = 0
        while True:
            match = re.search(pattern, self.pdf_data[start:])
            if not match:
                break
            
            pos = start + match.start()
            
            # Get trailer content (up to next startxref or %%EOF)
            trailer_start = pos
            trailer_end = min(len(self.pdf_data), pos + 200)
            
            # Look for the end of trailer
            end_patterns = [b'startxref', b'%%EOF']
            for end_pattern in end_patterns:
                end_pos = self.pdf_data.find(end_pattern, trailer_start)
                if end_pos != -1 and end_pos < trailer_end:
                    trailer_end = end_pos
            
            trailer_content = self.pdf_data[trailer_start:trailer_end].decode('latin-1', errors='replace')
            trailers.append((pos, trailer_content))
            start = pos + len(match.group())
        
        return trailers
    
    def find_startxref_positions(self) -> List[Tuple[int, int]]:
        """Find all startxref positions and their values."""
        if not self.pdf_data:
            return []
        
        startxrefs = []
        pattern = rb'startxref\s*\n(\d+)'
        
        for match in re.finditer(pattern, self.pdf_data):
            pos = match.start()
            xref_offset = int(match.group(1))
            startxrefs.append((pos, xref_offset))
        
        return startxrefs
    
    def analyze_structure(self) -> Dict:
        """Perform complete PDF structure analysis."""
        if not self.pdf_data:
            return {}
        
        print(f"\n🔍 ANALYZING PDF STRUCTURE: {os.path.basename(self.pdf_path)}")
        print("=" * 80)
        
        # Find PDF header
        header_pos, pdf_version = self.find_pdf_header()
        print(f"📄 PDF Header:")
        print(f"   Position: {header_pos}")
        print(f"   Version: {pdf_version}")
        
        # Find EOF markers
        eof_markers = self.find_eof_markers()
        print(f"\n📍 EOF Markers Found: {len(eof_markers)}")
        for i, (pos, context) in enumerate(eof_markers):
            print(f"   EOF #{i+1}: Position {pos:,} ({pos/self.file_size*100:.1f}% through file)")
            print(f"   Context: {repr(context.strip())}")
        
        # Find xref tables
        xref_tables = self.find_xref_tables()
        print(f"\n📋 Cross-Reference Tables Found: {len(xref_tables)}")
        for i, (pos, header) in enumerate(xref_tables):
            print(f"   Xref #{i+1}: Position {pos:,}")
            print(f"   Header: {header}")
        
        # Find trailers
        trailers = self.find_trailer_objects()
        print(f"\n🚛 Trailer Objects Found: {len(trailers)}")
        for i, (pos, content) in enumerate(trailers):
            print(f"   Trailer #{i+1}: Position {pos:,}")
            print(f"   Content preview: {repr(content[:100])}...")
        
        # Find startxref positions
        startxrefs = self.find_startxref_positions()
        print(f"\n🎯 StartXref Positions Found: {len(startxrefs)}")
        for i, (pos, xref_offset) in enumerate(startxrefs):
            print(f"   StartXref #{i+1}: Position {pos:,}, Points to {xref_offset:,}")
        
        # Analyze incremental structure
        print(f"\n🔬 INCREMENTAL SAVE ANALYSIS:")
        
        if len(eof_markers) > 1:
            print(f"   ✅ Multiple EOF markers detected - likely incremental saves")
            
            # Calculate content between EOF markers
            for i in range(len(eof_markers) - 1):
                current_eof = eof_markers[i][0]
                next_eof = eof_markers[i+1][0]
                content_size = next_eof - current_eof
                
                print(f"   📦 Incremental Update #{i+1}:")
                print(f"      From EOF at {current_eof:,} to EOF at {next_eof:,}")
                print(f"      Content size: {content_size:,} bytes")
                print(f"      Percentage of file: {content_size/self.file_size*100:.1f}%")
                
                # Show a sample of the incremental content
                sample_start = current_eof + 10  # Skip the %%EOF marker
                sample_end = min(sample_start + 100, next_eof)
                if sample_start < sample_end:
                    sample = self.pdf_data[sample_start:sample_end]
                    print(f"      Content sample: {repr(sample[:50])}...")
        
        elif len(eof_markers) == 1:
            print(f"   ⚠️  Single EOF marker - likely not incremental")
            eof_pos = eof_markers[0][0]
            content_after_eof = self.file_size - eof_pos - 5  # 5 bytes for %%EOF
            if content_after_eof > 10:
                print(f"   📦 Content after EOF: {content_after_eof} bytes")
                sample = self.pdf_data[eof_pos+5:eof_pos+55]
                print(f"   Content sample: {repr(sample)}...")
        else:
            print(f"   ❌ No EOF markers found - corrupted PDF?")
        
        # Return structured data
        return {
            'file_size': self.file_size,
            'pdf_version': pdf_version,
            'header_position': header_pos,
            'eof_markers': eof_markers,
            'xref_tables': xref_tables,
            'trailers': trailers,
            'startxrefs': startxrefs,
            'is_incremental': len(eof_markers) > 1
        }

def compare_pdf_structures(original_path: str, modified_path: str):
    """Compare two PDF structures to verify incremental save behavior."""
    print(f"\n🔄 COMPARING PDF STRUCTURES")
    print("=" * 80)
    
    # Analyze original PDF
    print(f"📄 ORIGINAL PDF:")
    original_analyzer = PDFStructureAnalyzer(original_path)
    original_data = original_analyzer.analyze_structure()
    
    print(f"\n📄 MODIFIED PDF:")
    modified_analyzer = PDFStructureAnalyzer(modified_path)
    modified_data = modified_analyzer.analyze_structure()
    
    print(f"\n📊 COMPARISON RESULTS:")
    print("=" * 50)
    
    # Compare file sizes
    size_diff = modified_data['file_size'] - original_data['file_size']
    print(f"📏 File Size Comparison:")
    print(f"   Original: {original_data['file_size']:,} bytes")
    print(f"   Modified: {modified_data['file_size']:,} bytes")
    print(f"   Difference: {size_diff:,} bytes ({size_diff/original_data['file_size']*100:+.1f}%)")
    
    # Compare EOF markers
    print(f"\n📍 EOF Markers Comparison:")
    print(f"   Original: {len(original_data['eof_markers'])} EOF markers")
    print(f"   Modified: {len(modified_data['eof_markers'])} EOF markers")
    
    # Check if original content is preserved
    if original_analyzer.pdf_data and modified_analyzer.pdf_data:
        original_size = original_data['file_size']
        if len(modified_analyzer.pdf_data) >= original_size:
            # Check if the beginning of modified file matches original
            matches = modified_analyzer.pdf_data[:original_size] == original_analyzer.pdf_data
            print(f"\n🔍 Content Preservation Check:")
            print(f"   Original content preserved: {'✅ YES' if matches else '❌ NO'}")
            
            if not matches:
                # Find where they differ
                for i, (a, b) in enumerate(zip(original_analyzer.pdf_data, modified_analyzer.pdf_data)):
                    if a != b:
                        print(f"   First difference at byte {i:,} ({i/original_size*100:.1f}%)")
                        break
        else:
            print(f"\n🔍 Content Preservation Check:")
            print(f"   ❌ Modified file is smaller than original!")
    
    # Determine if it's a true incremental save
    print(f"\n🎯 INCREMENTAL SAVE VERDICT:")
    if (modified_data['is_incremental'] and 
        len(modified_data['eof_markers']) > len(original_data['eof_markers']) and
        size_diff > 0):
        print(f"   ✅ TRUE INCREMENTAL SAVE DETECTED")
        print(f"   📦 New content appended after original EOF")
    else:
        print(f"   ❌ NOT A TRUE INCREMENTAL SAVE")
        print(f"   🔄 File appears to be rewritten")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_structure_analyzer.py <pdf_path> [second_pdf_for_comparison]")
        print("\nExamples:")
        print("  python pdf_structure_analyzer.py document.pdf")
        print("  python pdf_structure_analyzer.py original.pdf modified.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if len(sys.argv) > 2:
        # Compare two PDFs
        second_pdf = sys.argv[2]
        compare_pdf_structures(pdf_path, second_pdf)
    else:
        # Analyze single PDF
        analyzer = PDFStructureAnalyzer(pdf_path)
        analyzer.analyze_structure()
    
    print(f"\n✅ Analysis complete!") 