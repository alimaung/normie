#!/usr/bin/env python3
"""
Compact PDF Signature Validator using pyHanko
Focused, data-driven output with suppressed verbose errors
"""

import os
import warnings
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext

# Suppress warnings and verbose output
warnings.filterwarnings("ignore")

def validate_pdf_compact(pdf_path):
    """
    Compact validation with minimal output
    """
    
    if not os.path.exists(pdf_path):
        return "FILE_NOT_FOUND", []
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PdfFileReader(f)
            embedded_sigs = reader.embedded_signatures
            
            if not embedded_sigs:
                return "NO_SIGNATURES", []
            
            vc = ValidationContext()
            results = []
            
            for i, sig_obj in enumerate(embedded_sigs):
                field_name = getattr(sig_obj, 'field_name', f'Sig_{i+1}')
                
                try:
                    # Suppress stdout and stderr during validation
                    import sys
                    from io import StringIO
                    old_stdout = sys.stdout
                    old_stderr = sys.stderr
                    
                    sys.stdout = StringIO()
                    sys.stderr = StringIO()
                    
                    try:
                        status = validate_pdf_signature(sig_obj, vc)
                        details = status.pretty_print_details()
                        
                        # Determine status
                        if "cryptographically unsound" in details:
                            sig_status = "INVALID"
                        elif "does not cover the entire file" in details and "illegitimate" in details:
                            sig_status = "INVALID"
                        elif status.valid and getattr(status, 'trusted', False):
                            sig_status = "VALID"
                        elif status.valid:
                            sig_status = "UNKNOWN"
                        else:
                            sig_status = "INVALID"
                            
                    finally:
                        sys.stdout = old_stdout
                        sys.stderr = old_stderr
                    
                    results.append((field_name, sig_status))
                    
                except Exception as e:
                    error_str = str(e).lower()
                    if "not a recognized subfilter" in error_str or "adbe.pkcs7.sha1" in error_str:
                        sig_status = "INVALID"  # Legacy format
                    else:
                        sig_status = "CORRUPT"  # True corruption
                    
                    results.append((field_name, sig_status))
            
            # Determine overall status
            statuses = [status for _, status in results]
            if "CORRUPT" in statuses:
                overall = "CORRUPT"
            elif "INVALID" in statuses:
                overall = "INVALID"
            elif "UNKNOWN" in statuses:
                overall = "UNKNOWN"
            elif "VALID" in statuses:
                overall = "VALID"
            else:
                overall = "NO_SIGNATURES"
            
            return overall, results
            
    except Exception:
        return "ERROR", []

def main():
    print("PDF Signature Validator (Compact)")
    print("=" * 40)
    
    test_files = [
        "invalid.pdf",
        "unknown.pdf", 
        "corrupt.pdf"
    ]
    
    all_results = []
    
    for pdf_file in test_files:
        overall_status, sig_results = validate_pdf_compact(pdf_file)
        all_results.append((pdf_file, overall_status, sig_results))
        
        # Compact per-file output
        icons = {"VALID": "✅", "UNKNOWN": "🟡", "INVALID": "❌", "CORRUPT": "💥", "ERROR": "⚠️", "NO_SIGNATURES": "⚪"}
        icon = icons.get(overall_status, "❓")
        
        print(f"\n{icon} {pdf_file}")
        print(f"   Overall: {overall_status}")
        
        if sig_results:
            print(f"   Signatures: {len(sig_results)}")
            for field_name, status in sig_results:
                sig_icon = icons.get(status, "❓")
                print(f"     {sig_icon} {field_name}: {status}")
    
    # Final summary
    print(f"\n📋 SUMMARY")
    print("=" * 20)
    for pdf_file, overall_status, _ in all_results:
        icon = icons.get(overall_status, "❓")
        print(f"{icon} {pdf_file:<15} {overall_status}")

if __name__ == "__main__":
    main() 