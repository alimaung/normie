#!/usr/bin/env python3
"""
PDF Corruption Debug Script
Analyzes PDF files for structural corruption and integrity issues
"""
import os
import re
import zlib
from typing import List, Dict, Any, Optional

def debug_pdf_corruption(pdf_path: str):
    """Debug PDF file for corruption issues."""
    print(f"🔍 PDF Corruption Debug: {pdf_path}")
    print("=" * 70)
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    try:
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        print(f"📊 File size: {len(pdf_data):,} bytes")
        
        # Basic PDF structure checks
        check_pdf_header(pdf_data)
        check_pdf_trailer(pdf_data)
        check_eof_markers(pdf_data)
        check_xref_structure(pdf_data)
        check_stream_integrity(pdf_data)
        check_object_structure(pdf_data)
        
        # Advanced corruption checks
        check_for_null_bytes(pdf_data)
        check_for_truncation(pdf_data)
        validate_pdf_syntax(pdf_data)
        
        print(f"\n💡 RECOMMENDATIONS:")
        suggest_fixes(pdf_data)
        
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")

def check_pdf_header(pdf_data: bytes):
    """Check PDF header validity."""
    print(f"\n📄 PDF Header Check:")
    
    if pdf_data.startswith(b'%PDF-'):
        header_line = pdf_data.split(b'\n')[0]
        print(f"   ✅ Valid PDF header: {header_line.decode('ascii', errors='ignore')}")
        
        # Check version
        if b'%PDF-1.' in header_line:
            version = header_line[5:8].decode('ascii', errors='ignore')
            print(f"   📋 PDF Version: {version}")
        else:
            print(f"   ⚠️ Unusual PDF version format")
    else:
        print(f"   ❌ Invalid PDF header")
        print(f"   📋 First 50 bytes: {pdf_data[:50]}")

def check_pdf_trailer(pdf_data: bytes):
    """Check PDF trailer and EOF markers."""
    print(f"\n📋 PDF Trailer Check:")
    
    # Find all %%EOF markers
    eof_positions = []
    pos = 0
    while True:
        pos = pdf_data.find(b'%%EOF', pos)
        if pos == -1:
            break
        eof_positions.append(pos)
        pos += 5
    
    print(f"   📊 Found {len(eof_positions)} %%EOF markers at positions: {eof_positions}")
    
    if len(eof_positions) == 0:
        print(f"   ❌ No %%EOF markers found - PDF is truncated")
        return False
    
    # Check last %%EOF
    last_eof = eof_positions[-1]
    trailing_data = pdf_data[last_eof + 5:]
    
    if len(trailing_data.strip()) == 0:
        print(f"   ✅ Clean EOF termination")
    else:
        print(f"   ⚠️ {len(trailing_data)} bytes after final %%EOF")
        print(f"   📋 Trailing data: {trailing_data[:100]}")
    
    return True

def check_eof_markers(pdf_data: bytes):
    """Check EOF marker integrity."""
    print(f"\n🔚 EOF Markers Analysis:")
    
    # Find startxref entries
    startxref_pattern = rb'startxref\s*(\d+)\s*%%EOF'
    matches = list(re.finditer(startxref_pattern, pdf_data))
    
    print(f"   📊 Found {len(matches)} startxref entries:")
    
    for i, match in enumerate(matches):
        offset = int(match.group(1))
        eof_pos = match.end() - 5  # Position of %%EOF
        print(f"      {i+1}. Offset: {offset}, %%EOF at: {eof_pos}")
        
        # Validate xref offset
        if offset < len(pdf_data):
            xref_area = pdf_data[offset:offset+20]
            if b'xref' in xref_area or re.search(rb'\d+\s+\d+\s+obj', xref_area):
                print(f"         ✅ Valid xref/object at offset {offset}")
            else:
                print(f"         ❌ Invalid xref at offset {offset}")
                print(f"         📋 Content: {xref_area}")
        else:
            print(f"         ❌ Offset {offset} beyond file size {len(pdf_data)}")

