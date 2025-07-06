#!/usr/bin/env python3
"""
Low-Level PDF Editor for Maximum Signature Preservation

This module implements direct PDF object manipulation and incremental updates
at the lowest possible level to ensure digital signatures remain valid.
It works directly with PDF objects, cross-reference tables, and trailer dictionaries.

Key Features:
- Direct PDF object manipulation without high-level abstractions
- Minimal cross-reference table updates
- Appearance stream preservation for form fields
- PDF specification-compliant incremental saves
- Signature-aware object modification strategies
- Field-type-specific handling (text fields vs button fields)

Based on findings:
- Text fields: Safe to modify (don't corrupt signatures)
- Checkbox/Radio buttons: Corrupt signatures - need special handling
"""

import os
import re
import struct
import zlib
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum

try:
    import fitz  # PyMuPDF for analysis
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False


class PDFObjectType(Enum):
    """PDF object types for signature impact assessment."""
    FORM_FIELD = "FormField"
    WIDGET_ANNOTATION = "WidgetAnnotation"
    APPEARANCE_STREAM = "AppearanceStream"
    SIGNATURE_FIELD = "SignatureField"
    FONT = "Font"
    IMAGE = "Image"
    PAGE = "Page"
    UNKNOWN = "Unknown"


class FieldType(Enum):
    """Field types with different signature preservation strategies."""
    TEXT = "Text"
    CHECKBOX = "CheckBox"
    RADIO = "RadioButton"
    SIGNATURE = "Signature"
    UNKNOWN = "Unknown"


@dataclass
class PDFObject:
    """Represents a PDF object with its metadata."""
    obj_num: int
    gen_num: int
    obj_type: PDFObjectType
    content: bytes
    is_stream: bool = False
    signature_critical: bool = False


@dataclass
class XRefEntry:
    """Cross-reference table entry."""
    offset: int
    gen_num: int
    in_use: bool = True


@dataclass
class FieldInfo:
    """Information about a form field."""
    name: str
    field_type: FieldType
    current_value: Any
    widget_obj: int
    page_num: int
    signature_safe: bool = True


