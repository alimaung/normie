import ctypes
import os
from ctypes import c_void_p, c_char_p, c_int, c_uint, c_bool, c_wchar_p, POINTER, Structure, byref, create_string_buffer
from typing import Optional, List, Dict, Any
import datetime

class LitePDFSignatureVerifier:
    """Practical Python wrapper for LitePDF DLL signature verification"""
    
    def __init__(self, dll_path: str = None):
        """Initialize LitePDF wrapper
        
        Args:
            dll_path: Path to litePDF.dll file. If None, looks in current directory.
        """
        if dll_path is None:
            dll_path = os.path.join(os.path.dirname(__file__), "litePDF.dll")
        
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"LitePDF DLL not found at: {dll_path}")
        
        # Load the DLL
        self.dll = ctypes.CDLL(dll_path)
        self.context = None
        self._setup_core_functions()
        
    def _setup_core_functions(self):
        """Setup only the core functions that we know work"""
        
        # Core context functions
        self.dll.litePDF_CreateContext.argtypes = []
        self.dll.litePDF_CreateContext.restype = c_void_p
        
        self.dll.litePDF_FreeContext.argtypes = [c_void_p]
        self.dll.litePDF_FreeContext.restype = None
        
        # File loading
        self.dll.litePDF_LoadFromFile.argtypes = [c_void_p, c_char_p, c_char_p, c_bool, c_bool]
        self.dll.litePDF_LoadFromFile.restype = c_bool
        
        # Signature count (this works reliably)
        self.dll.litePDF_GetSignatureCount.argtypes = [c_void_p]
        self.dll.litePDF_GetSignatureCount.restype = c_uint
        
        # Try to setup signature data function (may cause issues)
        try:
            self.dll.litePDF_GetSignatureData.argtypes = [c_void_p, c_uint, POINTER(c_char_p), POINTER(c_uint)]
            self.dll.litePDF_GetSignatureData.restype = c_bool
            self.has_signature_data_func = True
        except:
            self.has_signature_data_func = False
        
        # Try to setup signature ranges function
        try:
            self.dll.litePDF_GetSignatureRanges.argtypes = [c_void_p, c_uint, POINTER(c_uint), POINTER(c_uint)]
            self.dll.litePDF_GetSignatureRanges.restype = c_uint
            self.has_signature_ranges_func = True
        except:
            self.has_signature_ranges_func = False
        
    def __enter__(self):
        """Context manager entry"""
        self.context = self.dll.litePDF_CreateContext()
        if not self.context:
            raise RuntimeError("Failed to create LitePDF context")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.context:
            self.dll.litePDF_FreeContext(self.context)
            self.context = None
    
    def load_pdf(self, pdf_path: str, password: str = None) -> bool:
        """Load PDF file for signature verification"""
        if not self.context:
            raise RuntimeError("No LitePDF context. Use within 'with' statement.")
        
        pdf_path_b = pdf_path.encode('utf-8')
        password_b = password.encode('utf-8') if password else None
        
        try:
            success = self.dll.litePDF_LoadFromFile(self.context, pdf_path_b, password_b, False, False)
            if success:
                print(f"   ✅ PDF loaded: {os.path.basename(pdf_path)}")
            return success
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False
    
    def close_pdf(self):
        """Close the currently loaded PDF"""
        if self.context:
            try:
                self.dll.litePDF_Close(self.context)
                print(f"   🔒 PDF closed")
            except Exception as e:
                print(f"Error closing PDF: {e}")
    
    def get_signature_count(self) -> int:
        """Get number of signatures in the PDF"""
        if not self.context:
            raise RuntimeError("No LitePDF context. Use within 'with' statement.")
        
        try:
            count = self.dll.litePDF_GetSignatureCount(self.context)
            print(f"   📊 Signature count retrieved: {count}")
            return count
        except Exception as e:
            print(f"Error getting signature count: {e}")
            return 0
    
    def get_signature_data_safe(self, signature_index: int) -> Optional[bytes]:
        """Safely attempt to get signature data"""
        if not self.context or not self.has_signature_data_func:
            return None
        
        try:
            data_ptr = c_char_p()
            data_length = c_uint()
            
            success = self.dll.litePDF_GetSignatureData(
                self.context, signature_index, byref(data_ptr), byref(data_length)
            )
            
            if success and data_ptr.value and data_length.value > 0:
                signature_data = ctypes.string_at(data_ptr.value, data_length.value)
                print(f"   📋 Signature {signature_index} data extracted: {len(signature_data)} bytes")
                return signature_data
        except Exception as e:
            print(f"Error getting signature data: {e}")
        
        return None
    
    def analyze_pdf_signatures(self, pdf_path: str, password: str = None) -> Dict[str, Any]:
        """Analyze PDF for signatures - safe version with proper cleanup"""
        result = {
            'pdf_path': pdf_path,
            'exists': os.path.exists(pdf_path),
            'loaded': False,
            'signature_count': 0,
            'has_signatures': False,
            'signatures': [],
            'errors': []
        }
        
        if not result['exists']:
            result['errors'].append(f"PDF file not found: {pdf_path}")
            return result
        
        try:
            # Load PDF
            if not self.load_pdf(pdf_path, password):
                result['errors'].append("Failed to load PDF")
                return result
            
            result['loaded'] = True
            
            # Get signature count
            sig_count = self.get_signature_count()
            result['signature_count'] = sig_count
            result['has_signatures'] = sig_count > 0
            
            # Analyze each signature
            for i in range(sig_count):
                sig_info = {
                    'index': i,
                    'has_data': False,
                    'data_size': 0,
                    'status': 'detected'
                }
                
                # Try to get signature data
                sig_data = self.get_signature_data_safe(i)
                if sig_data:
                    sig_info['has_data'] = True
                    sig_info['data_size'] = len(sig_data)
                    sig_info['status'] = 'data_extracted'
                
                result['signatures'].append(sig_info)
            
            # Close PDF to free memory
            self.close_pdf()
            
        except Exception as e:
            result['errors'].append(f"Analysis error: {str(e)}")
            # Try to close PDF even if there was an error
            try:
                self.close_pdf()
            except:
                pass
        
        return result