def check_xref_structure(pdf_data: bytes):
    """Check cross-reference table structure."""
    print(f"\n📇 XRef Structure Check:")
    
    # Find xref tables
    xref_positions = []
    pos = 0
    while True:
        pos = pdf_data.find(b'xref', pos)
        if pos == -1:
            break
        xref_positions.append(pos)
        pos += 4
    
    print(f"   📊 Found {len(xref_positions)} xref tables at positions: {xref_positions}")
    
    # Check for XRef streams (PDF 1.5+)
    xref_stream_pattern = rb'(\d+)\s+(\d+)\s+obj\s*<<[^>]*?/Type\s*/XRef'
    xref_streams = list(re.finditer(xref_stream_pattern, pdf_data))
    
    print(f"   📊 Found {len(xref_streams)} XRef streams")
    
    if len(xref_positions) == 0 and len(xref_streams) == 0:
        print(f"   ❌ No xref structures found")
    else:
        print(f"   ✅ XRef structures present")

def check_stream_integrity(pdf_data: bytes):
    """Check stream object integrity."""
    print(f"\n🌊 Stream Integrity Check:")
    
    # Find all stream objects
    stream_pattern = rb'(\d+)\s+(\d+)\s+obj.*?stream\s*\n(.*?)\nendstream'
    streams = list(re.finditer(stream_pattern, pdf_data, re.DOTALL))
    
    print(f"   📊 Found {len(streams)} stream objects")
    
    corrupted_streams = 0
    compression_errors = 0
    
    for i, match in enumerate(streams[:10]):  # Check first 10 streams
        obj_num = int(match.group(1))
        stream_content = match.group(3)
        
        # Check if stream is compressed
        obj_start = match.start()
        obj_content = pdf_data[obj_start:match.start(3)]
        
        if b'/Filter' in obj_content and b'/FlateDecode' in obj_content:
            # Try to decompress
            try:
                decompressed = zlib.decompress(stream_content)
                print(f"      Stream {obj_num}: ✅ Valid FlateDecode ({len(stream_content)} → {len(decompressed)} bytes)")
            except zlib.error as e:
                try:
                    decompressed = zlib.decompress(stream_content, -zlib.MAX_WBITS)
                    print(f"      Stream {obj_num}: ✅ Valid raw deflate ({len(stream_content)} → {len(decompressed)} bytes)")
                except:
                    print(f"      Stream {obj_num}: ❌ Compression error - {e}")
                    compression_errors += 1
            except Exception as e:
                print(f"      Stream {obj_num}: ❌ Stream corruption - {e}")
                corrupted_streams += 1
        else:
            print(f"      Stream {obj_num}: 📋 Uncompressed ({len(stream_content)} bytes)")
    
    if compression_errors > 0:
        print(f"   ❌ {compression_errors} streams have compression errors")
    if corrupted_streams > 0:
        print(f"   ❌ {corrupted_streams} streams are corrupted")
    
    if compression_errors == 0 and corrupted_streams == 0:
        print(f"   ✅ All checked streams are valid")

def check_object_structure(pdf_data: bytes):
    """Check PDF object structure."""
    print(f"\n🧱 Object Structure Check:")
    
    # Find all objects
    obj_pattern = rb'(\d+)\s+(\d+)\s+obj\b'
    obj_matches = list(re.finditer(obj_pattern, pdf_data))
    
    print(f"   📊 Found {len(obj_matches)} objects")
    
    # Check for orphaned objects
    orphaned_objects = 0
    malformed_objects = 0
    
    for match in obj_matches[:20]:  # Check first 20 objects
        obj_num = int(match.group(1))
        obj_start = match.end()
        
        # Find corresponding endobj
        endobj_pos = pdf_data.find(b'endobj', obj_start)
        
        if endobj_pos == -1:
            print(f"      Object {obj_num}: ❌ Missing endobj")
            orphaned_objects += 1
        else:
            obj_content = pdf_data[obj_start:endobj_pos]
            
            # Basic syntax check
            if obj_content.count(b'<<') != obj_content.count(b'>>'):
                print(f"      Object {obj_num}: ❌ Unmatched << >> brackets")
                malformed_objects += 1
            elif len(obj_content.strip()) == 0:
                print(f"      Object {obj_num}: ⚠️ Empty object")
            else:
                print(f"      Object {obj_num}: ✅ Valid structure")
    
    if orphaned_objects > 0:
        print(f"   ❌ {orphaned_objects} orphaned objects found")
    if malformed_objects > 0:
        print(f"   ❌ {malformed_objects} malformed objects found")

