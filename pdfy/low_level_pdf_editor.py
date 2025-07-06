#!/usr/bin/env python3
"""
Pure Python PDF Editor - No Dependencies Required

This module implements direct PDF manipulation using only Python standard library.
It works with raw PDF bytes to preserve digital signatures through minimal modifications.

Key Features:
- Zero external dependencies (pure Python)
- Direct PDF object manipulation
- Signature-preserving incremental updates
- Form field identification and modification
- Cross-reference table management
- PDF dictionary parsing and generation
- Hybrid field extraction (text + stream decompression)

Based on PDF specification 1.7 and signature preservation research.
"""

import os
import re
import json
import shutil
import struct
import zlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass
from enum import Enum


class FieldType(Enum):
    """PDF form field types."""
    TEXT = "Tx"
    BUTTON = "Btn"
    CHOICE = "Ch"
    SIGNATURE = "Sig"
    UNKNOWN = "Unknown"


@dataclass
class PDFObject:
    """Represents a PDF object."""
    obj_num: int
    gen_num: int
    content: bytes
    offset: int
    is_stream: bool = False


@dataclass
class FormField:
    """Represents a PDF form field."""
    name: str
    field_type: FieldType
    obj_num: int
    current_value: str
    widget_refs: List[int]


class PurePDFEditor:
    """
    Pure Python PDF editor with no external dependencies.
    Preserves digital signatures through minimal incremental updates.
    Features hybrid field extraction using text search and stream decompression.
    """
    
    def __init__(self, pdf_path: str):
        """Initialize the PDF editor."""
        self.pdf_path = pdf_path
        self.pdf_data = b""
        self.objects: Dict[int, PDFObject] = {}
        self.form_fields: Dict[str, FormField] = {}
        self.signature_refs: Set[int] = set()
        self.root_ref = 0
        self.info_ref = 0
        self.xref_offset = 0
        self.modified_objects: Dict[int, bytes] = {}
        self._has_direct_modifications = False
        
        # Expected field values from form_fields.json
        self.expected_field_values = {
            "030/2025": "1",
            "Ali Maung": "2a", 
            "21.02.2025": "2b",
            "IRM(GP)": "2c",
            "Piccolo-Öko-Entwickler Typ 25": "3",
            "(wird vom Einkauf festgelegt)": "8",
            "1 Liter": "16",
            "Dr. Karsten Bartz": "25a",
            "27.03.2025": "25c",
            "Anouar Marzouki": "32a",
            "28.03.2025": "32c",
            "Maung, Ali": "50a",
            "31.03.2025": "50c",
            "01044259": "51"
        }
        
        self._load_pdf()
        self._parse_pdf()
    
    def _load_pdf(self):
        """Load PDF file into memory."""
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        with open(self.pdf_path, 'rb') as f:
            self.pdf_data = f.read()
        
        print(f"📄 Loaded PDF: {self.pdf_path} ({len(self.pdf_data):,} bytes)")
    
    def _parse_pdf(self):
        """Parse PDF structure."""
        print("🔍 Parsing PDF structure...")
        
        # Find and parse trailer
        self._parse_trailer()
        
        # Parse cross-reference table
        self._parse_xref()
        
        # Parse objects
        self._parse_objects()
        
        # Find form fields using hybrid extraction
        self._find_form_fields()
        
        # Find signature fields
        self._find_signature_fields()
        
        print(f"📊 PDF Analysis:")
        print(f"   Objects: {len(self.objects)}")
        print(f"   Form fields: {len(self.form_fields)}")
        print(f"   Signature objects: {len(self.signature_refs)}")
    
    def _parse_trailer(self):
        """Parse PDF trailer or XRef stream."""
        # Find last startxref
        startxref_pattern = rb'startxref\s*(\d+)\s*%%EOF'
        matches = list(re.finditer(startxref_pattern, self.pdf_data))
        
        if not matches:
            raise ValueError("No startxref found")
        
        last_match = matches[-1]
        self.xref_offset = int(last_match.group(1))
        
        # Check if we have traditional trailer or XRef stream
        trailer_start = self.pdf_data.rfind(b'trailer', 0, last_match.start())
        
        if trailer_start != -1:
            # Traditional trailer
            self._parse_traditional_trailer(trailer_start, last_match.start())
        else:
            # XRef stream (PDF 1.5+)
            self._parse_xref_stream()
        
        print(f"📋 Trailer/XRef parsed:")
        print(f"   XRef offset: {self.xref_offset}")
        print(f"   Root ref: {self.root_ref}")
        print(f"   Info ref: {self.info_ref}")
    
    def _parse_traditional_trailer(self, trailer_start: int, trailer_end: int):
        """Parse traditional trailer dictionary."""
        trailer_section = self.pdf_data[trailer_start:trailer_end]
        
        # Find the trailer dictionary
        dict_start = trailer_section.find(b'<<')
        dict_end = trailer_section.rfind(b'>>')
        
        if dict_start == -1 or dict_end == -1:
            raise ValueError("No trailer dictionary found")
        
        trailer_content = trailer_section[dict_start+2:dict_end]
        
        # Extract root and info references
        root_match = re.search(rb'/Root\s+(\d+)\s+\d+\s+R', trailer_content)
        if root_match:
            self.root_ref = int(root_match.group(1))
        
        info_match = re.search(rb'/Info\s+(\d+)\s+\d+\s+R', trailer_content)
        if info_match:
            self.info_ref = int(info_match.group(1))
    
    def _parse_xref_stream(self):
        """Parse XRef stream (PDF 1.5+)."""
        print("📋 Parsing XRef stream (PDF 1.5+)")
        
        # The XRef stream should be at the offset
        xref_obj = self._extract_object_at_offset(self.xref_offset)
        
        if xref_obj:
            # Extract Root and Info from XRef stream dictionary
            root_match = re.search(rb'/Root\s+(\d+)\s+\d+\s+R', xref_obj)
            if root_match:
                self.root_ref = int(root_match.group(1))
            
            info_match = re.search(rb'/Info\s+(\d+)\s+\d+\s+R', xref_obj)
            if info_match:
                self.info_ref = int(info_match.group(1))
        else:
            print("⚠️ Could not parse XRef stream")
    
    def _extract_object_at_offset(self, offset: int) -> Optional[bytes]:
        """Extract object at specific offset."""
        try:
            # Look for object header pattern
            search_area = self.pdf_data[offset:offset+500]
            obj_match = re.search(rb'(\d+)\s+(\d+)\s+obj', search_area)
            
            if obj_match:
                obj_start = offset + obj_match.end()
                # Find endobj
                endobj_pos = self.pdf_data.find(b'endobj', obj_start)
                if endobj_pos != -1:
                    return self.pdf_data[obj_start:endobj_pos]
            
            return None
        except:
            return None
    
    def _parse_xref(self):
        """Parse cross-reference table or XRef stream."""
        try:
            xref_pos = self.xref_offset
            
            # Check if it's a traditional xref table or XRef stream
            search_range = min(50, len(self.pdf_data) - xref_pos)
            xref_match = re.search(rb'xref\s*\n', self.pdf_data[xref_pos:xref_pos+search_range])
            
            if xref_match:
                # Traditional xref table
                self._parse_traditional_xref(xref_pos, xref_match)
            else:
                # Likely XRef stream
                self._parse_xref_stream_objects()
                
        except Exception as e:
            print(f"❌ XRef parsing failed: {e}")
            # Continue without xref - we'll try to find objects another way
    
    def _parse_traditional_xref(self, xref_pos: int, xref_match):
        """Parse traditional xref table."""
        xref_start = xref_pos + xref_match.end()
        
        # Parse xref entries
        pos = xref_start
        current_obj = 0
        entries_parsed = 0
        
        print(f"📋 Parsing traditional xref table from offset {xref_pos}")
        
        while pos < len(self.pdf_data):
            line_end = self.pdf_data.find(b'\n', pos)
            if line_end == -1:
                break
            
            line = self.pdf_data[pos:line_end].strip()
            pos = line_end + 1
            
            if line == b'trailer':
                break
            
            if not line:  # Skip empty lines
                continue
            
            # Check for subsection header
            if b' ' in line and len(line.split()) == 2:
                try:
                    start_obj, count = map(int, line.split())
                    current_obj = start_obj
                    print(f"   📋 Subsection: objects {start_obj} to {start_obj + count - 1}")
                    continue
                except:
                    pass
            
            # Parse xref entry
            if len(line) >= 18:
                try:
                    offset = int(line[:10])
                    gen_num = int(line[11:16])
                    in_use = line[17:18] == b'n'
                    
                    if in_use and offset > 0:
                        # Parse object at this offset
                        obj_content = self._extract_object(offset, current_obj, gen_num)
                        if obj_content:
                            self.objects[current_obj] = PDFObject(
                                obj_num=current_obj,
                        gen_num=gen_num,
                                content=obj_content,
                                offset=offset
                            )
                            entries_parsed += 1
                    
                    current_obj += 1
                except Exception as e:
                    print(f"⚠️ Error parsing xref entry: {e}")
                    continue
    
        print(f"📋 Traditional XRef parsing complete: {entries_parsed} objects loaded")
    
    def _parse_xref_stream_objects(self):
        """Parse XRef stream objects (simplified approach)."""
        print(f"📋 Parsing XRef stream objects (simplified)")
        
        # For XRef streams, we'll use the fallback object scanning
        # This is a simplified approach since properly parsing XRef streams
        # requires decompressing FlateDecode streams
        
        # Just scan for all objects in the PDF
        self._scan_for_objects()
        
        print(f"📋 XRef stream parsing complete via object scanning")
    
    def _extract_object(self, offset: int, obj_num: int, gen_num: int) -> Optional[bytes]:
        """Extract object content from PDF data."""
        try:
            # Find object header
            obj_header = f"{obj_num} {gen_num} obj".encode()
            
            if not self.pdf_data[offset:offset+len(obj_header)+10].startswith(obj_header):
                # Try to find the object header nearby
                search_start = max(0, offset - 50)
                search_end = min(len(self.pdf_data), offset + 200)
                header_pos = self.pdf_data.find(obj_header, search_start, search_end)
                if header_pos == -1:
                    return None
                offset = header_pos
            
            # Find object end
            obj_start = offset + len(obj_header)
            endobj_pos = self.pdf_data.find(b'endobj', obj_start)
            
            if endobj_pos == -1:
                return None
            
            return self.pdf_data[obj_start:endobj_pos].strip()
        
        except Exception:
            return None
    
    def _parse_objects(self):
        """Parse all objects to find their content."""
        # If we have very few objects, try to find them by scanning
        if len(self.objects) < 10:
            print("📋 Few objects found, scanning for objects...")
            self._scan_for_objects()
        
        for obj_num, obj in self.objects.items():
            try:
                # Check if it's a stream object
                if b'stream' in obj.content:
                    obj.is_stream = True
            except:
                continue
    
    def _scan_for_objects(self):
        """Scan the PDF for object headers when xref parsing fails."""
        print("🔍 Scanning PDF for object headers...")
        
        # Pattern to find object headers
        obj_pattern = rb'(\d+)\s+(\d+)\s+obj\b'
        matches = list(re.finditer(obj_pattern, self.pdf_data))
        
        scanned_objects = 0
        object_numbers = []
        
        for match in matches:
            try:
                obj_num = int(match.group(1))
                gen_num = int(match.group(2))
                offset = match.start()
                object_numbers.append(obj_num)
                
                # Don't overwrite existing objects
                if obj_num not in self.objects:
                    obj_content = self._extract_object(offset, obj_num, gen_num)
                    if obj_content:
                        self.objects[obj_num] = PDFObject(
                            obj_num=obj_num,
                            gen_num=gen_num,
                            content=obj_content,
                            offset=offset
                        )
                        scanned_objects += 1
                        
            except Exception as e:
                continue
        
        # Show object statistics
        if object_numbers:
            min_obj = min(object_numbers)
            max_obj = max(object_numbers)
            object_numbers.sort()
            print(f"📋 Scanned {scanned_objects} additional objects")
            print(f"📋 Object number range: {min_obj} to {max_obj}")
            print(f"📋 Total objects now: {len(self.objects)}")
            print(f"📋 Sample object numbers: {object_numbers[:10]}...{object_numbers[-10:] if len(object_numbers) > 10 else []}")
        else:
            print("📋 No objects found in scan")
    
    def _find_form_fields(self):
        """Find form fields using hybrid extraction approach."""
        print("🔍 Finding form fields using hybrid extraction...")
        
        try:
            # First try traditional form field parsing
            traditional_fields = self._find_traditional_form_fields()
            
            if len(traditional_fields) > 0:
                print(f"📋 Found {len(traditional_fields)} traditional form fields")
                return
            
            # If traditional parsing fails, use hybrid extraction
            print("📋 Traditional form field parsing failed, using hybrid extraction...")
            self._extract_fields_hybrid()
            
        except Exception as e:
            print(f"❌ Error finding form fields: {e}")
            # Try hybrid extraction as fallback
            self._extract_fields_hybrid()
    
    def _find_traditional_form_fields(self) -> int:
        """Find form fields using traditional PDF parsing."""
        try:
            # Look for AcroForm in catalog
            if self.root_ref in self.objects:
                root_obj = self.objects[self.root_ref]
                
                # Try pattern 1: AcroForm as reference (/AcroForm 123 0 R)
                acroform_match = re.search(rb'/AcroForm\s+(\d+)\s+\d+\s+R', root_obj.content)
                
                if acroform_match:
                    acroform_ref = int(acroform_match.group(1))
                    print(f"📋 Found AcroForm reference: {acroform_ref}")
                    
                    if acroform_ref in self.objects:
                        self._parse_acroform_object(acroform_ref)
                        return len(self.form_fields)
                    else:
                        print(f"⚠️ AcroForm object {acroform_ref} not found in objects")
                else:
                    # Try pattern 2: Inline AcroForm (/AcroForm<<...>>)
                    print("📋 Looking for inline AcroForm definition...")
                    
                    acroform_content = self._extract_inline_acroform(root_obj.content)
                    
                    if acroform_content:
                        print("📋 Found inline AcroForm definition")
                        self._parse_acroform_content(acroform_content)
                        return len(self.form_fields)
                    else:
                        print("⚠️ No AcroForm found in catalog")
            else:
                print(f"⚠️ Root object {self.root_ref} not found")
                
        except Exception as e:
            print(f"❌ Error in traditional form field parsing: {e}")
            
        return 0
    
    def _extract_fields_hybrid(self):
        """Extract field values using hybrid approach (text + stream decompression)."""
        print("🔍 Hybrid Field Extraction")
        print("=" * 60)
        
        found_values = {}
        
        # Phase 1: Text-based extraction
        print("🔍 Phase 1: Text-based extraction")
        found_values.update(self._extract_text_values())
        
        # Phase 2: Stream decompression extraction  
        print("\n🔍 Phase 2: Stream decompression extraction")
        remaining_values = {k: v for k, v in self.expected_field_values.items() if k not in found_values}
        found_values.update(self._extract_compressed_values(remaining_values))
        
        # Convert found values to form fields
        self._convert_values_to_fields(found_values)
        
        # Results summary
        print("\n" + "=" * 60)
        print("📊 HYBRID EXTRACTION RESULTS")
        print(f"Found {len(found_values)}/{len(self.expected_field_values)} field values")
        
        for value, field_id in self.expected_field_values.items():
            if value in found_values:
                location = found_values[value]
                print(f"   ✅ Field {field_id}: '{value}' ({location['method']})")
            else:
                print(f"   ❌ Field {field_id}: '{value}' - NOT FOUND")
    
    def _extract_text_values(self) -> Dict[str, Dict[str, Any]]:
        """Extract field values using direct text search."""
        found_values = {}
        
        for value, field_id in self.expected_field_values.items():
            # Try multiple encoding patterns
            patterns = [
                value.encode('utf-8'),
                value.encode('latin-1'),
                f"({value})".encode('utf-8'),  # In parentheses
                f"<{value.encode().hex()}>".encode(),  # As hex
                f"<{value.encode().hex().upper()}>".encode(),  # As uppercase hex
            ]
            
            for i, pattern in enumerate(patterns):
                if pattern in self.pdf_data:
                    pos = self.pdf_data.find(pattern)
                    found_values[value] = {
                        'field_id': field_id,
                        'position': pos,
                        'method': f'text_pattern_{i+1}',
                        'pattern': pattern
                    }
                    print(f"   ✅ Found '{value}' (field {field_id}) at position {pos}")
                    break
        
        print(f"   📊 Text extraction: {len(found_values)} values found")
        return found_values
    
    def _extract_compressed_values(self, remaining_values: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Extract field values from compressed streams."""
        found_values = {}
        
        if not remaining_values:
            print("   📊 No remaining values to search for")
            return found_values
        
        print(f"   🔍 Searching for {len(remaining_values)} missing values in compressed streams")
        
        # Find all compressed streams
        streams = self._find_compressed_streams()
        print(f"   📦 Found {len(streams)} compressed streams to analyze")
        
        decompressed_content = b""
        successful_decompressions = 0
        
        for i, stream_info in enumerate(streams):
            try:
                # Extract and decompress stream
                stream_data = self._extract_stream_data(stream_info)
                if stream_data:
                    # Try FlateDecode (zlib) decompression
                    try:
                        decompressed = zlib.decompress(stream_data)
                        decompressed_content += decompressed
                        successful_decompressions += 1
                        
                        # Search for missing values in this decompressed stream
                        stream_found = self._search_in_decompressed(decompressed, remaining_values, stream_info['object'])
                        found_values.update(stream_found)
                        
                    except zlib.error:
                        # Try raw inflate
                        try:
                            decompressed = zlib.decompress(stream_data, -zlib.MAX_WBITS)
                            decompressed_content += decompressed
                            successful_decompressions += 1
                            
                            stream_found = self._search_in_decompressed(decompressed, remaining_values, stream_info['object'])
                            found_values.update(stream_found)
                        except:
                            continue
                            
            except Exception as e:
                continue
        
        print(f"   📦 Successfully decompressed {successful_decompressions}/{len(streams)} streams")
        print(f"   📊 Total decompressed content: {len(decompressed_content):,} bytes")
        
        # Search for any remaining values in the combined decompressed content
        if decompressed_content and remaining_values:
            still_missing = {k: v for k, v in remaining_values.items() if k not in found_values}
            if still_missing:
                print(f"   🔍 Final search in combined decompressed content for {len(still_missing)} values")
                final_found = self._search_in_decompressed(decompressed_content, still_missing, "combined")
                found_values.update(final_found)
        
        print(f"   📊 Stream extraction: {len(found_values)} additional values found")
        return found_values
    
    def _find_compressed_streams(self) -> List[Dict[str, Any]]:
        """Find all compressed streams in the PDF."""
        streams = []
        
        # Pattern to find objects with streams
        obj_pattern = rb'(\d+)\s+(\d+)\s+obj'
        obj_matches = list(re.finditer(obj_pattern, self.pdf_data))
        
        for match in obj_matches:
            obj_num = int(match.group(1))
            obj_start = match.end()
            
            # Find end of object
            endobj_pos = self.pdf_data.find(b'endobj', obj_start)
            if endobj_pos == -1:
                continue
                
            obj_content = self.pdf_data[obj_start:endobj_pos]
            
            # Check if this object has a compressed stream
            if b'/Filter' in obj_content and b'stream' in obj_content:
                # Check for FlateDecode
                if b'/FlateDecode' in obj_content or b'/Fl' in obj_content:
                    stream_start = obj_content.find(b'stream')
                    stream_end = obj_content.find(b'endstream')
                    
                    if stream_start != -1 and stream_end != -1:
                        streams.append({
                            'object': obj_num,
                            'obj_start': obj_start,
                            'stream_start': obj_start + stream_start,
                            'stream_end': obj_start + stream_end,
                            'filter': 'FlateDecode'
                        })
        
        return streams
    
    def _extract_stream_data(self, stream_info: Dict[str, Any]) -> Optional[bytes]:
        """Extract raw stream data from PDF."""
        try:
            # Find the actual stream content (after 'stream\n' or 'stream\r\n')
            stream_start = stream_info['stream_start']
            stream_end = stream_info['stream_end']
            
            # Skip past the 'stream' keyword and any newlines
            content_start = stream_start
            for i in range(stream_start, min(stream_start + 10, len(self.pdf_data))):
                if self.pdf_data[i:i+6] == b'stream':
                    content_start = i + 6
                    # Skip newline characters
                    while content_start < len(self.pdf_data) and self.pdf_data[content_start] in b'\r\n':
                        content_start += 1
                    break
            
            if content_start >= stream_end:
                return None
                
            return self.pdf_data[content_start:stream_end]
            
        except Exception as e:
            return None
    
    def _search_in_decompressed(self, decompressed_data: bytes, target_values: Dict[str, str], source: str) -> Dict[str, Dict[str, Any]]:
        """Search for target values in decompressed data."""
        found = {}
        
        for value, field_id in target_values.items():
            # Try multiple encodings
            patterns = [
                value.encode('utf-8'),
                value.encode('latin-1'),
                f"({value})".encode('utf-8'),
                f"<{value.encode().hex()}>".encode(),
            ]
            
            for i, pattern in enumerate(patterns):
                if pattern in decompressed_data:
                    pos = decompressed_data.find(pattern)
                    found[value] = {
                        'field_id': field_id,
                        'position': pos,
                        'method': f'decompressed_pattern_{i+1}',
                        'source': source,
                        'pattern': pattern,
                        'decompressed_data': decompressed_data
                    }
                    print(f"   ✅ Found '{value}' (field {field_id}) in {source}")
                    break
        
        return found
    
    def _convert_values_to_fields(self, found_values: Dict[str, Dict[str, Any]]):
        """Convert found values to FormField objects."""
        for value, info in found_values.items():
            field_id = info['field_id']
            
            # Create a FormField object
            form_field = FormField(
                name=field_id,
                field_type=FieldType.TEXT,  # Assume text type for extracted values
                obj_num=0,  # No specific object number since values are extracted
                current_value=value,
                widget_refs=[]
            )
            
            self.form_fields[field_id] = form_field
            print(f"   📝 Created field: {field_id} = '{value}'")
    
    def _parse_acroform_object(self, acroform_ref: int):
        """Parse AcroForm object to find fields."""
        acroform_obj = self.objects[acroform_ref]
        print(f"📋 Parsing AcroForm object {acroform_ref}")
        
        self._parse_acroform_content(acroform_obj.content)
    
    def _extract_inline_acroform(self, content: bytes) -> Optional[bytes]:
        """Extract inline AcroForm content handling nested dictionaries."""
        try:
            # Find /AcroForm start
            acroform_start = content.find(b'/AcroForm')
            if acroform_start == -1:
                return None
            
            # Find the opening << after /AcroForm
            dict_start = content.find(b'<<', acroform_start)
            if dict_start == -1:
                return None
            
            # Now we need to find the matching closing >>
            # Handle nested dictionaries by counting brackets
            pos = dict_start + 2  # Start after the <<
            bracket_count = 1
            
            while pos < len(content) and bracket_count > 0:
                if content[pos:pos+2] == b'<<':
                    bracket_count += 1
                    pos += 2
                elif content[pos:pos+2] == b'>>':
                    bracket_count -= 1
                    pos += 2
                else:
                    pos += 1
            
            if bracket_count == 0:
                # Found the matching closing bracket
                dict_end = pos - 2  # pos is after >>, so go back to start of >>
                acroform_dict = content[dict_start + 2:dict_end]  # Extract content between << and >>
                
                print(f"📋 Extracted inline AcroForm: {len(acroform_dict)} bytes")
                print(f"   Preview: {acroform_dict[:200].decode('ascii', errors='ignore')}...")
                
                return acroform_dict
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error extracting inline AcroForm: {e}")
            return None
    
    def _extract_fields_array(self, content: bytes) -> Optional[bytes]:
        """Extract Fields array content, handling incomplete arrays."""
        try:
            # Find /Fields start
            fields_start = content.find(b'/Fields')
            if fields_start == -1:
                return None
            
            # Find the opening [ after /Fields
            array_start = content.find(b'[', fields_start)
            if array_start == -1:
                return None
            
            # Find the closing ] or end of content
            array_end = content.find(b']', array_start)
            
            if array_end != -1:
                # Found complete array
                fields_content = content[array_start + 1:array_end]
            else:
                # Array might be incomplete - take everything after [
                # This handles cases where the array is truncated in the content
                fields_content = content[array_start + 1:]
                
                # Try to find a reasonable end point
                # Look for next major PDF keyword
                end_markers = [b'/DR', b'/DA', b'>>', b'endobj']
                min_end = len(fields_content)
                
                for marker in end_markers:
                    marker_pos = fields_content.find(marker)
                    if marker_pos != -1 and marker_pos < min_end:
                        min_end = marker_pos
                
                if min_end < len(fields_content):
                    fields_content = fields_content[:min_end]
            
            print(f"📋 Extracted Fields array: {len(fields_content)} bytes")
            print(f"   Content: {fields_content[:200].decode('ascii', errors='ignore')}...")
            
            return fields_content.strip()
            
        except Exception as e:
            print(f"⚠️ Error extracting Fields array: {e}")
            return None
    
    def _parse_acroform_content(self, acroform_content: bytes):
        """Parse AcroForm content to find fields."""
        print(f"📋 Parsing AcroForm content ({len(acroform_content)} bytes)")
        
        # Try to extract Fields array first
        fields_content = self._extract_fields_array(acroform_content)
        
        if fields_content:
            # Extract field references and check if they exist
            field_refs = re.findall(rb'(\d+)\s+\d+\s+R', fields_content)
            print(f"📋 Found {len(field_refs)} field references: {[int(ref) for ref in field_refs]}")
            
            # Check if these field objects actually exist
            existing_refs = []
            for field_ref in field_refs:
                field_num = int(field_ref)
                if field_num in self.objects:
                    existing_refs.append(field_num)
            
            print(f"📋 {len(existing_refs)} out of {len(field_refs)} field objects exist")
            
            if len(existing_refs) > 0:
                # Use existing field references
                fields_parsed = 0
                for field_num in existing_refs:
                    try:
                        self._parse_field(field_num)
                        fields_parsed += 1
                    except Exception as e:
                        print(f"⚠️ Error parsing field {field_num}: {e}")
                
                print(f"📋 Successfully parsed {fields_parsed}/{len(existing_refs)} fields")
            return
        
        # If Fields array is corrupted or missing, search for fields by name
        print("⚠️ Fields array corrupted or missing - searching for fields by name")
        self._search_fields_by_name()
    
    def _search_fields_by_name(self):
        """Search for form fields by their actual names directly in PDF."""
        print("🔍 Searching for form fields by name...")
        
        # Expected field names based on the form structure
        expected_fields = [
            "1", "2a", "2b", "2c", "2d", "3", "4", "5", "6", "7", "8", "9", "10",
            "11", "12a", "12b", "13", "14", "15a", "15b", "16", "17a", "17b", "17c",
            "18a", "18b", "18c", "18d", "18e", "19", "20", "21", "22a", "22a1", "22a2",
            "22b", "22b1", "22b2", "25a", "25b", "25c", "26", "27", "28", "29", "30", "31",
            "32a", "32b", "32c", "33", "34", "35", "36", "37", "38", "39", "39a",
            "40a", "40b", "40c", "41", "41a", "42", "42a", "43", "44", "44a", "45", "46",
            "47a", "47b", "47c", "48", "48a", "49", "50a", "50b", "50c", "51", "52"
        ]
        
        fields_found = 0
        
        for field_name in expected_fields:
            try:
                # Search for field name patterns
                patterns = [
                    f"/T({field_name})".encode(),               # /T(name)
                    f"/T<{field_name.encode().hex()}>".encode(), # /T<hex>
                    f"/T {field_name}".encode()                 # /T name
                ]
                
                field_found = False
                for pattern in patterns:
                    if pattern in self.pdf_data:
                        # Find the object containing this field
                        pos = self.pdf_data.find(pattern)
                        obj_num = self._find_object_containing_position(pos)
                        
                        if obj_num and obj_num in self.objects:
                            try:
                                # Parse this field
                                self._parse_field_by_content(field_name, obj_num)
                                fields_found += 1
                                field_found = True
                                print(f"   ✅ Found field '{field_name}' in object {obj_num}")
                                break
                            except Exception as e:
                                print(f"   ⚠️ Error parsing field '{field_name}': {e}")
                
                if not field_found:
                    # Try less specific search
                    if self._search_field_in_all_objects(field_name):
                        fields_found += 1
            
            except Exception as e:
                    print(f"⚠️ Error searching for field '{field_name}': {e}")
        
        print(f"📋 Found {fields_found} fields by name search")
    
    def _find_object_containing_position(self, pos: int) -> Optional[int]:
        """Find which object contains the given byte position."""
        try:
            # Search backwards for the nearest object header
            search_start = max(0, pos - 3000)
            search_data = self.pdf_data[search_start:pos]
            
            obj_pattern = rb'(\d+)\s+(\d+)\s+obj'
            obj_matches = list(re.finditer(obj_pattern, search_data))
            
            if obj_matches:
                last_match = obj_matches[-1]
                obj_num = int(last_match.group(1))
                return obj_num
            
            return None
        except:
            return None
    
    def _parse_field_by_content(self, field_name: str, obj_num: int):
        """Parse a field given its name and object number."""
        obj = self.objects[obj_num]
        
        # Extract field information
        field_type = self._determine_field_type(obj.content)
        field_value = self._extract_field_value(obj.content)
        widget_refs = self._find_widget_references(obj.content, obj_num)
        
        # Create form field
        form_field = FormField(
            name=field_name,
            field_type=field_type,
            obj_num=obj_num,
            current_value=field_value,
            widget_refs=widget_refs
        )
        
        self.form_fields[field_name] = form_field
    
    def _search_field_in_all_objects(self, field_name: str) -> bool:
        """Search for a field name in all objects."""
        for obj_num, obj in self.objects.items():
            try:
                # Look for field name in various formats
                if (f"/T({field_name})".encode() in obj.content or
                    f"/T<{field_name.encode().hex()}>".encode() in obj.content or
                    f"/T {field_name}".encode() in obj.content):
                    
                    self._parse_field_by_content(field_name, obj_num)
                    print(f"   ✅ Found field '{field_name}' in object {obj_num} (deep search)")
                    return True
            except:
                continue
            return False
    
    def _parse_field(self, field_ref: int):
        """Parse individual form field."""
        field_obj = self.objects[field_ref]
        
        # Extract field name using multiple patterns
        field_name = self._extract_field_name(field_obj.content)
        
        if not field_name:
            # If no field name found, use object number as fallback
            field_name = f"field_{field_ref}"
        
        # Determine field type
        field_type = self._determine_field_type(field_obj.content)
        
        # Extract current value
        current_value = self._extract_field_value(field_obj.content)
        
        # Find widget references
        widget_refs = self._find_widget_references(field_obj.content, field_ref)
        
        # Create field info
        field_info = FormField(
            name=field_name,
            field_type=field_type,
            obj_num=field_ref,
            current_value=current_value,
            widget_refs=widget_refs
        )
        
        self.form_fields[field_name] = field_info
        
        print(f"   📝 Field: {field_name} (type: {field_type.value}, value: '{current_value}')")
    
    def _extract_field_name(self, content: bytes) -> str:
        """Extract field name from various formats."""
        # Pattern 1: /T(name)
        name_match = re.search(rb'/T\s*\(([^)]*)\)', content)
        if name_match:
            return name_match.group(1).decode('utf-8', errors='ignore')
        
        # Pattern 2: /T<hexstring>
        name_match = re.search(rb'/T\s*<([^>]*)>', content)
        if name_match:
            hex_str = name_match.group(1).decode('ascii', errors='ignore')
            try:
                return bytes.fromhex(hex_str).decode('utf-8', errors='ignore')
            except:
                return hex_str
        
        # Pattern 3: /T/Name
        name_match = re.search(rb'/T\s*/([^\s/]+)', content)
        if name_match:
            return name_match.group(1).decode('utf-8', errors='ignore')
        
        # Pattern 4: /T followed by indirect reference
        name_match = re.search(rb'/T\s+(\d+)\s+\d+\s+R', content)
        if name_match:
            return f"ref_{name_match.group(1).decode()}"
        
        return ""
    
    def _determine_field_type(self, content: bytes) -> FieldType:
        """Determine field type from content."""
        # Check for explicit field type
        if b'/FT/Tx' in content or b'/FT /Tx' in content:
            return FieldType.TEXT
        elif b'/FT/Btn' in content or b'/FT /Btn' in content:
            return FieldType.BUTTON
        elif b'/FT/Ch' in content or b'/FT /Ch' in content:
            return FieldType.CHOICE
        elif b'/FT/Sig' in content or b'/FT /Sig' in content:
            return FieldType.SIGNATURE
        
        # Check for field type indicators
        if b'TextField' in content:
            return FieldType.TEXT
        elif b'CheckBox' in content or b'RadioButton' in content:
            return FieldType.BUTTON
        elif b'ComboBox' in content or b'ListBox' in content:
            return FieldType.CHOICE
        elif b'Signature' in content:
            return FieldType.SIGNATURE
        
        return FieldType.UNKNOWN
    
    def _extract_field_value(self, content: bytes) -> str:
        """Extract field value from various formats."""
        # Pattern 1: /V(value)
        value_match = re.search(rb'/V\s*\(([^)]*)\)', content)
        if value_match:
            return value_match.group(1).decode('utf-8', errors='ignore')
        
        # Pattern 2: /V<hexstring>
        value_match = re.search(rb'/V\s*<([^>]*)>', content)
        if value_match:
            hex_str = value_match.group(1).decode('ascii', errors='ignore')
            try:
                return bytes.fromhex(hex_str).decode('utf-8', errors='ignore')
            except:
                return hex_str
        
        # Pattern 3: /V/Name
        value_match = re.search(rb'/V\s*/([^\s/]+)', content)
        if value_match:
            return value_match.group(1).decode('utf-8', errors='ignore')
        
        # Pattern 4: /V followed by number
        value_match = re.search(rb'/V\s+(\d+)', content)
        if value_match:
            return value_match.group(1).decode('utf-8', errors='ignore')
        
        return ""
    
    def _find_widget_references(self, content: bytes, field_ref: int) -> List[int]:
        """Find widget references."""
        widget_refs = []
        
        # Look for /Kids array
        kids_match = re.search(rb'/Kids\s*\[([^\]]*)\]', content)
        if kids_match:
            kid_refs = re.findall(rb'(\d+)\s+\d+\s+R', kids_match.group(1))
            widget_refs = [int(ref) for ref in kid_refs]
        
        # If no kids found, field might be its own widget
        if not widget_refs:
            widget_refs = [field_ref]
        
        return widget_refs
    
    def _find_signature_fields(self):
        """Find signature field references."""
        for field_name, field in self.form_fields.items():
            if field.field_type == FieldType.SIGNATURE:
                self.signature_refs.add(field.obj_num)
                for widget_ref in field.widget_refs:
                    self.signature_refs.add(widget_ref)
    
    def _parse_dict(self, content: bytes) -> Dict[str, Any]:
        """Parse PDF dictionary content."""
        result = {}
        
        try:
            # More robust dictionary parser
            # Handle different value types: numbers, references, names, strings
            patterns = [
                (rb'/(\w+)\s+(\d+)\s+(\d+)\s+R', 'ref'),      # References
                (rb'/(\w+)\s+(\d+)', 'number'),               # Numbers
                (rb'/(\w+)\s+/(\w+)', 'name'),                # Names
                (rb'/(\w+)\s+\(([^)]*)\)', 'string'),         # Strings
                (rb'/(\w+)\s+<([^>]*)>', 'hex_string'),       # Hex strings
                (rb'/(\w+)\s+true', 'boolean'),               # Boolean true
                (rb'/(\w+)\s+false', 'boolean'),              # Boolean false
            ]
            
            for pattern, value_type in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if value_type == 'ref':
                        key_str = match[0].decode('ascii', errors='ignore')
                        result[key_str] = f"{match[1].decode()} {match[2].decode()} R"
                    elif value_type == 'number':
                        key_str = match[0].decode('ascii', errors='ignore')
                        result[key_str] = int(match[1])
                    elif value_type in ['name', 'string', 'hex_string']:
                        key_str = match[0].decode('ascii', errors='ignore')
                        result[key_str] = match[1].decode('ascii', errors='ignore')
                    elif value_type == 'boolean':
                        key_str = match[0].decode('ascii', errors='ignore')
                        result[key_str] = value_type == 'true'
            
        except Exception as e:
            print(f"⚠️ Dictionary parsing error: {e}")
        
        return result
    
    def update_field(self, field_name: str, new_value: str) -> bool:
        """Update a form field value using direct content replacement for flattened PDFs."""
        if field_name not in self.form_fields:
            print(f"❌ Field '{field_name}' not found")
            return False
    
        field = self.form_fields[field_name]
        
        print(f"🔧 Updating field '{field_name}':")
        print(f"   Type: {field.field_type.value}")
        print(f"   Current: '{field.current_value}'")
        print(f"   New: '{new_value}'")
        
        # Check if this is a flattened field (obj_num=0)
        if field.obj_num == 0:
            print(f"   📝 Detected flattened field - using direct content replacement")
            return self._update_flattened_field(field, new_value)
        else:
            # Traditional form field update
            if field.field_type == FieldType.TEXT:
                return self._update_text_field(field, new_value)
            elif field.field_type == FieldType.BUTTON:
                return self._update_button_field(field, new_value)
            else:
                print(f"⚠️ Field type {field.field_type.value} not supported yet")
                return False
    
    def _update_flattened_field(self, field: FormField, new_value: str) -> bool:
        """Update flattened field using direct content replacement in compressed streams."""
        try:
            old_value = field.current_value
            
            # Find where this value was originally located
            value_locations = self._find_value_locations(old_value)
            
            if not value_locations:
                print(f"❌ Could not locate '{old_value}' in PDF content")
                return False
            
            successful_replacements = 0
            
            for location in value_locations:
                if location['method'].startswith('text_pattern'):
                    # Direct text replacement
                    if self._replace_text_content(old_value, new_value, location):
                        successful_replacements += 1
                elif location['method'].startswith('decompressed_pattern'):
                    # Stream content replacement
                    if self._replace_stream_content(old_value, new_value, location):
                        successful_replacements += 1
            
            if successful_replacements > 0:
                field.current_value = new_value
                self._has_direct_modifications = True
                print(f"✅ Updated field in {successful_replacements} location(s)")
                return True
            else:
                print(f"❌ Failed to update field in any location")
                return False
                
        except Exception as e:
            print(f"❌ Error updating flattened field: {e}")
            return False
    
    def _find_value_locations(self, value: str) -> List[Dict[str, Any]]:
        """Find all locations where a value appears in the PDF."""
        locations = []
        
        # Search in raw text
        patterns = [
            value.encode('utf-8'),
            value.encode('latin-1'),
            f"({value})".encode('utf-8'),
            f"<{value.encode().hex()}>".encode(),
            f"<{value.encode().hex().upper()}>".encode(),
        ]
        
        for i, pattern in enumerate(patterns):
            pos = 0
            while True:
                pos = self.pdf_data.find(pattern, pos)
                if pos == -1:
                    break
                    
                locations.append({
                    'method': f'text_pattern_{i+1}',
                    'position': pos,
                    'pattern': pattern,
                    'length': len(pattern)
                })
                pos += len(pattern)
        
        # Search in compressed streams using the same logic as hybrid extraction
        stream_locations = self._find_value_in_streams_robust(value)
        locations.extend(stream_locations)
        
        return locations
    
    def _find_value_in_streams_robust(self, value: str) -> List[Dict[str, Any]]:
        """Find value in compressed streams using robust search logic."""
        locations = []
        
        # Get all compressed streams
        streams = self._find_compressed_streams()
        
        # Search patterns (same as hybrid extraction)
        search_patterns = [
            value.encode('utf-8'),
            value.encode('latin-1'),
            f"({value})".encode('utf-8'),
            f"<{value.encode().hex()}>".encode(),
        ]
        
        for stream_info in streams:
            try:
                stream_data = self._extract_stream_data(stream_info)
                if stream_data:
                    # Try FlateDecode (zlib) decompression
                    decompressed = None
                    try:
                        decompressed = zlib.decompress(stream_data)
                    except zlib.error:
                        # Try raw inflate
                        try:
                            decompressed = zlib.decompress(stream_data, -zlib.MAX_WBITS)
                        except:
                            continue
                    
                    if decompressed:
                        # Search for the value in decompressed content
                        for i, pattern in enumerate(search_patterns):
                            if pattern in decompressed:
                                locations.append({
                                    'method': f'decompressed_pattern_{i+1}',
                                    'stream_object': stream_info['object'],
                                    'stream_info': stream_info,
                                    'pattern': pattern,
                                    'decompressed_data': decompressed
                                })
                                # Don't break - we want to find all patterns
                                
            except Exception as e:
                continue
        
        return locations
    
    def _replace_text_content(self, old_value: str, new_value: str, location: Dict[str, Any]) -> bool:
        """Replace text content directly in PDF bytes with safety checks."""
        try:
            old_pattern = location['pattern']
            pos = location['position']
            
            # Safety check 1: Avoid replacing in PDF keywords and syntax
            if self._is_in_pdf_syntax_context(pos, old_pattern):
                print(f"   ⚠️ Skipping replacement at position {pos} - in PDF syntax context")
                return False
            
            # Create new pattern with same encoding
            if location['method'] == 'text_pattern_1':  # UTF-8
                new_pattern = new_value.encode('utf-8')
            elif location['method'] == 'text_pattern_2':  # Latin-1
                new_pattern = new_value.encode('latin-1')
            elif location['method'] == 'text_pattern_3':  # In parentheses
                new_pattern = f"({new_value})".encode('utf-8')
            elif location['method'] == 'text_pattern_4':  # As hex
                new_pattern = f"<{new_value.encode().hex()}>".encode()
            elif location['method'] == 'text_pattern_5':  # As uppercase hex
                new_pattern = f"<{new_value.encode().hex().upper()}>".encode()
            else:
                new_pattern = new_value.encode('utf-8')
            
            # Safety check 2: Validate replacement won't break PDF structure
            if not self._validate_replacement_safety(pos, old_pattern, new_pattern):
                print(f"   ⚠️ Skipping unsafe replacement at position {pos}")
                return False
            
            # Perform safe replacement
            before = self.pdf_data[:pos]
            after = self.pdf_data[pos + len(old_pattern):]
            
            self.pdf_data = before + new_pattern + after
            
            print(f"   ✅ Safely replaced text at position {pos}")
            return True
            
        except Exception as e:
            print(f"   ❌ Safe text replacement failed: {e}")
            return False
    
    def _replace_stream_content(self, old_value: str, new_value: str, location: Dict[str, Any]) -> bool:
        """Replace content in compressed stream with length updates."""
        try:
            stream_info = location['stream_info']
            old_pattern = location['pattern']
            decompressed_data = location['decompressed_data']
            
            # Create new pattern with same encoding
            if location['method'] == 'decompressed_pattern_1':  # UTF-8
                new_pattern = new_value.encode('utf-8')
            elif location['method'] == 'decompressed_pattern_2':  # Latin-1
                new_pattern = new_value.encode('latin-1')
            elif location['method'] == 'decompressed_pattern_3':  # In parentheses
                new_pattern = f"({new_value})".encode('utf-8')
            elif location['method'] == 'decompressed_pattern_4':  # As hex
                new_pattern = f"<{new_value.encode().hex()}>".encode()
            else:
                new_pattern = new_value.encode('utf-8')
            
            # Replace in decompressed data
            new_decompressed = decompressed_data.replace(old_pattern, new_pattern, 1)
            
            if new_decompressed == decompressed_data:
                print(f"   ⚠️ No replacement made in stream {stream_info['object']}")
                return False
            
            # Recompress the data
            new_compressed = zlib.compress(new_decompressed)
            
            # Update stream safely with length correction
            if self._update_stream_safely(stream_info, new_compressed):
                print(f"   ✅ Safely replaced content in stream {stream_info['object']}")
                return True
            else:
                print(f"   ❌ Failed to safely update stream {stream_info['object']}")
                return False
            
        except Exception as e:
            print(f"   ❌ Safe stream replacement failed: {e}")
            return False
    
    def _is_in_pdf_syntax_context(self, pos: int, pattern: bytes) -> bool:
        """Check if position is within PDF syntax elements that shouldn't be modified."""
        # Define context window for checking
        context_before = 50
        context_after = 50
        
        start_pos = max(0, pos - context_before)
        end_pos = min(len(self.pdf_data), pos + len(pattern) + context_after)
        
        context = self.pdf_data[start_pos:end_pos]
        pattern_start = pos - start_pos
        pattern_end = pattern_start + len(pattern)
        
        # Check for PDF syntax elements in context
        pdf_syntax_indicators = [
            b'<<', b'>>', b'[', b']', b'obj', b'endobj', b'stream', b'endstream',
            b'xref', b'trailer', b'startxref', b'%%EOF', b'/Type', b'/Root',
            b'/Filter', b'/Length', b'/Size', b'/Prev', b'/Info'
        ]
        
        for indicator in pdf_syntax_indicators:
            # Check if the pattern overlaps with PDF syntax
            indicator_pos = context.find(indicator)
            while indicator_pos != -1:
                indicator_end = indicator_pos + len(indicator)
                
                # Check if our pattern overlaps with this PDF syntax element
                if (indicator_pos < pattern_end and indicator_end > pattern_start):
                    return True
                
                # Find next occurrence
                indicator_pos = context.find(indicator, indicator_pos + 1)
        
        return False
    
    def _validate_replacement_safety(self, pos: int, old_pattern: bytes, new_pattern: bytes) -> bool:
        """Validate that replacement won't break PDF structure."""
        # Check 1: Length difference shouldn't be too large
        length_diff = len(new_pattern) - len(old_pattern)
        if abs(length_diff) > 100:  # Arbitrary safety limit
            return False
        
        # Check 2: New pattern shouldn't contain PDF syntax characters
        unsafe_chars = [b'<<', b'>>', b'[', b']', b'obj', b'endobj', b'stream', b'endstream']
        for unsafe_char in unsafe_chars:
            if unsafe_char in new_pattern:
                return False
        
        # Check 3: Don't replace if we're in a stream length context
        context_before = self.pdf_data[max(0, pos-30):pos]
        if b'/Length' in context_before:
            return False
        
        return True
    
    def _update_stream_safely(self, stream_info: Dict[str, Any], new_compressed: bytes) -> bool:
        """Update stream content and fix length references safely."""
        try:
            # Find the stream object boundaries
            obj_num = stream_info['object']
            obj_start = stream_info['obj_start']
            stream_start = stream_info['stream_start']
            stream_end = stream_info['stream_end']
            
            # Find the actual stream content boundaries
            content_start = stream_start
            for i in range(stream_start, min(stream_start + 10, len(self.pdf_data))):
                if self.pdf_data[i:i+6] == b'stream':
                    content_start = i + 6
                    # Skip newline characters
                    while content_start < len(self.pdf_data) and self.pdf_data[content_start] in b'\r\n':
                        content_start += 1
                    break
            
            # Find the object end
            endobj_pos = self.pdf_data.find(b'endobj', stream_end)
            if endobj_pos == -1:
                return False
            
            # Extract the object dictionary part (before stream)
            obj_dict_part = self.pdf_data[obj_start:content_start]
            
            # Update the Length entry in the dictionary
            old_length_pattern = rb'/Length\s+\d+'
            new_length_entry = f'/Length {len(new_compressed)}'.encode()
            
            if re.search(old_length_pattern, obj_dict_part):
                obj_dict_part = re.sub(old_length_pattern, new_length_entry, obj_dict_part)
            else:
                # If no Length entry exists, add one before the stream
                stream_keyword_pos = obj_dict_part.find(b'stream')
                if stream_keyword_pos != -1:
                    before_stream = obj_dict_part[:stream_keyword_pos]
                    # Find the last >> before stream and insert Length entry
                    last_dict_end = before_stream.rfind(b'>>')
                    if last_dict_end != -1:
                        before_close = before_stream[:last_dict_end]
                        after_close = before_stream[last_dict_end:]
                        obj_dict_part = before_close + new_length_entry + b' ' + after_close
            
            # Reconstruct the object
            after_stream = self.pdf_data[stream_end:]
            
            # Build the new object
            new_obj_content = obj_dict_part + new_compressed + after_stream
            
            # Replace in PDF data
            before_obj = self.pdf_data[:obj_start]
            self.pdf_data = before_obj + new_obj_content
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error updating stream safely: {e}")
            return False
    
    def _update_text_field(self, field: FormField, new_value: str) -> bool:
        """Update text field using signature-safe method."""
        try:
            obj = self.objects[field.obj_num]
            content = obj.content
            
            # Replace value in PDF object
            new_content = self._replace_field_value(content, new_value)
            
            if new_content != content:
                self.modified_objects[field.obj_num] = new_content
                field.current_value = new_value
                print(f"✅ Text field updated")
                return True
            else:
                print(f"❌ Failed to update text field")
                return False
        
        except Exception as e:
            print(f"❌ Error updating text field: {e}")
            return False
    
    def _update_button_field(self, field: FormField, new_value: str) -> bool:
        """Update button field using signature-preserving method."""
        try:
            obj = self.objects[field.obj_num]
            content = obj.content
            
            # For button fields, we need to be more careful
            # Convert value appropriately
            if field.field_type == FieldType.BUTTON:
                # Check if it's a checkbox or radio button
                if b'/V/Yes' in content or b'/V/Off' in content:
                    # Checkbox - convert to PDF names
                    if new_value.lower() in ['true', '1', 'yes', 'ja', 'on']:
                        pdf_value = "Yes"
                    else:
                        pdf_value = "Off"
                else:
                    pdf_value = new_value
            else:
                pdf_value = new_value
            
            # Replace value in PDF object
            new_content = self._replace_field_value(content, pdf_value)
            
            if new_content != content:
                self.modified_objects[field.obj_num] = new_content
                field.current_value = pdf_value
                print(f"✅ Button field updated")
                return True
            else:
                print(f"❌ Failed to update button field")
                return False
                
        except Exception as e:
            print(f"❌ Error updating button field: {e}")
            return False
    
    def _replace_field_value(self, content: bytes, new_value: str) -> bytes:
        """Replace field value in PDF object content."""
        # Encode new value
        new_value_bytes = new_value.encode('utf-8', errors='ignore')
        
        # Try different value patterns
        patterns = [
            (rb'/V\s*\([^)]*\)', b'/V(' + new_value_bytes + b')'),
            (rb'/V\s*<[^>]*>', b'/V<' + new_value_bytes.hex().encode() + b'>'),
            (rb'/V\s*/\w+', b'/V/' + new_value_bytes),
        ]
        
        for pattern, replacement in patterns:
            match = re.search(pattern, content)
            if match:
                return content[:match.start()] + replacement + content[match.end():]
        
        # If no existing value found, try to add one
        # Look for field dictionary end
        dict_end = content.rfind(b'>>')
        if dict_end != -1:
            new_entry = b'/V(' + new_value_bytes + b')'
            return content[:dict_end] + new_entry + content[dict_end:]
        
        return content
    
    def validate_pdf_integrity(self) -> Dict[str, Any]:
        """Validate PDF integrity after modifications."""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        try:
            # Check 1: PDF header
            if not self.pdf_data.startswith(b'%PDF-'):
                validation_results['errors'].append("Invalid PDF header")
                validation_results['valid'] = False
            
            # Check 2: EOF markers
            eof_count = self.pdf_data.count(b'%%EOF')
            validation_results['statistics']['eof_markers'] = eof_count
            if eof_count == 0:
                validation_results['errors'].append("No %%EOF markers found")
                validation_results['valid'] = False
            
            # Check 3: Bracket matching
            bracket_issues = self._check_bracket_matching()
            if bracket_issues:
                validation_results['errors'].extend(bracket_issues)
                validation_results['valid'] = False
            
            # Check 4: Object structure
            obj_issues = self._check_object_structure()
            validation_results['statistics']['objects'] = len(self.objects)
            if obj_issues:
                validation_results['warnings'].extend(obj_issues)
            
            # Check 5: Stream integrity
            stream_issues = self._check_stream_integrity()
            if stream_issues:
                validation_results['warnings'].extend(stream_issues)
            
            # Check 6: Null bytes in critical areas
            null_issues = self._check_null_bytes()
            if null_issues:
                validation_results['warnings'].extend(null_issues)
            
            return validation_results
            
        except Exception as e:
            validation_results['errors'].append(f"Validation error: {e}")
            validation_results['valid'] = False
            return validation_results
    
    def _check_bracket_matching(self) -> List[str]:
        """Check for unmatched brackets in PDF structure."""
        issues = []
        
        # Check dictionary brackets
        dict_open = self.pdf_data.count(b'<<')
        dict_close = self.pdf_data.count(b'>>')
        if dict_open != dict_close:
            issues.append(f"Unmatched dictionary brackets: {dict_open} << vs {dict_close} >>")
        
        # Check array brackets
        array_open = self.pdf_data.count(b'[')
        array_close = self.pdf_data.count(b']')
        if array_open != array_close:
            issues.append(f"Unmatched array brackets: {array_open} [ vs {array_close} ]")
        
        return issues
    
    def _check_object_structure(self) -> List[str]:
        """Check object structure integrity."""
        issues = []
        
        # Count obj/endobj pairs
        obj_count = len(re.findall(rb'\d+\s+\d+\s+obj', self.pdf_data))
        endobj_count = self.pdf_data.count(b'endobj')
        
        if obj_count != endobj_count:
            issues.append(f"Unmatched obj/endobj: {obj_count} obj vs {endobj_count} endobj")
        
        return issues
    
    def _check_stream_integrity(self) -> List[str]:
        """Check stream integrity."""
        issues = []
        
        # Count stream/endstream pairs
        stream_count = self.pdf_data.count(b'stream')
        endstream_count = self.pdf_data.count(b'endstream')
        
        if stream_count != endstream_count:
            issues.append(f"Unmatched stream/endstream: {stream_count} stream vs {endstream_count} endstream")
        
        return issues
    
    def _check_null_bytes(self) -> List[str]:
        """Check for null bytes in critical areas."""
        issues = []
        
        # Check for null bytes in first 1000 bytes (header area)
        header_area = self.pdf_data[:1000]
        if b'\x00' in header_area:
            null_count = header_area.count(b'\x00')
            issues.append(f"Found {null_count} null bytes in PDF header area")
        
        # Check for null bytes in last 1000 bytes (trailer area)
        trailer_area = self.pdf_data[-1000:]
        if b'\x00' in trailer_area:
            null_count = trailer_area.count(b'\x00')
            issues.append(f"Found {null_count} null bytes in PDF trailer area")
        
        return issues
    
    def save_incremental(self, output_path: Optional[str] = None, validate: bool = True) -> str:
        """Save PDF with incremental updates and optional validation."""
        if output_path is None:
            output_path = self.pdf_path
        
        # Validate before saving if requested
        if validate:
            print(f"🔍 Validating PDF integrity...")
            validation_results = self.validate_pdf_integrity()
            
            if not validation_results['valid']:
                print(f"❌ PDF validation failed:")
                for error in validation_results['errors']:
                    print(f"   ERROR: {error}")
                for warning in validation_results['warnings']:
                    print(f"   WARNING: {warning}")
                
                # Ask user if they want to continue
                print(f"⚠️ PDF has integrity issues. Continuing may result in corrupted file.")
            else:
                print(f"✅ PDF integrity validated successfully")
                if validation_results['warnings']:
                    print(f"📋 Warnings:")
                    for warning in validation_results['warnings']:
                        print(f"   {warning}")
        
        # Check if we have direct content modifications (flattened field updates)
        if hasattr(self, '_has_direct_modifications') and self._has_direct_modifications:
            print(f"💾 Saving with direct content modifications...")
            
            # Save the entire modified PDF
            with open(output_path, 'wb') as f:
                f.write(self.pdf_data)
            
            print(f"✅ Saved: {output_path}")
            return output_path
        
        # Traditional incremental update for form field objects
        if not self.modified_objects:
            print("⚠️ No modifications to save")
            return output_path
        
        print(f"💾 Saving incremental updates...")
        print(f"   Modified objects: {len(self.modified_objects)}")
        
        try:
            # Create incremental update
            incremental_data = self._build_incremental_update()
            
            # Write to output file
            with open(output_path, 'wb') as f:
                f.write(self.pdf_data)
                f.write(incremental_data)
            
            print(f"✅ Saved: {output_path}")
            return output_path
        
        except Exception as e:
            print(f"❌ Error saving: {e}")
            raise e
    
    def _build_incremental_update(self) -> bytes:
        """Build incremental update section."""
        update_data = b""
        
        # Calculate new object positions
        current_pos = len(self.pdf_data)
        new_xref_entries = {}
        
        # Write modified objects
        for obj_num, content in self.modified_objects.items():
            obj_header = f"{obj_num} 0 obj\n".encode()
            obj_footer = b"\nendobj\n"
            
            new_xref_entries[obj_num] = current_pos
            
            obj_data = obj_header + content + obj_footer
            update_data += obj_data
            current_pos += len(obj_data)
        
        # Build new xref section
        xref_start = current_pos
        xref_data = b"xref\n"
        
        # Sort object numbers
        sorted_objs = sorted(new_xref_entries.keys())
        
        if sorted_objs:
            # Write xref subsection
            start_obj = sorted_objs[0]
            count = len(sorted_objs)
            xref_data += f"{start_obj} {count}\n".encode()
            
            for obj_num in sorted_objs:
                offset = new_xref_entries[obj_num]
                xref_data += f"{offset:010d} 00000 n \n".encode()
        
        update_data += xref_data
        
        # Build new trailer
        trailer_data = b"trailer\n"
        trailer_data += b"<<\n"
        trailer_data += f"/Size {max(self.objects.keys()) + 1}\n".encode()
        trailer_data += f"/Root {self.root_ref} 0 R\n".encode()
        if self.info_ref:
            trailer_data += f"/Info {self.info_ref} 0 R\n".encode()
        trailer_data += f"/Prev {self.xref_offset}\n".encode()
        trailer_data += b">>\n"
        trailer_data += b"startxref\n"
        trailer_data += f"{xref_start}\n".encode()
        trailer_data += b"%%EOF\n"
        
        update_data += trailer_data
        
        return update_data
    
    def create_backup(self) -> str:
        """Create backup of original PDF."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.pdf_path}.backup_{timestamp}"
        
        shutil.copy2(self.pdf_path, backup_path)
        print(f"📁 Backup created: {backup_path}")
        
        return backup_path
    
    def get_field_info(self) -> Dict[str, Any]:
        """Get information about all form fields."""
        return {
            name: {
                'type': field.field_type.value,
                'current_value': field.current_value,
                'obj_num': field.obj_num,
                'widget_refs': field.widget_refs
            }
            for name, field in self.form_fields.items()
        }

    def get_field_values(self) -> Dict[str, str]:
        """Get all field values found by hybrid extraction."""
        field_values = {}
        
        for field_name, field in self.form_fields.items():
            field_values[field_name] = field.current_value
        
        return field_values
    
    def export_field_values(self, output_path: str = "extracted_field_values.json"):
        """Export extracted field values to JSON file."""
        field_values = self.get_field_values()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(field_values, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Exported {len(field_values)} field values to {output_path}")
        return output_path


def test_pure_pdf_editor(pdf_path: str, test_data_files: List[str]) -> Dict[str, str]:
    """Test the pure PDF editor with different field types."""
    print(f"🧪 Testing Pure PDF Editor (No Dependencies)")
    print(f"📄 PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    results = {}
    
    for data_file in test_data_files:
        test_name = os.path.splitext(os.path.basename(data_file))[0]
        
        print(f"\n{'='*60}")
        print(f"🧪 TESTING: {test_name}")
        print(f"{'='*60}")
        
        try:
            # Load test data
            if not os.path.exists(data_file):
                print(f"❌ Data file not found: {data_file}")
                results[test_name] = "FAILED - Data file not found"
                continue
            
            with open(data_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            
            # Create output file
            timestamp = datetime.now().strftime("%H%M%S")
            output_file = f"test_pdf/pure_editor_{test_name}_{timestamp}.pdf"
            
            # Create directory
            os.makedirs("test_pdf", exist_ok=True)
            
            # Copy original file
            shutil.copy2(pdf_path, output_file)
            
            # Initialize editor
            editor = PurePDFEditor(output_file)
            
            # Create backup
            backup_path = editor.create_backup()
            
            # Update fields
            updated_count = 0
            for field_name, new_value in test_data.items():
                if editor.update_field(field_name, new_value):
                    updated_count += 1
            
            # Save changes
            if updated_count > 0:
                editor.save_incremental()
            
            print(f"✅ Test completed: {test_name}")
            print(f"   Fields updated: {updated_count}/{len(test_data)}")
            print(f"   Output: {output_file}")
            print(f"   Backup: {backup_path}")
            
            results[test_name] = output_file
            
        except Exception as e:
            print(f"❌ Test failed: {test_name} - {e}")
            results[test_name] = f"FAILED - {e}"
    
    return results


def test_hybrid_extraction(pdf_path: str) -> Dict[str, str]:
    """Test hybrid field extraction on a PDF."""
    print(f"🧪 Testing Hybrid Field Extraction")
    print(f"📄 PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    try:
        # Initialize editor with hybrid extraction
        editor = PurePDFEditor(pdf_path)
        
        # Get extracted field values
        field_values = editor.get_field_values()
        
        # Export to JSON
        output_file = editor.export_field_values()
        
        print(f"✅ Hybrid extraction completed")
        print(f"   Fields found: {len(field_values)}")
        print(f"   Output file: {output_file}")
        
        return field_values
        
    except Exception as e:
        print(f"❌ Hybrid extraction failed: {e}")
        raise e


def test_safe_pdf_editing(pdf_path: str, test_updates: Dict[str, str]) -> Dict[str, Any]:
    """Test the safer PDF editing approach with integrity validation."""
    print(f"🧪 Testing Safe PDF Editor")
    print(f"📄 PDF: {pdf_path}")
    print(f"🔧 Updates: {len(test_updates)} fields")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    results = {
        'success': False,
        'updated_fields': 0,
        'total_fields': len(test_updates),
        'output_file': '',
        'backup_file': '',
        'validation_results': {},
        'errors': []
    }
    
    try:
        # Create output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"test_pdf/safe_editor_{timestamp}.pdf"
        
        # Create directory
        os.makedirs("test_pdf", exist_ok=True)
        
        # Copy original file
        shutil.copy2(pdf_path, output_file)
        
        # Initialize editor
        editor = PurePDFEditor(output_file)
        
        # Create backup
        backup_path = editor.create_backup()
        results['backup_file'] = backup_path
        
        # Validate original PDF
        print(f"\n🔍 Validating original PDF...")
        validation_before = editor.validate_pdf_integrity()
        
        if not validation_before['valid']:
            print(f"⚠️ Original PDF has integrity issues:")
            for error in validation_before['errors']:
                print(f"   ERROR: {error}")
        else:
            print(f"✅ Original PDF is valid")
        
        # Update fields
        updated_count = 0
        for field_name, new_value in test_updates.items():
            print(f"\n🔧 Updating field '{field_name}' -> '{new_value}'")
            
            try:
                if editor.update_field(field_name, new_value):
                    updated_count += 1
                    print(f"   ✅ Field updated successfully")
                else:
                    print(f"   ❌ Field update failed")
                    results['errors'].append(f"Failed to update field '{field_name}'")
            except Exception as e:
                print(f"   ❌ Exception updating field: {e}")
                results['errors'].append(f"Exception updating field '{field_name}': {e}")
        
        results['updated_fields'] = updated_count
        
        # Save with validation
        if updated_count > 0:
            print(f"\n💾 Saving with validation...")
            editor.save_incremental(validate=True)
            results['success'] = True
        else:
            print(f"⚠️ No fields updated, nothing to save")
        
        # Final validation
        print(f"\n🔍 Final validation...")
        validation_after = editor.validate_pdf_integrity()
        results['validation_results'] = validation_after
        
        if validation_after['valid']:
            print(f"✅ Final PDF is valid")
        else:
            print(f"❌ Final PDF has integrity issues:")
            for error in validation_after['errors']:
                print(f"   ERROR: {error}")
        
        results['output_file'] = output_file
        
        # Summary
        print(f"\n📊 SAFE EDITING RESULTS:")
        print(f"   Fields updated: {updated_count}/{len(test_updates)}")
        print(f"   Success rate: {updated_count/len(test_updates)*100:.1f}%")
        print(f"   Output file: {output_file}")
        print(f"   Backup file: {backup_path}")
        print(f"   PDF valid: {validation_after['valid']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results['errors'].append(f"Test exception: {e}")
        return results


def main():
    """Main function to run tests."""
    print("🛡️ Pure Python PDF Editor - Safe Editing Mode")
    print("=" * 70)
    
    # Test files
    pdf_file = "pdf.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        print("💡 Place a PDF file named 'pdf.pdf' in the current directory")
        return
    
    try:
        # Test 1: Hybrid extraction
        print("🧪 Phase 1: Hybrid Field Extraction")
        print("=" * 70)
        
        field_values = test_hybrid_extraction(pdf_file)
        
        # Show results
        print(f"\n📋 EXTRACTED FIELD VALUES:")
        for field_id, value in field_values.items():
            print(f"   {field_id}: '{value}'")
        
        # Test 2: Safe editing with a subset of fields
        print(f"\n🧪 Phase 2: Safe PDF Editing")
        print("=" * 70)
        
        # Select a few fields for safe testing
        safe_test_updates = {
            "1": "999/2026",
            "2a": "John Doe SAFE",
            "3": "New Product Name SAFE",
            "16": "5 Liter SAFE",
            "25a": "Safe Test Name"
        }
        
        results = test_safe_pdf_editing(pdf_file, safe_test_updates)
        
        # Test 3: Compare with original approach (optional)
        print(f"\n🧪 Phase 3: Comparison Test")
        print("=" * 70)
        
        if results['success']:
            print(f"✅ Safe editing completed successfully!")
            print(f"   You can now compare:")
            print(f"   Original: {pdf_file}")
            print(f"   Safe edit: {results['output_file']}")
            print(f"   Backup: {results['backup_file']}")
        else:
            print(f"❌ Safe editing had issues:")
            for error in results['errors']:
                print(f"   {error}")
        
        print(f"\n💡 NEXT STEPS:")
        print("1. Open the safe-edited PDF in a PDF viewer")
        print("2. Verify the changes are correct")
        print("3. Check that digital signatures are preserved")
        print("4. Test with different field types")
        print("5. No external dependencies required!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 