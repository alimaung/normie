#!/usr/bin/env python3
"""
PDF Raw Structure Decoder
Converts PDF bytes to raw text to show pure PDF structure (/FT, /V, etc.)
"""

import sys
import os

def pdf_to_raw_text(pdf_path, output_path=None):
    """
    Convert PDF bytes to raw text showing pure PDF structure
    """
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        print(f"Processing PDF: {pdf_path}")
        print(f"File size: {len(pdf_bytes)} bytes")
        
        # Convert bytes to text using latin-1 encoding to preserve all bytes
        # This will show the raw PDF structure including /FT, /V, etc.
        raw_text = pdf_bytes.decode('latin-1', errors='ignore')
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(raw_text)
            print(f"Raw PDF structure saved to: {output_path}")
        else:
            # Print first 2000 characters to console
            print("\nRAW PDF STRUCTURE:")
            print("=" * 50)
            print(raw_text[:2000])
            if len(raw_text) > 2000:
                print(f"\n... (showing first 2000 chars of {len(raw_text)} total)")
        
        return raw_text
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdfparse.py <pdf_file> [output_file]")
        print("Example: python pdfparse.py document.pdf raw_structure.txt")
        return
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    # Convert PDF to raw text
    raw_text = pdf_to_raw_text(pdf_path, output_path)
    
    if raw_text and not output_path:
        # Show some statistics
        ft_count = raw_text.count('/FT')
        v_count = raw_text.count('/V')
        t_count = raw_text.count('/T')
        
        print(f"\nStructure elements found:")
        print(f"/FT (Field Type): {ft_count}")
        print(f"/V (Value): {v_count}")
        print(f"/T (Text/Title): {t_count}")

if __name__ == "__main__":
    main()
