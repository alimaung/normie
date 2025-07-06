#!/usr/bin/env python3
"""
Debug script to investigate missing field 25a
"""
import re
import zlib
from low_level_pdf_editor import PurePDFEditor

def debug_missing_field():
    """Debug why field 25a cannot be located."""
    print("🔍 Debugging Missing Field 25a")
    print("=" * 60)
    
    # Load the original PDF
    editor = PurePDFEditor("pdf.pdf")
    
    target_value = "Dr. Karsten Bartz"
    print(f"🎯 Searching for: '{target_value}'")
    
    # Manual search in raw PDF data
    print(f"\n📄 Raw PDF Data Search:")
    patterns = [
        target_value.encode('utf-8'),
        target_value.encode('latin-1'),
        f"({target_value})".encode('utf-8'),
        f"<{target_value.encode().hex()}>".encode(),
        f"<{target_value.encode().hex().upper()}>".encode(),
    ]
    
    for i, pattern in enumerate(patterns):
        positions = []
        pos = 0
        while True:
            pos = editor.pdf_data.find(pattern, pos)
            if pos == -1:
                break
            positions.append(pos)
            pos += len(pattern)
        
        if positions:
            print(f"   ✅ Pattern {i+1}: Found at positions {positions}")
        else:
            print(f"   ❌ Pattern {i+1}: Not found")
    
    # Search in compressed streams
    print(f"\n📦 Compressed Streams Search:")
    streams = editor._find_compressed_streams()
    print(f"   Analyzing {len(streams)} compressed streams...")
    
    found_in_streams = []
    
    for stream_info in streams:
        try:
            stream_data = editor._extract_stream_data(stream_info)
            if stream_data:
                # Try decompression
                decompressed = None
                try:
                    decompressed = zlib.decompress(stream_data)
                except:
                    try:
                        decompressed = zlib.decompress(stream_data, -zlib.MAX_WBITS)
                    except:
                        continue
                
                if decompressed:
                    for i, pattern in enumerate(patterns):
                        if pattern in decompressed:
                            found_in_streams.append({
                                'stream': stream_info['object'],
                                'pattern': i+1,
                                'size': len(decompressed)
                            })
                            print(f"   ✅ Found in stream {stream_info['object']} (pattern {i+1}, {len(decompressed)} bytes decompressed)")
                            
                            # Show context around the match
                            pos = decompressed.find(pattern)
                            start = max(0, pos - 50)
                            end = min(len(decompressed), pos + len(pattern) + 50)
                            context = decompressed[start:end]
                            print(f"      Context: {context}")
                            break
        except Exception as e:
            continue
    
    if not found_in_streams:
        print("   ❌ Not found in any compressed streams")
    
    # Try partial matches
    print(f"\n🔍 Partial Match Search:")
    partial_searches = [
        "Karsten",
        "Bartz", 
        "Dr.",
        "Karsten Bartz"
    ]
    
    for partial in partial_searches:
        print(f"   Searching for partial: '{partial}'")
        
        # Raw data search
        pattern = partial.encode('utf-8')
        positions = []
        pos = 0
        while True:
            pos = editor.pdf_data.find(pattern, pos)
            if pos == -1:
                break
            positions.append(pos)
            pos += len(pattern)
        
        if positions:
            print(f"     ✅ Raw data: Found at positions {positions[:5]}...")  # Show first 5
        
        # Stream search
        stream_matches = 0
        for stream_info in streams[:10]:  # Check first 10 streams
            try:
                stream_data = editor._extract_stream_data(stream_info)
                if stream_data:
                    try:
                        decompressed = zlib.decompress(stream_data)
                        if pattern in decompressed:
                            stream_matches += 1
                    except:
                        try:
                            decompressed = zlib.decompress(stream_data, -zlib.MAX_WBITS)
                            if pattern in decompressed:
                                stream_matches += 1
                        except:
                            continue
            except:
                continue
        
        if stream_matches > 0:
            print(f"     ✅ Streams: Found in {stream_matches} streams")
        else:
            print(f"     ❌ Streams: Not found")
    
    # Check what the hybrid extraction actually found
    print(f"\n📋 Hybrid Extraction Results for field 25a:")
    if "25a" in editor.form_fields:
        field = editor.form_fields["25a"]
        print(f"   Field name: {field.name}")
        print(f"   Current value: '{field.current_value}'")
        print(f"   Object number: {field.obj_num}")
        print(f"   Field type: {field.field_type}")
    else:
        print("   ❌ Field 25a not found in form_fields")

if __name__ == "__main__":
    debug_missing_field() 