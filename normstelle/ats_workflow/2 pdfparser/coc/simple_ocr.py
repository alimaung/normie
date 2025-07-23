#!/usr/bin/env python3
"""
Simple PDF OCR Text Extraction Script

A simplified version that works with basic dependencies and gracefully handles missing components.
Focuses on Tesseract OCR with optional fallbacks.

Requirements:
- pip install pytesseract pillow PyPDF2 fitz (or pymupdf)
- Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
import argparse
from datetime import datetime

# Try to import required packages with graceful fallbacks
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Install with: pip install Pillow")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: pytesseract not available. Install with: pip install pytesseract")

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    try:
        import PyPDF2
        PYPDF2_AVAILABLE = True
    except ImportError:
        PYPDF2_AVAILABLE = False
        print("Warning: No PDF library available. Install with: pip install PyMuPDF or pip install PyPDF2")

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("Warning: pdf2image not available. Install with: pip install pdf2image")
    print("Note: Also requires poppler-utils to be installed on your system")


class SimplePDFOCR:
    """Simple PDF OCR text extraction with basic dependencies."""
    
    def __init__(self, output_dir: str = "ocr_output", language: str = "eng"):
        """
        Initialize simple PDF OCR extractor.
        
        Args:
            output_dir: Directory to save extracted text
            language: Language code for OCR (e.g., 'eng', 'deu', 'fra')
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.language = language
        
        # Setup logging
        self.setup_logging()
        
        # Check available components
        self.check_dependencies()
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_file = self.output_dir / f"simple_ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_dependencies(self):
        """Check which dependencies are available."""
        self.logger.info("Checking available dependencies...")
        
        if TESSERACT_AVAILABLE:
            try:
                version = pytesseract.get_tesseract_version()
                self.logger.info(f"Tesseract OCR available: {version}")
                self.tesseract_available = True
            except Exception as e:
                self.logger.warning(f"Tesseract not properly configured: {e}")
                self.tesseract_available = False
        else:
            self.tesseract_available = False
        
        self.logger.info(f"PIL available: {PIL_AVAILABLE}")
        self.logger.info(f"PyMuPDF available: {PYMUPDF_AVAILABLE}")
        self.logger.info(f"PyPDF2 available: {PYPDF2_AVAILABLE}")
        self.logger.info(f"pdf2image available: {PDF2IMAGE_AVAILABLE}")
        
        if not self.tesseract_available:
            self.logger.error("Tesseract OCR is not available. Please install tesseract and pytesseract.")
            return False
        
        if not PIL_AVAILABLE:
            self.logger.error("PIL is not available. Please install Pillow.")
            return False
        
        return True
    
    def extract_text_from_images_pymupdf(self, pdf_path: str) -> List[str]:
        """Extract text by converting PDF pages to images using PyMuPDF."""
        if not PYMUPDF_AVAILABLE:
            raise RuntimeError("PyMuPDF not available")
        
        self.logger.info(f"Using PyMuPDF to extract images from {pdf_path}")
        page_texts = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                self.logger.info(f"Processing page {page_num + 1}/{len(doc)}")
                
                page = doc.load_page(page_num)
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Convert to PIL Image
                from io import BytesIO
                image = Image.open(BytesIO(img_data))
                
                # Extract text using Tesseract
                text = pytesseract.image_to_string(image, lang=self.language)
                page_texts.append(text.strip())
                
                self.logger.info(f"Extracted {len(text)} characters from page {page_num + 1}")
            
            doc.close()
            return page_texts
            
        except Exception as e:
            self.logger.error(f"Error processing with PyMuPDF: {e}")
            return []
    
    def extract_text_from_images_pdf2image(self, pdf_path: str) -> List[str]:
        """Extract text by converting PDF pages to images using pdf2image."""
        if not PDF2IMAGE_AVAILABLE:
            raise RuntimeError("pdf2image not available")
        
        self.logger.info(f"Using pdf2image to extract images from {pdf_path}")
        page_texts = []
        
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            
            for i, image in enumerate(images):
                self.logger.info(f"Processing page {i + 1}/{len(images)}")
                
                # Extract text using Tesseract
                text = pytesseract.image_to_string(image, lang=self.language)
                page_texts.append(text.strip())
                
                self.logger.info(f"Extracted {len(text)} characters from page {i + 1}")
            
            return page_texts
            
        except Exception as e:
            self.logger.error(f"Error processing with pdf2image: {e}")
            return []
    
    def extract_text_pypdf2_fallback(self, pdf_path: str) -> str:
        """Fallback method using PyPDF2 for text-based PDFs."""
        if not PYPDF2_AVAILABLE:
            raise RuntimeError("PyPDF2 not available")
        
        self.logger.info(f"Using PyPDF2 fallback for {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text + "\n\n"
                    self.logger.info(f"Extracted {len(page_text)} characters from page {page_num + 1}")
                
                return text.strip()
                
        except Exception as e:
            self.logger.error(f"Error with PyPDF2 fallback: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict:
        """
        Extract text from PDF using available methods.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extraction results
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not self.tesseract_available:
            raise RuntimeError("Tesseract OCR is not available")
        
        self.logger.info(f"Processing PDF: {pdf_path}")
        
        results = {
            "pdf_file": str(pdf_path),
            "timestamp": datetime.now().isoformat(),
            "method_used": None,
            "total_pages": 0,
            "pages": [],
            "full_text": "",
            "error": None
        }
        
        page_texts = []
        
        # Try different extraction methods in order of preference
        try:
            # Method 1: PyMuPDF (best quality)
            if PYMUPDF_AVAILABLE:
                page_texts = self.extract_text_from_images_pymupdf(str(pdf_path))
                if page_texts:
                    results["method_used"] = "PyMuPDF + Tesseract OCR"
            
            # Method 2: pdf2image (requires poppler)
            if not page_texts and PDF2IMAGE_AVAILABLE:
                page_texts = self.extract_text_from_images_pdf2image(str(pdf_path))
                if page_texts:
                    results["method_used"] = "pdf2image + Tesseract OCR"
            
            # Method 3: PyPDF2 fallback (text-based PDFs only)
            if not page_texts and PYPDF2_AVAILABLE:
                fallback_text = self.extract_text_pypdf2_fallback(str(pdf_path))
                if fallback_text.strip():
                    page_texts = [fallback_text]
                    results["method_used"] = "PyPDF2 text extraction"
            
            if not page_texts:
                raise RuntimeError("No extraction method succeeded")
            
            # Populate results
            results["total_pages"] = len(page_texts)
            results["full_text"] = "\n\n".join(page_texts)
            
            for i, text in enumerate(page_texts):
                results["pages"].append({
                    "page_number": i + 1,
                    "text": text,
                    "character_count": len(text)
                })
            
            self.logger.info(f"Successfully extracted {len(results['full_text'])} characters total")
            
        except Exception as e:
            error_msg = f"Failed to extract text: {e}"
            self.logger.error(error_msg)
            results["error"] = error_msg
        
        return results
    
    def save_results(self, results: Dict, output_format: str = "both") -> tuple:
        """Save extraction results to files."""
        pdf_name = Path(results["pdf_file"]).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        text_file = None
        json_file = None
        
        if output_format in ["text", "both"]:
            text_file = self.output_dir / f"{pdf_name}_extracted_{timestamp}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"PDF Text Extraction Results\n")
                f.write(f"{'=' * 50}\n")
                f.write(f"Source PDF: {results['pdf_file']}\n")
                f.write(f"Extraction Time: {results['timestamp']}\n")
                f.write(f"Method Used: {results['method_used']}\n")
                f.write(f"Total Pages: {results['total_pages']}\n")
                if results.get('error'):
                    f.write(f"Error: {results['error']}\n")
                f.write(f"{'=' * 50}\n\n")
                f.write(results["full_text"])
            
            self.logger.info(f"Text saved to: {text_file}")
        
        if output_format in ["json", "both"]:
            json_file = self.output_dir / f"{pdf_name}_extracted_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON saved to: {json_file}")
        
        return str(text_file) if text_file else None, str(json_file) if json_file else None
    
    def batch_process(self, pdf_directory: str, output_format: str = "both") -> List[Dict]:
        """Process multiple PDF files in a directory."""
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            raise FileNotFoundError(f"Directory not found: {pdf_dir}")
        
        pdf_files = list(pdf_dir.glob("*.pdf")) + list(pdf_dir.glob("*.PDF"))
        
        if not pdf_files:
            self.logger.warning(f"No PDF files found in {pdf_dir}")
            return []
        
        self.logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        all_results = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            self.logger.info(f"Processing file {i}/{len(pdf_files)}: {pdf_file.name}")
            
            try:
                results = self.extract_text_from_pdf(str(pdf_file))
                self.save_results(results, output_format)
                all_results.append(results)
            except Exception as e:
                error_msg = f"Failed to process {pdf_file}: {e}"
                self.logger.error(error_msg)
                all_results.append({
                    "pdf_file": str(pdf_file),
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
        
        return all_results


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Extract text from PDF files using OCR (Simple Version)")
    
    parser.add_argument("input", help="PDF file or directory containing PDF files")
    parser.add_argument("-l", "--language", default="eng", 
                       help="Language code for OCR (e.g., eng, deu, fra)")
    parser.add_argument("-o", "--output", default="ocr_output", 
                       help="Output directory")
    parser.add_argument("-f", "--format", choices=["text", "json", "both"], 
                       default="both", help="Output format")
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = SimplePDFOCR(
        output_dir=args.output,
        language=args.language
    )
    
    # Check if dependencies are available
    if not extractor.check_dependencies():
        print("\nMissing required dependencies. Please install:")
        print("1. pip install pytesseract Pillow")
        print("2. Install Tesseract OCR for your system")
        print("3. pip install PyMuPDF (recommended) or pip install PyPDF2")
        sys.exit(1)
    
    input_path = Path(args.input)
    
    try:
        if input_path.is_file():
            # Process single PDF
            results = extractor.extract_text_from_pdf(str(input_path))
            extractor.save_results(results, args.format)
            
            print(f"\nExtraction completed!")
            if results.get('error'):
                print(f"Error: {results['error']}")
            else:
                print(f"Method used: {results['method_used']}")
                print(f"Pages processed: {results['total_pages']}")
                print(f"Text length: {len(results['full_text'])} characters")
                if results.get('full_text'):
                    print(f"Preview: {results['full_text'][:200]}...")
        
        elif input_path.is_dir():
            # Process directory
            all_results = extractor.batch_process(str(input_path), args.format)
            
            print(f"\nBatch processing completed!")
            print(f"Processed {len(all_results)} files")
            
            # Summary
            successful = sum(1 for r in all_results if not r.get('error'))
            failed = len(all_results) - successful
            print(f"Successful: {successful}, Failed: {failed}")
        
        else:
            print(f"Error: {input_path} is not a valid file or directory")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 