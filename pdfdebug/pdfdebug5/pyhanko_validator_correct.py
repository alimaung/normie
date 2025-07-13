#!/usr/bin/env python3
"""
Correct PDF Signature Validator using pyHanko
Based on the official pyHanko documentation
"""

import os
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext

def validate_pdf_with_pyhanko(pdf_path):
    """
    Validate PDF signatures using pyHanko with proper API
    """
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    try:
        print(f"📄 Validating: {pdf_path}")
        print("=" * 50)
        
        # Open PDF with pyHanko
        with open(pdf_path, 'rb') as f:
            reader = PdfFileReader(f)
            
            try:
                page_count = len(reader.root.pages) if hasattr(reader.root, 'pages') else reader.root['/Pages']['/Count']
                print(f"📄 Pages: {page_count}")
            except:
                print(f"📄 Pages: Unable to determine")
            print(f"🔒 Encrypted: {reader.encrypted}")
            
            # Get embedded signatures using the documented property
            embedded_sigs = reader.embedded_signatures
            print(f"📋 Embedded signatures: {len(embedded_sigs)}")
            
            if not embedded_sigs:
                print("  No embedded signatures found")
                return
            
            # Create validation context (no specific trust roots for now)
            vc = ValidationContext()
            
            # Validate each signature
            for i, sig_obj in enumerate(embedded_sigs):
                field_name = getattr(sig_obj, 'field_name', f'Signature_{i+1}')
                print(f"\n🔍 Signature {i+1}: {field_name}")
                
                try:
                    # Use the documented validation function
                    status = validate_pdf_signature(sig_obj, vc)
                    
                    print(f"  ✅ Validation completed")
                    print(f"  Valid: {status.valid}")
                    print(f"  Trusted: {getattr(status, 'trusted', 'N/A')}")
                    print(f"  Bottom line: {status.bottom_line}")
                    
                    # Try to get detailed information
                    try:
                        details = status.pretty_print_details()
                        print(f"  Details:\n{details}")
                    except Exception as e:
                        print(f"  Details error: {e}")
                    
                    # Determine Adobe-style status based on pyHanko's detailed analysis
                    details = status.pretty_print_details()
                    
                    if "cryptographically unsound" in details:
                        adobe_status = "INVALID"  # Signature has been invalidated
                    elif "does not cover the entire file" in details and "illegitimate" in details:
                        adobe_status = "INVALID"  # Document modified after signing
                    elif status.valid and getattr(status, 'trusted', False):
                        adobe_status = "VALID"    # Valid and trusted
                    elif status.valid:
                        adobe_status = "UNKNOWN"  # Valid but not trusted (normal)
                    else:
                        adobe_status = "INVALID"  # Generic invalid
                    
                    print(f"  🎯 Adobe-style status: {adobe_status}")
                    
                    # Provide interpretation
                    if adobe_status == "VALID":
                        print(f"  🟢 EXCELLENT: Signature is valid and trusted")
                    elif adobe_status == "UNKNOWN":
                        print(f"  🟡 GOOD: Signature is valid but certificate not trusted (normal)")
                    else:
                        print(f"  🔴 BAD: Signature is invalid")
                    
                except Exception as e:
                    print(f"  ❌ Validation failed: {e}")
                    
                    # Adobe-style interpretation: check error type
                    error_str = str(e).lower()
                    if "not a recognized subfilter" in error_str or "adbe.pkcs7.sha1" in error_str:
                        # Legacy format that Adobe can read but pyHanko can't
                        print(f"  🎯 Adobe-style status: INVALID")
                        print(f"  🔴 BAD: Legacy signature format (Adobe can read, pyHanko cannot)")
                    else:
                        # True corruption
                        print(f"  🎯 Adobe-style status: CORRUPT")
                        print(f"  💥 VERY BAD: Signature data is corrupted")
                
    except Exception as e:
        print(f"❌ Error opening PDF: {e}")

def main():
    print("============================================================")
    print("Correct PDF Signature Validator (pyHanko)")
    print("============================================================")
    
    # Test files
    test_files = [
        "invalid.pdf",
        "unknown.pdf",
        "corrupt.pdf"
    ]
    
    results = []
    
    for pdf_file in test_files:
        # Capture overall status for summary
        overall_status = "ERROR"
        try:
            with open(pdf_file, 'rb') as f:
                reader = PdfFileReader(f)
                embedded_sigs = reader.embedded_signatures
                if embedded_sigs:
                    vc = ValidationContext()
                    
                    # Check the last signature for overall status
                    for sig_obj in embedded_sigs:
                        try:
                            status = validate_pdf_signature(sig_obj, vc)
                            details = status.pretty_print_details()
                            
                            if "cryptographically unsound" in details:
                                overall_status = "INVALID"
                            elif "does not cover the entire file" in details and "illegitimate" in details:
                                overall_status = "INVALID"
                            elif status.valid and getattr(status, 'trusted', False):
                                overall_status = "VALID"
                            elif status.valid:
                                overall_status = "UNKNOWN"
                            else:
                                overall_status = "INVALID"
                            break  # Use first successful validation
                        except Exception as e:
                            # Adobe-style interpretation: if we can't parse, check the error type
                            error_str = str(e).lower()
                            if "not a recognized subfilter" in error_str or "adbe.pkcs7.sha1" in error_str:
                                # Legacy format that Adobe can read but pyHanko can't - this is INVALID in Adobe terms
                                overall_status = "INVALID"
                            else:
                                # True corruption that neither can handle well
                                overall_status = "CORRUPT"
                else:
                    overall_status = "NO_SIGNATURES"
        except:
            overall_status = "ERROR"
        
        results.append((pdf_file, overall_status))
        validate_pdf_with_pyhanko(pdf_file)
        print("\n" + "="*50 + "\n")
    
    # Summary
    print("📋 SUMMARY")
    print("=" * 20)
    for pdf_file, status in results:
        icons = {"VALID": "✅", "UNKNOWN": "🟡", "INVALID": "❌", "CORRUPT": "💥", "ERROR": "⚠️", "NO_SIGNATURES": "⚪"}
        icon = icons.get(status, "❓")
        print(f"{icon} {pdf_file:<15} {status}")
    print()

if __name__ == "__main__":
    main() 