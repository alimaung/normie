#!/usr/bin/env python3
"""
PDF OCR Text Extraction Script

This script extracts text from PDF files using OCR (Optical Character Recognition).
Supports multiple OCR engines with fallback options for better accuracy.

Features:
- Multiple OCR engines: Tesseract, EasyOCR, PaddleOCR
- Image preprocessing for better OCR accuracy
- Batch processing of multiple PDFs
- Output to text files or JSON format
- Progress tracking and logging
- Error handling and recovery

Requirements:
- pip install pytesseract pillow pdf2image easyocr paddlepaddle paddleocr opencv-python
- Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse
from datetime import datetime

try:
    import cv2
    import numpy as np
    from PIL import Image
    import pytesseract
    from pdf2image import convert_from_path
    import easyocr
    from paddleocr import PaddleOCR
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Install with: pip install pytesseract pillow pdf2image easyocr paddlepaddle paddleocr opencv-python")
    sys.exit(1)


class PDFOCRExtractor:
    """PDF OCR text extraction with multiple engine support."""
    
    def __init__(self, 
                 ocr_engine: str = "tesseract",
                 language: str = "eng",
                 preprocess: bool = True,
                 dpi: int = 300,
                 output_dir: str = "ocr_output"):
        """
        Initialize PDF OCR extractor.
        
        Args:
            ocr_engine: OCR engine to use ('tesseract', 'easyocr', 'paddleocr', 'all')
            language: Language code for OCR (e.g., 'eng', 'deu', 'fra')
            preprocess: Whether to preprocess images for better OCR
            dpi: DPI for PDF to image conversion
            output_dir: Directory to save extracted text
        """
        self.ocr_engine = ocr_engine.lower()
        self.language = language
        self.preprocess = preprocess
        self.dpi = dpi
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Initialize OCR engines
        self.ocr_engines = {}
        self.init_ocr_engines()
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_file = self.output_dir / f"ocr_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_ocr_engines(self):
        """Initialize available OCR engines."""
        try:
            # Test Tesseract
            pytesseract.get_tesseract_version()
            self.ocr_engines['tesseract'] = True
            self.logger.info("Tesseract OCR initialized")
        except Exception as e:
            self.logger.warning(f"Tesseract not available: {e}")
            self.ocr_engines['tesseract'] = False
        
        try:
            # Initialize EasyOCR
            self.easy_reader = easyocr.Reader([self.language])
            self.ocr_engines['easyocr'] = True
            self.logger.info("EasyOCR initialized")
        except Exception as e:
            self.logger.warning(f"EasyOCR not available: {e}")
            self.ocr_engines['easyocr'] = False
        
        try:
            # Initialize PaddleOCR
            self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang=self.language)
            self.ocr_engines['paddleocr'] = True
            self.logger.info("PaddleOCR initialized")
        except Exception as e:
            self.logger.warning(f"PaddleOCR not available: {e}")
            self.ocr_engines['paddleocr'] = False
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        if not self.preprocess:
            return image
        
        # Convert PIL to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to PIL
        return Image.fromarray(cleaned)
    
    def extract_text_tesseract(self, image: Image.Image) -> str:
        """Extract text using Tesseract OCR."""
        if not self.ocr_engines.get('tesseract'):
            raise RuntimeError("Tesseract not available")
        
        # Configure Tesseract
        config = '--oem 3 --psm 6'  # Use LSTM OCR Engine Mode with uniform text block
        
        try:
            text = pytesseract.image_to_string(
                image, 
                lang=self.language, 
                config=config
            )
            return text.strip()
        except Exception as e:
            self.logger.error(f"Tesseract OCR failed: {e}")
            return ""
    
    def extract_text_easyocr(self, image: Image.Image) -> str:
        """Extract text using EasyOCR."""
        if not self.ocr_engines.get('easyocr'):
            raise RuntimeError("EasyOCR not available")
        
        try:
            # Convert PIL to numpy array
            img_array = np.array(image)
            
            # Extract text
            results = self.easy_reader.readtext(img_array)
            
            # Combine all detected text
            text_lines = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Filter low confidence detections
                    text_lines.append(text)
            
            return '\n'.join(text_lines)
        except Exception as e:
            self.logger.error(f"EasyOCR failed: {e}")
            return ""
    
    def extract_text_paddleocr(self, image: Image.Image) -> str:
        """Extract text using PaddleOCR."""
        if not self.ocr_engines.get('paddleocr'):
            raise RuntimeError("PaddleOCR not available")
        
        try:
            # Convert PIL to numpy array
            img_array = np.array(image)
            
            # Extract text
            results = self.paddle_ocr.ocr(img_array, cls=True)
            
            # Combine all detected text
            text_lines = []
            for line in results:
                if line:
                    for word_info in line:
                        if len(word_info) >= 2:
                            text, confidence = word_info[1]
                            if confidence > 0.5:  # Filter low confidence detections
                                text_lines.append(text)
            
            return '\n'.join(text_lines)
        except Exception as e:
            self.logger.error(f"PaddleOCR failed: {e}")
            return ""
    
    def pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Convert PDF pages to images.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PIL Images
        """
        try:
            images = convert_from_path(pdf_path, dpi=self.dpi)
            self.logger.info(f"Converted {len(images)} pages from {pdf_path}")
            return images
        except Exception as e:
            self.logger.error(f"Failed to convert PDF to images: {e}")
            return []
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict:
        """
        Extract text from PDF using OCR.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extraction results
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        self.logger.info(f"Processing PDF: {pdf_path}")
        
        # Convert PDF to images
        images = self.pdf_to_images(str(pdf_path))
        if not images:
            return {"error": "Failed to convert PDF to images"}
        
        results = {
            "pdf_file": str(pdf_path),
            "timestamp": datetime.now().isoformat(),
            "total_pages": len(images),
            "ocr_engine": self.ocr_engine,
            "pages": [],
            "full_text": ""
        }
        
        all_text = []
        
        for page_num, image in enumerate(images, 1):
            self.logger.info(f"Processing page {page_num}/{len(images)}")
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            page_results = {
                "page_number": page_num,
                "text": {},
                "errors": []
            }
            
            # Extract text using selected engine(s)
            if self.ocr_engine == "all":
                # Try all available engines
                for engine in ["tesseract", "easyocr", "paddleocr"]:
                    if self.ocr_engines.get(engine):
                        try:
                            if engine == "tesseract":
                                text = self.extract_text_tesseract(processed_image)
                            elif engine == "easyocr":
                                text = self.extract_text_easyocr(processed_image)
                            elif engine == "paddleocr":
                                text = self.extract_text_paddleocr(processed_image)
                            
                            page_results["text"][engine] = text
                        except Exception as e:
                            error_msg = f"{engine} failed on page {page_num}: {e}"
                            self.logger.error(error_msg)
                            page_results["errors"].append(error_msg)
            else:
                # Use single engine
                try:
                    if self.ocr_engine == "tesseract":
                        text = self.extract_text_tesseract(processed_image)
                    elif self.ocr_engine == "easyocr":
                        text = self.extract_text_easyocr(processed_image)
                    elif self.ocr_engine == "paddleocr":
                        text = self.extract_text_paddleocr(processed_image)
                    else:
                        raise ValueError(f"Unknown OCR engine: {self.ocr_engine}")
                    
                    page_results["text"][self.ocr_engine] = text
                    all_text.append(text)
                except Exception as e:
                    error_msg = f"OCR failed on page {page_num}: {e}"
                    self.logger.error(error_msg)
                    page_results["errors"].append(error_msg)
            
            results["pages"].append(page_results)
        
        # Combine all text
        if self.ocr_engine == "all":
            # For "all" mode, combine the best results from each engine
            combined_text = []
            for page in results["pages"]:
                page_texts = list(page["text"].values())
                if page_texts:
                    # Use the longest text as it's likely the most complete
                    best_text = max(page_texts, key=len)
                    combined_text.append(best_text)
            results["full_text"] = "\n\n".join(combined_text)
        else:
            results["full_text"] = "\n\n".join(all_text)
        
        return results
    
    def save_results(self, results: Dict, output_format: str = "both") -> Tuple[str, str]:
        """
        Save extraction results to files.
        
        Args:
            results: Extraction results dictionary
            output_format: Output format ('text', 'json', 'both')
            
        Returns:
            Tuple of (text_file_path, json_file_path)
        """
        pdf_name = Path(results["pdf_file"]).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        text_file = None
        json_file = None
        
        if output_format in ["text", "both"]:
            text_file = self.output_dir / f"{pdf_name}_ocr_{timestamp}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"PDF OCR Extraction Results\n")
                f.write(f"{'=' * 50}\n")
                f.write(f"Source PDF: {results['pdf_file']}\n")
                f.write(f"Extraction Time: {results['timestamp']}\n")
                f.write(f"OCR Engine: {results['ocr_engine']}\n")
                f.write(f"Total Pages: {results['total_pages']}\n")
                f.write(f"{'=' * 50}\n\n")
                f.write(results["full_text"])
            
            self.logger.info(f"Text saved to: {text_file}")
        
        if output_format in ["json", "both"]:
            json_file = self.output_dir / f"{pdf_name}_ocr_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON saved to: {json_file}")
        
        return str(text_file) if text_file else None, str(json_file) if json_file else None
    
    def batch_process(self, pdf_directory: str, output_format: str = "both") -> List[Dict]:
        """
        Process multiple PDF files in a directory.
        
        Args:
            pdf_directory: Directory containing PDF files
            output_format: Output format ('text', 'json', 'both')
            
        Returns:
            List of extraction results
        """
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
    parser = argparse.ArgumentParser(description="Extract text from PDF files using OCR")
    
    parser.add_argument("input", help="PDF file or directory containing PDF files")
    parser.add_argument("-e", "--engine", choices=["tesseract", "easyocr", "paddleocr", "all"], 
                       default="tesseract", help="OCR engine to use")
    parser.add_argument("-l", "--language", default="eng", 
                       help="Language code for OCR (e.g., eng, deu, fra)")
    parser.add_argument("-o", "--output", default="ocr_output", 
                       help="Output directory")
    parser.add_argument("-f", "--format", choices=["text", "json", "both"], 
                       default="both", help="Output format")
    parser.add_argument("--no-preprocess", action="store_true", 
                       help="Disable image preprocessing")
    parser.add_argument("--dpi", type=int, default=300, 
                       help="DPI for PDF to image conversion")
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = PDFOCRExtractor(
        ocr_engine=args.engine,
        language=args.language,
        preprocess=not args.no_preprocess,
        dpi=args.dpi,
        output_dir=args.output
    )
    
    input_path = Path(args.input)
    
    try:
        if input_path.is_file():
            # Process single PDF
            results = extractor.extract_text_from_pdf(str(input_path))
            extractor.save_results(results, args.format)
            
            print(f"\nExtraction completed!")
            print(f"Text length: {len(results['full_text'])} characters")
            if results.get('full_text'):
                print(f"Preview: {results['full_text'][:200]}...")
        
        elif input_path.is_dir():
            # Process directory
            all_results = extractor.batch_process(str(input_path), args.format)
            
            print(f"\nBatch processing completed!")
            print(f"Processed {len(all_results)} files")
            
            # Summary
            successful = sum(1 for r in all_results if 'error' not in r)
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