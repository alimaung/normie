import base64
import json
from datetime import datetime
import binascii

def parse_pdf_date(date_string):
    """
    Parse PDF date format (D:YYYYMMDDHHmmSS±HH'mm')
    """
    try:
        # Remove 'D:' prefix if present
        if date_string.startswith('D:'):
            date_string = date_string[2:]
        
        # Basic format: YYYYMMDDHHmmSS
        year = int(date_string[0:4])
        month = int(date_string[4:6])
        day = int(date_string[6:8])
        hour = int(date_string[8:10])
        minute = int(date_string[10:12])
        second = int(date_string[12:14])
        
        # Parse timezone if present
        tz_info = ""
        if len(date_string) > 14:
            tz_info = date_string[14:]
        
        dt = datetime(year, month, day, hour, minute, second)
        return dt.isoformat() + tz_info
    except:
        return date_string

def get_field_value(data, field):
    """
    Get field value from either direct field or nested in /V
    """
    if field in data:
        return data[field]
    elif '/V' in data and isinstance(data['/V'], dict) and field in data['/V']:
        return data['/V'][field]
    return None

def analyze_signature_field(field_data):
    """
    Analyze a signature field and extract all available metadata
    """
    signature_info = {
        'signature_type': 'Digital Signature',
        'metadata': {},
        'contents_info': {}
    }
    
    # Extract all standard metadata fields
    metadata_fields = {
        'Filter': '/Filter',
        'SubFilter': '/SubFilter',
        'Name': '/Name',
        'Location': '/Location',
        'Reason': '/Reason',
        'SigningTime': '/M',
        'Type': '/Type'
    }
    
    for key, pdf_key in metadata_fields.items():
        value = get_field_value(field_data, pdf_key)
        if value:
            signature_info['metadata'][key] = value
    
    # Parse signing time if present
    signing_time = get_field_value(field_data, '/M')
    if signing_time:
        signature_info['metadata']['SigningTime'] = signing_time
        signature_info['metadata']['SigningTime_ISO'] = parse_pdf_date(signing_time)
    
    # Extract software information
    prop_build = get_field_value(field_data, '/Prop_Build')
    if prop_build and '/App' in prop_build:
        app_info = prop_build['/App']
        if '/Name' in app_info:
            signature_info['metadata']['SigningApplication'] = app_info['/Name']
    
    # Handle ByteRange
    byte_range = get_field_value(field_data, '/ByteRange')
    if byte_range:
        signature_info['contents_info']['ByteRange'] = byte_range
    
    # Handle Contents (the actual signature data)
    if '/V' in field_data and isinstance(field_data['/V'], dict):
        sig_data = field_data['/V']
        if 'Contents' in sig_data:
            try:
                raw_contents = base64.b64decode(sig_data['Contents'])
                hex_preview = binascii.hexlify(raw_contents[:50]).decode('utf-8')
                signature_info['contents_info']['ContentLength'] = len(raw_contents)
                signature_info['contents_info']['ContentPreview'] = hex_preview
                
                # Analyze signature format based on SubFilter
                subfilter = get_field_value(field_data, '/SubFilter')
                if subfilter:
                    signature_info['contents_info']['SignatureFormat'] = subfilter
                    if subfilter == '/adbe.pkcs7.sha1':
                        signature_info['contents_info']['HashAlgorithm'] = 'SHA1'
            except Exception as e:
                signature_info['contents_info']['error'] = f"Failed to analyze contents: {str(e)}"
    
    return signature_info

def analyze_signatures_from_json(json_path):
    """
    Read JSON file and analyze all signature fields
    """
    try:
        # Read the JSON file
        with open(json_path, 'r', encoding='utf-8') as file:
            form_fields = json.load(file)
        
        results = {}
        
        # Look for signature fields
        for field_name, field_data in form_fields.items():
            if '/FT' in field_data and field_data['/FT'] == '/Sig':
                print(f"\nAnalyzing signature in field: {field_name}")
                results[field_name] = analyze_signature_field(field_data)
        
        # Save the results
        output_path = 'signature_analysis.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        return results
    
    except Exception as e:
        return {'error': f'Failed to process JSON file: {str(e)}'}

# Usage
if __name__ == "__main__":
    json_path = 'form_fields.json'
    
    print("Analyzing signatures...")
    results = analyze_signatures_from_json(json_path)
    
    # Print results in a readable format
    for field_name, sig_info in results.items():
        print(f"\nSignature Field: {field_name}")
        
        print("\nMetadata:")
        for key, value in sig_info['metadata'].items():
            print(f"  {key}: {value}")
        
        print("\nContents Information:")
        for key, value in sig_info['contents_info'].items():
            print(f"  {key}: {value}")