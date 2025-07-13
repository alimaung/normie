#!/usr/bin/env python3
"""
PDF signature validator with diff analysis disabled
Focuses only on cryptographic validity, ignoring incremental updates
"""

import sys
import os
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext

def validate_pdf_signatures(pdf_path):
    """
    Validate PDF signatures without diff analysis
    Only checks cryptographic validity, ignores incremental updates
    """
    results = {
        'file': pdf_path,
        'signatures': [],
        'overall_status': 'UNKNOWN'
    }
    
    try:
        with open(pdf_path, 'rb') as doc:
            reader = PdfFileReader(doc)
            signatures = reader.embedded_signatures
            
            if not signatures:
                results['overall_status'] = 'NO_SIGNATURES'
                return results
            
            # Use default validation context (no specific trust roots)
            vc = ValidationContext()
            
            for i, sig in enumerate(signatures):
                sig_result = {
                    'index': i,
                    'field_name': sig.field_name if hasattr(sig, 'field_name') else f'Signature_{i}',
                    'status': 'UNKNOWN'
                }
                
                try:
                    # Validate WITHOUT diff analysis - skip_diff=True
                    status = validate_pdf_signature(sig, vc, skip_diff=True)
                    
                    # Extract key information
                    sig_result['status'] = 'VALID' if status.bottom_line else 'INVALID'
                    sig_result['coverage'] = str(status.coverage) if hasattr(status, 'coverage') else 'Unknown'
                    sig_result['intact'] = status.intact if hasattr(status, 'intact') else None
                    sig_result['valid'] = status.valid if hasattr(status, 'valid') else None
                    sig_result['trusted'] = status.trusted if hasattr(status, 'trusted') else None
                    
                except Exception as e:
                    sig_result['status'] = 'ERROR'
                    sig_result['error'] = str(e)
                
                results['signatures'].append(sig_result)
            
            # Determine overall status
            if all(sig['status'] == 'VALID' for sig in results['signatures']):
                results['overall_status'] = 'ALL_VALID'
            elif any(sig['status'] == 'VALID' for sig in results['signatures']):
                results['overall_status'] = 'MIXED'
            else:
                results['overall_status'] = 'ALL_INVALID'
                
    except Exception as e:
        results['overall_status'] = 'ERROR'
        results['error'] = str(e)
    
    return results

def print_validation_results(results):
    """Print validation results in a clean format"""
    file_path = results['file']
    filename = os.path.basename(file_path)
    
    # Status emoji mapping
    status_emoji = {
        'ALL_VALID': '✅',
        'MIXED': '⚠️',
        'ALL_INVALID': '❌',
        'NO_SIGNATURES': '📄',
        'ERROR': '💥',
        'UNKNOWN': '❓'
    }
    
    emoji = status_emoji.get(results['overall_status'], '❓')
    print(f"{emoji} {filename:<25} {results['overall_status']}")
    
    # Show individual signature details
    for sig in results['signatures']:
        status_str = sig['status']
        if sig['status'] == 'VALID':
            coverage = sig.get('coverage', 'Unknown')
            print(f"   └─ {sig['field_name']}: ✅ VALID (Coverage: {coverage})")
        elif sig['status'] == 'INVALID':
            print(f"   └─ {sig['field_name']}: ❌ INVALID")
        else:
            error = sig.get('error', 'Unknown error')
            print(f"   └─ {sig['field_name']}: 💥 ERROR - {error}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python pyhanko_validator_no_diff.py <pdf_file1> [pdf_file2] ...")
        print("  Validates PDF signatures without incremental update analysis")
        print("  Focuses only on cryptographic validity")
        sys.exit(1)
    
    pdf_files = sys.argv[1:]
    
    print(f"{'='*60}")
    print(f"PDF Signature Validation (No Diff Analysis)")
    print(f"{'='*60}")
    
    all_results = []
    
    for pdf_path in pdf_files:
        if not os.path.exists(pdf_path):
            print(f"💥 {os.path.basename(pdf_path):<25} FILE_NOT_FOUND")
            continue
        
        results = validate_pdf_signatures(pdf_path)
        all_results.append(results)
        print_validation_results(results)
    
    # Summary
    if len(all_results) > 1:
        print(f"\n{'='*60}")
        valid_count = sum(1 for r in all_results if r['overall_status'] == 'ALL_VALID')
        total_count = len(all_results)
        print(f"Summary: {valid_count}/{total_count} files have all signatures valid")

if __name__ == "__main__":
    main() 