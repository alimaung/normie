from struct import unpack
from io import BytesIO
import math
import binascii
from schema import PidTagSchema
import json
import csv
import sys

def hexify(PropID):
    """Convert property ID to hexadecimal string format"""
    return "{0:#0{1}x}".format(PropID, 10).upper()[2:]

def lookup(ulPropID):
    """Look up property name from property ID"""
    if hexify(ulPropID) in PidTagSchema:
        (PropertyName, PropertyType) = PidTagSchema[hexify(ulPropID)]
        return PropertyName
    else:
        return hex(ulPropID)

def extract_contacts_from_oab(oab_file_path, output_format='json'):
    """
    Extract contacts from OAB file
    
    Args:
        oab_file_path (str): Path to the OAB file (typically udetails.oab)
        output_format (str): Output format - 'json', 'csv', or 'dict'
    
    Returns:
        list: List of contact dictionaries
    """
    contacts = []
    
    print(f"Processing OAB file: {oab_file_path}")
    
    try:
        with open(oab_file_path, 'rb') as f:
            # Read header information
            (ulVersion, ulSerial, ulTotRecs) = unpack('<III', f.read(4 * 3))
            assert ulVersion == 32, 'This only supports OAB Version 4 Details File'
            print(f"Total Record Count: {ulTotRecs}")
            
            # Read OAB_META_DATA
            cbSize = unpack('<I', f.read(4))[0]
            meta = BytesIO(f.read(cbSize - 4))
            
            # Read header attributes
            HDR_cAtts = unpack('<I', meta.read(4))[0]
            print(f"Header Attributes Count: {HDR_cAtts}")
            
            for rgProp in range(HDR_cAtts):
                ulPropID = unpack('<I', meta.read(4))[0]
                ulFlags = unpack('<I', meta.read(4))[0]
            
            # Read OAB attributes (the ones we care about)
            OAB_cAtts = unpack('<I', meta.read(4))[0]
            OAB_Atts = []
            print(f"OAB Attributes Count: {OAB_cAtts}")
            
            for rgProp in range(OAB_cAtts):
                ulPropID = unpack('<I', meta.read(4))[0]
                ulFlags = unpack('<I', meta.read(4))[0]
                OAB_Atts.append(ulPropID)
            
            # Skip OAB_V4_REC header properties
            cbSize = unpack('<I', f.read(4))[0]
            f.read(cbSize - 4)
            
            # Process contact records
            counter = 0
            processed = 0
            
            while counter < ulTotRecs:
                counter += 1
                
                # Show progress every 1000 records
                if counter % 1000 == 0:
                    percent = int((counter / ulTotRecs) * 100)
                    print(f"Progress: {percent}% ({counter}/{ulTotRecs})")
                
                try:
                    read = f.read(4)
                    if not read:
                        break
                    
                    # Read chunk size
                    cbSize = unpack('<I', read)[0]
                    chunk = BytesIO(f.read(cbSize - 4))
                    
                    # Read presence bit array
                    presenceBitArray = bytearray(chunk.read(int(math.ceil(OAB_cAtts / 8.0))))
                    indices = [i for i in range(OAB_cAtts) if (presenceBitArray[i // 8] >> (7 - (i % 8))) & 1 == 1]
                    
                    def read_str():
                        """Read null-terminated string"""
                        buf = b""
                        while True:
                            n = chunk.read(1)
                            if n == b"\0" or n == b"":
                                break
                            buf += n
                        try:
                            return buf.decode('utf-8')
                        except UnicodeDecodeError:
                            return buf.decode('utf-8', errors='replace')
                    
                    def read_int():
                        """Read variable-length integer"""
                        byte_count = unpack('<B', chunk.read(1))[0]
                        if 0x81 <= byte_count <= 0x84:
                            byte_count = unpack('<I', (chunk.read(byte_count - 0x80) + b"\0\0\0")[0:4])[0]
                        else:
                            if byte_count > 127:
                                return -1
                        return byte_count
                    
                    contact = {}
                    
                    # Process each property present in this record
                    for i in indices:
                        PropID = hexify(OAB_Atts[i])
                        if PropID not in PidTagSchema:
                            continue
                        
                        (Name, Type) = PidTagSchema[PropID]
                        
                        try:
                            if Type == "PtypString8" or Type == "PtypString":
                                val = read_str()
                                if val:  # Only add non-empty values
                                    contact[Name] = val
                            
                            elif Type == "PtypBoolean":
                                val = unpack('<?', chunk.read(1))[0]
                                contact[Name] = val
                            
                            elif Type == "PtypInteger32":
                                val = read_int()
                                if val != -1:  # Only add valid integers
                                    contact[Name] = val
                            
                            elif Type == "PtypBinary":
                                bin_data = chunk.read(read_int())
                                if bin_data:
                                    contact[Name] = binascii.b2a_hex(bin_data).decode('ascii')
                            
                            elif Type == "PtypMultipleString" or Type == "PtypMultipleString8":
                                byte_count = read_int()
                                arr = []
                                for j in range(byte_count):
                                    val = read_str()
                                    if val:
                                        arr.append(val)
                                if arr:  # Only add non-empty arrays
                                    contact[Name] = arr
                            
                            elif Type == "PtypMultipleInteger32":
                                byte_count = read_int()
                                arr = []
                                for j in range(byte_count):
                                    val = read_int()
                                    if Name == "OfflineAddressBookTruncatedProperties":
                                        val = hexify(val)
                                        if val in PidTagSchema:
                                            val = PidTagSchema[val][0]
                                    if val != -1:
                                        arr.append(val)
                                if arr:
                                    contact[Name] = arr
                            
                            elif Type == "PtypMultipleBinary":
                                byte_count = read_int()
                                arr = []
                                for j in range(byte_count):
                                    bin_len = read_int()
                                    bin_data = chunk.read(bin_len)
                                    if bin_data:
                                        arr.append(binascii.b2a_hex(bin_data).decode('ascii'))
                                if arr:
                                    contact[Name] = arr
                        
                        except Exception as e:
                            print(f"Error processing property {Name}: {e}")
                            continue
                    
                    # Only add contacts that have meaningful data
                    if contact and any(key in contact for key in ['DisplayName', 'EmailAddress', 'SmtpAddress']):
                        contacts.append(contact)
                        processed += 1
                
                except Exception as e:
                    print(f"Error processing record {counter}: {e}")
                    continue
            
            print(f"Successfully extracted {processed} contacts from {counter} records")
            
    except Exception as e:
        print(f"Error reading OAB file: {e}")
        return []
    
    return contacts

def save_contacts(contacts, output_file, format_type='json'):
    """Save contacts to file in specified format"""
    
    if format_type.lower() == 'json':
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, indent=2, ensure_ascii=False)
        print(f"Contacts saved to {output_file} (JSON format)")
    
    elif format_type.lower() == 'csv':
        if not contacts:
            print("No contacts to save")
            return
        
        # Get all unique field names
        all_fields = set()
        for contact in contacts:
            all_fields.update(contact.keys())
        
        # Convert lists to strings for CSV
        csv_contacts = []
        for contact in contacts:
            csv_contact = {}
            for field in all_fields:
                value = contact.get(field, '')
                if isinstance(value, list):
                    csv_contact[field] = '; '.join(str(v) for v in value)
                else:
                    csv_contact[field] = str(value) if value else ''
            csv_contacts.append(csv_contact)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
            writer.writeheader()
            writer.writerows(csv_contacts)
        print(f"Contacts saved to {output_file} (CSV format)")

def main():
    """Main function to extract contacts"""
    
    # Default OAB file (can be changed)
    oab_file = 'udetails.oab'
    
    if len(sys.argv) > 1:
        oab_file = sys.argv[1]
    
    print("=== OAB Contact Extractor ===")
    print(f"Extracting contacts from: {oab_file}")
    
    # Extract contacts
    contacts = extract_contacts_from_oab(oab_file)
    
    if contacts:
        # Save in multiple formats
        save_contacts(contacts, 'contacts.json', 'json')
        save_contacts(contacts, 'contacts.csv', 'csv')
        
        # Print summary
        print(f"\n=== Extraction Summary ===")
        print(f"Total contacts extracted: {len(contacts)}")
        
        # Show sample contact
        if contacts:
            print(f"\n=== Sample Contact ===")
            sample = contacts[0]
            for key, value in sample.items():
                if isinstance(value, list):
                    print(f"{key}: {', '.join(str(v) for v in value)}")
                else:
                    print(f"{key}: {value}")
        
        # Show field statistics
        field_counts = {}
        for contact in contacts:
            for field in contact.keys():
                field_counts[field] = field_counts.get(field, 0) + 1
        
        print(f"\n=== Field Statistics ===")
        for field, count in sorted(field_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(contacts)) * 100
            print(f"{field}: {count} contacts ({percentage:.1f}%)")
    
    else:
        print("No contacts extracted. Please check the OAB file.")

if __name__ == "__main__":
    main() 