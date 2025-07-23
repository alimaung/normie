#!/usr/bin/env python3
"""
Test script for CAS Number Extractor
Quick test to verify CAS extraction functionality
"""

import os
import sys

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cas_extractor import ChemicalExtractor


def test_chemical_extractor():
    """Test the chemical identifier extractor with available SDS files"""
    print("🧪 Testing Chemical Identifier Extractor")
    print("=" * 50)
    
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sds_dir = os.path.join(script_dir, "sds")
    
    if not os.path.exists(sds_dir):
        print(f"❌ SDS directory not found: {sds_dir}")
        return
    
    # Find PDF files
    pdf_files = [f for f in os.listdir(sds_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ No PDF files found in: {sds_dir}")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files")
    
    # Initialize extractor
    extractor = ChemicalExtractor()
    
    # Test with first few files
    test_files = pdf_files[:3]  # Test first 3 files
    
    for filename in test_files:
        pdf_path = os.path.join(sds_dir, filename)
        print(f"\n🔍 Testing: {filename}")
        print("-" * 40)
        
        try:
            result = extractor.extract_chemical_identifiers(pdf_path)
            
            print(f"Section 3 Found: {'✅' if result.section_3_found else '❌'}")
            print(f"Extraction Confidence: {result.extraction_confidence:.3f}")
            print(f"Detected Substances: {len(result.detected_substances)}")
            
            print(f"\n📊 Summary:")
            print(f"  🧪 CAS Numbers: {len(result.cas_numbers)} ({result.unique_cas_count} unique)")
            print(f"  🏷️ EC Numbers: {len(result.ec_numbers)} ({result.unique_ec_count} unique)")
            print(f"  📋 REACH Numbers: {len(result.reach_numbers)} ({result.unique_reach_count} unique)")
            
            if result.cas_numbers:
                print("\n🧪 CAS Numbers:")
                for i, identifier in enumerate(result.cas_numbers, 1):
                    substance_info = f" ({identifier.substance_name})" if identifier.substance_name else ""
                    concentration_info = f" - {identifier.concentration}" if identifier.concentration else ""
                    print(f"  {i}. {identifier.number}{substance_info}{concentration_info}")
                    print(f"     Context: {identifier.context_phrase} (confidence: {identifier.confidence:.2f})")
                    print(f"     Section: {identifier.section}, Line: {identifier.line_number}")
            
            if result.ec_numbers:
                print("\n🏷️ EC Numbers:")
                for i, identifier in enumerate(result.ec_numbers, 1):
                    substance_info = f" ({identifier.substance_name})" if identifier.substance_name else ""
                    concentration_info = f" - {identifier.concentration}" if identifier.concentration else ""
                    print(f"  {i}. {identifier.number}{substance_info}{concentration_info}")
                    print(f"     Context: {identifier.context_phrase} (confidence: {identifier.confidence:.2f})")
                    print(f"     Section: {identifier.section}, Line: {identifier.line_number}")
            
            if result.reach_numbers:
                print("\n📋 REACH Numbers:")
                for i, identifier in enumerate(result.reach_numbers, 1):
                    substance_info = f" ({identifier.substance_name})" if identifier.substance_name else ""
                    print(f"  {i}. {identifier.number}{substance_info}")
                    print(f"     Context: {identifier.context_phrase} (confidence: {identifier.confidence:.2f})")
                    print(f"     Section: {identifier.section}, Line: {identifier.line_number}")
            
            if result.detected_substances:
                print(f"\n🔬 Substances: {', '.join(result.detected_substances)}")
            
            if result.extraction_notes:
                print(f"\n📝 Notes:")
                for note in result.extraction_notes:
                    print(f"  • {note}")
        
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
    
    print(f"\n✅ Chemical identifier extractor test completed!")


if __name__ == "__main__":
    test_chemical_extractor() 