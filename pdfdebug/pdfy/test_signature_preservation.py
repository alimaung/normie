#!/usr/bin/env python3
"""
Enhanced test script for signature preservation using the new PDF SDK.
Tests different field types with the signature-preserving PDF editor.
"""

import os
import sys
import shutil
import json
from datetime import datetime
from pathlib import Path

# Add the pdfy directory to the path to import the PDF SDK
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pdfy'))

try:
    from .pdfsdk import (
        SignaturePreservingPDFEditor,
        save_pdf_with_signature_preservation,
        analyze_pdf_fields
    )
    SDK_AVAILABLE = True
except ImportError as e:
    print(f"❌ Could not import PDF SDK: {e}")
    SDK_AVAILABLE = False

def test_signature_preservation(pdf_path, test_data, test_name):
    """Test signature preservation with the new PDF SDK."""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING SIGNATURE PRESERVATION: {test_name}")
    print(f"📄 PDF: {pdf_path}")
    print(f"🔢 Fields: {len(test_data)}")
    print(f"{'='*60}")
    
    if not SDK_AVAILABLE:
        print("❌ PDF SDK not available - skipping test")
        return False
    
    # Create test directory
    test_dir = Path("test_pdf_sdk")
    test_dir.mkdir(exist_ok=True)
    
    # Create test copy
    timestamp = datetime.now().strftime("%H%M%S")
    test_filename = f"signature_test_{test_name}_{timestamp}.pdf"
    test_path = test_dir / test_filename
    
    try:
        # Copy original PDF
        shutil.copy2(pdf_path, test_path)
        print(f"📄 Created test copy: {test_path}")
        
        # Analyze the PDF first
        print(f"\n🔍 Analyzing PDF structure...")
        analysis = analyze_pdf_fields(str(test_path))
        
        print(f"📊 PDF Analysis:")
        print(f"   Total fields: {analysis['total_fields']}")
        print(f"   Text fields: {analysis['text_fields']}")
        print(f"   Checkbox fields: {analysis['checkbox_fields']}")
        print(f"   Radio fields: {analysis['radio_fields']}")
        print(f"   Signature fields: {analysis['signature_fields']}")
        print(f"   Signature-safe fields: {analysis['signature_safe_fields']}")
        
        # Test field updates with signature preservation
        print(f"\n🔄 Testing field updates with signature preservation...")
        
        result_path = save_pdf_with_signature_preservation(str(test_path), test_data)
        
        print(f"✅ Signature preservation test completed!")
        print(f"📄 Result: {result_path}")
        print(f"💡 Next: Verify signature validity in Adobe Acrobat")
        
        return True
        
    except Exception as e:
        print(f"❌ Signature preservation test failed: {e}")
        return False

def test_individual_field_updates(pdf_path, test_data, test_name):
    """Test individual field updates to isolate signature corruption."""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING INDIVIDUAL FIELD UPDATES: {test_name}")
    print(f"📄 PDF: {pdf_path}")
    print(f"{'='*60}")
    
    if not SDK_AVAILABLE:
        print("❌ PDF SDK not available - skipping test")
        return {}
    
    test_dir = Path("test_pdf_sdk")
    test_dir.mkdir(exist_ok=True)
    
    results = {}
    
    for field_name, field_value in test_data.items():
        print(f"\n🔄 Testing individual field: {field_name} = '{field_value}'")
        
        # Create unique test file for each field
        timestamp = datetime.now().strftime("%H%M%S")
        test_filename = f"field_test_{test_name}_{field_name}_{timestamp}.pdf"
        test_path = test_dir / test_filename
        
        try:
            # Copy original PDF
            shutil.copy2(pdf_path, test_path)
            
            # Test single field update
            single_field_data = {field_name: field_value}
            
            with SignaturePreservingPDFEditor(str(test_path)) as editor:
                # Update single field
                update_result = editor.update_field(field_name, field_value)
                
                if update_result:
                    # Save with incremental update
                    saved_path = editor.save_incremental()
                    
                    results[field_name] = {
                        'success': True,
                        'file_path': saved_path,
                        'field_type': 'unknown'  # Will be determined by analysis
                    }
                    print(f"✅ Field {field_name} updated successfully")
                else:
                    results[field_name] = {
                        'success': False,
                        'error': 'Field not updated',
                        'field_type': 'unknown'
                    }
                    print(f"❌ Field {field_name} not updated")
                    
        except Exception as e:
            results[field_name] = {
                'success': False,
                'error': str(e),
                'field_type': 'unknown'
            }
            print(f"❌ Error updating field {field_name}: {e}")
    
    return results

