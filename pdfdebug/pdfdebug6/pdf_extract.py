#!/usr/bin/env python3
"""
PDF Field Extractor
Extracts form fields and text fields from PDF files and saves them in JSON format
"""

import sys
import os
import json
import glob
from pathlib import Path

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

def extract_pdf_fields_pypdf2(pdf_path, output_path=None):
    """
    Extract only the specific form fields we're testing from a PDF file using PyPDF2
    """
    # Define the fields we're actually testing (5 of each type)
    TARGET_FIELDS = {
        # Text fields
        "1", "9", "7", "4", "3",
        # Radio buttons  
        "5", "6", "13", "14", "15a",
        # Checkboxes
        "18a", "18b", "18c", "18d", "15b"
    }
    
    try:
        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            print(f"Processing PDF: {pdf_path}")
            print(f"Total pages: {len(reader.pages)}")
            
            # Initialize result dictionary
            result = {
                "metadata": {
                    "filename": os.path.basename(pdf_path),
                    "pages": len(reader.pages)
                },
                "form_fields": [],
                "target_fields_found": 0,
                "target_fields_total": len(TARGET_FIELDS)
            }
            
            # Extract document metadata if available
            if reader.metadata:
                for key, value in reader.metadata.items():
                    if value and key not in result["metadata"]:
                        result["metadata"][key] = value
            
            # Extract only the target form fields
            if reader.get_fields():
                for field_name, field_value in reader.get_fields().items():
                    # Only process fields we're testing
                    if field_name not in TARGET_FIELDS:
                        continue
                    
                    # Skip signature fields
                    if isinstance(field_value, dict) and field_value.get("/FT") == "/Sig":
                        continue
                    
                    # Determine field type
                    field_type = "Unknown"
                    if isinstance(field_value, dict):
                        ft = field_value.get("/FT")
                        if ft == "/Tx":
                            field_type = "Text"
                        elif ft == "/Btn":
                            field_type = "Button"
                        elif ft == "/Ch":
                            field_type = "Choice"
                        elif ft == "/Sig":
                            field_type = "Signature"
                    
                    # Extract field value
                    value = str(field_value)
                    if isinstance(field_value, dict) and "/V" in field_value:
                        value = str(field_value["/V"])
                    
                    # Create field info object
                    field_info = {
                        "name": field_name,
                        "type": field_type,
                        "value": value
                    }
                    
                    result["form_fields"].append(field_info)
                    result["target_fields_found"] += 1
            
            return result
            
    except Exception as e:
        print(f"Error extracting PDF fields with PyPDF2: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_pdf_fields_fitz(pdf_path, output_path=None):
    """
    Extract only the specific form fields we're testing from a PDF file using PyMuPDF (fitz)
    """
    # Define the fields we're actually testing (5 of each type)
    TARGET_FIELDS = {
        # Text fields
        "1", "9", "7", "4", "3",
        # Radio buttons  
        "5", "6", "13", "14", "15a",
        # Checkboxes
        "18a", "18b", "18c", "18d", "15b"
    }
    
    try:
        doc = fitz.open(pdf_path)
        
        print(f"Processing PDF: {pdf_path}")
        print(f"Total pages: {len(doc)}")
        
        # Initialize result dictionary
        result = {
            "metadata": {
                "filename": os.path.basename(pdf_path),
                "pages": len(doc)
            },
            "form_fields": [],
            "target_fields_found": 0,
            "target_fields_total": len(TARGET_FIELDS)
        }
        
        # Extract document metadata
        metadata = doc.metadata
        for key, value in metadata.items():
            if value and key not in result["metadata"]:
                result["metadata"][key] = value
        
        # Extract only the target form fields from all pages
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get form fields on this page
            widgets = page.widgets()
            for widget in widgets:
                # Only process fields we're testing
                if widget.field_name not in TARGET_FIELDS:
                    continue
                
                # Skip signature fields
                if widget.field_type == fitz.PDF_WIDGET_TYPE_SIGNATURE:
                    continue
                
                # Determine field type
                field_type = "Unknown"
                if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                    field_type = "Text"
                elif widget.field_type == fitz.PDF_WIDGET_TYPE_BUTTON:
                    field_type = "Button"
                elif widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                    field_type = "Checkbox"
                elif widget.field_type == fitz.PDF_WIDGET_TYPE_RADIOBUTTON:
                    field_type = "RadioButton"
                elif widget.field_type == fitz.PDF_WIDGET_TYPE_LISTBOX:
                    field_type = "ListBox"
                elif widget.field_type == fitz.PDF_WIDGET_TYPE_COMBOBOX:
                    field_type = "ComboBox"
                
                # Create field info object
                field_info = {
                    "name": widget.field_name,
                    "type": field_type,
                    "value": str(widget.field_value) if widget.field_value is not None else "",
                    "page": page_num + 1
                }
                
                result["form_fields"].append(field_info)
                result["target_fields_found"] += 1
        
        doc.close()
        return result
        
    except Exception as e:
        print(f"Error extracting PDF fields with PyMuPDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_pdf_fields(pdf_path, output_path=None):
    """
    Extract form fields and text fields from a PDF file
    """
    # Try PyMuPDF first (more reliable), then fall back to PyPDF2
    result = None
    
    if FITZ_AVAILABLE:
        print("Using PyMuPDF for extraction...")
        result = extract_pdf_fields_fitz(pdf_path, output_path)
    
    if result is None and PYPDF2_AVAILABLE:
        print("Falling back to PyPDF2 for extraction...")
        result = extract_pdf_fields_pypdf2(pdf_path, output_path)
    
    if result is None:
        print("Error: No PDF library available or extraction failed")
        return None
    
    # Save results to JSON file
    if output_path:
        output_file = output_path
    else:
        # Generate output filename if not provided
        output_file = os.path.splitext(pdf_path)[0] + "_fields.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"PDF field extraction saved to: {output_file}")
        
        # Print summary
        print(f"Extracted {result['target_fields_found']}/{result['target_fields_total']} target fields")
        
        return result
        
    except Exception as e:
        print(f"Error saving results: {e}")
        return None

def process_test_pdf_directory():
    """
    Process all PDF files in the test_pdf directory
    """
    # Get the directory of this script
    script_dir = Path(__file__).parent
    test_pdf_dir = script_dir / "test_pdf"
    
    print(f"Looking for PDFs in: {test_pdf_dir}")
    
    if not test_pdf_dir.exists():
        print(f"Error: test_pdf directory not found: {test_pdf_dir}")
        return
    
    # Find all PDF files in the test_pdf directory
    pdf_files = list(test_pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in test_pdf directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF file
    for pdf_file in pdf_files:
        print(f"\n{'='*50}")
        print(f"Processing: {pdf_file.name}")
        print('='*50)
        
        # Generate output filename
        output_file = pdf_file.with_name(pdf_file.stem + '_fields.json')
        
        # Extract fields
        result = extract_pdf_fields(str(pdf_file), str(output_file))
        
        if result:
            print(f"✅ Successfully processed: {pdf_file.name}")
        else:
            print(f"❌ Failed to process: {pdf_file.name}")
    
    print(f"\n{'='*50}")
    print("Processing complete!")
    print('='*50)

def main():
    if not PYPDF2_AVAILABLE and not FITZ_AVAILABLE:
        print("Error: No PDF library available. Please install PyPDF2 or PyMuPDF:")
        print("  pip install PyPDF2")
        print("  pip install PyMuPDF")
        return
    
    # Check if command line arguments are provided
    if len(sys.argv) >= 2:
        # Original single file processing
        pdf_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file not found: {pdf_path}")
            return
        
        extract_pdf_fields(pdf_path, output_path)
    else:
        # Process all PDFs in test_pdf directory
        process_test_pdf_directory()

if __name__ == "__main__":
    main() 