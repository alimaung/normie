import fitz  # PyMuPDF
from pypdf import PdfReader
import json
import sys
import hashlib
from collections import defaultdict
import re

class PDFTemplateExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.reader = PdfReader(pdf_path)
        
    def extract_metadata(self):
        """Extract PDF metadata that might help identify template origin"""
        metadata = {}
        
        # PyMuPDF metadata
        fitz_meta = self.doc.metadata
        if fitz_meta:
            metadata['fitz'] = {
                'title': fitz_meta.get('title', ''),
                'author': fitz_meta.get('author', ''),
                'subject': fitz_meta.get('subject', ''),
                'creator': fitz_meta.get('creator', ''),
                'producer': fitz_meta.get('producer', ''),
                'creationDate': fitz_meta.get('creationDate', ''),
                'modDate': fitz_meta.get('modDate', ''),
                'keywords': fitz_meta.get('keywords', '')
            }
        
        # PyPDF metadata
        if self.reader.metadata:
            metadata['pypdf'] = {
                'title': str(self.reader.metadata.get('/Title', '')),
                'author': str(self.reader.metadata.get('/Author', '')),
                'subject': str(self.reader.metadata.get('/Subject', '')),
                'creator': str(self.reader.metadata.get('/Creator', '')),
                'producer': str(self.reader.metadata.get('/Producer', '')),
                'creation_date': str(self.reader.metadata.get('/CreationDate', '')),
                'mod_date': str(self.reader.metadata.get('/ModDate', ''))
            }
        
        return metadata
    
    def extract_document_structure(self):
        """Extract document structure information"""
        structure = {
            'page_count': len(self.doc),
            'page_sizes': [],
            'total_text_blocks': 0,
            'total_images': 0,
            'total_drawings': 0
        }
        
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            page_rect = page.rect
            structure['page_sizes'].append({
                'page': page_num + 1,
                'width': page_rect.width,
                'height': page_rect.height,
                'ratio': page_rect.width / page_rect.height if page_rect.height > 0 else 0
            })
            
            blocks = page.get_text("dict")["blocks"]
            text_blocks = sum(1 for block in blocks if block['type'] == 0)
            image_blocks = sum(1 for block in blocks if block['type'] == 1)
            
            structure['total_text_blocks'] += text_blocks
            structure['total_images'] += image_blocks
            
            # Count drawing objects
            drawings = page.get_drawings()
            structure['total_drawings'] += len(drawings)
        
        return structure
    
    def extract_text_with_proper_encoding(self, page):
        """Extract text with multiple encoding attempts to get proper German characters"""
        # Try different text extraction methods with PyMuPDF
        methods = [
            lambda: page.get_text("text"),  # Default method
            lambda: page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES),  # Preserve ligatures
            lambda: page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE),  # Preserve whitespace
            lambda: page.get_text("dict")  # Dict method for more control
        ]
        
        for method in methods:
            try:
                result = method()
                if isinstance(result, dict):
                    # Handle dict method
                    text_lines = []
                    for block in result.get("blocks", []):
                        if block.get('type') == 0:  # text block
                            for line in block.get("lines", []):
                                line_text = ""
                                for span in line.get("spans", []):
                                    line_text += span.get("text", "") + " "
                                if line_text.strip():
                                    text_lines.append(line_text.strip())
                    return text_lines
                else:
                    # Handle text method
                    lines = [line.strip() for line in result.split('\n') if line.strip()]
                    # Check if we got proper German characters
                    if self.has_proper_german_chars(lines):
                        return lines
            except Exception:
                continue
        
        # Fallback to original method if all fail
        return [line.strip() for line in page.get_text().split('\n') if line.strip()]
    
    def has_proper_german_chars(self, lines):
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

    def extract_document_version(self, all_text_lines):
        """Extract document version information from text"""
        version_info = {
            'document_id': None,
            'version_date': None,
            'version_pattern': None,
            'is_latest': False,
            'page_references': []
        }
        
        # Pattern for T00221:YYYY-MM-DD format
        version_pattern = r'T00221:(\d{4}-\d{2}-\d{2})'
        
        for i, line in enumerate(all_text_lines):
            # Look for version pattern
            match = re.search(version_pattern, line)
            if match:
                version_info['document_id'] = 'T00221'
                version_info['version_date'] = match.group(1)
                version_info['version_pattern'] = match.group(0)
                
                # Check if this is the latest known version (2025-05-07)
                if match.group(1) == '2025-05-07':
                    version_info['is_latest'] = True
                
                version_info['page_references'].append({
                    'line_index': i,
                    'text': line,
                    'pattern': match.group(0)
                })
        
        return version_info

    def extract_text_comprehensive(self):
        """Extract all text with proper encoding handling"""
        all_text = []
        text_patterns = defaultdict(int)
        font_usage = defaultdict(int)
        all_text_lines = []
        
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            
            # Try to get text with proper encoding first
            page_lines = self.extract_text_with_proper_encoding(page)
            
            # Also extract detailed formatting information
            blocks = page.get_text("dict")["blocks"]
            page_text = {
                'page': page_num + 1,
                'blocks': [],
                'raw_text': '\n'.join(page_lines),
                'text_lines': page_lines
            }
            
            for block in blocks:
                if block['type'] == 0:  # text block
                    block_data = {
                        'bbox': block['bbox'],
                        'lines': []
                    }
                    
                    for line in block["lines"]:
                        line_text = ""
                        line_data = {
                            'bbox': line['bbox'],
                            'spans': []
                        }
                        
                        for span in line["spans"]:
                            span_text = span["text"].strip()
                            if span_text:
                                span_data = {
                                    "text": span_text,
                                    "bbox": span["bbox"],
                                    "font": span["font"],
                                    "size": round(span["size"], 2),
                                    "flags": span["flags"],
                                    "color": span.get("color", 0)
                                }
                                line_data['spans'].append(span_data)
                                line_text += span_text + " "
                                
                                # Track font usage
                                font_key = f"{span['font']}_{span['size']}"
                                font_usage[font_key] += 1
                        
                        if line_text.strip():
                            block_data['lines'].append(line_data)
                            
                            # Track text patterns (could be form labels, headers, etc.)
                            cleaned_text = re.sub(r'\s+', ' ', line_text.strip())
                            if len(cleaned_text) > 2:
                                text_patterns[cleaned_text] += 1
                    
                    if block_data['lines']:
                        page_text['blocks'].append(block_data)
            
            all_text.append(page_text)
            all_text_lines.extend(page_lines)
        
        # Extract version information
        version_info = self.extract_document_version(all_text_lines)
        
        return {
            'pages': all_text,
            'text_patterns': dict(text_patterns),
            'font_usage': dict(font_usage),
            'version_info': version_info,
            'all_text_lines': all_text_lines
        }
    
    def extract_form_fields_detailed(self):
        """Extract detailed form field information"""
        fields = []
        field_types = defaultdict(int)
        field_positions = []
        
        if self.reader.get_fields() is not None:
            for fname, fdata in self.reader.get_fields().items():
                field_info = {
                    "name": fname,
                    "value": str(fdata.get('/V', '')),
                    "default_value": str(fdata.get('/DV', '')),
                    "type": str(fdata.get('/FT', '')),
                    "subtype": str(fdata.get('/Subtype', '')),
                    "flags": fdata.get('/Ff', 0),
                    "rect": fdata.get('/Rect'),
                    "tooltip": str(fdata.get('/TU', '')),
                    "options": []
                }
                
                # Extract options for choice fields
                if '/Opt' in fdata:
                    options = fdata['/Opt']
                    if options:
                        field_info['options'] = [str(opt) for opt in options]
                
                # Extract appearance information
                if '/AP' in fdata:
                    field_info['has_appearance'] = True
                
                fields.append(field_info)
                
                # Track field types and positions
                field_type = str(fdata.get('/FT', 'unknown'))
                field_types[field_type] += 1
                
                if fdata.get('/Rect'):
                    rect = fdata['/Rect']
                    field_positions.append({
                        'name': fname,
                        'x': rect[0],
                        'y': rect[1],
                        'width': rect[2] - rect[0],
                        'height': rect[3] - rect[1]
                    })
        
        return {
            'fields': fields,
            'field_count': len(fields),
            'field_types': dict(field_types),
            'field_positions': field_positions
        }
    
    def extract_layout_elements(self):
        """Extract layout elements like lines, rectangles, etc."""
        layout_elements = []
        
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            page_elements = {
                'page': page_num + 1,
                'drawings': [],
                'images': []
            }
            
            # Extract drawings (lines, rectangles, etc.)
            drawings = page.get_drawings()
            for drawing in drawings:
                page_elements['drawings'].append({
                    'bbox': drawing['rect'],
                    'type': drawing.get('type', 'unknown'),
                    'items': len(drawing.get('items', []))
                })
            
            # Extract images
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                page_elements['images'].append({
                    'index': img_index,
                    'xref': img[0],
                    'smask': img[1],
                    'width': img[2],
                    'height': img[3],
                    'bpc': img[4],
                    'colorspace': img[5],
                    'alt': img[6],
                    'name': img[7],
                    'filter': img[8]
                })
            
            layout_elements.append(page_elements)
        
        return layout_elements
    
    def generate_template_signature(self):
        """Generate a signature that could help identify this template"""
        # Combine various elements to create a signature
        signature_data = []
        
        # Add form field names and types (these are usually consistent in templates)
        form_info = self.extract_form_fields_detailed()
        field_signature = []
        for field in form_info['fields']:
            field_signature.append(f"{field['name']}:{field['type']}")
        signature_data.extend(sorted(field_signature))
        
        # Add common text patterns (likely to be template labels/headers)
        text_info = self.extract_text_comprehensive()
        common_patterns = []
        for pattern, count in text_info['text_patterns'].items():
            if count >= 1 and len(pattern) > 5:  # Only significant patterns
                common_patterns.append(pattern)
        signature_data.extend(sorted(common_patterns[:20]))  # Top 20 patterns
        
        # Add document structure info
        structure = self.extract_document_structure()
        signature_data.append(f"pages:{structure['page_count']}")
        signature_data.append(f"text_blocks:{structure['total_text_blocks']}")
        
        # Create hash of signature
        signature_string = "|".join(signature_data)
        signature_hash = hashlib.md5(signature_string.encode()).hexdigest()
        
        return {
            'signature_elements': signature_data,
            'signature_hash': signature_hash,
            'signature_string': signature_string
        }
    
    def extract_all(self):
        """Extract all information for template identification"""
        return {
            'metadata': self.extract_metadata(),
            'structure': self.extract_document_structure(),
            'text': self.extract_text_comprehensive(),
            'form_fields': self.extract_form_fields_detailed(),
            'layout': self.extract_layout_elements(),
            'template_signature': self.generate_template_signature()
        }
    
    def close(self):
        """Clean up resources"""
        if self.doc:
            self.doc.close()

