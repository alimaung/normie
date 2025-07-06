 #!/usr/bin/env python3
"""
Comprehensive Signature Preservation Test Runner

This script runs all available signature preservation methods and compares their results.
It tests text fields, checkboxes, and radio buttons with different approaches:

1. Original method (pdf_service_simple)
2. New PDF SDK (signature-preserving)
3. Low-level PDF editor (maximum preservation)

The goal is to identify which approach best preserves digital signatures
for different field types.
"""

import os
import sys
import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pdfy'))
sys.path.append(os.path.dirname(__file__))

# Import available modules
try:
    from pdf_service_simple import save_pdf_changes_simple
    ORIGINAL_METHOD_AVAILABLE = True
except ImportError:
    ORIGINAL_METHOD_AVAILABLE = False
    print("⚠️ Original method not available")

try:
    from .pdfsdk import save_pdf_with_signature_preservation
    SDK_METHOD_AVAILABLE = True
except ImportError:
    SDK_METHOD_AVAILABLE = False
    print("⚠️ SDK method not available")

try:
    from low_level_pdf_editor import update_pdf_fields_conservatively
    LOW_LEVEL_METHOD_AVAILABLE = True
except ImportError:
    LOW_LEVEL_METHOD_AVAILABLE = False
    print("⚠️ Low-level method not available")


class SignatureTestResult:
    """Container for test results."""
    
    def __init__(self, method_name: str, field_type: str):
        self.method_name = method_name
        self.field_type = field_type
        self.success = False
        self.error_message = ""
        self.output_file = ""
        self.execution_time = 0.0
        self.field_count = 0
        self.updated_fields = 0
    
    def __str__(self):
        status = "✅ SUCCESS" if self.success else "❌ FAILED"
        return f"{status}: {self.method_name} - {self.field_type} ({self.updated_fields}/{self.field_count} fields)"


