#!/usr/bin/env python3
"""
Enhanced PDF signature validator using pyHanko's full API
Provides detailed validation information including incremental update analysis
"""

import sys
import os
from pathlib import Path
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext

def validate_pdf_signatures_enhanced(pdf_path):
    """
    Enhanced signature validation with detailed analysis
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
                    'status': 'UNKNOWN',
                    'details': {}
                }
                
                try:
                    # Validate with full analysis
                    status = validate_pdf_signature(sig, vc)
                    
                    # Extract detailed information
                    sig_result['status'] = 'VALID' if status.bottom_line else 'INVALID'
                    sig_result['details'] = {
                        'bottom_line': status.bottom_line,
                        'coverage': str(status.coverage) if hasattr(status, 'coverage') else 'Unknown',
                        'modification_level': str(status.modification_level) if hasattr(status, 'modification_level') else 'Unknown',
                        'docmdp_ok': status.docmdp_ok if hasattr(status, 'docmdp_ok') else None,
                        'intact': status.intact if hasattr(status, 'intact') else None,
                        'valid': status.valid if hasattr(status, 'valid') else None,
                        'trusted': status.trusted if hasattr(status, 'trusted') else None
                    }
                    
                    # Get human-readable details
                    try:
                        sig_result['human_readable'] = status.pretty_print_details()
                    except Exception as e:
                        sig_result['human_readable'] = f"Error getting details: {e}"
                    
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

def validate_pdf_signatures_fast(pdf_path):
    """
    Fast validation without incremental update analysis
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
            
            vc = ValidationContext()
            
            for i, sig in enumerate(signatures):
                sig_result = {
                    'index': i,
                    'field_name': sig.field_name if hasattr(sig, 'field_name') else f'Signature_{i}',
                    'status': 'UNKNOWN'
                }
                
                try:
                    # Validate without diff analysis for speed
                    status = validate_pdf_signature(sig, vc, skip_diff=True)
                    sig_result['status'] = 'VALID' if status.bottom_line else 'INVALID'
                    sig_result['coverage'] = str(status.coverage) if hasattr(status, 'coverage') else 'Unknown'
                    
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

def print_validation_results(results, detailed=False):
    """Print validation results in a readable format"""
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
    print(f"{emoji} {filename:<20} {results['overall_status']}")
    
    if detailed and results['signatures']:
        for sig in results['signatures']:
            print(f"  └─ {sig['field_name']}: {sig['status']}")
            if 'details' in sig:
                details = sig['details']
                print(f"     Coverage: {details.get('coverage', 'Unknown')}")
                print(f"     Modification Level: {details.get('modification_level', 'Unknown')}")
                print(f"     DocMDP OK: {details.get('docmdp_ok', 'Unknown')}")
            
            if 'human_readable' in sig and detailed:
                print("     Human-readable details:")
                for line in sig['human_readable'].split('\n'):
                    if line.strip():
                        print(f"       {line}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python pyhanko_validator_enhanced.py <pdf_file> [--detailed] [--fast]")
        print("  --detailed: Show detailed validation information")
        print("  --fast: Skip incremental update analysis for faster validation")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    detailed = '--detailed' in sys.argv
    fast = '--fast' in sys.argv
    
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found")
        sys.exit(1)
    
    print(f"{'='*60}")
    print(f"PDF Signature Validation Report")
    print(f"{'='*60}")
    
    if fast:
        print("Running FAST validation (no incremental update analysis)")
        results = validate_pdf_signatures_fast(pdf_path)
    else:
        print("Running FULL validation (with incremental update analysis)")
        results = validate_pdf_signatures_enhanced(pdf_path)
    
    print_validation_results(results, detailed)
    
    if results['overall_status'] == 'ERROR':
        print(f"Error: {results.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main() 