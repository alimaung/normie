#!/usr/bin/env python3
"""
PDF Text Extractor

A simple script to extract raw text from PDF files using PyMuPDF.
Supports both single file and batch processing modes.

Author: Generated for normie project
Dependencies: PyMuPDF
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, List

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF (fitz) is required. Install with: pip install PyMuPDF")
    sys.exit(1)


class PDFTextExtractor:
    """Simple PDF text extractor using PyMuPDF"""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the PDF text extractor
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
    
    def extract_text_from_file(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from a single PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            if self.verbose:
                print(f"Opening PDF: {pdf_path}")
            
            doc = fitz.open(pdf_path)
            text = ""
            
            if self.verbose:
                print(f"PDF has {len(doc)} pages")
            
            for page_num in range(len(doc)):
                if self.verbose:
                    print(f"Processing page {page_num + 1}/{len(doc)}")
                
                page = doc.load_page(page_num)
                page_text = page.get_text()
                text += page_text + "\n"
            
            doc.close()
            
            if not text.strip():
                if self.verbose:
                    print("Warning: No text found - possibly a scanned PDF")
                return None
            
            if self.verbose:
                print(f"Extracted {len(text)} characters of text")
            
            return text
            
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return None
    
    def extract_text_batch(self, folder_path: str) -> List[tuple]:
        """
        Extract text from all PDF files in a folder
        
        Args:
            folder_path: Path to folder containing PDF files
            
        Returns:
            List of tuples (filename, extracted_text)
        """
        results = []
        
        if not os.path.exists(folder_path):
            print(f"Error: Folder not found: {folder_path}")
            return results
        
        # Find all PDF files
        pdf_files = []
        for ext in ['*.pdf', '*.PDF']:
            pdf_files.extend(Path(folder_path).glob(ext))
        
        if not pdf_files:
            print(f"No PDF files found in: {folder_path}")
            return results
        
        print(f"Found {len(pdf_files)} PDF files to process...")
        
        for pdf_file in pdf_files:
            if self.verbose:
                print(f"\nProcessing: {pdf_file.name}")
            else:
                print(f"Processing: {pdf_file.name}")
            
            text = self.extract_text_from_file(str(pdf_file))
            results.append((pdf_file.name, text))
        
        return results


def save_text_to_file(text: str, output_path: str) -> bool:
    """
    Save extracted text to a file
    
    Args:
        text: Text content to save
        output_path: Path to output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"Error saving text to {output_path}: {e}")
        return False


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="Extract raw text from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract text from a single file and print to console
  python pdf_text_extractor.py --single path/to/document.pdf
  
  # Extract text and save to file
  python pdf_text_extractor.py --single document.pdf --output extracted_text.txt
  
  # Process all PDFs in a folder
  python pdf_text_extractor.py --batch path/to/pdf/folder
  
  # Process with verbose output
  python pdf_text_extractor.py --single document.pdf --verbose
        """
    )
    
    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--single', 
        type=str, 
        help='Extract text from a single PDF file'
    )
    mode_group.add_argument(
        '--batch', 
        type=str, 
        help='Extract text from all PDF files in a folder'
    )
    
    # Optional arguments
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file to save extracted text (single mode only)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for batch mode (creates .txt files for each PDF)'
    )
    parser.add_argument(
        '--verbose', '-v', 
        action='store_true',
        help='Show verbose output'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show text statistics (character count, word count, etc.)'
    )
    
    args = parser.parse_args()
    
    # Create extractor instance
    extractor = PDFTextExtractor(verbose=args.verbose)
    
    if args.single:
        # Single file mode
        print(f"Extracting text from: {args.single}")
        
        if not os.path.exists(args.single):
            print(f"Error: File not found: {args.single}")
            sys.exit(1)
        
        text = extractor.extract_text_from_file(args.single)
        
        if text is None:
            print("Failed to extract text from PDF")
            sys.exit(1)
        
        # Show statistics if requested
        if args.stats:
            char_count = len(text)
            word_count = len(text.split())
            line_count = len(text.splitlines())
            print(f"\nText Statistics:")
            print(f"  Characters: {char_count:,}")
            print(f"  Words: {word_count:,}")
            print(f"  Lines: {line_count:,}")
        
        # Save to file or print to console
        if args.output:
            if save_text_to_file(text, args.output):
                print(f"Text saved to: {args.output}")
            else:
                sys.exit(1)
        else:
            print("\n" + "="*80)
            print("EXTRACTED TEXT:")
            print("="*80)
            print(text)
    
    else:
        # Batch mode
        print(f"Extracting text from all PDFs in: {args.batch}")
        
        results = extractor.extract_text_batch(args.batch)
        
        if not results:
            print("No files processed")
            sys.exit(1)
        
        successful = 0
        failed = 0
        
        for filename, text in results:
            if text is not None:
                successful += 1
                
                if args.output_dir:
                    # Save each file's text to separate .txt file
                    output_filename = Path(filename).stem + "_extracted.txt"
                    output_path = os.path.join(args.output_dir, output_filename)
                    
                    # Create output directory if it doesn't exist
                    os.makedirs(args.output_dir, exist_ok=True)
                    
                    if save_text_to_file(text, output_path):
                        print(f"  ✅ Saved: {output_path}")
                    else:
                        print(f"  ❌ Failed to save: {output_path}")
                        failed += 1
                        successful -= 1
                else:
                    # Print basic info
                    char_count = len(text)
                    word_count = len(text.split())
                    print(f"  ✅ {filename}: {char_count:,} chars, {word_count:,} words")
            else:
                failed += 1
                print(f"  ❌ {filename}: Failed to extract text")
        
        print(f"\n📊 Summary: {successful} successful, {failed} failed")


if __name__ == "__main__":
    main()

