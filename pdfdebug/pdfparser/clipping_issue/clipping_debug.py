#!/usr/bin/env python3
"""
PDF Clipping Debug Script
Compares two PDF files to identify differences that cause text clipping in form fields.
"""

import sys
import os
import json
from pathlib import Path

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("Warning: PyPDF2 not available")

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    print("Warning: PyMuPDF not available")

def analyze_field_with_fitz(pdf_path, target_fields):
    """
    Use PyMuPDF to extract detailed field information for target fields only.
    """
    if not FITZ_AVAILABLE:
        print("PyMuPDF not available")
        return None
    
    try:
        doc = fitz.open(pdf_path)
        result = {
            'fields': {},
            'raw_objects': {}
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                field_name = widget.field_name
                if field_name in target_fields:
                    # Get detailed widget information
                    field_info = {
                        'field_name': field_name,
                        'field_type': widget.field_type_string,
                        'field_value': str(widget.field_value or ''),
                        'rect': list(widget.rect),
                        'text_maxlen': getattr(widget, 'text_maxlen', None),
                        'text_format': getattr(widget, 'text_format', None),
                        'border_color': getattr(widget, 'border_color', None),
                        'fill_color': getattr(widget, 'fill_color', None),
                        'text_color': getattr(widget, 'text_color', None),
                        'border_width': getattr(widget, 'border_width', None),
                        'page_number': page_num + 1
                    }
                    
                    result['fields'][field_name] = field_info
                    
                    # Try to get raw PDF object information
                    try:
                        # Get the annotation object
                        annot = widget.parent
                        if annot:
                            # Extract raw PDF content
                            raw_info = {
                                'type': annot.type[1],  # Remove /
                                'rect': list(annot.rect),
                                'flags': annot.flags,
                                'contents': annot.info.get('content', ''),
                                'has_appearance': bool(annot.get_ap()),
                            }
                            
                            # Try to get appearance stream
                            ap_stream = annot.get_ap()
                            if ap_stream:
                                raw_info['appearance_stream_length'] = len(ap_stream)
                                raw_info['appearance_stream_preview'] = ap_stream[:200].decode('latin-1', errors='ignore')
                            
                            result['raw_objects'][field_name] = raw_info
                    except Exception as e:
                        print(f"Could not extract raw object for field {field_name}: {e}")
        
        doc.close()
        return result
        
    except Exception as e:
        print(f"Error analyzing PDF with PyMuPDF: {e}")
        return None

def analyze_field_with_pypdf2(pdf_path, target_fields):
    """
    Simple PyPDF2 analysis that avoids complex field extraction.
    """
    if not PYPDF2_AVAILABLE:
        return None
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            result = {'annotations': {}}
            
            # Look through all pages for annotations
            for page_num, page in enumerate(reader.pages):
                if '/Annots' in page:
                    for annot_ref in page['/Annots']:
                        try:
                            annot_obj = annot_ref.get_object()
                            if annot_obj.get('/Subtype') == '/Widget':
                                # Try to get field name safely
                                field_name_obj = annot_obj.get('/T')
                                if field_name_obj:
                                    field_name = str(field_name_obj)
                                    if field_name in target_fields:
                                        # Store the raw annotation object
                                        result['annotations'][field_name] = {
                                            'raw_object': annot_obj,
                                            'page': page_num + 1,
                                            'object_keys': sorted(annot_obj.keys()),
                                            'has_appearance': '/AP' in annot_obj
                                        }
                        except Exception as e:
                            continue  # Skip problematic annotations
            
            return result
            
    except Exception as e:
        print(f"Error with PyPDF2: {e}")
        return None

def compare_raw_objects(no_clip_pypdf2, clip_pypdf2, field_name):
    """
    Compare raw PDF annotation objects between the two files.
    """
    print(f"\n{'='*60}")
    print(f"RAW OBJECT COMPARISON FOR FIELD {field_name}")
    print(f"{'='*60}")
    
    no_clip_annot = no_clip_pypdf2['annotations'].get(field_name, {}).get('raw_object')
    clip_annot = clip_pypdf2['annotations'].get(field_name, {}).get('raw_object')
    
    if not no_clip_annot or not clip_annot:
        print(f"Could not find raw objects for field {field_name}")
        return
    
    print(f"Object keys comparison:")
    no_clip_keys = sorted(no_clip_annot.keys())
    clip_keys = sorted(clip_annot.keys())
    print(f"  No clipping keys: {no_clip_keys}")
    print(f"  Clipping keys:    {clip_keys}")
    
    if no_clip_keys != clip_keys:
        print(f"  *** KEY DIFFERENCE! ***")
        missing_in_clip = set(no_clip_keys) - set(clip_keys)
        missing_in_no_clip = set(clip_keys) - set(no_clip_keys)
        if missing_in_clip:
            print(f"    Missing in clipping: {missing_in_clip}")
        if missing_in_no_clip:
            print(f"    Missing in no clipping: {missing_in_no_clip}")
    
    # Compare each property
    all_keys = set(no_clip_keys) | set(clip_keys)
    differences_found = False
    
    for key in sorted(all_keys):
        no_clip_val = no_clip_annot.get(key, '<MISSING>')
        clip_val = clip_annot.get(key, '<MISSING>')
        
        if key == '/AP':
            print(f"\n/AP (Appearance) Analysis:")
            if no_clip_val != '<MISSING>' and clip_val != '<MISSING>':
                compare_appearance_streams(no_clip_val, clip_val, field_name)
            elif no_clip_val != clip_val:
                print(f"  *** APPEARANCE PRESENCE DIFFERENCE! ***")
                print(f"    No clipping: {no_clip_val}")
                print(f"    Clipping:    {clip_val}")
                differences_found = True
        else:
            # Convert to string for comparison
            no_clip_str = str(no_clip_val)
            clip_str = str(clip_val)
            
            if no_clip_str != clip_str:
                print(f"\n*** DIFFERENCE in {key}: ***")
                print(f"  No clipping: {no_clip_str}")
                print(f"  Clipping:    {clip_str}")
                differences_found = True
    
    if not differences_found:
        print("\nNo obvious differences found in object properties")

def compare_appearance_streams(no_clip_ap, clip_ap, field_name):
    """
    Deep comparison of appearance dictionaries.
    """
    print(f"  Appearance dictionary comparison:")
    
    # Check if both have /N (Normal appearance)
    no_clip_has_n = hasattr(no_clip_ap, 'get') and '/N' in no_clip_ap
    clip_has_n = hasattr(clip_ap, 'get') and '/N' in clip_ap
    
    print(f"    No clipping has /N: {no_clip_has_n}")
    print(f"    Clipping has /N:    {clip_has_n}")
    
    if no_clip_has_n != clip_has_n:
        print(f"    *** NORMAL APPEARANCE PRESENCE DIFFERENCE! ***")
        return
    
    if no_clip_has_n and clip_has_n:
        no_clip_n = no_clip_ap['/N']
        clip_n = clip_ap['/N']
        
        print(f"    Normal appearance types:")
        print(f"      No clipping: {type(no_clip_n)}")
        print(f"      Clipping:    {type(clip_n)}")
        
        # Try to extract stream data
        try:
            if hasattr(no_clip_n, 'get_data'):
                no_clip_stream = no_clip_n.get_data()
                print(f"    No clipping stream length: {len(no_clip_stream)}")
                print(f"    No clipping stream preview: {no_clip_stream[:100]}")
            
            if hasattr(clip_n, 'get_data'):
                clip_stream = clip_n.get_data()
                print(f"    Clipping stream length: {len(clip_stream)}")
                print(f"    Clipping stream preview: {clip_stream[:100]}")
                
                # Compare streams if both available
                if hasattr(no_clip_n, 'get_data') and hasattr(clip_n, 'get_data'):
                    if no_clip_stream != clip_stream:
                        print(f"    *** STREAM CONTENT DIFFERENCE! ***")
                        print(f"    This is likely the cause of clipping!")
                    else:
                        print(f"    Stream contents are identical")
                        
        except Exception as e:
            print(f"    Error extracting stream data: {e}")

def analyze_specific_fields(no_clipping_path, clipping_path, target_fields=["10", "31"]):
    """
    Focused analysis of specific fields that have clipping issues.
    """
    print("=" * 80)
    print(f"FOCUSED CLIPPING ANALYSIS - Fields: {', '.join(target_fields)}")
    print("=" * 80)
    print(f"No clipping file: {no_clipping_path}")
    print(f"Clipping file: {clipping_path}")
    print()
    
    # Analyze with PyMuPDF first (more reliable)
    print("Analyzing with PyMuPDF...")
    no_clip_fitz = analyze_field_with_fitz(no_clipping_path, target_fields)
    clip_fitz = analyze_field_with_fitz(clipping_path, target_fields)
    
    if no_clip_fitz and clip_fitz:
        print("\nPyMuPDF Field Comparison:")
        print("-" * 40)
        
        for field_name in target_fields:
            if field_name in no_clip_fitz['fields'] and field_name in clip_fitz['fields']:
                no_clip_field = no_clip_fitz['fields'][field_name]
                clip_field = clip_fitz['fields'][field_name]
                
                print(f"\nField {field_name}:")
                print(f"  Value lengths - No clip: {len(no_clip_field['field_value'])}, Clip: {len(clip_field['field_value'])}")
                print(f"  Values identical: {no_clip_field['field_value'] == clip_field['field_value']}")
                print(f"  Rectangles identical: {no_clip_field['rect'] == clip_field['rect']}")
                print(f"  Max length - No clip: {no_clip_field['text_maxlen']}, Clip: {clip_field['text_maxlen']}")
                
                # Check raw object differences
                if field_name in no_clip_fitz['raw_objects'] and field_name in clip_fitz['raw_objects']:
                    no_clip_raw = no_clip_fitz['raw_objects'][field_name]
                    clip_raw = clip_fitz['raw_objects'][field_name]
                    
                    print(f"  Appearance streams - No clip: {no_clip_raw.get('has_appearance')}, Clip: {clip_raw.get('has_appearance')}")
                    
                    if no_clip_raw.get('appearance_stream_length') and clip_raw.get('appearance_stream_length'):
                        print(f"  Stream lengths - No clip: {no_clip_raw['appearance_stream_length']}, Clip: {clip_raw['appearance_stream_length']}")
                        if no_clip_raw['appearance_stream_length'] != clip_raw['appearance_stream_length']:
                            print(f"    *** STREAM LENGTH DIFFERENCE - This could be the clipping cause! ***")
    
    # Analyze with PyPDF2 for deeper object comparison
    print(f"\nAnalyzing with PyPDF2 for raw object comparison...")
    no_clip_pypdf2 = analyze_field_with_pypdf2(no_clipping_path, target_fields)
    clip_pypdf2 = analyze_field_with_pypdf2(clipping_path, target_fields)
    
    if no_clip_pypdf2 and clip_pypdf2:
        for field_name in target_fields:
            if field_name in no_clip_pypdf2['annotations'] and field_name in clip_pypdf2['annotations']:
                compare_raw_objects(no_clip_pypdf2, clip_pypdf2, field_name)

def main():
    if len(sys.argv) != 3:
        print("Usage: python clipping_debug.py <no_clipping.pdf> <clipping.pdf>")
        print("Example: python clipping_debug.py no_clipping.pdf clipping.pdf")
        return
    
    no_clipping_path = sys.argv[1]
    clipping_path = sys.argv[2]
    
    if not os.path.exists(no_clipping_path):
        print(f"Error: File not found: {no_clipping_path}")
        return
    
    if not os.path.exists(clipping_path):
        print(f"Error: File not found: {clipping_path}")
        return
    
    # Run focused analysis on fields 10 and 31 ONLY
    analyze_specific_fields(no_clipping_path, clipping_path, ["10", "31"])

if __name__ == "__main__":
    main()
