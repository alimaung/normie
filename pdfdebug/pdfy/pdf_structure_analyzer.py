#!/usr/bin/env python3
"""
PDF Structure Analyzer
Analyzes raw PDF structure to understand how form data is stored
"""
import re
import json
from collections import defaultdict

def analyze_pdf_structure(pdf_path: str):
    """Analyze PDF structure to understand form data storage."""
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    print(f"📄 PDF Structure Analysis: {pdf_path}")
    print(f"📊 File size: {len(pdf_data):,} bytes")
    print("=" * 60)
    
    # 1. Basic PDF Information
    analyze_pdf_basics(pdf_data)
    
    # 2. Object Structure
    analyze_object_structure(pdf_data)
    
    # 3. Form-related Content
    analyze_form_content(pdf_data)
    
    # 4. Text/Value Analysis  
    analyze_field_values(pdf_data)
    
    # 5. Signature Analysis
    analyze_signatures(pdf_data)
    
    # 6. Compression Analysis
    analyze_compression(pdf_data)

def analyze_pdf_basics(pdf_data: bytes):
    """Analyze basic PDF information."""
    print("🔍 1. BASIC PDF INFORMATION")
    
    # PDF Version
    version_match = re.search(rb'%PDF-(\d+\.\d+)', pdf_data)
    if version_match:
        version = version_match.group(1).decode()
        print(f"   PDF Version: {version}")
    
    # File structure markers
    eof_count = pdf_data.count(b'%%EOF')
    startxref_count = pdf_data.count(b'startxref')
    print(f"   %%EOF markers: {eof_count}")
    print(f"   startxref markers: {startxref_count}")
    
    # Incremental updates (multiple xref sections indicate form filling/signing)
    if eof_count > 1:
        print(f"   📝 INCREMENTAL UPDATES: {eof_count} (indicates form was filled/signed)")
    
    # Linear optimization
    if b'/Linearized' in pdf_data:
        print("   📦 Linearized: Yes (optimized for web)")
    
    print()

def analyze_object_structure(pdf_data: bytes):
    """Analyze object structure."""
    print("🔍 2. OBJECT STRUCTURE")
    
    # Find all objects
    obj_pattern = rb'(\d+)\s+(\d+)\s+obj'
    obj_matches = list(re.finditer(obj_pattern, pdf_data))
    
    object_numbers = []
    for match in obj_matches:
        obj_num = int(match.group(1))
        object_numbers.append(obj_num)
    
    if object_numbers:
        object_numbers.sort()
        print(f"   Total objects: {len(object_numbers)}")
        print(f"   Object range: {min(object_numbers)} to {max(object_numbers)}")
        print(f"   First 10: {object_numbers[:10]}")
        print(f"   Last 10: {object_numbers[-10:]}")
        
        # Check for gaps (deleted objects)
        expected_range = set(range(min(object_numbers), max(object_numbers) + 1))
        missing_objects = expected_range - set(object_numbers)
        if missing_objects:
            print(f"   📝 Missing objects: {len(missing_objects)} (may be deleted/freed)")
            print(f"   📝 Missing range examples: {sorted(list(missing_objects))[:10]}")
    
    print()

def analyze_form_content(pdf_data: bytes):
    """Analyze form-related content."""
    print("🔍 3. FORM-RELATED CONTENT")
    
    # AcroForm analysis
    acroform_count = pdf_data.count(b'/AcroForm')
    print(f"   AcroForm references: {acroform_count}")
    
    # Field type indicators
    field_indicators = {
        b'/FT': 'Field Type',
        b'/T(': 'Field Name (parentheses)',
        b'/V(': 'Field Value (parentheses)', 
        b'/V<': 'Field Value (hex)',
        b'/V/': 'Field Value (name)',
        b'/AP': 'Appearance',
        b'/Widget': 'Widget',
        b'/Annot': 'Annotation'
    }
    
    for indicator, description in field_indicators.items():
        count = pdf_data.count(indicator)
        print(f"   {description}: {count}")
    
    # Look for flattened form indicators
    flattened_indicators = [
        b'/Subtype/Widget',
        b'/Subtype/FreeText', 
        b'/Type/Annot',
        b'/AP/N',  # Normal appearance
        b'/AS/',   # Appearance state
    ]
    
    print("   📝 Flattened form indicators:")
    for indicator in flattened_indicators:
        count = pdf_data.count(indicator)
        if count > 0:
            print(f"      {indicator.decode()}: {count}")
    
    print()