def practical_signature_check():
    """Practical signature verification example"""
    print("=== Practical PDF Signature Verification ===\n")
    
    # Test with available PDFs - including signed PDFs
    test_pdfs = [
        r"C:\Users\RAVEN\Desktop\normie\pdfdebug\pdfdebug6\test_pdf\test_checkboxes_194349.pdf",
        r"C:\Users\RAVEN\Desktop\normie\pdfdebug\pdfdebug6\test_pdf\test_radio_buttons_194347.pdf",
        r"C:\Users\RAVEN\Desktop\normie\pdfdebug\pdfdebug6\test_pdf\test_text_fields_194346.pdf",
        r"C:\Users\RAVEN\Desktop\normie\pdfparser\030-2025_01044259_Freigabe.pdf",
        r"C:\Users\RAVEN\Desktop\normie\pdfparser\033-2025_01044262_Freigabe - Copy.pdf",
        r"C:\Users\RAVEN\Desktop\normie\Normstelle\Piccolo\Maung, Ali\5.Freigabe\030-2025_01044259_Freigabe.pdf",
    ]
    
    try:
        with LitePDFSignatureVerifier() as verifier:
            print("✅ LitePDF initialized successfully\n")
            
            results = []
            
            for pdf_path in test_pdfs:
                print(f"📄 Checking: {pdf_path}")
                
                result = verifier.analyze_pdf_signatures(pdf_path)
                results.append(result)
                
                if result['exists']:
                    if result['loaded']:
                        print(f"   ✅ Loaded successfully")
                        print(f"   📝 Signatures found: {result['signature_count']}")
                        
                        if result['has_signatures']:
                            for sig in result['signatures']:
                                print(f"      - Signature {sig['index']}: {sig['status']}")
                                if sig['has_data']:
                                    print(f"        Data size: {sig['data_size']} bytes")
                        else:
                            print("   ℹ️  No signatures found")
                    else:
                        print(f"   ❌ Failed to load")
                else:
                    print(f"   ⚠️  File not found")
                
                if result['errors']:
                    for error in result['errors']:
                        print(f"   ❌ {error}")
                
                print()
            
            # Summary
            print("=" * 50)
            print("📊 SUMMARY")
            print("=" * 50)
            
            total_pdfs = len(results)
            loaded_pdfs = sum(1 for r in results if r['loaded'])
            signed_pdfs = sum(1 for r in results if r['has_signatures'])
            total_signatures = sum(r['signature_count'] for r in results)
            
            print(f"Total PDFs tested: {total_pdfs}")
            print(f"Successfully loaded: {loaded_pdfs}")
            print(f"PDFs with signatures: {signed_pdfs}")
            print(f"Total signatures found: {total_signatures}")
            
            if signed_pdfs > 0:
                print(f"\n🔐 Signed PDFs:")
                for result in results:
                    if result['has_signatures']:
                        print(f"   - {os.path.basename(result['pdf_path'])}: {result['signature_count']} signature(s)")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def quick_signature_test(pdf_path: str):
    """Quick test for a specific PDF"""
    print(f"=== Quick Signature Test: {pdf_path} ===\n")
    
    try:
        with LitePDFSignatureVerifier() as verifier:
            result = verifier.analyze_pdf_signatures(pdf_path)
            
            print(f"File: {result['pdf_path']}")
            print(f"Exists: {result['exists']}")
            print(f"Loaded: {result['loaded']}")
            print(f"Signature count: {result['signature_count']}")
            print(f"Has signatures: {result['has_signatures']}")
            
            if result['signatures']:
                print("\nSignature details:")
                for sig in result['signatures']:
                    print(f"  [{sig['index']}] Status: {sig['status']}, Data: {sig['has_data']}, Size: {sig['data_size']}")
            
            if result['errors']:
                print("\nErrors:")
                for error in result['errors']:
                    print(f"  - {error}")
            
            return result
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def demo_usage():
    """Demonstrate how to use the LitePDF signature verifier"""
    print("=== LitePDF Signature Verification Demo ===\n")
    
    print("📖 This demo shows how to use LitePDF DLL with Python to check PDF signatures.\n")
    
    # Show the basic usage pattern
    print("💡 Basic Usage Pattern:")
    print("""
    from lite_pdf import LitePDFSignatureVerifier
    
    # Check a single PDF
    with LitePDFSignatureVerifier() as verifier:
        result = verifier.analyze_pdf_signatures("document.pdf")
        
        if result['has_signatures']:
            print(f"Found {result['signature_count']} signatures")
            for sig in result['signatures']:
                print(f"Signature {sig['index']}: {sig['status']}")
        else:
            print("No signatures found")
    """)
    
    # Run practical test
    practical_signature_check()


if __name__ == "__main__":
    print("🔐 LitePDF Signature Verification Tool")
    print("=" * 50)
    
    demo_usage()
    
    print("\n" + "=" * 50)
    print("📋 CAPABILITIES:")
    print("✅ Load PDF files")
    print("✅ Count digital signatures")
    print("✅ Extract signature data (when available)")
    print("✅ Handle password-protected PDFs")
    print("✅ Graceful error handling")
    print("⚠️  Some advanced functions may not be available in this DLL version")
    
    print("\n📖 USAGE NOTES:")
    print("1. Place litePDF.dll in the same directory as this script")
    print("2. Use the context manager (with statement) for proper cleanup")
    print("3. This provides basic signature detection - full validation requires additional crypto libraries")
    print("4. The DLL version you have supports core functionality but may be missing some advanced features")
    print("5. For production use, consider error handling and validation of signature data")
