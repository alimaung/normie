#!/usr/bin/env python3
"""
Comprehensive signature debugging script for PDF files.
This will analyze signature validity, structure, and properties in detail.
"""

import fitz
import sys
import os
from datetime import datetime
import hashlib

def analyze_signature_structure(pdf_path):
    """
    Deep analysis of PDF signature structure and validity.
    """
    print(f"🔍 SIGNATURE ANALYSIS: {os.path.basename(pdf_path)}")
    print("=" * 80)
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return False
    
    try:
        doc = fitz.open(pdf_path)
        print(f"✅ PDF opened successfully")
        print(f"   Pages: {len(doc)}")
        print(f"   File size: {os.path.getsize(pdf_path):,} bytes")
        
        # Get PDF metadata
        metadata = doc.metadata
        print(f"   Title: {metadata.get('title', 'N/A')}")
        print(f"   Author: {metadata.get('author', 'N/A')}")
        print(f"   Creator: {metadata.get('creator', 'N/A')}")
        print(f"   Producer: {metadata.get('producer', 'N/A')}")
        
        # Check PDF version and encryption
        print(f"   Is encrypted: {doc.is_encrypted}")
        print(f"   Needs password: {doc.needs_pass}")
        
        print("\n" + "="*50)
        print("📋 SIGNATURE FIELD ANALYSIS")
        print("="*50)
        
        signature_fields = []
        total_fields = 0
        
        # Analyze all pages for signature fields
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                total_fields += 1
                field_name = widget.field_name
                field_type = widget.field_type_string
                
                if field_type == 'Signature':
                    print(f"\n🔏 SIGNATURE FIELD: {field_name}")
                    print(f"   Page: {page_num + 1}")
                    print(f"   Field type: {field_type}")
                    print(f"   Field flags: {widget.field_flags}")
                    print(f"   Is signed: {widget.is_signed}")
                    
                    # Get field rectangle
                    rect = widget.rect
                    print(f"   Position: ({rect.x0:.1f}, {rect.y0:.1f}, {rect.x1:.1f}, {rect.y1:.1f})")
                    
                    # Try to get signature value
                    try:
                        field_value = widget.field_value
                        print(f"   Field value type: {type(field_value)}")
                        if field_value:
                            print(f"   Field value length: {len(str(field_value))}")
                            # Don't print full value as it might be binary
                            if len(str(field_value)) > 100:
                                print(f"   Field value preview: {str(field_value)[:50]}...")
                            else:
                                print(f"   Field value: {field_value}")
                        else:
                            print(f"   Field value: None/Empty")
                    except Exception as e:
                        print(f"   ❌ Error getting field value: {e}")
                    
                    # Check if widget has signature data
                    if hasattr(widget, 'signature_contents'):
                        try:
                            sig_contents = widget.signature_contents
                            print(f"   Signature contents: {len(sig_contents) if sig_contents else 0} bytes")
                        except:
                            print(f"   Signature contents: Not accessible")
                    
                    signature_fields.append({
                        'name': field_name,
                        'page': page_num + 1,
                        'is_signed': widget.is_signed,
                        'field_value': widget.field_value,
                        'widget': widget
                    })
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total form fields: {total_fields}")
        print(f"   Signature fields found: {len(signature_fields)}")
        print(f"   Signed fields: {sum(1 for f in signature_fields if f['is_signed'])}")
        print(f"   Empty signature fields: {sum(1 for f in signature_fields if not f['is_signed'])}")
        
        # Advanced signature analysis
        print("\n" + "="*50)
        print("🔬 ADVANCED SIGNATURE ANALYSIS")
        print("="*50)
        
        # Check for signature dictionary in PDF structure
        try:
            # Get the raw PDF data for signature analysis
            pdf_data = open(pdf_path, 'rb').read()
            
            # Look for signature-related PDF objects
            sig_keywords = [b'/Sig', b'/Contents', b'/ByteRange', b'/SubFilter', b'/M', b'/Reason']
            
            for keyword in sig_keywords:
                count = pdf_data.count(keyword)
                print(f"   {keyword.decode('utf-8', errors='ignore')} occurrences: {count}")
            
            # Check for signature timestamps
            if b'/M' in pdf_data:
                print(f"   📅 Signature timestamps found in PDF")
            
            # Check for signature validation info
            if b'/SubFilter' in pdf_data:
                print(f"   🔐 Signature subfilter information present")
                
        except Exception as e:
            print(f"   ❌ Error in advanced analysis: {e}")
        
        # File integrity check
        print(f"\n🔍 FILE INTEGRITY:")
        try:
            # Calculate file hash
            with open(pdf_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            print(f"   File MD5: {file_hash}")
            
            # Check if file can be saved
            can_save = doc.can_save_incrementally()
            print(f"   Can save incrementally: {can_save}")
            
        except Exception as e:
            print(f"   ❌ Error checking file integrity: {e}")
        
        doc.close()
        
        print("\n" + "="*80)
        print("✅ SIGNATURE ANALYSIS COMPLETE")
        print("="*80)
        
        return signature_fields
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        return []

def compare_signatures(original_path, modified_path):
    """
    Compare signatures between original and modified PDF.
    """
    print(f"\n🔄 SIGNATURE COMPARISON")
    print("="*50)
    
    print(f"📄 ORIGINAL: {os.path.basename(original_path)}")
    original_sigs = analyze_signature_structure(original_path)
    
    print(f"\n📄 MODIFIED: {os.path.basename(modified_path)}")
    modified_sigs = analyze_signature_structure(modified_path)
    
    print(f"\n📊 COMPARISON RESULTS:")
    print(f"   Original signatures: {len(original_sigs)}")
    print(f"   Modified signatures: {len(modified_sigs)}")
    
    if len(original_sigs) != len(modified_sigs):
        print(f"   ⚠️  Signature count changed!")
    
    # Compare individual signatures
    for i, (orig, mod) in enumerate(zip(original_sigs, modified_sigs)):
        print(f"\n   Signature {i+1} ({orig['name']}):")
        print(f"     Original signed: {orig['is_signed']}")
        print(f"     Modified signed: {mod['is_signed']}")
        
        if orig['is_signed'] != mod['is_signed']:
            print(f"     ❌ Signature status changed!")
        
        if orig['field_value'] != mod['field_value']:
            print(f"     ⚠️  Field value changed!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python signature_debug.py <pdf_path> [second_pdf_for_comparison]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Single PDF analysis
    signatures = analyze_signature_structure(pdf_path)
    
    # If second PDF provided, do comparison
    if len(sys.argv) > 2:
        second_pdf = sys.argv[2]
        compare_signatures(pdf_path, second_pdf)
    
    print(f"\n💡 RECOMMENDATIONS:")
    if not signatures:
        print("   - No signature fields found")
    else:
        signed_count = sum(1 for s in signatures if s['is_signed'])
        if signed_count == 0:
            print("   - All signature fields are empty")
        elif signed_count < len(signatures):
            print("   - Some signatures are missing")
        else:
            print("   - All signature fields appear to be signed")
            print("   - Test in Adobe Acrobat to verify signature validity") 