def analyze_field_values(pdf_data: bytes):
    """Analyze field values from form_fields.json."""
    print("🔍 4. FIELD VALUE ANALYSIS")
    
    # Expected values from form_fields.json
    expected_values = {
        "030/2025": "Field 1 - Antragsnummer",
        "Ali Maung": "Field 2a - Name", 
        "21.02.2025": "Field 2b - Date",
        "IRM(GP)": "Field 2c - Department",
        "Piccolo-Öko-Entwickler Typ 25": "Field 3 - Product name",
        "(wird vom Einkauf festgelegt)": "Field 8 - Supplier",
        "1 Liter": "Field 16 - Unit",
        "Dr. Karsten Bartz": "Field 25a - Environmental officer",
        "27.03.2025": "Field 25c - Environmental review date",
        "Anouar Marzouki": "Field 32a - Safety officer",
        "28.03.2025": "Field 32c - Safety review date",
        "Maung, Ali": "Field 50a - Standards office",
        "31.03.2025": "Field 50c - Standards office date",
        "01044259": "Field 51 - Part number"
    }
    
    found_values = {}
    for value, description in expected_values.items():
        # Search for the value in various encodings
        patterns = [
            value.encode('utf-8'),
            value.encode('latin-1'),
            f"({value})".encode('utf-8'),  # In parentheses
            f"<{value.encode().hex()}>".encode(),  # As hex
        ]
        
        for pattern in patterns:
            if pattern in pdf_data:
                pos = pdf_data.find(pattern)
                found_values[value] = {
                    'description': description,
                    'position': pos,
                    'pattern': pattern
                }
                print(f"   ✅ Found: '{value}' at {pos} ({description})")
                break
        else:
            print(f"   ❌ Missing: '{value}' ({description})")
    
    print(f"   📊 Found {len(found_values)}/{len(expected_values)} expected values")
    print()

def analyze_signatures(pdf_data: bytes):
    """Analyze digital signatures."""
    print("🔍 5. SIGNATURE ANALYSIS")
    
    signature_indicators = {
        b'/Type/Sig': 'Signature field',
        b'/Filter/Adobe.PPKLite': 'Adobe signature',
        b'/SubFilter/adbe.pkcs7': 'PKCS#7 signature',
        b'/ByteRange': 'Signature byte range',
        b'/Contents<': 'Signature content',
        b'/M(D:': 'Signature date',
        b'/Name(': 'Signer name'
    }
    
    for indicator, description in signature_indicators.items():
        count = pdf_data.count(indicator)
        if count > 0:
            print(f"   {description}: {count}")
    
    # Extract signer names
    name_pattern = rb'/Name\(([^)]+)\)'
    name_matches = re.findall(name_pattern, pdf_data)
    if name_matches:
        print("   📝 Signers found:")
        for name in name_matches:
            print(f"      - {name.decode('utf-8', errors='ignore')}")
    
    print()

def analyze_compression(pdf_data: bytes):
    """Analyze compression and encoding."""
    print("🔍 6. COMPRESSION & ENCODING")
    
    # Stream compression
    compression_types = {
        b'/Filter/FlateDecode': 'Flate compression',
        b'/Filter/DCTDecode': 'JPEG compression', 
        b'/Filter/LZWDecode': 'LZW compression',
        b'/Filter/CCITTFaxDecode': 'CCITT Fax compression'
    }
    
    for comp_type, description in compression_types.items():
        count = pdf_data.count(comp_type)
        if count > 0:
            print(f"   {description}: {count}")
    
    # Object streams (PDF 1.5+)
    objstm_count = pdf_data.count(b'/Type/ObjStm')
    if objstm_count > 0:
        print(f"   📦 Object streams: {objstm_count} (compressed objects)")
    
    # XRef streams
    xref_stm_count = pdf_data.count(b'/Type/XRef')
    if xref_stm_count > 0:
        print(f"   📦 XRef streams: {xref_stm_count} (compressed cross-reference)")
    
    print()
    print("=" * 60)
    print("🔍 ANALYSIS COMPLETE")

if __name__ == "__main__":
    analyze_pdf_structure("pdf.pdf") 