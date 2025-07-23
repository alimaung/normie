#!/usr/bin/env python3
import fitz  # PyMuPDF
import sys
import os
import json

def extract_text_with_proper_encoding(page):
    """Extract text with multiple encoding attempts to get proper German characters"""
    # Try different text extraction methods with PyMuPDF
    methods = [
        lambda: page.get_text("text"),  # Default method
        lambda: page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES),  # Preserve ligatures
        lambda: page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE),  # Preserve whitespace
    ]
    
    for method in methods:
        try:
            result = method()
            lines = [line.strip() for line in result.split('\n') if line.strip()]
            
            # Check if we got proper German characters
            if has_proper_german_chars(lines):
                return lines
        except Exception:
            continue
    
    # Fallback to original method if all fail
    return [line.strip() for line in page.get_text().split('\n') if line.strip()]

def has_proper_german_chars(lines):
    """Check if text contains proper German characters instead of encoding artifacts"""
    # Look for common German words with umlauts
    german_indicators = ['für', 'über', 'müssen', 'Gefährdung', 'Erläuterung', 'Häufigkeit']
    artifact_indicators = ['fⁿr', 'ⁿber', 'mⁿssen', 'GefΣhrdung', 'ErlΣuterung', 'HΣufigkeit']
    
    text = ' '.join(lines)
    
    # If we find proper German chars, it's good
    if any(word in text for word in german_indicators):
        return True
    
    # If we find artifacts but no proper chars, it's bad
    if any(artifact in text for artifact in artifact_indicators):
        return False
    
    # Default to True if we can't determine
    return True

def extract_text_simple(pdf_path):
    """Extract all text from PDF and split by newlines with proper encoding"""
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        
        pages = []
        all_lines = []
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Use proper encoding extraction
            lines = extract_text_with_proper_encoding(page)
            
            pages.append({
                "page_number": page_num + 1,
                "lines": lines,
                "line_count": len(lines)
            })
            
            # Add to overall lines list
            all_lines.extend(lines)
        
        doc.close()
        
        return {
            "file": pdf_path,
            "total_pages": len(pages),
            "total_lines": len(all_lines),
            "pages": pages,
            "all_lines": all_lines
        }
        
    except Exception as e:
        return {
            "file": pdf_path,
            "error": str(e),
            "total_pages": 0,
            "total_lines": 0,
            "pages": [],
            "all_lines": []
        }

def main(pdf_path=None, output_file=None):
    if pdf_path is None:
        if len(sys.argv) < 2:
            print("Usage: python simple_text_extractor.py <pdf_file> [output_file]")
            print("\nThis script extracts all visible text from a PDF file.")
            print("\nExamples:")
            print("  python simple_text_extractor.py document.pdf")
            print("  python simple_text_extractor.py document.pdf extracted_text.json")
            print("  python simple_text_extractor.py T00221.pdf template.json")
            sys.exit(1)
        
        pdf_path = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        sys.exit(1)
    
    if not pdf_path.lower().endswith('.pdf'):
        print(f"Error: '{pdf_path}' is not a PDF file.")
        sys.exit(1)
    
    # Extract the text
    result = extract_text_simple(pdf_path)
    
    # Generate output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_file = f"{base_name}_simple.json"
    
    # Save to file with UTF-8 encoding
    try:
        with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Text extraction completed successfully!")
        print(f"Output saved to: {output_file}")
        print(f"File size: {os.path.getsize(output_file)} bytes")
        
        # Print summary to console
        if 'error' not in result:
            print(f"\nSummary:")
            print(f"- Pages: {result.get('total_pages', 0)}")
            print(f"- Total lines: {result.get('total_lines', 0)}")
            print(f"- Average lines per page: {result.get('total_lines', 0) / max(result.get('total_pages', 1), 1):.1f}")
        else:
            print(f"\nError during extraction: {result['error']}")
        
    except Exception as e:
        print(f"Error saving to file {output_file}: {e}")
        print("Falling back to console output:")
        
        # Fallback to console output
        try:
            # Ensure stdout uses UTF-8 encoding
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            
            json_output = json.dumps(result, indent=2, ensure_ascii=False)
            sys.stdout.write(json_output)
            sys.stdout.flush()
            
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Fallback to ASCII-safe output if there are encoding issues
            json_output = json.dumps(result, indent=2, ensure_ascii=True)
            sys.stdout.write(json_output)
            sys.stdout.flush()

if __name__ == "__main__":
    main() 