def check_for_null_bytes(pdf_data: bytes):
    """Check for unexpected null bytes."""
    print(f"\n🕳️ Null Byte Check:")
    
    null_positions = []
    pos = 0
    while True:
        pos = pdf_data.find(b'\x00', pos)
        if pos == -1:
            break
        null_positions.append(pos)
        pos += 1
        if len(null_positions) > 10:  # Limit to first 10
            break
    
    if len(null_positions) > 0:
        print(f"   ⚠️ Found {len(null_positions)} null bytes at positions: {null_positions[:10]}")
        
        # Check if nulls are in problematic areas
        critical_nulls = 0
        for pos in null_positions[:10]:
            context = pdf_data[max(0, pos-20):pos+21]
            if b'obj' in context or b'endobj' in context or b'stream' in context:
                critical_nulls += 1
        
        if critical_nulls > 0:
            print(f"   ❌ {critical_nulls} null bytes in critical PDF structures")
        else:
            print(f"   ✅ Null bytes appear to be in content areas")
    else:
        print(f"   ✅ No null bytes found")

def check_for_truncation(pdf_data: bytes):
    """Check for file truncation."""
    print(f"\n✂️ Truncation Check:")
    
    # Check if file ends properly
    last_100_bytes = pdf_data[-100:]
    
    if b'%%EOF' in last_100_bytes:
        print(f"   ✅ File ends with %%EOF marker")
    else:
        print(f"   ❌ File does not end with %%EOF")
        print(f"   📋 Last 100 bytes: {last_100_bytes}")

def validate_pdf_syntax(pdf_data: bytes):
    """Validate basic PDF syntax."""
    print(f"\n📝 PDF Syntax Validation:")
    
    issues = []
    
    # Check for common syntax errors
    if pdf_data.count(b'<<') != pdf_data.count(b'>>'):
        issues.append("Unmatched dictionary brackets << >>")
    
    if pdf_data.count(b'[') != pdf_data.count(b']'):
        issues.append("Unmatched array brackets [ ]")
    
    # Check for stream/endstream pairs
    stream_count = pdf_data.count(b'stream\n') + pdf_data.count(b'stream\r\n')
    endstream_count = pdf_data.count(b'endstream')
    
    if stream_count != endstream_count:
        issues.append(f"Mismatched stream/endstream pairs ({stream_count} vs {endstream_count})")
    
    # Check for obj/endobj pairs
    obj_count = len(re.findall(rb'\d+\s+\d+\s+obj\b', pdf_data))
    endobj_count = pdf_data.count(b'endobj')
    
    if obj_count != endobj_count:
        issues.append(f"Mismatched obj/endobj pairs ({obj_count} vs {endobj_count})")
    
    if issues:
        print(f"   ❌ Syntax issues found:")
        for issue in issues:
            print(f"      - {issue}")
    else:
        print(f"   ✅ Basic syntax appears valid")

def suggest_fixes(pdf_data: bytes):
    """Suggest fixes for common issues."""
    suggestions = []
    
    # Check if file is readable by looking at structure
    if not pdf_data.startswith(b'%PDF-'):
        suggestions.append("🔧 File is not a valid PDF - restore from backup")
    elif not b'%%EOF' in pdf_data:
        suggestions.append("🔧 File is truncated - restore from backup")
    elif pdf_data.count(b'<<') != pdf_data.count(b'>>'):
        suggestions.append("🔧 Dictionary bracket corruption - content replacement may have damaged structure")
    else:
        suggestions.append("✅ File structure appears recoverable")
        suggestions.append("💡 Try opening in PDF viewer to verify readability")
        suggestions.append("💡 If corrupted, restore from backup and use safer update methods")
    
    for suggestion in suggestions:
        print(f"   {suggestion}")

def debug_test_pdf_directory():
    """Debug all PDF files in test_pdf directory."""
    print("🔍 Debugging All PDFs in test_pdf Directory")
    print("=" * 70)
    
    test_dir = "test_pdf"
    if not os.path.exists(test_dir):
        print(f"❌ Directory {test_dir} not found")
        return
    
    pdf_files = [f for f in os.listdir(test_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ No PDF files found in {test_dir}")
        return
    
    print(f"📊 Found {len(pdf_files)} PDF files:")
    
    for pdf_file in sorted(pdf_files):
        pdf_path = os.path.join(test_dir, pdf_file)
        file_size = os.path.getsize(pdf_path)
        print(f"\n{'='*50}")
        print(f"🔍 Analyzing: {pdf_file} ({file_size:,} bytes)")
        print(f"{'='*50}")
        
        debug_pdf_corruption(pdf_path)

if __name__ == "__main__":
    debug_test_pdf_directory() 