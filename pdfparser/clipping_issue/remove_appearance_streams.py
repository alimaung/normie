#!/usr/bin/env python3
"""
Remove appearance streams (/AP) from PDF form fields to force regeneration.
"""

import sys
import os
import re

def remove_appearance_streams(input_file, output_file):
    """
    Remove /AP entries from PDF objects to force appearance stream regeneration.
    """
    print(f"Reading PDF: {input_file}")
    
    try:
        with open(input_file, 'rb') as f:
            pdf_data = f.read()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return False
    
    print(f"Original PDF size: {len(pdf_data)} bytes")
    
    # Target objects containing fields "10" and "31" (objects 17 and 226)
    target_objects = [17, 226]
    
    modified_data = pdf_data
    total_changes = 0
    
    for obj_num in target_objects:
        print(f"\nProcessing object {obj_num}...")
        
        # Find the object
        obj_pattern = rf'{obj_num}\s+0\s+obj'.encode()
        match = re.search(obj_pattern, modified_data)
        
        if not match:
            print(f"  Object {obj_num} not found")
            continue
        
        start_pos = match.start()
        
        # Find end of object
        endobj_match = re.search(rb'endobj', modified_data[start_pos:])
        if endobj_match:
            end_pos = start_pos + endobj_match.end()
        else:
            print(f"  Could not find end of object {obj_num}")
            continue
        
        # Extract object data
        obj_data = modified_data[start_pos:end_pos]
        original_obj_data = obj_data
        
        try:
            obj_text = obj_data.decode('latin-1', errors='replace')
        except:
            print(f"  Could not decode object {obj_num}")
            continue
        
        # Check if object has appearance streams
        has_ap = '/AP' in obj_text
        print(f"  Has /AP entry: {has_ap}")
        
        if has_ap:
            # Remove /AP entries completely
            # Pattern: /AP<<...>> or /AP <reference>
            
            # Method 1: Remove /AP<<...>> (nested dictionary)
            ap_dict_pattern = r'/AP\s*<<[^>]*>>'
            obj_text_modified = re.sub(ap_dict_pattern, '', obj_text, flags=re.DOTALL)
            
            # Method 2: Remove /AP <reference> (object reference)
            ap_ref_pattern = r'/AP\s+\d+\s+\d+\s+R'
            obj_text_modified = re.sub(ap_ref_pattern, '', obj_text_modified)
            
            # Method 3: Remove any remaining /AP entries
            ap_simple_pattern = r'/AP[^/\s]*'
            obj_text_modified = re.sub(ap_simple_pattern, '', obj_text_modified)
            
            # Clean up any double spaces
            obj_text_modified = re.sub(r'\s+', ' ', obj_text_modified)
            
            if obj_text_modified != obj_text:
                print(f"  ✅ Removed /AP entries from object {obj_num}")
                
                # Convert back to bytes
                try:
                    modified_obj_data = obj_text_modified.encode('latin-1')
                    
                    # Replace in the full PDF data
                    modified_data = modified_data[:start_pos] + modified_obj_data + modified_data[end_pos:]
                    total_changes += 1
                    
                    print(f"  Size change: {len(original_obj_data)} -> {len(modified_obj_data)} bytes")
                    
                except Exception as e:
                    print(f"  Error encoding modified object: {e}")
            else:
                print(f"  No /AP entries found to remove")
        else:
            print(f"  No /AP entries found")
    
    if total_changes > 0:
        print(f"\nSaving modified PDF to: {output_file}")
        print(f"Total objects modified: {total_changes}")
        print(f"Final PDF size: {len(modified_data)} bytes")
        
        try:
            with open(output_file, 'wb') as f:
                f.write(modified_data)
            print("✅ PDF saved successfully!")
            print("\n🔄 The PDF viewer should now regenerate appearance streams automatically.")
            print("This should fix the text clipping issue.")
            return True
        except Exception as e:
            print(f"Error saving PDF: {e}")
            return False
    else:
        print("No changes were made.")
        return False

def analyze_appearance_streams(input_file):
    """
    Analyze what appearance streams exist in the PDF.
    """
    print(f"Analyzing appearance streams in: {input_file}")
    
    try:
        with open(input_file, 'rb') as f:
            pdf_data = f.read()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return
    
    # Find all /AP entries
    ap_matches = list(re.finditer(rb'/AP', pdf_data))
    
    print(f"Found {len(ap_matches)} /AP entries in the PDF")
    
    for i, match in enumerate(ap_matches[:10]):  # Limit to first 10
        start = max(0, match.start() - 50)
        end = min(len(pdf_data), match.end() + 100)
        context = pdf_data[start:end]
        
        try:
            context_text = context.decode('latin-1', errors='replace')
            print(f"\n/AP entry {i+1}:")
            print(f"  Context: {repr(context_text)}")
        except:
            print(f"\n/AP entry {i+1}: (binary context)")

def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage: python remove_appearance_streams.py <input.pdf> [output.pdf]")
        print("If no output file is specified, '_no_ap' will be added to the input filename.")
        return
    
    input_file = sys.argv[1]
    
    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    else:
        # Generate output filename
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_no_ap{ext}"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
    
    print("PDF APPEARANCE STREAM REMOVER")
    print("=" * 50)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    
    # First analyze what we're working with
    print("\n" + "="*50)
    print("ANALYSIS PHASE")
    print("="*50)
    analyze_appearance_streams(input_file)
    
    # Then remove appearance streams
    print("\n" + "="*50)
    print("REMOVAL PHASE")
    print("="*50)
    success = remove_appearance_streams(input_file, output_file)
    
    if success:
        print(f"\n🎉 Appearance streams removed! Test the output file: {output_file}")
        print("The PDF viewer should regenerate the appearance streams and fix the clipping.")
    else:
        print(f"\n❌ No changes were made or an error occurred.")

if __name__ == "__main__":
    main() 