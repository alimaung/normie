#!/usr/bin/env python3
"""
PDF Field Extractor
Extracts form fields and text fields from PDF files and saves them in JSON format
"""

import sys
import os
import json
import PyPDF2
from collections import defaultdict

def extract_pdf_fields(pdf_path, output_path=None):
    """
    Extract form fields and text fields from a PDF file and save in JSON format
    """
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
                "text_fields": []
            }
            
            # Extract document metadata if available
            if reader.metadata:
                for key, value in reader.metadata.items():
                    if value and key not in result["metadata"]:
                        result["metadata"][key] = value
            
            # Extract form fields (interactive form elements)
            if reader.get_fields():
                for field_name, field_value in reader.get_fields().items():
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
                    
                    # Get field position if available
                    position = {}
                    if isinstance(field_value, dict) and "/Rect" in field_value:
                        rect = field_value["/Rect"]
                        if isinstance(rect, list) and len(rect) == 4:
                            position = {
                                "x1": rect[0],
                                "y1": rect[1],
                                "x2": rect[2],
                                "y2": rect[3]
                            }
                    
                    # Create field info object
                    field_info = {
                        "name": field_name,
                        "type": field_type,
                        "value": value
                    }
                    
                    if position:
                        field_info["position"] = position
                    
                    result["form_fields"].append(field_info)
            
            # Extract text content from each page with position information if possible
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                
                # If page has text, try to extract text elements with positions
                if page_text:
                    # Split text into lines for basic positioning
                    lines = page_text.split('\n')
                    y_position = 0
                    line_height = 1.0  # Estimated line height
                    
                    for line_num, line in enumerate(lines):
                        if line.strip():
                            # Create a text field entry with estimated position
                            text_field = {
                                "page": page_num + 1,
                                "text": line,
                                "position": {
                                    "y": y_position,
                                    "line": line_num
                                }
                            }
                            result["text_fields"].append(text_field)
                        
                        y_position += line_height
            
            # Save results to JSON file
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"PDF field extraction saved to: {output_path}")
            else:
                # Generate output filename if not provided
                output_path = os.path.splitext(pdf_path)[0] + "_fields.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"PDF field extraction saved to: {output_path}")
            
            # Print summary
            print(f"\nExtracted {len(result['form_fields'])} form fields and {len(result['text_fields'])} text fields")
            
            return result
            
    except Exception as e:
        print(f"Error extracting PDF fields: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    if len(sys.argv) < 2:
        print("PDF Field Extractor")
        print("Usage: python pdf_extract.py <pdf_file> [output_json_file]")
        print("Example: python pdf_extract.py document.pdf fields.json")
        return
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    extract_pdf_fields(pdf_path, output_path)

if __name__ == "__main__":
    main() 