def main(pdf_path, output_file=None):
    """Main function to extract comprehensive PDF information"""
    try:
        extractor = PDFTemplateExtractor(pdf_path)
        result = extractor.extract_all()
        extractor.close()
        
        # Add file information
        result['file_info'] = {
            'path': pdf_path,
            'size': None
        }
        
        try:
            import os
            result['file_info']['size'] = os.path.getsize(pdf_path)
        except:
            pass
        
        # Generate output filename if not provided
        if output_file is None:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_file = f"{base_name}_extracted.json"
        
        # Save to file with UTF-8 encoding
        try:
            with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"Extraction completed successfully!")
            print(f"Output saved to: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
            
            # Also print summary to console
            print(f"\nSummary:")
            print(f"- Pages: {result.get('structure', {}).get('page_count', 'unknown')}")
            print(f"- Text lines: {len(result.get('text', {}).get('all_text_lines', []))}")
            print(f"- Form fields: {result.get('form_fields', {}).get('field_count', 0)}")
            
            version_info = result.get('text', {}).get('version_info', {})
            if version_info.get('document_id'):
                print(f"- Document ID: {version_info['document_id']}")
                print(f"- Version date: {version_info['version_date']}")
                print(f"- Is latest: {version_info['is_latest']}")
            
        except Exception as e:
            print(f"Error saving to file {output_file}: {e}")
            print("Falling back to console output:")
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        
    except Exception as e:
        error_result = {
            'error': str(e),
            'file_info': {'path': pdf_path}
        }
        
        # Try to save error to file if output_file was specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(error_result, f, indent=2, ensure_ascii=False)
                print(f"Error saved to: {output_file}")
            except:
                pass
        
        print(json.dumps(error_result, indent=2, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extractor.py <pdf_file> [output_file]")
        print("\nThis script extracts comprehensive information from a PDF including:")
        print("- Metadata (author, creator, etc.)")
        print("- Document structure (pages, layout)")
        print("- All visible text with positioning and formatting")
        print("- Form fields with detailed properties")
        print("- Layout elements (drawings, images)")
        print("- Template signature for identification")
        print("\nExamples:")
        print("  python extractor.py document.pdf")
        print("  python extractor.py document.pdf extracted_text.json")
        print("  python extractor.py T00221.pdf template.json")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    main(pdf_file, output_file)