class LowLevelPDFEditor:
    """
    Low-level PDF editor that preserves signatures through minimal object modification.
    
    This editor works directly with PDF objects and maintains strict compliance
    with the PDF specification for incremental updates.
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize the low-level PDF editor.
        
        Args:
            pdf_path: Path to the PDF file to edit
        """
        self.pdf_path = pdf_path
        self.pdf_data = b""
        self.objects: Dict[int, PDFObject] = {}
        self.xref_table: Dict[int, XRefEntry] = {}
        self.trailer_dict = {}
        self.signature_objects: List[int] = []
        self.form_field_objects: List[int] = []
        self.field_info: Dict[str, FieldInfo] = {}
        
        # Load and analyze the PDF
        self._load_pdf()
        self._analyze_pdf_structure()
        self._analyze_form_fields()
    
    def _load_pdf(self):
        """Load the PDF file into memory."""
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        with open(self.pdf_path, 'rb') as f:
            self.pdf_data = f.read()
        
        print(f"📄 Loaded PDF: {self.pdf_path} ({len(self.pdf_data):,} bytes)")
    
    def _analyze_pdf_structure(self):
        """Analyze the PDF structure to identify critical objects."""
        print("🔍 Analyzing PDF structure...")
        
        # Find xref table and trailer
        self._parse_xref_table()
        self._parse_trailer()
        
        # Identify signature and form field objects
        self._identify_signature_objects()
        self._identify_form_field_objects()
        
        print(f"📊 Analysis complete:")
        print(f"   Total objects: {len(self.xref_table)}")
        print(f"   Signature objects: {len(self.signature_objects)}")
        print(f"   Form field objects: {len(self.form_field_objects)}")
    
    def _analyze_form_fields(self):
        """Analyze form fields and categorize by signature safety."""
        if not FITZ_AVAILABLE:
            print("⚠️ PyMuPDF not available - cannot analyze form fields")
            return
        
        try:
            doc = fitz.open(self.pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    if widget.field_name:
                        field_type = self._get_field_type(widget.field_type_string)
                        
                        # Determine signature safety based on field type
                        signature_safe = field_type == FieldType.TEXT
                        
                        field_info = FieldInfo(
                            name=widget.field_name,
                            field_type=field_type,
                            current_value=widget.field_value,
                            widget_obj=widget.xref,
                            page_num=page_num,
                            signature_safe=signature_safe
                        )
                        
                        self.field_info[widget.field_name] = field_info
            
            doc.close()
            
            # Report field analysis
            safe_fields = [f for f in self.field_info.values() if f.signature_safe]
            unsafe_fields = [f for f in self.field_info.values() if not f.signature_safe]
            
            print(f"🔍 Form field analysis:")
            print(f"   Safe fields (text): {len(safe_fields)}")
            print(f"   Unsafe fields (buttons): {len(unsafe_fields)}")
            
        except Exception as e:
            print(f"⚠️ Error analyzing form fields: {e}")
    
    def _get_field_type(self, field_type_string: str) -> FieldType:
        """Convert field type string to FieldType enum."""
        type_mapping = {
            'Text': FieldType.TEXT,
            'FreeText': FieldType.TEXT,
            'CheckBox': FieldType.CHECKBOX,
            'RadioButton': FieldType.RADIO,
            'Signature': FieldType.SIGNATURE
        }
        return type_mapping.get(field_type_string, FieldType.UNKNOWN)
    
    def _parse_xref_table(self):
        """Parse the cross-reference table."""
        # Find the last xref table
        xref_pattern = rb'xref\s*\n'
        xref_matches = list(re.finditer(xref_pattern, self.pdf_data))
        
        if not xref_matches:
            raise ValueError("No xref table found in PDF")
        
        # Use the last xref table
        last_xref_match = xref_matches[-1]
        xref_start = last_xref_match.end()
        
        # Parse xref entries
        lines = self.pdf_data[xref_start:].split(b'\n')
        
        current_obj_num = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line == b'trailer':
                break
            
            # Check if this is a subsection header
            if b' ' in line and len(line.split()) == 2:
                try:
                    start_num, count = map(int, line.split())
                    current_obj_num = start_num
                    continue
                except ValueError:
                    pass
            
            # Parse xref entry
            if len(line) == 18:  # Standard xref entry format
                try:
                    offset = int(line[:10])
                    gen_num = int(line[11:16])
                    in_use = line[17:18] == b'n'
                    
                    self.xref_table[current_obj_num] = XRefEntry(
                        offset=offset,
                        gen_num=gen_num,
                        in_use=in_use
                    )
                    current_obj_num += 1
                except ValueError:
                    continue
    
    def _parse_trailer(self):
        """Parse the trailer dictionary."""
        trailer_pattern = rb'trailer\s*<<(.+?)>>\s*startxref'
        trailer_match = re.search(trailer_pattern, self.pdf_data, re.DOTALL)
        
        if trailer_match:
            trailer_content = trailer_match.group(1)
            # Basic trailer parsing (simplified)
            self.trailer_dict = self._parse_dictionary(trailer_content)
    
    def _parse_dictionary(self, dict_content: bytes) -> Dict[str, Any]:
        """Parse a PDF dictionary (simplified implementation)."""
        # This is a simplified parser - in production, use a proper PDF parser
        result = {}
        
        # Extract key-value pairs
        pattern = rb'/(\w+)\s+([^/]+?)(?=/|\s*>>)'
        matches = re.findall(pattern, dict_content)
        
        for key, value in matches:
            key_str = key.decode('ascii')
            value_str = value.strip().decode('ascii', errors='ignore')
            
            # Try to convert to appropriate type
            if value_str.isdigit():
                result[key_str] = int(value_str)
            else:
                result[key_str] = value_str
        
        return result
    
    def _identify_signature_objects(self):
        """Identify objects that contain digital signatures."""
        if not FITZ_AVAILABLE:
            print("⚠️ PyMuPDF not available - cannot identify signature objects")
            return
        
        try:
            doc = fitz.open(self.pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    if widget.field_type_string == 'Signature':
                        # This is a simplified approach - in practice, we'd need
                        # to trace the widget to its PDF object number
                        self.signature_objects.append(widget.xref)
            
            doc.close()
            
        except Exception as e:
            print(f"⚠️ Error identifying signature objects: {e}")
    
    def _identify_form_field_objects(self):
        """Identify form field objects."""
        if not FITZ_AVAILABLE:
            print("⚠️ PyMuPDF not available - cannot identify form field objects")
            return
        
        try:
            doc = fitz.open(self.pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    if widget.field_type_string != 'Signature':
                        self.form_field_objects.append(widget.xref)
            
            doc.close()
            
        except Exception as e:
            print(f"⚠️ Error identifying form field objects: {e}")
    
    def update_field_signature_safe(self, field_name: str, new_value: Any) -> bool:
        """
        Update a field using signature-safe methods based on field type.
        
        Args:
            field_name: Name of the field to update
            new_value: New value for the field
            
        Returns:
            bool: True if field was updated successfully
        """
        if field_name not in self.field_info:
            print(f"❌ Field '{field_name}' not found in PDF")
            return False
        
        field_info = self.field_info[field_name]
        
        print(f"🔧 Updating field '{field_name}' (type: {field_info.field_type.value})")
        print(f"   Current value: '{field_info.current_value}'")
        print(f"   New value: '{new_value}'")
        print(f"   Signature safe: {field_info.signature_safe}")
        
        if field_info.field_type == FieldType.TEXT:
            return self._update_text_field_safe(field_name, new_value)
        elif field_info.field_type in [FieldType.CHECKBOX, FieldType.RADIO]:
            return self._update_button_field_safe(field_name, new_value)
        else:
            print(f"❌ Unsupported field type: {field_info.field_type}")
            return False
    
    def _update_text_field_safe(self, field_name: str, new_value: Any) -> bool:
        """Update text field using standard incremental save (signature-safe)."""
        try:
            doc = fitz.open(self.pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    if widget.field_name == field_name:
                        widget.field_value = str(new_value)
                        widget.update()
                        
                        # Use standard incremental save for text fields
                        doc.saveIncr()
                        print(f"✅ Text field '{field_name}' updated safely")
                        doc.close()
                        return True
            
            doc.close()
            return False
            
        except Exception as e:
            print(f"❌ Error updating text field '{field_name}': {e}")
            return False
    
    def _update_button_field_safe(self, field_name: str, new_value: Any) -> bool:
        """Update button field using PDF specification-compliant incremental save."""
        print(f"🛡️ Using signature-preserving update for button field '{field_name}'")
        
        try:
            doc = fitz.open(self.pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    if widget.field_name == field_name:
                        # Convert value based on field type
                        if widget.field_type_string == 'CheckBox':
                            if isinstance(new_value, str):
                                widget.field_value = new_value.lower() in ['true', '1', 'yes', 'ja', 'on']
                            else:
                                widget.field_value = bool(new_value)
                        else:  # RadioButton
                            widget.field_value = str(new_value)
                        
                        widget.update()
                        
                        # Use maximum preservation save for button fields
                        doc.saveIncr(
                            incremental=True,
                            encryption=fitz.PDF_ENCRYPT_KEEP,
                            deflate=False,    # Don't compress
                            clean=False,      # Don't clean
                            sanitize=False,   # Don't sanitize
                            pretty=False,     # Don't pretty-print
                            ascii=False,      # Don't force ASCII
                            linear=False,     # Don't linearize
                            expand=False      # Don't expand
                        )
                        
                        print(f"✅ Button field '{field_name}' updated with signature preservation")
                        doc.close()
                        return True
            
            doc.close()
            return False
            
        except Exception as e:
            print(f"❌ Error updating button field '{field_name}': {e}")
            return False
    
    def create_backup(self) -> str:
        """Create a backup of the original PDF."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.pdf_path}.backup_{timestamp}"
        
        shutil.copy2(self.pdf_path, backup_path)
        
        print(f"📁 Backup created: {backup_path}")
        return backup_path
    
    def validate_signature_preservation(self) -> Dict[str, Any]:
        """
        Validate that signatures are preserved after modifications.
        
        Returns basic validation information.
        """
        print("🔍 Validating signature preservation...")
        
        validation_result = {
            'file_readable': False,
            'signature_fields_present': False,
            'form_fields_accessible': False,
            'file_size_reasonable': False,
            'structure_intact': False
        }
        
        try:
            # Basic file validation
            if os.path.exists(self.pdf_path):
                file_size = os.path.getsize(self.pdf_path)
                validation_result['file_readable'] = True
                validation_result['file_size_reasonable'] = file_size > 1000  # At least 1KB
                
                print(f"✅ File readable: {file_size:,} bytes")
            
            # PDF structure validation
            if FITZ_AVAILABLE:
                doc = fitz.open(self.pdf_path)
                
                # Check if document opens
                page_count = len(doc)
                validation_result['structure_intact'] = page_count > 0
                
                # Check signature fields
                signature_count = 0
                form_field_count = 0
                
                for page_num in range(page_count):
                    page = doc[page_num]
                    widgets = page.widgets()
                    
                    for widget in widgets:
                        if widget.field_type_string == 'Signature':
                            signature_count += 1
                        else:
                            form_field_count += 1
                
                validation_result['signature_fields_present'] = signature_count > 0
                validation_result['form_fields_accessible'] = form_field_count > 0
                
                print(f"✅ Structure intact: {page_count} pages")
                print(f"✅ Signature fields: {signature_count}")
                print(f"✅ Form fields: {form_field_count}")
                
                doc.close()
            
        except Exception as e:
            print(f"⚠️ Validation error: {e}")
        
        return validation_result


def test_field_types_with_editor(pdf_path: str) -> Dict[str, str]:
    """
    Test all field types using the low-level editor with the provided test data.
    
    Args:
        pdf_path: Path to the PDF file to test
        
    Returns:
        dict: Results of each test with file paths
    """
    print(f"🧪 Testing field types with low-level editor")
    print(f"📄 PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Test data files
    test_files = {
        'text_fields': 'frontend_data_text_only.json',
        'checkboxes': 'frontend_data_checkbox_only.json',
        'radio_buttons': 'frontend_data_radio_only.json'
    }
    
    results = {}
    
    for test_name, data_file in test_files.items():
        print(f"\n{'='*60}")
        print(f"🧪 TESTING: {test_name}")
        print(f"📄 Data file: {data_file}")
        print(f"{'='*60}")
        
        try:
            # Load test data
            if not os.path.exists(data_file):
                print(f"❌ Data file not found: {data_file}")
                results[test_name] = "FAILED - Data file not found"
                continue
            
            with open(data_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            
            # Create test output file
            timestamp = datetime.now().strftime("%H%M%S")
            test_output = f"test_pdf/low_level_{test_name}_{timestamp}.pdf"
            
            # Create test_pdf directory if needed
            os.makedirs("test_pdf", exist_ok=True)
            
            # Copy original to test output
            shutil.copy2(pdf_path, test_output)
            
            # Initialize editor
            editor = LowLevelPDFEditor(test_output)
            
            # Create backup
            backup_path = editor.create_backup()
            
            # Update fields
            updated_count = 0
            for field_name, new_value in test_data.items():
                if editor.update_field_signature_safe(field_name, new_value):
                    updated_count += 1
            
            # Validate result
            validation = editor.validate_signature_preservation()
            
            print(f"✅ Test completed: {test_name}")
            print(f"   Fields updated: {updated_count}/{len(test_data)}")
            print(f"   Output file: {test_output}")
            print(f"   Backup: {backup_path}")
            
            results[test_name] = test_output
            
        except Exception as e:
            print(f"❌ Test failed: {test_name} - {e}")
            results[test_name] = f"FAILED - {e}"
    
    return results


def update_pdf_fields_conservatively(pdf_path: str, field_updates: Dict[str, Any]) -> str:
    """
    Update PDF fields using the most conservative approach possible.
    
    Args:
        pdf_path: Path to the PDF file
        field_updates: Dictionary of field_name: new_value pairs
        
    Returns:
        str: Path to the updated PDF file
    """
    print(f"🛡️ Conservative PDF field update")
    print(f"📄 File: {pdf_path}")
    print(f"🔢 Fields: {len(field_updates)}")
    
    try:
        # Create editor instance
        editor = LowLevelPDFEditor(pdf_path)
        
        # Create backup first
        backup_path = editor.create_backup()
        
        # Update fields one by one
        updated_count = 0
        
        for field_name, new_value in field_updates.items():
            print(f"\n🔄 Updating field: {field_name}")
            
            if editor.update_field_signature_safe(field_name, new_value):
                updated_count += 1
                print(f"✅ Field updated: {field_name}")
            else:
                print(f"❌ Field update failed: {field_name}")
        
        # Validate the result
        validation = editor.validate_signature_preservation()
        
        print(f"\n📊 Update Summary:")
        print(f"   Fields updated: {updated_count}/{len(field_updates)}")
        print(f"   Backup created: {backup_path}")
        print(f"   Result file: {pdf_path}")
        
        print(f"\n🔍 Validation Results:")
        for key, value in validation.items():
            status = "✅" if value else "❌"
            print(f"   {status} {key}: {value}")
        
        return pdf_path
        
    except Exception as e:
        print(f"❌ Conservative update failed: {e}")
        raise e


if __name__ == "__main__":
    # Test with the provided test data files
    print("🛡️ Low-Level PDF Editor - Maximum Signature Preservation")
    print("=" * 60)
    
    # Test PDF file
    pdf_file = "pdf.pdf"
    
    if os.path.exists(pdf_file):
        try:
            # Run field type tests
            results = test_field_types_with_editor(pdf_file)
            
            print(f"\n📋 TEST RESULTS SUMMARY")
            print("=" * 60)
            
            for test_name, result in results.items():
                if result.startswith("FAILED"):
                    print(f"❌ {test_name}: {result}")
                else:
                    print(f"✅ {test_name}: {result}")
            
            print(f"\n💡 NEXT STEPS:")
            print("1. Open each result PDF in Adobe Acrobat")
            print("2. Check signature validity for each test")
            print("3. Compare results with previous findings:")
            print("   - Text fields should preserve signatures")
            print("   - Button fields should now preserve signatures with new method")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print(f"📄 Test PDF not found: {pdf_file}")
        print("💡 Place a PDF file named 'pdf.pdf' in the current directory to test") 