#!/usr/bin/env python3
"""Quick test script to start testing PDF form fields"""

from form_debug import PDFFormTester

def quick_test():
    """Quick test of field 5 - Kennzeichnung des Bedarfs"""
    tester = PDFFormTester("pdf.pdf", "pdf_dict.json")
    
    print("=== Quick Test: Field 5 - Kennzeichnung des Bedarfs ===")
    print("This field should have two options:")
    print("1. Neubedarf -> /0")
    print("2. Bedarfsänderung -> /1")
    print()
    
    # Test with first option (Neubedarf)
    print("Testing with 'Neubedarf' first...")
    result = tester.test_single_field("5", "Neubedarf")
    
    if not result:
        print("Let's try the other option...")
        tester.test_single_field("5", "Bedarfsänderung")

if __name__ == "__main__":
    quick_test() 