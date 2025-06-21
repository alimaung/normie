import win32com.client
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class OutlookAddressBookExtractorFixed:
    """
    Fixed version of the address book extractor that properly handles 
    email address extraction using Outlook's PropertyAccessor.
    """
    
    def __init__(self):
        self.outlook = None
        self.namespace = None
        
    def connect_to_outlook(self) -> bool:
        """Establish connection to Outlook application."""
        try:
            print("🔗 Attempting to connect to Outlook...")
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            print("✅ Successfully connected to Outlook")
            return True
        except Exception as e:
            print(f"❌ Error connecting to Outlook: {e}")
            print("💡 Troubleshooting tips:")
            print("   • Make sure Microsoft Outlook is installed")
            print("   • Try starting Outlook manually first")
            print("   • Check if Outlook is running in safe mode")
            print("   • Ensure you have proper permissions to access Outlook")
            return False
    
    def extract_email_addresses(self, contact) -> Dict[str, str]:
        """
        Extract email addresses using the proper AddressEntry/ExchangeUser method
        and PropertyAccessor for MAPI properties.
        """
        emails = {}
        
        # Method 1: Try using PropertyAccessor with correct MAPI property tags
        try:
            property_accessor = contact.PropertyAccessor
            
            # Correct MAPI property tags for email addresses
            email_props = {
                'email1': 'http://schemas.microsoft.com/mapi/proptag/0x8083001E',  # PR_EMAIL1_ADDRESS_W
                'email2': 'http://schemas.microsoft.com/mapi/proptag/0x8093001E',  # PR_EMAIL2_ADDRESS_W  
                'email3': 'http://schemas.microsoft.com/mapi/proptag/0x80A3001E',  # PR_EMAIL3_ADDRESS_W
            }
            
            for email_key, prop_tag in email_props.items():
                try:
                    email_value = property_accessor.GetProperty(prop_tag)
                    if email_value and str(email_value).strip():
                        emails[email_key] = str(email_value).strip()
                        print(f"  ✅ Found {email_key}: {email_value}")
                except Exception as e:
                    print(f"  Debug: {email_key} via PropertyAccessor failed: {e}")
                    continue
                    
        except Exception as e:
            print(f"  Debug: PropertyAccessor method failed: {e}")
        
        # Method 2: Try alternative MAPI property tags (Unicode vs ANSI)
        if not emails:
            try:
                property_accessor = contact.PropertyAccessor
                
                # Try ANSI versions (001F suffix instead of 001E)
                email_props_ansi = {
                    'email1': 'http://schemas.microsoft.com/mapi/proptag/0x8083001F',  # PR_EMAIL1_ADDRESS_A
                    'email2': 'http://schemas.microsoft.com/mapi/proptag/0x8093001F',  # PR_EMAIL2_ADDRESS_A  
                    'email3': 'http://schemas.microsoft.com/mapi/proptag/0x80A3001F',  # PR_EMAIL3_ADDRESS_A
                }
                
                for email_key, prop_tag in email_props_ansi.items():
                    try:
                        email_value = property_accessor.GetProperty(prop_tag)
                        if email_value and str(email_value).strip():
                            emails[email_key] = str(email_value).strip()
                            print(f"  ✅ Found {email_key} (ANSI): {email_value}")
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"  Debug: ANSI PropertyAccessor method failed: {e}")
        
        # Method 3: Try to access through AddressEntry if this contact has one
        try:
            # Some contacts might have an associated AddressEntry
            if hasattr(contact, 'AddressEntry'):
                address_entry = contact.AddressEntry
                if address_entry:
                    print(f"  🔍 Found AddressEntry, trying GetExchangeUser...")
                    
                    # Try GetExchangeUser method
                    try:
                        exchange_user = address_entry.GetExchangeUser()
                        if exchange_user:
                            print(f"  ✅ Got ExchangeUser object")
                            
                            # Extract email from ExchangeUser
                            if hasattr(exchange_user, 'PrimarySmtpAddress'):
                                smtp_addr = exchange_user.PrimarySmtpAddress
                                if smtp_addr and str(smtp_addr).strip():
                                    emails['email1'] = str(smtp_addr).strip()
                                    print(f"  ✅ Found email via ExchangeUser: {smtp_addr}")
                    except Exception as e:
                        print(f"  Debug: GetExchangeUser failed: {e}")
                        
                    # Try PropertyAccessor on AddressEntry
                    try:
                        addr_property_accessor = address_entry.PropertyAccessor
                        # Try common email property on AddressEntry
                        email_value = addr_property_accessor.GetProperty('http://schemas.microsoft.com/mapi/proptag/0x39FE001E')  # PR_SMTP_ADDRESS
                        if email_value and str(email_value).strip():
                            emails['email1'] = str(email_value).strip()
                            print(f"  ✅ Found email via AddressEntry PropertyAccessor: {email_value}")
                    except Exception as e:
                        print(f"  Debug: AddressEntry PropertyAccessor failed: {e}")
                        
        except Exception as e:
            print(f"  Debug: AddressEntry method failed: {e}")
        
        # Method 4: Try to extract from display name or other fields as fallback
        try:
            # Sometimes email info is embedded in other fields
            full_name = getattr(contact, 'FullName', '')
            if '@' in full_name and not emails:
                # Extract email from name field if it contains one
                import re
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', full_name)
                if email_match:
                    emails['email1'] = email_match.group()
                    print(f"  ✅ Found email in FullName: {email_match.group()}")
        except Exception:
            pass
        
        return emails
    
    def extract_contact_info(self, contact) -> Dict[str, Any]:
        """
        Extract contact information with fixed email handling.
        """
        contact_info = {}
        
        # Basic contact fields that work (excluding email fields)
        fields_mapping = {
            'FullName': 'full_name',
            'FirstName': 'first_name',
            'LastName': 'last_name',
            'CompanyName': 'company',
            'JobTitle': 'job_title',
            'Department': 'department',
            'OfficeLocation': 'office_location',
            'BusinessTelephoneNumber': 'phone_business',
            'HomeTelephoneNumber': 'phone_home',
            'MobileTelephoneNumber': 'phone_mobile',
            'BusinessFaxNumber': 'fax_business',
            'BusinessAddress': 'address_business',
            'HomeAddress': 'address_home',
            'WebPage': 'website',
            'Categories': 'categories',
        }
        
        # Extract basic fields safely
        for outlook_field, json_field in fields_mapping.items():
            try:
                if hasattr(contact, outlook_field):
                    value = getattr(contact, outlook_field, None)
                    if value is not None and str(value).strip():
                        contact_info[json_field] = str(value).strip()
            except Exception as e:
                # Skip fields that cause errors
                continue
        
        # Extract email addresses using our fixed method
        emails = self.extract_email_addresses(contact)
        if emails:
            for email_key, email_value in emails.items():
                if email_key == 'email1':
                    contact_info['email_primary'] = email_value
                elif email_key == 'email2':
                    contact_info['email_secondary'] = email_value
                elif email_key == 'email3':
                    contact_info['email_tertiary'] = email_value
        
        # Add creation and modification dates if available
        try:
            if hasattr(contact, 'CreationTime') and contact.CreationTime:
                contact_info['created_date'] = contact.CreationTime.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass
            
        try:
            if hasattr(contact, 'LastModificationTime') and contact.LastModificationTime:
                contact_info['modified_date'] = contact.LastModificationTime.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass
        
        return contact_info
    
    def is_valid_contact(self, contact_info: Dict[str, Any]) -> bool:
        """Check if a contact has enough information to be considered valid."""
        key_fields = ['full_name', 'first_name', 'last_name', 'email_primary', 'company']
        
        for field in key_fields:
            if contact_info.get(field) and contact_info[field].strip():
                return True
        
        return False
    
    def get_contacts_from_folder(self, folder) -> List[Dict[str, Any]]:
        """Extract contacts from a specific folder with improved error handling."""
        contacts = []
        
        try:
            items = folder.Items
            total_items = items.Count
            print(f"Processing {total_items} items in folder: {folder.Name}")
            
            if total_items == 0:
                print(f"  No items found in folder: {folder.Name}")
                return contacts
            
            processed_contacts = 0
            skipped_items = 0
            
            for i, item in enumerate(items, 1):
                try:
                    # Show progress for large folders
                    if total_items > 50 and (i % 25 == 0 or i == total_items):
                        print(f"  Progress: {i}/{total_items} items processed...")
                    
                    # Check if item is a contact
                    if hasattr(item, 'Class') and item.Class == 40:  # olContact
                        contact_info = self.extract_contact_info(item)
                        if contact_info and self.is_valid_contact(contact_info):
                            contacts.append(contact_info)
                            processed_contacts += 1
                        else:
                            if contact_info:
                                print(f"  Debug: Contact {i} lacks key information")
                            else:
                                print(f"  Warning: Contact {i} had no extractable information")
                    else:
                        # Item is not a contact
                        skipped_items += 1
                        
                except Exception as e:
                    print(f"  Warning: Could not process item {i}: {e}")
                    skipped_items += 1
                    continue
            
            print(f"  ✅ Folder '{folder.Name}': {processed_contacts} contacts extracted, {skipped_items} items skipped")
                    
        except Exception as e:
            print(f"❌ Error processing folder {folder.Name}: {e}")
        
        return contacts
    
    def extract_gal_contacts(self, address_list) -> List[Dict[str, Any]]:
        """
        Extract contacts from Global Address List using AddressEntry.GetExchangeUser() method.
        """
        gal_contacts = []
        
        try:
            entries = address_list.AddressEntries
            total_entries = entries.Count
            print(f"📊 Found {total_entries} entries in GAL: {address_list.Name}")
            
            if total_entries == 0:
                return gal_contacts
            
            processed = 0
            for entry in entries:
                try:
                    processed += 1
                    if processed % 50 == 0 or processed == total_entries:
                        print(f"  Progress: {processed}/{total_entries} GAL entries processed...")
                    
                    gal_contact = {
                        'source': 'Global Address List',
                        'entry_type': getattr(entry, 'Type', 'Unknown')
                    }
                    
                    # Basic info from AddressEntry
                    if hasattr(entry, 'Name') and entry.Name:
                        gal_contact['full_name'] = str(entry.Name).strip()
                    
                    if hasattr(entry, 'Address') and entry.Address:
                        address = str(entry.Address).strip()
                        if '@' in address:
                            gal_contact['email_primary'] = address
                        else:
                            gal_contact['exchange_address'] = address
                    
                    # Try GetExchangeUser method (the recommended approach)
                    try:
                        exchange_user = entry.GetExchangeUser()
                        if exchange_user:
                            print(f"  ✅ Got ExchangeUser for: {gal_contact.get('full_name', 'Unknown')}")
                            
                            # Extract Exchange-specific information
                            exchange_fields = {
                                'FirstName': 'first_name',
                                'LastName': 'last_name',
                                'CompanyName': 'company',
                                'Department': 'department',
                                'JobTitle': 'job_title',
                                'BusinessTelephoneNumber': 'phone_business',
                                'MobileTelephoneNumber': 'phone_mobile',
                                'OfficeLocation': 'office_location',
                                'PrimarySmtpAddress': 'email_primary'
                            }
                            
                            for ex_field, json_field in exchange_fields.items():
                                try:
                                    value = getattr(exchange_user, ex_field, None)
                                    if value and str(value).strip():
                                        gal_contact[json_field] = str(value).strip()
                                except Exception:
                                    continue
                    
                    except Exception as exchange_error:
                        print(f"  Debug: GetExchangeUser failed for {gal_contact.get('full_name', 'Unknown')}: {exchange_error}")
                    
                    # Try PropertyAccessor on AddressEntry for additional properties
                    try:
                        property_accessor = entry.PropertyAccessor
                        
                        # Common MAPI properties for GAL entries
                        gal_properties = {
                            'http://schemas.microsoft.com/mapi/proptag/0x39FE001E': 'email_primary',  # PR_SMTP_ADDRESS
                            'http://schemas.microsoft.com/mapi/proptag/0x3A00001E': 'full_name',      # PR_ACCOUNT  
                            'http://schemas.microsoft.com/mapi/proptag/0x3A06001E': 'first_name',    # PR_GIVEN_NAME
                            'http://schemas.microsoft.com/mapi/proptag/0x3A11001E': 'last_name',     # PR_SURNAME
                            'http://schemas.microsoft.com/mapi/proptag/0x3A16001E': 'company',       # PR_COMPANY_NAME
                            'http://schemas.microsoft.com/mapi/proptag/0x3A17001E': 'job_title',     # PR_TITLE
                            'http://schemas.microsoft.com/mapi/proptag/0x3A18001E': 'department',    # PR_DEPARTMENT_NAME
                            'http://schemas.microsoft.com/mapi/proptag/0x3A19001E': 'office_location', # PR_OFFICE_LOCATION
                            'http://schemas.microsoft.com/mapi/proptag/0x3A08001E': 'phone_business', # PR_BUSINESS_TELEPHONE_NUMBER
                            'http://schemas.microsoft.com/mapi/proptag/0x3A1C001E': 'phone_mobile',   # PR_MOBILE_TELEPHONE_NUMBER
                        }
                        
                        for prop_tag, json_field in gal_properties.items():
                            try:
                                value = property_accessor.GetProperty(prop_tag)
                                if value and str(value).strip():
                                    # Don't overwrite if we already have this field
                                    if json_field not in gal_contact or not gal_contact[json_field]:
                                        gal_contact[json_field] = str(value).strip()
                            except Exception:
                                continue
                                
                    except Exception as prop_error:
                        print(f"  Debug: PropertyAccessor failed for GAL entry: {prop_error}")
                    
                    # Only add contact if we have meaningful information
                    if (gal_contact.get('full_name') or 
                        gal_contact.get('email_primary') or 
                        gal_contact.get('exchange_address')):
                        gal_contacts.append(gal_contact)
                        
                except Exception as entry_error:
                    print(f"  Warning: Could not process GAL entry {processed}: {entry_error}")
                    continue
            
            print(f"✅ Successfully processed {len(gal_contacts)} valid contacts from GAL")
            
        except Exception as e:
            print(f"❌ Error processing GAL entries: {e}")
        
        return gal_contacts
    
    def extract_address_book(self) -> Dict[str, Any]:
        """Extract all contacts from Outlook address book."""
        if not self.connect_to_outlook():
            return {}
        
        all_contacts = []
        folders_processed = []
        
        try:
            # Get the default Contacts folder
            contacts_folder = self.namespace.GetDefaultFolder(10)  # olFolderContacts = 10
            
            # Extract contacts from main contacts folder
            main_contacts = self.get_contacts_from_folder(contacts_folder)
            all_contacts.extend(main_contacts)
            folders_processed.append({
                'name': contacts_folder.Name,
                'count': len(main_contacts)
            })
            
            # Process subfolders in Contacts
            try:
                for subfolder in contacts_folder.Folders:
                    subfolder_contacts = self.get_contacts_from_folder(subfolder)
                    all_contacts.extend(subfolder_contacts)
                    folders_processed.append({
                        'name': f"{contacts_folder.Name}/{subfolder.Name}",
                        'count': len(subfolder_contacts)
                    })
            except Exception as e:
                print(f"Warning: Could not process subfolders: {e}")
            
            # Extract from Global Address List using the proper method
            try:
                print("\n🌐 Searching for Global Address List...")
                address_lists = self.namespace.AddressLists
                print(f"Found {address_lists.Count} address lists")
                
                # List all available address lists
                print("Available address lists:")
                for i, addr_list in enumerate(address_lists):
                    print(f"  {i+1}. {addr_list.Name}")
                
                gal_processed = False
                for address_list in address_lists:
                    list_name = address_list.Name.lower()
                    if any(keyword in list_name for keyword in ['global address list', 'gal', 'global', 'directory']):
                        print(f"\n📖 Processing Global Address List: {address_list.Name}")
                        gal_contacts = self.extract_gal_contacts(address_list)
                        
                        if gal_contacts:
                            all_contacts.extend(gal_contacts)
                            folders_processed.append({
                                'name': f"GAL - {address_list.Name}",
                                'count': len(gal_contacts)
                            })
                            gal_processed = True
                            print(f"✅ Successfully extracted {len(gal_contacts)} contacts from GAL")
                        else:
                            print(f"⚠️ No contacts found in GAL: {address_list.Name}")
                
                if not gal_processed:
                    print("⚠️ No Global Address List found or accessible")
                        
            except Exception as e:
                print(f"❌ Error accessing Global Address List: {e}")
        
        except Exception as e:
            print(f"Error extracting address book: {e}")
            return {}
        
        # Create final result structure
        result = {
            'extraction_info': {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_contacts': len(all_contacts),
                'folders_processed': folders_processed,
                'extraction_method': 'Fixed PropertyAccessor method'
            },
            'contacts': all_contacts
        }
        
        return result
    
    def save_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """Save the address book data to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"outlook_addressbook_fixed_{timestamp}.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Address book saved successfully to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return ""


def main():
    """Main function to extract and save Outlook address book with fixed email handling."""
    print("🚀 Outlook Address Book Extractor (FIXED VERSION)")
    print("=" * 60)
    print("This version uses PropertyAccessor to properly extract email addresses")
    print("=" * 60)
    
    # Create extractor instance
    extractor = OutlookAddressBookExtractorFixed()
    
    # Extract address book
    address_book_data = extractor.extract_address_book()
    
    if not address_book_data:
        print("❌ Failed to extract address book data")
        return
    
    # Print summary
    extraction_info = address_book_data.get('extraction_info', {})
    print(f"\n📊 Extraction Summary:")
    print(f"Total contacts found: {extraction_info.get('total_contacts', 0)}")
    print(f"Extraction time: {extraction_info.get('timestamp', 'Unknown')}")
    print(f"Method used: {extraction_info.get('extraction_method', 'Unknown')}")
    
    folders_info = extraction_info.get('folders_processed', [])
    if folders_info:
        print("\n📁 Folders processed:")
        for folder in folders_info:
            print(f"  - {folder['name']}: {folder['count']} contacts")
    
    # Save to JSON
    saved_file = extractor.save_to_json(address_book_data)
    
    if saved_file:
        print(f"\n✅ Address book successfully extracted and saved!")
        print(f"📁 File location: {saved_file}")
        
        # Show sample of first few contacts
        contacts = address_book_data.get('contacts', [])
        if contacts:
            print(f"\n📋 Sample contacts (showing first 3):")
            for i, contact in enumerate(contacts[:3], 1):
                name = contact.get('full_name', 'No name')
                email = contact.get('email_primary', 'No primary email')
                email2 = contact.get('email_secondary', '')
                email3 = contact.get('email_tertiary', '')
                company = contact.get('company', 'No company')
                
                print(f"  {i}. {name}")
                print(f"     Company: {company}")
                print(f"     Email 1: {email}")
                if email2:
                    print(f"     Email 2: {email2}")
                if email3:
                    print(f"     Email 3: {email3}")
                print()
        
        # Show email extraction statistics
        emails_found = sum(1 for c in contacts if c.get('email_primary'))
        emails2_found = sum(1 for c in contacts if c.get('email_secondary'))
        emails3_found = sum(1 for c in contacts if c.get('email_tertiary'))
        
        print(f"📧 Email Extraction Statistics:")
        print(f"  - Primary emails found: {emails_found}/{len(contacts)}")
        print(f"  - Secondary emails found: {emails2_found}/{len(contacts)}")
        print(f"  - Tertiary emails found: {emails3_found}/{len(contacts)}")
        
    else:
        print("❌ Failed to save address book")


if __name__ == "__main__":
    main() 