def compare_with_original_method(pdf_path, test_data, test_name):
    """Compare new SDK with original method."""
    print(f"\n{'='*60}")
    print(f"🔬 COMPARING METHODS: {test_name}")
    print(f"📄 PDF: {pdf_path}")
    print(f"{'='*60}")
    
    test_dir = Path("test_pdf_sdk")
    test_dir.mkdir(exist_ok=True)
    
    # Test with original method
    try:
        from pdf_service_simple import save_pdf_changes_simple
        
        timestamp = datetime.now().strftime("%H%M%S")
        original_test_path = test_dir / f"original_method_{test_name}_{timestamp}.pdf"
        shutil.copy2(pdf_path, original_test_path)
        
        print(f"🔄 Testing original method...")
        original_result = save_pdf_changes_simple(str(original_test_path), test_data)
        print(f"✅ Original method completed: {original_result}")
        
    except Exception as e:
        print(f"❌ Original method failed: {e}")
        original_result = None
    
    # Test with new SDK
    try:
        if SDK_AVAILABLE:
            sdk_test_path = test_dir / f"new_sdk_{test_name}_{timestamp}.pdf"
            shutil.copy2(pdf_path, sdk_test_path)
            
            print(f"🔄 Testing new SDK method...")
            sdk_result = save_pdf_with_signature_preservation(str(sdk_test_path), test_data)
            print(f"✅ New SDK method completed: {sdk_result}")
        else:
            sdk_result = None
            
    except Exception as e:
        print(f"❌ New SDK method failed: {e}")
        sdk_result = None
    
    # Compare results
    print(f"\n📊 COMPARISON RESULTS:")
    print(f"   Original method: {'✅ Success' if original_result else '❌ Failed'}")
    print(f"   New SDK method: {'✅ Success' if sdk_result else '❌ Failed'}")
    
    return {
        'original_method': original_result,
        'new_sdk_method': sdk_result
    }

def main():
    """Run comprehensive signature preservation tests."""
    print("🚀 Starting comprehensive signature preservation tests...")
    print("=" * 60)
    
    # Test configuration
    original_pdf = "pdf.pdf"
    
    if not os.path.exists(original_pdf):
        print(f"❌ Original PDF not found: {original_pdf}")
        return
    
    # Test data files
    test_configs = [
        ("frontend_data_text_only.json", "text_fields"),
        ("frontend_data_checkbox_only.json", "checkbox_fields"),
        ("frontend_data_radio_only.json", "radio_fields"),
        ("frontend_data.json", "all_fields")  # If available
    ]
    
    all_results = {}
    
    for data_file, test_name in test_configs:
        if not os.path.exists(data_file):
            print(f"⏭️ Skipping {test_name} - data file not found: {data_file}")
            continue
        
        # Load test data
        with open(data_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        print(f"\n🔧 Processing {test_name} with {len(test_data)} fields...")
        
        # Test 1: Signature preservation with new SDK
        preservation_result = test_signature_preservation(original_pdf, test_data, test_name)
        
        # Test 2: Individual field updates
        individual_results = test_individual_field_updates(original_pdf, test_data, test_name)
        
        # Test 3: Compare with original method
        comparison_results = compare_with_original_method(original_pdf, test_data, test_name)
        
        # Store results
        all_results[test_name] = {
            'preservation_test': preservation_result,
            'individual_tests': individual_results,
            'method_comparison': comparison_results
        }
    
    # Generate comprehensive report
    print(f"\n{'='*60}")
    print("📋 COMPREHENSIVE TEST REPORT")
    print(f"{'='*60}")
    
    for test_name, results in all_results.items():
        print(f"\n🧪 {test_name.upper()}:")
        print(f"   Signature preservation: {'✅ Success' if results['preservation_test'] else '❌ Failed'}")
        
        individual_success = sum(1 for r in results['individual_tests'].values() if r['success'])
        individual_total = len(results['individual_tests'])
        print(f"   Individual field tests: {individual_success}/{individual_total} successful")
        
        comparison = results['method_comparison']
        print(f"   Original method: {'✅ Success' if comparison['original_method'] else '❌ Failed'}")
        print(f"   New SDK method: {'✅ Success' if comparison['new_sdk_method'] else '❌ Failed'}")
    
    # Summary recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"1. Check signature validity in Adobe Acrobat for all test files")
    print(f"2. Compare signature preservation between original and new SDK methods")
    print(f"3. Identify which field types maintain signature validity")
    print(f"4. Focus on problematic field types for further optimization")
    
    print(f"\n📁 Test files created in test_pdf_sdk/ directory:")
    test_dir = Path("test_pdf_sdk")
    if test_dir.exists():
        for file in sorted(test_dir.glob("*.pdf")):
            size = file.stat().st_size
            print(f"   - {file.name} ({size:,} bytes)")

if __name__ == "__main__":
    main() 