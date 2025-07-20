#!/usr/bin/env python3
"""
Adobe-style PDF Signature Validator using pyHanko
Properly detects: UNKNOWN (good), INVALID (bad), CORRUPT (very bad)
"""

import os
import sys
from datetime import datetime
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature, ValidationContext, RevocationCheckingRule
from pyhanko.sign.validation.errors import *
import io

def validate_pdf_signatures_pyhanko(pdf_path):
    """
    Validate PDF signatures using pyHanko - much more accurate than PyMuPDF
    Returns Adobe-style validation results
    """
    
    if not os.path.exists(pdf_path):
        return "FILE_NOT_FOUND", f"PDF file not found: {pdf_path}", []
    
    try:
        print(f"📄 Validating: {pdf_path}")
        print("=" * 50)
        
        # Open PDF with pyHanko
        with open(pdf_path, 'rb') as f:
            reader = PdfFileReader(f)
            
            print(f"📄 Pages: {len(reader.root.pages)}")
            print(f"🔒 Encrypted: {reader.encrypted}")
            
            # Get signature fields
            sig_fields = reader.root.acro_form.signature_fields if reader.root.acro_form else []
            print(f"📋 Signature fields found: {len(sig_fields)}")
            
            # Validate each signature
            validation_results = []
            
            for field_name in sig_fields:
                print(f"\n🔍 Validating signature field: {field_name}")
                
                try:
                    # Create validation context
                    vc = ValidationContext(
                        trust_roots=None,  # No specific trust roots
                        revocation_checking=RevocationCheckingRule.DISABLED,  # Disable OCSP/CRL for now
                        best_signature_time=None
                    )
                    
                    # Validate the signature
                    sig_obj = reader.embedded_signatures[field_name]
                    validation_result = validate_pdf_signature(
                        sig_obj, 
                        validation_context=vc
                    )
                    
                    # Analyze validation result
                    status, details = analyze_validation_result(validation_result, field_name)
                    validation_results.append({
                        'field_name': field_name,
                        'status': status,
                        'details': details,
                        'validation_result': validation_result
                    })
                    
                    print(f"  Status: {status}")
                    print(f"  Details: {details}")
                    
                except Exception as e:
                    error_status = categorize_validation_error(e)
                    validation_results.append({
                        'field_name': field_name,
                        'status': error_status,
                        'details': str(e),
                        'error': e
                    })
                    print(f"  ❌ Error: {error_status} - {e}")
            
            # Determine overall status
            overall_status = determine_overall_status(validation_results)
            
            return overall_status, f"Validated {len(validation_results)} signatures", validation_results
            
    except Exception as e:
        return "ERROR", f"Failed to open/read PDF: {e}", []

def analyze_validation_result(validation_result, field_name):
    """Analyze pyHanko validation result and return Adobe-style status"""
    
    try:
        # Check if validation was successful
        if validation_result.valid:
            # Check trust status
            if validation_result.trusted:
                return "VALID", "Signature is valid and trusted"
            else:
                return "UNKNOWN", "Signature is valid but certificate not trusted (this is normal)"
        else:
            # Check why validation failed
            summary = validation_result.summary()
            
            # Look for specific failure reasons
            if "document has been modified" in summary.lower():
                return "INVALID", "Document has been modified after signing"
            elif "certificate" in summary.lower() and "expired" in summary.lower():
                return "INVALID", "Certificate has expired"
            elif "certificate" in summary.lower() and "revoked" in summary.lower():
                return "INVALID", "Certificate has been revoked"
            elif "corrupt" in summary.lower() or "malformed" in summary.lower():
                return "CORRUPT", "Signature data is corrupted"
            else:
                return "INVALID", f"Signature validation failed: {summary}"
                
    except Exception as e:
        return "CORRUPT", f"Cannot analyze validation result: {e}"

def categorize_validation_error(error):
    """Categorize validation errors into Adobe-style statuses"""
    
    error_str = str(error).lower()
    
    if "corrupt" in error_str or "malformed" in error_str:
        return "CORRUPT"
    elif "modified" in error_str or "changed" in error_str:
        return "INVALID"
    elif "certificate" in error_str:
        return "INVALID"
    else:
        return "ERROR"

def determine_overall_status(validation_results):
    """Determine overall document signature status"""
    
    if not validation_results:
        return "NO_SIGNATURES"
    
    statuses = [result['status'] for result in validation_results]
    
    # Priority order: CORRUPT > INVALID > ERROR > UNKNOWN > VALID
    if "CORRUPT" in statuses:
        return "CORRUPT"
    elif "INVALID" in statuses:
        return "INVALID"
    elif "ERROR" in statuses:
        return "ERROR"
    elif "UNKNOWN" in statuses:
        return "UNKNOWN"
    elif "VALID" in statuses:
        return "VALID"
    else:
        return "NO_SIGNATURES"

def get_status_icon(status):
    """Get icon for status"""
    icons = {
        "VALID": "✅",
        "UNKNOWN": "🟡",
        "INVALID": "❌",
        "CORRUPT": "💥",
        "ERROR": "⚠️",
        "NO_SIGNATURES": "⚪"
    }
    return icons.get(status, "❓")

def interpret_status(status):
    """Provide Adobe-style interpretation"""
    interpretations = {
        "VALID": "🟢 EXCELLENT: Signatures are valid and certificates are trusted",
        "UNKNOWN": "🟡 GOOD: Signatures are intact but certificates not in trust store (normal)",
        "INVALID": "🔴 BAD: Signatures have been invalidated (document modified or cert issues)",
        "CORRUPT": "🔴 VERY BAD: Signature data is corrupted or malformed",
        "ERROR": "⚠️ ERROR: Could not validate signatures",
        "NO_SIGNATURES": "⚪ INFO: No digital signatures found"
    }
    return interpretations.get(status, "❓ UNKNOWN STATUS")

def main():
    print("============================================================")
    print("Adobe-style PDF Signature Validator (pyHanko)")
    print("============================================================")
    
    # Test files
    test_files = [
        "invalid.pdf",
        "unknown.pdf",
        "corrupt.pdf"
    ]
    
    for pdf_file in test_files:
        print(f"\n📄 Testing: {pdf_file}")
        print("=" * 50)
        
        if not os.path.exists(pdf_file):
            print(f"❌ File not found: {pdf_file}")
            continue
            
        overall_status, summary, validation_results = validate_pdf_signatures_pyhanko(pdf_file)
        
        print(f"\n📊 Results Summary:")
        print(f"  Overall Status: {get_status_icon(overall_status)} {overall_status}")
        print(f"  Summary: {summary}")
        
        print(f"\n💡 Adobe-style Interpretation:")
        print(f"  {interpret_status(overall_status)}")
        
        # Detailed results
        if validation_results:
            print(f"\n🔍 Detailed Results:")
            for result in validation_results:
                icon = get_status_icon(result['status'])
                print(f"  {icon} {result['field_name']}: {result['status']}")
                print(f"    {result['details']}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    main() 