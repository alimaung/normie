# OAB Contact Extractor - Usage Guide

## Overview

This tool extracts contact information from Microsoft Outlook Offline Address Book (OAB) files. OAB files contain contact data that Outlook uses for email address autocomplete and directory lookups.

## What are OAB Files?

OAB (Offline Address Book) files are proprietary Microsoft format files that store:
- Email addresses and contact details
- Organizational directory information
- Distribution lists and groups
- User profiles and metadata

Common OAB files in a typical setup:
- `udetails.oab` - Main contact details file (largest, contains all contact info)
- `ubrowse.oab` - Browse/search index
- `uANRdex.oab` - Ambiguous Name Resolution index
- `uRDNdex.oab` - Relative Distinguished Name index
- `uPDNdex.oab` - Proxy Distinguished Name index
- `utmplts.oab` - Templates file

## Files in This Package

- `extract_contacts.py` - Main extraction script (improved version)
- `boa.py` - Original extraction script (basic functionality)
- `schema.py` - Property definitions and data types
- `show_sample_contacts.py` - Display sample extracted contacts

## Usage

### Basic Usage

```bash
# Extract contacts from default udetails.oab file
python extract_contacts.py

# Extract contacts from specific OAB file
python extract_contacts.py path/to/your/file.oab
```

### Output Files

The script generates two output files:
- `contacts.json` - Complete contact data in JSON format
- `contacts.csv` - Contact data in CSV format (suitable for Excel/spreadsheets)

### View Sample Contacts

```bash
python show_sample_contacts.py
```

## Contact Information Extracted

The extractor captures all available contact fields, including:

### Core Information
- **DisplayName** - Full display name
- **EmailAddress** - Primary email address
- **SmtpAddress** - SMTP email address
- **GivenName** - First name
- **Surname** - Last name
- **Account** - User account/ID

### Contact Details
- **BusinessTelephoneNumber** - Work phone
- **MobileTelephoneNumber** - Mobile phone
- **HomeTelephoneNumber** - Home phone
- **PrimaryFaxNumber** - Fax number
- **PagerTelephoneNumber** - Pager number

### Address Information
- **StreetAddress** - Street address
- **Locality** - City
- **StateOrProvince** - State/Province
- **PostalCode** - ZIP/Postal code
- **Country** - Country

### Organizational Details
- **CompanyName** - Company name
- **DepartmentName** - Department
- **Title** - Job title
- **OfficeLocation** - Office location
- **Assistant** - Assistant name

### Technical Details
- **AddressBookProxyAddresses** - All email aliases
- **AddressBookObjectGuid** - Unique identifier
- **DisplayType** - Object type (user, group, etc.)
- **ObjectType** - Exchange object type

## Example Output

### JSON Format
```json
{
  "DisplayName": "Smith, John",
  "EmailAddress": "/o=Company/ou=Exchange/cn=Recipients/cn=John.Smith",
  "SmtpAddress": "John.Smith@company.com",
  "GivenName": "John",
  "Surname": "Smith",
  "BusinessTelephoneNumber": "+1 555-123-4567",
  "CompanyName": "Acme Corporation",
  "Title": "Software Engineer",
  "DepartmentName": "IT Development"
}
```

### CSV Format
The CSV file contains the same data but formatted for spreadsheet applications, with multiple values separated by semicolons.

## Statistics and Analysis

The extractor provides detailed statistics showing:
- Total contacts extracted
- Field coverage percentages
- Sample contact display
- Most common fields

## Troubleshooting

### Common Issues

1. **"This only supports OAB Version 4 Details File"**
   - Your OAB file is not version 4
   - Try using a different OAB file from your Outlook installation

2. **"No contacts extracted"**
   - The OAB file might be corrupted or empty
   - Ensure you're using the `udetails.oab` file (largest one)

3. **Unicode/Encoding Errors**
   - The script handles most encoding issues automatically
   - Check the output files for any garbled text

### OAB File Locations

#### Windows (Outlook)
```
%LOCALAPPDATA%\Microsoft\Outlook\Offline Address Books\{GUID}\
```

#### Typical paths:
```
C:\Users\[Username]\AppData\Local\Microsoft\Outlook\Offline Address Books\
```

## Advanced Usage

### Programmatic Usage

```python
from extract_contacts import extract_contacts_from_oab, save_contacts

# Extract contacts
contacts = extract_contacts_from_oab('udetails.oab')

# Save in different formats
save_contacts(contacts, 'my_contacts.json', 'json')
save_contacts(contacts, 'my_contacts.csv', 'csv')

# Process contacts programmatically
for contact in contacts:
    if 'SmtpAddress' in contact:
        print(f"Email: {contact['SmtpAddress']}")
```

### Filtering Contacts

You can modify the extraction script to filter contacts based on criteria:

```python
# Only extract contacts with phone numbers
filtered_contacts = [c for c in contacts if 'BusinessTelephoneNumber' in c]

# Only extract contacts from specific department
dept_contacts = [c for c in contacts if c.get('DepartmentName', '').startswith('IT')]
```

## Performance Notes

- Processing large OAB files (>50MB) may take several minutes
- The script shows progress indicators during processing
- Memory usage scales with the number of contacts
- JSON output files can be quite large (>2MB for thousands of contacts)

## Security Considerations

- OAB files may contain sensitive organizational information
- Handle extracted contact data according to your organization's privacy policies
- Consider encrypting output files if they contain sensitive data
- Be mindful of data retention and sharing policies

## Dependencies

- Python 3.x
- Standard library modules only (no external dependencies required)

## Credits

Based on the original work by [antimatter15](https://github.com/antimatter15/boa) who reverse-engineered the OAB format in 2014. 