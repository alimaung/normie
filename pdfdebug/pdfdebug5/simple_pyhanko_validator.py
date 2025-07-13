#!/usr/bin/env python3
"""
Simple PDF Signature Validator using pyHanko
Tests basic signature validation functionality
"""

import os
import sys
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature

def simple_validate_signatures(pdf_path):
    """Simple signature validation using pyHanko"""
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    try:
        print(f"📄 Validating: {pdf_path}")
        print("=" * 50)
        
        # Open PDF with pyHanko
        with open(pdf_path, 'rb') as f:
            reader = PdfFileReader(f)
            
            print(f"📄 Pages: {len(reader.root.pages)}")
            print(f"🔒 Encrypted: {reader.encrypted}")
            
            # Check if document has embedded signatures
            if hasattr(reader, 'embedded_signatures'):
                sig_fields = list(reader.embedded_signatures.keys())
                print(f"📋 Embedded signatures: {len(sig_fields)}")
                
                if sig_fields:
                    for field_name in sig_fields:
                        print(f"\n🔍 Signature field: {field_name}")
                        
                        try:
                            # Get signature object
                            sig_obj = reader.embedded_signatures[field_name]
                            print(f"  Signature object: {type(sig_obj)}")
                            
                            # Try basic validation
                            try:
                                validation_result = validate_pdf_signature(sig_obj)
                                print(f"  ✅ Validation successful")
                                print(f"  Valid: {validation_result.valid}")
                                print(f"  Trusted: {getattr(validation_result, 'trusted', 'N/A')}")
                                
                                # Try to get summary
                                try:
                                    summary = validation_result.summary()
                                    print(f"  Summary: {summary}")
                                except:
                                    print(f"  Summary: Not available")
                                
                            except Exception as e:
                                print(f"  ❌ Validation failed: {e}")
                                
                        except Exception as e:
                            print(f"  ❌ Error accessing signature: {e}")
                else:
                    print("  No embedded signatures found")
            else:
                print("📋 No embedded signatures support")
                
            # Check for form signature fields
            if reader.root.acro_form:
                try:
                    sig_fields = reader.root.acro_form.signature_fields
                    print(f"📋 Form signature fields: {len(sig_fields) if sig_fields else 0}")
                    
                    if sig_fields:
                        for field_name in sig_fields:
                            print(f"  📝 Form field: {field_name}")
                except Exception as e:
                    print(f"📋 Error reading form fields: {e}")
            else:
                print("📋 No AcroForm found")
                
    except Exception as e:
        print(f"❌ Error opening PDF: {e}")

def main():
    print("============================================================")
    print("Simple PDF Signature Validator (pyHanko)")
    print("============================================================")
    
    # Test files
    test_files = [
        "invalid.pdf",
        "unknown.pdf"
    ]
    
    for pdf_file in test_files:
        simple_validate_signatures(pdf_file)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main() 