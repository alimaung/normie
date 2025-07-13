#!/usr/bin/env python3
"""
PDF Stream Decompressor
Finds and decompresses all FlateDecode streams in a PDF file
"""

import os
import re
import zlib
from pathlib import Path
from datetime import datetime

def find_compressed_streams(pdf_data: bytes):
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
                        'filter': 'FlateDecode',
                        'obj_content': obj_content
                    })
    
    return streams

def extract_stream_data(pdf_data: bytes, stream_info: dict):
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

def decompress_pdf_streams(pdf_path: str, output_dir: str = "decompressed_streams"):
    """Decompress all FlateDecode streams in a PDF and save to files."""
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Load PDF
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    print(f"🔍 Analyzing PDF: {pdf_path}")
    print(f"📊 File size: {len(pdf_data):,} bytes")
    
    # Find all compressed streams
    streams = find_compressed_streams(pdf_data)
    print(f"📦 Found {len(streams)} FlateDecode streams")
    
    # Create summary file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_file = output_path / f"summary_{timestamp}.txt"
    
    with open(summary_file, 'w', encoding='utf-8') as summary:
        summary.write(f"PDF Stream Decompression Summary\n")
        summary.write(f"PDF File: {pdf_path}\n")
        summary.write(f"Timestamp: {timestamp}\n")
        summary.write(f"Total streams found: {len(streams)}\n")
        summary.write("=" * 60 + "\n\n")
        
        successful_decompressions = 0
        
        for i, stream_info in enumerate(streams):
            obj_num = stream_info['object']
            print(f"\n📦 Processing stream {i+1}/{len(streams)}: Object {obj_num}")
            
            # Extract stream data
            stream_data = extract_stream_data(pdf_data, stream_info)
            if not stream_data:
                print(f"   ❌ Could not extract stream data")
                summary.write(f"Object {obj_num}: FAILED - Could not extract stream data\n")
                continue
            
            print(f"   📊 Raw stream size: {len(stream_data)} bytes")
            
            # Try to decompress
            decompressed = None
            decomp_method = None
            
            try:
                # Try standard zlib decompression
                decompressed = zlib.decompress(stream_data)
                decomp_method = "zlib"
                print(f"   ✅ Decompressed with zlib: {len(decompressed)} bytes")
            except zlib.error:
                try:
                    # Try raw inflate
                    decompressed = zlib.decompress(stream_data, -zlib.MAX_WBITS)
                    decomp_method = "raw_inflate"
                    print(f"   ✅ Decompressed with raw inflate: {len(decompressed)} bytes")
                except Exception as e:
                    print(f"   ❌ Decompression failed: {e}")
                    summary.write(f"Object {obj_num}: FAILED - Decompression error: {e}\n")
                    continue
            
            if decompressed:
                successful_decompressions += 1
                
                # Save raw compressed data
                raw_file = output_path / f"obj_{obj_num}_raw.bin"
                with open(raw_file, 'wb') as f:
                    f.write(stream_data)
                
                # Save decompressed data
                decomp_file = output_path / f"obj_{obj_num}_decompressed.bin"
                with open(decomp_file, 'wb') as f:
                    f.write(decompressed)
                
                # Save as text (if possible)
                text_file = output_path / f"obj_{obj_num}_text.txt"
                try:
                    with open(text_file, 'w', encoding='utf-8', errors='ignore') as f:
                        f.write(f"Object {obj_num} - Decompressed Content\n")
                        f.write(f"Method: {decomp_method}\n")
                        f.write(f"Raw size: {len(stream_data)} bytes\n")
                        f.write(f"Decompressed size: {len(decompressed)} bytes\n")
                        f.write("=" * 50 + "\n\n")
                        f.write("Raw bytes (first 200):\n")
                        f.write(str(decompressed[:200]) + "\n\n")
                        f.write("As text:\n")
                        f.write(decompressed.decode('utf-8', errors='ignore'))
                except Exception as e:
                    print(f"   ⚠️ Could not save as text: {e}")
                
                # Save object dictionary info
                dict_file = output_path / f"obj_{obj_num}_dict.txt"
                with open(dict_file, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(f"Object {obj_num} - Dictionary Content\n")
                    f.write("=" * 50 + "\n")
                    f.write(stream_info['obj_content'].decode('utf-8', errors='ignore'))
                
                # Update summary
                summary.write(f"Object {obj_num}: SUCCESS - {decomp_method} - {len(stream_data)} → {len(decompressed)} bytes\n")
                
                # Show preview of decompressed content
                preview = decompressed[:100].decode('utf-8', errors='ignore').replace('\n', '\\n')
                print(f"   📄 Preview: {preview}")
        
        summary.write(f"\nSUMMARY:\n")
        summary.write(f"Successful decompressions: {successful_decompressions}/{len(streams)}\n")
        summary.write(f"Success rate: {successful_decompressions/len(streams)*100:.1f}%\n")
    
    print(f"\n✅ Processing complete!")
    print(f"📊 Successfully decompressed: {successful_decompressions}/{len(streams)} streams")
    print(f"📁 Results saved to: {output_path}")
    print(f"📄 Summary: {summary_file}")

def main():
    """Main function."""
    pdf_path = "pdf.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    decompress_pdf_streams(pdf_path)

if __name__ == "__main__":
    main() 