#!/usr/bin/env python3
"""
Example usage of LitePDF DLL for PDF signature verification

This demonstrates how to use the LitePDF library with Python to check for
digital signatures in PDF files.
"""

from lite_pdf import LitePDFSignatureVerifier
import os

def check_single_pdf(pdf_path: str):
    """Check a single PDF for signatures"""
    print(f"🔍 Checking: {pdf_path}")
    
    try:
        with LitePDFSignatureVerifier() as verifier:
            result = verifier.analyze_pdf_signatures(pdf_path)
            
            if not result['exists']:
                print(f"   ❌ File not found")
                return False
            
            if not result['loaded']:
                print(f"   ❌ Failed to load PDF")
                return False
            
            print(f"   ✅ PDF loaded successfully")
            print(f"   📝 Signatures found: {result['signature_count']}")
            
            if result['has_signatures']:
                print(f"   🔐 This PDF is digitally signed!")
                for sig in result['signatures']:
                    print(f"      - Signature {sig['index']}: {sig['status']}")
                    if sig['has_data']:
                        print(f"        Data size: {sig['data_size']} bytes")
                return True
            else:
                print(f"   ℹ️  No digital signatures found")
                return False
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def batch_check_pdfs(pdf_paths: list):
    """Check multiple PDFs for signatures"""
    print("🔐 Batch PDF Signature Verification")
    print("=" * 50)
    
    results = []
    
    for pdf_path in pdf_paths:
        has_signatures = check_single_pdf(pdf_path)
        results.append({
            'path': pdf_path,
            'has_signatures': has_signatures
        })
        print()
    
    # Summary
    print("📊 SUMMARY")
    print("-" * 30)
    signed_count = sum(1 for r in results if r['has_signatures'])
    print(f"Total PDFs checked: {len(results)}")
    print(f"PDFs with signatures: {signed_count}")
    
    if signed_count > 0:
        print(f"\n🔐 Signed PDFs:")
        for result in results:
            if result['has_signatures']:
                print(f"   - {os.path.basename(result['path'])}")

def main():
    """Main example function"""
    print("LitePDF Signature Verification Example")
    print("=" * 50)
    
    # Example 1: Check a single PDF
    print("\n📄 Example 1: Single PDF Check")
    print("-" * 30)
    
    # You can replace this with any PDF file path
    single_pdf = "../test_pdf/test_checkboxes_194349.pdf"
    check_single_pdf(single_pdf)
    
    # Example 2: Batch check multiple PDFs
    print("\n📄 Example 2: Batch PDF Check")
    print("-" * 30)
    
    # List of PDFs to check
    pdf_list = [
        "../test_pdf/test_checkboxes_194349.pdf",
        "../test_pdf/test_radio_buttons_194347.pdf", 
        "../test_pdf/test_text_fields_194346.pdf",
    ]
    
    batch_check_pdfs(pdf_list)
    
    # Example 3: Programmatic usage
    print("\n💻 Example 3: Programmatic Usage")
    print("-" * 30)
    
    try:
        with LitePDFSignatureVerifier() as verifier:
            # Check multiple files programmatically
            for pdf_path in pdf_list:
                if os.path.exists(pdf_path):
                    result = verifier.analyze_pdf_signatures(pdf_path)
                    
                    print(f"File: {os.path.basename(pdf_path)}")
                    print(f"  Loaded: {result['loaded']}")
                    print(f"  Signatures: {result['signature_count']}")
                    
                    if result['errors']:
                        print(f"  Errors: {', '.join(result['errors'])}")
                    
                    print()
                    
    except Exception as e:
        print(f"Error in programmatic usage: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Examples completed!")
    print("\n📖 Key Points:")
    print("• LitePDF DLL provides basic signature detection")
    print("• Use context manager (with statement) for proper cleanup")
    print("• Some PDFs may not load due to format or DLL version compatibility")
    print("• This detects signatures but doesn't validate them cryptographically")
    print("• For full validation, additional crypto libraries would be needed")

if __name__ == "__main__":
    main() 