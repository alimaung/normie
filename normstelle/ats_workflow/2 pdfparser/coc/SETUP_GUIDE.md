# Quick Setup Guide for PDF OCR

## Problem Resolution

Based on the error you encountered, here's how to fix the missing dependencies:

### Step 1: Install Tesseract OCR

**Windows:**
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location (usually `C:\Program Files\Tesseract-OCR`)
3. Add to PATH or the script will try to find it automatically

**Alternative - Chocolatey (Windows):**
```powershell
choco install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### Step 2: Install Python Dependencies

**Option A: Minimal Setup (Recommended)**
```bash
pip install pytesseract Pillow PyMuPDF
```

**Option B: Full Setup**
```bash
pip install -r simple_requirements.txt
```

### Step 3: Test the Installation

```bash
# Test with the simple version
python simple_ocr.py --help

# Test basic functionality (if you have a test PDF)
python simple_ocr.py test.pdf
```

## Usage Examples

### Simple OCR Script (`simple_ocr.py`)

This is the recommended version for most users:

```bash
# Process a single PDF
python simple_ocr.py document.pdf

# Process all PDFs in a directory
python simple_ocr.py coc/

# German language support
python simple_ocr.py document.pdf -l deu

# Custom output directory
python simple_ocr.py document.pdf -o extracted_text/
```

### Advanced OCR Script (`coc_ocr.py`)

Only use this if you need multiple OCR engines:

```bash
# Requires additional dependencies
pip install easyocr paddlepaddle paddleocr opencv-python

# Use multiple OCR engines
python coc_ocr.py document.pdf -e all
```

## Troubleshooting

### Error: "Tesseract not found"
- Make sure Tesseract is installed and in your PATH
- On Windows, try installing to the default location

### Error: "poppler not found" (pdf2image)
- This is optional - the script will use PyMuPDF instead
- If needed: `sudo apt install poppler-utils` (Ubuntu) or `brew install poppler` (macOS)

### Error: "No module named 'fitz'"
```bash
pip install PyMuPDF
```

### Poor OCR Quality
- Try higher DPI: `--dpi 600` (not available in simple version)
- Use different OCR engine: `-e easyocr` (advanced version only)
- Make sure the PDF isn't password protected or corrupted

## File Output

The script creates:
- `filename_extracted_TIMESTAMP.txt` - Clean text output
- `filename_extracted_TIMESTAMP.json` - Structured data with metadata
- `simple_ocr_TIMESTAMP.log` - Processing log

## Performance Tips

- **PyMuPDF** is the fastest and most reliable option
- For large batches, process files individually to avoid memory issues
- Text-based PDFs (not scanned) will be processed much faster 