#!/usr/bin/env python3
"""
Hybrid Field Extractor
Combines text-based extraction with stream decompression to find field values
"""
import re
import zlib
import json
from typing import Dict, List, Any, Optional

def extract_all_field_values(pdf_path: str):
    """Extract field values using both text search and stream decompression."""
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    print(f"🔍 Hybrid Field Extraction: {pdf_path}")
    print(f"📊 File size: {len(pdf_data):,} bytes")
    print("=" * 60)
    
    # Expected field values from form_fields.json
    expected_values = {
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
    
    found_values = {}
    
    # Phase 1: Text-based extraction
    print("🔍 Phase 1: Text-based extraction")
    found_values.update(extract_text_values(pdf_data, expected_values))
    
    # Phase 2: Stream decompression extraction
    print("\n🔍 Phase 2: Stream decompression extraction")
    remaining_values = {k: v for k, v in expected_values.items() if k not in found_values}
    found_values.update(extract_compressed_values(pdf_data, remaining_values))
    
    # Results summary
    print("\n" + "=" * 60)
    print("📊 EXTRACTION RESULTS")
    print(f"Found {len(found_values)}/{len(expected_values)} field values")
    
    for value, field_id in expected_values.items():
        if value in found_values:
            location = found_values[value]
            print(f"   ✅ Field {field_id}: '{value}' ({location['method']} at {location['position']})")
        else:
            print(f"   ❌ Field {field_id}: '{value}' - NOT FOUND")
    
    return found_values

def extract_text_values(pdf_data: bytes, expected_values: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    """Extract field values using direct text search."""
    found_values = {}
    
    for value, field_id in expected_values.items():
        # Try multiple encoding patterns
        patterns = [
            value.encode('utf-8'),
            value.encode('latin-1'),
            f"({value})".encode('utf-8'),  # In parentheses
            f"<{value.encode().hex()}>".encode(),  # As hex
            f"<{value.encode().hex().upper()}>".encode(),  # As uppercase hex
        ]
        
        for i, pattern in enumerate(patterns):
            if pattern in pdf_data:
                pos = pdf_data.find(pattern)
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

def extract_compressed_values(pdf_data: bytes, remaining_values: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    """Extract field values from compressed streams."""
    found_values = {}
    
    if not remaining_values:
        print("   📊 No remaining values to search for")
        return found_values
    
    print(f"   🔍 Searching for {len(remaining_values)} missing values in compressed streams")
    
    # Find all compressed streams
    streams = find_compressed_streams(pdf_data)
    print(f"   📦 Found {len(streams)} compressed streams to analyze")
    
    decompressed_content = b""
    successful_decompressions = 0
    
    for i, stream_info in enumerate(streams):
        try:
            # Extract and decompress stream
            stream_data = extract_stream_data(pdf_data, stream_info)
            if stream_data:
                # Try FlateDecode (zlib) decompression
                try:
                    decompressed = zlib.decompress(stream_data)
                    decompressed_content += decompressed
                    successful_decompressions += 1
                    
                    # Search for missing values in this decompressed stream
                    stream_found = search_in_decompressed(decompressed, remaining_values, stream_info['object'])
                    found_values.update(stream_found)
                    
                except zlib.error:
                    # Try raw inflate
                    try:
                        decompressed = zlib.decompress(stream_data, -zlib.MAX_WBITS)
                        decompressed_content += decompressed
                        successful_decompressions += 1
                        
                        stream_found = search_in_decompressed(decompressed, remaining_values, stream_info['object'])
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
            final_found = search_in_decompressed(decompressed_content, still_missing, "combined")
            found_values.update(final_found)
    
    print(f"   📊 Stream extraction: {len(found_values)} additional values found")
    return found_values

def find_compressed_streams(pdf_data: bytes) -> List[Dict[str, Any]]:
    """Find all compressed streams in the PDF."""
    streams = []
    
    # Pattern to find objects with streams
    obj_pattern = rb'(\d+)\s+(\d+)\s+obj'
    obj_matches = list(re.finditer(obj_pattern, pdf_data))
    
    for match in obj_matches:
        obj_num = int(match.group(1))
        obj_start = match.end()
        
        # Find end of object
        endobj_pos = pdf_data.find(b'endobj', obj_start)
        if endobj_pos == -1:
            continue
            
        obj_content = pdf_data[obj_start:endobj_pos]
        
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

def extract_stream_data(pdf_data: bytes, stream_info: Dict[str, Any]) -> Optional[bytes]:
    """Extract raw stream data from PDF."""
    try:
        # Find the actual stream content (after 'stream\n' or 'stream\r\n')
        stream_start = stream_info['stream_start']
        stream_end = stream_info['stream_end']
        
        # Skip past the 'stream' keyword and any newlines
        content_start = stream_start
        for i in range(stream_start, min(stream_start + 10, len(pdf_data))):
            if pdf_data[i:i+6] == b'stream':
                content_start = i + 6
                # Skip newline characters
                while content_start < len(pdf_data) and pdf_data[content_start] in b'\r\n':
                    content_start += 1
                break
        
        if content_start >= stream_end:
            return None
            
        return pdf_data[content_start:stream_end]
        
    except Exception as e:
        return None

def search_in_decompressed(decompressed_data: bytes, target_values: Dict[str, str], source: str) -> Dict[str, Dict[str, Any]]:
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
                    'pattern': pattern
                }
                print(f"   ✅ Found '{value}' (field {field_id}) in {source}")
                break
    
    return found

if __name__ == "__main__":
    extract_all_field_values("pdf.pdf") 