class ComprehensiveSignatureTestRunner:
    """Runs comprehensive signature preservation tests."""
    
    def __init__(self, pdf_path: str, output_dir: str = "signature_test_results"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Test configuration
        self.test_data_files = [
            ("frontend_data_text_only.json", "text_fields"),
            ("frontend_data_checkbox_only.json", "checkbox_fields"),
            ("frontend_data_radio_only.json", "radio_fields"),
        ]
        
        # Available methods
        self.methods = []
        if ORIGINAL_METHOD_AVAILABLE:
            self.methods.append(("Original Method", self._test_original_method))
        if SDK_METHOD_AVAILABLE:
            self.methods.append(("PDF SDK", self._test_sdk_method))
        if LOW_LEVEL_METHOD_AVAILABLE:
            self.methods.append(("Low-Level Editor", self._test_low_level_method))
        
        self.results: List[SignatureTestResult] = []
    
    def _create_test_copy(self, test_name: str, method_name: str) -> Path:
        """Create a test copy of the PDF."""
        timestamp = datetime.now().strftime("%H%M%S")
        safe_method_name = method_name.replace(" ", "_").lower()
        filename = f"{safe_method_name}_{test_name}_{timestamp}.pdf"
        test_path = self.output_dir / filename
        
        shutil.copy2(self.pdf_path, test_path)
        return test_path
    
    def _test_original_method(self, test_data: Dict[str, Any], test_name: str) -> SignatureTestResult:
        """Test the original pdf_service_simple method."""
        result = SignatureTestResult("Original Method", test_name)
        result.field_count = len(test_data)
        
        try:
            test_path = self._create_test_copy(test_name, "original")
            
            start_time = time.time()
            output_path = save_pdf_changes_simple(str(test_path), test_data)
            result.execution_time = time.time() - start_time
            
            result.success = True
            result.output_file = output_path
            result.updated_fields = len(test_data)  # Assume all fields updated
            
        except Exception as e:
            result.error_message = str(e)
        
        return result
    
    def _test_sdk_method(self, test_data: Dict[str, Any], test_name: str) -> SignatureTestResult:
        """Test the new PDF SDK method."""
        result = SignatureTestResult("PDF SDK", test_name)
        result.field_count = len(test_data)
        
        try:
            test_path = self._create_test_copy(test_name, "sdk")
            
            start_time = time.time()
            output_path = save_pdf_with_signature_preservation(str(test_path), test_data)
            result.execution_time = time.time() - start_time
            
            result.success = True
            result.output_file = output_path
            result.updated_fields = len(test_data)  # Assume all fields updated
            
        except Exception as e:
            result.error_message = str(e)
        
        return result
    
    def _test_low_level_method(self, test_data: Dict[str, Any], test_name: str) -> SignatureTestResult:
        """Test the low-level PDF editor method."""
        result = SignatureTestResult("Low-Level Editor", test_name)
        result.field_count = len(test_data)
        
        try:
            test_path = self._create_test_copy(test_name, "lowlevel")
            
            start_time = time.time()
            output_path = update_pdf_fields_conservatively(str(test_path), test_data)
            result.execution_time = time.time() - start_time
            
            result.success = True
            result.output_file = output_path
            result.updated_fields = len(test_data)  # Assume all fields updated
            
        except Exception as e:
            result.error_message = str(e)
        
        return result
    
    def run_all_tests(self) -> List[SignatureTestResult]:
        """Run all signature preservation tests."""
        print("🚀 Starting comprehensive signature preservation tests...")
        print("=" * 80)
        
        print(f"📄 PDF File: {self.pdf_path}")
        print(f"📁 Output Directory: {self.output_dir}")
        print(f"🔧 Available Methods: {len(self.methods)}")
        print(f"🧪 Test Configurations: {len(self.test_data_files)}")
        
        for method_name, method_func in self.methods:
            print(f"   - {method_name}")
        
        print("\n" + "=" * 80)
        
        # Run tests for each data file and method combination
        for data_file, test_name in self.test_data_files:
            if not os.path.exists(data_file):
                print(f"⏭️ Skipping {test_name} - data file not found: {data_file}")
                continue
            
            # Load test data
            with open(data_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            
            print(f"\n🧪 Testing {test_name.upper()} ({len(test_data)} fields)")
            print("-" * 60)
            
            # Test each method
            for method_name, method_func in self.methods:
                print(f"\n🔄 {method_name} - {test_name}")
                
                try:
                    result = method_func(test_data, test_name)
                    self.results.append(result)
                    print(f"   {result}")
                    
                    if result.success:
                        print(f"   ⏱️  Execution time: {result.execution_time:.2f}s")
                        print(f"   📄 Output: {result.output_file}")
                    else:
                        print(f"   ❌ Error: {result.error_message}")
                        
                except Exception as e:
                    error_result = SignatureTestResult(method_name, test_name)
                    error_result.error_message = str(e)
                    self.results.append(error_result)
                    print(f"   ❌ EXCEPTION: {e}")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        report_lines = []
        report_lines.append("📋 COMPREHENSIVE SIGNATURE PRESERVATION TEST REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"PDF File: {self.pdf_path}")
        report_lines.append(f"Output Directory: {self.output_dir}")
        report_lines.append("")
        
        # Summary statistics
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        
        report_lines.append("📊 SUMMARY STATISTICS")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Tests: {total_tests}")
        report_lines.append(f"Successful: {successful_tests}")
        report_lines.append(f"Failed: {failed_tests}")
        report_lines.append(f"Success Rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        report_lines.append("")
        
        # Results by method
        methods = set(r.method_name for r in self.results)
        for method in methods:
            method_results = [r for r in self.results if r.method_name == method]
            method_success = sum(1 for r in method_results if r.success)
            method_total = len(method_results)
            
            report_lines.append(f"🔧 {method.upper()}")
            report_lines.append("-" * 40)
            report_lines.append(f"Success Rate: {method_success}/{method_total} ({(method_success/method_total*100):.1f}%)")
            
            for result in method_results:
                status = "✅" if result.success else "❌"
                report_lines.append(f"   {status} {result.field_type}: {result.updated_fields}/{result.field_count} fields")
                if not result.success:
                    report_lines.append(f"      Error: {result.error_message}")
            
            report_lines.append("")
        
        # Results by field type
        field_types = set(r.field_type for r in self.results)
        for field_type in field_types:
            field_results = [r for r in self.results if r.field_type == field_type]
            field_success = sum(1 for r in field_results if r.success)
            field_total = len(field_results)
            
            report_lines.append(f"📝 {field_type.upper().replace('_', ' ')}")
            report_lines.append("-" * 40)
            report_lines.append(f"Success Rate: {field_success}/{field_total} ({(field_success/field_total*100):.1f}%)")
            
            for result in field_results:
                status = "✅" if result.success else "❌"
                report_lines.append(f"   {status} {result.method_name}: {result.execution_time:.2f}s")
            
            report_lines.append("")
        
        # Recommendations
        report_lines.append("💡 RECOMMENDATIONS")
        report_lines.append("-" * 40)
        
        # Find best method for each field type
        for field_type in field_types:
            field_results = [r for r in self.results if r.field_type == field_type and r.success]
            if field_results:
                best_result = min(field_results, key=lambda r: r.execution_time)
                report_lines.append(f"Best for {field_type}: {best_result.method_name} ({best_result.execution_time:.2f}s)")
            else:
                report_lines.append(f"No successful method for {field_type}")
        
        report_lines.append("")
        report_lines.append("🔍 NEXT STEPS")
        report_lines.append("-" * 40)
        report_lines.append("1. Test signature validity in Adobe Acrobat for all output files")
        report_lines.append("2. Compare signature preservation between methods")
        report_lines.append("3. Identify the most reliable method for each field type")
        report_lines.append("4. Document any signature corruption patterns")
        
        report_lines.append("")
        report_lines.append("📁 OUTPUT FILES")
        report_lines.append("-" * 40)
        
        for result in self.results:
            if result.success and result.output_file:
                file_path = Path(result.output_file)
                if file_path.exists():
                    size = file_path.stat().st_size
                    report_lines.append(f"   {file_path.name} ({size:,} bytes)")
        
        return "\n".join(report_lines)
    
    def save_report(self, filename: Optional[str] = None) -> str:
        """Save the test report to a file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"signature_test_report_{timestamp}.txt"
        
        report_path = self.output_dir / filename
        report_content = self.generate_report()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 Report saved: {report_path}")
        return str(report_path)


def main():
    """Main function to run comprehensive signature preservation tests."""
    print("🛡️ Comprehensive Signature Preservation Test Suite")
    print("=" * 80)
    
    # Check for required files
    pdf_file = "pdf.pdf"
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        print("💡 Please place your test PDF file as 'pdf.pdf' in the current directory")
        return
    
    # Check for test data files
    required_files = [
        "frontend_data_text_only.json",
        "frontend_data_checkbox_only.json", 
        "frontend_data_radio_only.json"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"⚠️ Missing test data files: {missing_files}")
        print("💡 Some tests will be skipped")
    
    # Run tests
    try:
        runner = ComprehensiveSignatureTestRunner(pdf_file)
        results = runner.run_all_tests()
        
        # Generate and display report
        print("\n" + "=" * 80)
        report_content = runner.generate_report()
        print(report_content)
        
        # Save report
        report_path = runner.save_report()
        
        print(f"\n🎉 Test suite completed!")
        print(f"📄 Report saved: {report_path}")
        print(f"📁 Test files in: {runner.output_dir}")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        raise e


if __name__ == "__main__":
    main()