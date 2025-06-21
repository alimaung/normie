import win32com.client
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class OutlookAddressBookExtractor:
    """
    A class to extract contacts from Outlook address book using win32com
    and save them to a JSON file.
    """
    
    def __init__(self):
        self.outlook = None
        self.namespace = None
        
    def connect_to_outlook(self) -> bool:
        """
        Establish connection to Outlook application.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
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
    
    def extract_contact_info(self, contact) -> Dict[str, Any]:
        """
        Extract relevant information from a contact object.
        
        Args:
            contact: Outlook contact object
            
        Returns:
            Dict containing contact information
        """
        contact_info = {}
        
        # Basic contact fields
        fields_mapping = {
            'FullName': 'full_name',
            'FirstName': 'first_name',
            'LastName': 'last_name',
            'Email1Address': 'email_primary',
            'Email2Address': 'email_secondary',
            'Email3Address': 'email_tertiary',
            'CompanyName': 'company',
            'JobTitle': 'job_title',
            'BusinessTelephoneNumber': 'phone_business',
            'HomeTelephoneNumber': 'phone_home',
            'MobileTelephoneNumber': 'phone_mobile',
            'BusinessFaxNumber': 'fax_business',
            'BusinessAddress': 'address_business',
            'HomeAddress': 'address_home',
            'WebPage': 'website',
            'Categories': 'categories',
            'Body': 'notes'
        }
        
        # Alternative field names to try for email addresses
        email_alternatives = [
            (['Email1Address', 'EmailAddress', 'PrimarySmtpAddress'], 'email_primary'),
            (['Email2Address', 'Email2DisplayName'], 'email_secondary'),
            (['Email3Address', 'Email3DisplayName'], 'email_tertiary')
        ]
        
        # Fields that are commonly missing and shouldn't generate warnings
        common_missing_fields = {'Body', 'Email2Address', 'Email3Address', 'Categories', 'WebPage'}
        
        for outlook_field, json_field in fields_mapping.items():
            try:
                # Check if the field exists first
                if hasattr(contact, outlook_field):
                    value = getattr(contact, outlook_field, None)
                    if value is not None and str(value).strip():
                        contact_info[json_field] = str(value).strip()
                else:
                    # Only warn for important fields that are unexpectedly missing
                    if outlook_field not in common_missing_fields:
                        print(f"Debug: Contact missing field {outlook_field}")
            except Exception as e:
                # Only show warnings for unexpected errors, not for commonly missing fields
                if outlook_field not in common_missing_fields:
                    print(f"Warning: Could not extract {outlook_field}: {e}")
                continue
        
        # Try alternative email field names if the standard ones didn't work
        for field_alternatives, json_field in email_alternatives:
            if json_field not in contact_info:  # Only try if we haven't found this email yet
                for field_name in field_alternatives:
                    try:
                        if hasattr(contact, field_name):
                            value = getattr(contact, field_name, None)
                            if value is not None and str(value).strip():
                                contact_info[json_field] = str(value).strip()
                                break  # Found a value, stop trying alternatives
                    except Exception:
                        continue
        
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
    
    def get_contacts_from_folder(self, folder) -> List[Dict[str, Any]]:
        """
        Extract contacts from a specific folder.
        
        Args:
            folder: Outlook folder object
            
        Returns:
            List of contact dictionaries
        """
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
            diagnostic_count = 0
            
            for i, item in enumerate(items, 1):
                try:
                    # Show progress for large folders
                    if total_items > 50 and (i % 25 == 0 or i == total_items):
                        print(f"  Progress: {i}/{total_items} items processed...")
                    
                    # Check if item is a contact (olContactItem = 40)
                    if hasattr(item, 'Class') and item.Class == 40:  # olContact
                        # Run diagnostics on first few contacts if we're having issues
                        if diagnostic_count < 2 and processed_contacts == 0:
                            self.diagnose_contact_properties(item)
                            diagnostic_count += 1
                        
                        contact_info = self.extract_contact_info(item)
                        if contact_info and self.is_valid_contact(contact_info):
                            contacts.append(contact_info)
                            processed_contacts += 1
                        else:
                            if contact_info:
                                print(f"  Debug: Contact {i} lacks key information (name/email/company)")
                            else:
                                print(f"  Warning: Contact {i} had no extractable information")
                    else:
                        # Item is not a contact (could be distribution list, etc.)
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
        Extract contacts from Global Address List with enhanced error handling.
        
        Args:
            address_list: Outlook AddressList object (GAL)
            
        Returns:
            List of contact dictionaries from GAL
        """
        gal_contacts = []
        
        try:
            entries = address_list.AddressEntries
            total_entries = entries.Count
            print(f"📊 Found {total_entries} entries in GAL")
            
            if total_entries == 0:
                return gal_contacts
            
            # Process entries with progress indication
            processed = 0
            for entry in entries:
                try:
                    # Show progress for large GALs
                    processed += 1
                    if processed % 100 == 0 or processed == total_entries:
                        print(f"  Progress: {processed}/{total_entries} entries processed...")
                    
                    # Extract basic info from GAL entry
                    gal_contact = {
                        'source': 'Global Address List',
                        'entry_type': getattr(entry, 'Type', 'Unknown')
                    }
                    
                    # Basic fields
                    if hasattr(entry, 'Name') and entry.Name:
                        gal_contact['full_name'] = str(entry.Name).strip()
                    
                    if hasattr(entry, 'Address') and entry.Address:
                        address = str(entry.Address).strip()
                        # Check if it's an email address or Exchange address
                        if '@' in address:
                            gal_contact['email_primary'] = address
                        else:
                            gal_contact['exchange_address'] = address
                    
                    # Try to get additional details from the entry
                    try:
                        # Some GAL entries support GetExchangeUser() for more details
                        if hasattr(entry, 'GetExchangeUser'):
                            exchange_user = entry.GetExchangeUser()
                            if exchange_user:
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
                                    except:
                                        continue
                        
                        # Alternative method: try Details() for additional info
                        elif hasattr(entry, 'Details'):
                            try:
                                details = entry.Details()
                                if details:
                                    detail_fields = ['CompanyName', 'Department', 'JobTitle', 'OfficeLocation']
                                    for field in detail_fields:
                                        if hasattr(details, field):
                                            value = getattr(details, field, None)
                                            if value and str(value).strip():
                                                gal_contact[field.lower().replace('name', '')] = str(value).strip()
                            except:
                                pass
                    
                    except Exception as detail_error:
                        # Continue without detailed info if extraction fails
                        pass
                    
                    # Only add contact if we have at least a name or email
                    if gal_contact.get('full_name') or gal_contact.get('email_primary') or gal_contact.get('exchange_address'):
                        gal_contacts.append(gal_contact)
                        
                except Exception as entry_error:
                    # Skip problematic entries but continue processing
                    continue
            
            print(f"✅ Successfully processed {len(gal_contacts)} valid contacts from GAL")
            
        except Exception as e:
            print(f"❌ Error processing GAL entries: {e}")
        
        return gal_contacts
    
    def search_gal(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for specific contacts in the Global Address List.
        
        Args:
            search_term: Name or email to search for
            
        Returns:
            List of matching contacts from GAL
        """
        if not self.connect_to_outlook():
            return []
        
        matching_contacts = []
        
        try:
            print(f"🔍 Searching GAL for: '{search_term}'")
            address_lists = self.namespace.AddressLists
            
            for address_list in address_lists:
                list_name = address_list.Name.lower()
                if any(keyword in list_name for keyword in ['global address list', 'gal', 'global', 'directory']):
                    print(f"📖 Searching in: {address_list.Name}")
                    
                    try:
                        # Use Outlook's built-in search if available
                        entries = address_list.AddressEntries
                        
                        for entry in entries:
                            try:
                                name = getattr(entry, 'Name', '').lower()
                                address = getattr(entry, 'Address', '').lower()
                                
                                # Check if search term matches name or address
                                if (search_term.lower() in name or 
                                    search_term.lower() in address):
                                    
                                    # Extract detailed info for matching entry
                                    contact_info = {
                                        'full_name': getattr(entry, 'Name', ''),
                                        'source': 'Global Address List - Search Result'
                                    }
                                    
                                    if hasattr(entry, 'Address'):
                                        address = str(entry.Address).strip()
                                        if '@' in address:
                                            contact_info['email_primary'] = address
                                        else:
                                            contact_info['exchange_address'] = address
                                    
                                    # Try to get additional details
                                    try:
                                        if hasattr(entry, 'GetExchangeUser'):
                                            exchange_user = entry.GetExchangeUser()
                                            if exchange_user:
                                                for field, key in [('CompanyName', 'company'), 
                                                                 ('Department', 'department'),
                                                                 ('JobTitle', 'job_title'),
                                                                 ('PrimarySmtpAddress', 'email_primary')]:
                                                    value = getattr(exchange_user, field, None)
                                                    if value:
                                                        contact_info[key] = str(value).strip()
                                    except:
                                        pass
                                    
                                    matching_contacts.append(contact_info)
                                    
                            except Exception as e:
                                continue
                    
                    except Exception as e:
                        print(f"Error searching in {address_list.Name}: {e}")
                        continue
            
            print(f"✅ Found {len(matching_contacts)} matching contacts")
            
        except Exception as e:
            print(f"❌ Error searching GAL: {e}")
        
        return matching_contacts
    
    def extract_address_book(self) -> Dict[str, Any]:
        """
        Extract all contacts from Outlook address book.
        
        Returns:
            Dictionary containing all contacts and metadata
        """
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
            
            # Enhanced Global Address List (GAL) extraction
            try:
                print("\n🌐 Searching for Global Address List...")
                address_lists = self.namespace.AddressLists
                print(f"Found {address_lists.Count} address lists")
                
                # List all available address lists for debugging
                print("Available address lists:")
                for i, addr_list in enumerate(address_lists):
                    print(f"  {i+1}. {addr_list.Name} (Type: {getattr(addr_list, 'AddressListType', 'Unknown')})")
                
                gal_processed = False
                for address_list in address_lists:
                    # More comprehensive GAL detection
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
                'folders_processed': folders_processed
            },
            'contacts': all_contacts
        }
        
        return result
    
    def save_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Save the address book data to a JSON file.
        
        Args:
            data: Dictionary containing address book data
            filename: Optional filename, if not provided, generates timestamp-based name
            
        Returns:
            String path of the saved file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"outlook_addressbook_{timestamp}.json"
        
        # Ensure the file has .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Save in the same directory as the script
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
    
    def diagnose_contact_properties(self, contact, max_contacts: int = 3) -> None:
        """
        Diagnostic method to list available properties on a contact object.
        This helps identify the correct property names for field extraction.
        
        Args:
            contact: Outlook contact object
            max_contacts: Maximum number of contacts to diagnose
        """
        try:
            print(f"\n🔍 Diagnostic info for contact:")
            print(f"   Contact Class: {getattr(contact, 'Class', 'Unknown')}")
            print(f"   Contact Type: {type(contact)}")
            
            # Try to get basic info
            name = getattr(contact, 'FullName', 'No FullName')
            print(f"   FullName: {name}")
            
            # List some common properties and their values
            common_props = [
                'Email1Address', 'Email2Address', 'Email3Address',
                'EmailAddress', 'PrimarySmtpAddress',
                'Email1DisplayName', 'Email2DisplayName', 'Email3DisplayName',
                'FirstName', 'LastName', 'CompanyName', 'JobTitle'
            ]
            
            print("   Available properties:")
            for prop in common_props:
                try:
                    if hasattr(contact, prop):
                        value = getattr(contact, prop, None)
                        if value:
                            print(f"     {prop}: {str(value)[:50]}...")
                        else:
                            print(f"     {prop}: <empty>")
                    else:
                        print(f"     {prop}: <not available>")
                except Exception as e:
                    print(f"     {prop}: <error: {e}>")
            
        except Exception as e:
            print(f"   Diagnostic error: {e}")
    
    def is_valid_contact(self, contact_info: Dict[str, Any]) -> bool:
        """
        Check if a contact has enough information to be considered valid.
        
        Args:
            contact_info: Dictionary containing contact information
            
        Returns:
            bool: True if contact has meaningful information, False otherwise
        """
        # A contact is considered valid if it has at least one of these key fields
        key_fields = ['full_name', 'first_name', 'last_name', 'email_primary', 'company']
        
        for field in key_fields:
            if contact_info.get(field) and contact_info[field].strip():
                return True
        
        return False


def main():
    """
    Main function to extract and save Outlook address book.
    """
    print("🚀 Outlook Address Book Extractor")
    print("=" * 50)
    
    # Create extractor instance
    extractor = OutlookAddressBookExtractor()
    
    # Check if user wants to search GAL specifically
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'diagnostic':
            # Diagnostic mode - show detailed property info
            print("🔍 Diagnostic Mode: Analyzing contact properties")
            print("=" * 50)
            
            extractor = OutlookAddressBookExtractor()
            if not extractor.connect_to_outlook():
                print("❌ Failed to connect to Outlook")
                return
            
            try:
                # Get the default Contacts folder
                contacts_folder = extractor.namespace.GetDefaultFolder(10)  # olFolderContacts
                items = contacts_folder.Items
                
                print(f"📁 Analyzing contacts in folder: {contacts_folder.Name}")
                print(f"📊 Total items in folder: {items.Count}")
                
                contact_count = 0
                for i, item in enumerate(items):
                    if hasattr(item, 'Class') and item.Class == 40:  # olContact
                        contact_count += 1
                        if contact_count <= 3:  # Analyze first 3 contacts
                            print(f"\n--- Contact #{contact_count} ---")
                            extractor.diagnose_contact_properties(item)
                        else:
                            break
                
                if contact_count == 0:
                    print("❌ No contacts found in the default contacts folder")
                else:
                    print(f"\n✅ Diagnostic complete. Analyzed {min(contact_count, 3)} contacts.")
                    
            except Exception as e:
                print(f"❌ Error in diagnostic mode: {e}")
            
            return
            
        elif sys.argv[1].lower() == 'search' and len(sys.argv) > 2:
            # GAL search mode
            search_term = ' '.join(sys.argv[2:])
            print(f"🔍 GAL Search Mode: Looking for '{search_term}'")
            
            results = extractor.search_gal(search_term)
            
            if results:
                print(f"\n📋 Search Results ({len(results)} found):")
                for i, contact in enumerate(results, 1):
                    name = contact.get('full_name', 'No name')
                    email = contact.get('email_primary', contact.get('exchange_address', 'No email'))
                    company = contact.get('company', 'No company')
                    department = contact.get('department', '')
                    dept_info = f" - {department}" if department else ""
                    print(f"  {i}. {name} ({email}) - {company}{dept_info}")
                
                # Save search results
                search_data = {
                    'search_info': {
                        'search_term': search_term,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'results_count': len(results)
                    },
                    'contacts': results
                }
                
                filename = f"gal_search_{search_term.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                saved_file = extractor.save_to_json(search_data, filename)
                
                if saved_file:
                    print(f"\n✅ Search results saved to: {saved_file}")
            else:
                print(f"\n❌ No contacts found matching '{search_term}'")
            
            return
        
        elif sys.argv[1].lower() == 'gal-only':
            # GAL-only extraction mode
            print("🌐 GAL-Only Extraction Mode")
            
            if not extractor.connect_to_outlook():
                print("❌ Failed to connect to Outlook")
                return
            
            try:
                address_lists = extractor.namespace.AddressLists
                gal_contacts = []
                
                for address_list in address_lists:
                    list_name = address_list.Name.lower()
                    if any(keyword in list_name for keyword in ['global address list', 'gal', 'global', 'directory']):
                        print(f"📖 Extracting from GAL: {address_list.Name}")
                        contacts = extractor.extract_gal_contacts(address_list)
                        gal_contacts.extend(contacts)
                
                if gal_contacts:
                    gal_data = {
                        'extraction_info': {
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'total_contacts': len(gal_contacts),
                            'source': 'Global Address List Only'
                        },
                        'contacts': gal_contacts
                    }
                    
                    filename = f"gal_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    saved_file = extractor.save_to_json(gal_data, filename)
                    
                    print(f"\n✅ GAL extraction complete!")
                    print(f"📊 Total GAL contacts: {len(gal_contacts)}")
                    print(f"📁 File location: {saved_file}")
                else:
                    print("❌ No GAL contacts found")
                
            except Exception as e:
                print(f"❌ Error in GAL-only mode: {e}")
            
            return
    
    # Default: Full address book extraction
    print("📚 Full Address Book Extraction Mode")
    print("This will extract from:")
    print("  • Personal Contacts folders")
    print("  • Contact subfolders")
    print("  • Global Address List (if available)")
    
    # Extract address book
    address_book_data = extractor.extract_address_book()
    
    if not address_book_data:
        print("❌ Failed to extract address book data")
        return
    
    # Print summary
    extraction_info = address_book_data.get('extraction_info', {})
    print(f"\n�� Extraction Summary:")
    print(f"Total contacts found: {extraction_info.get('total_contacts', 0)}")
    print(f"Extraction time: {extraction_info.get('timestamp', 'Unknown')}")
    
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
        
        # Show sample of first few contacts (if any)
        contacts = address_book_data.get('contacts', [])
        if contacts:
            print(f"\n📋 Sample contacts (showing first 3):")
            for i, contact in enumerate(contacts[:3], 1):
                name = contact.get('full_name', 'No name')
                email = contact.get('email_primary', 'No email')
                company = contact.get('company', 'No company')
                source = contact.get('source', 'Personal Contacts')
                print(f"  {i}. {name} ({email}) - {company} [{source}]")
        
        # Show GAL statistics if available
        gal_contacts = [c for c in contacts if c.get('source') == 'Global Address List']
        if gal_contacts:
            print(f"\n🌐 GAL Statistics:")
            print(f"  - GAL contacts found: {len(gal_contacts)}")
            print(f"  - Personal contacts: {len(contacts) - len(gal_contacts)}")
    else:
        print("❌ Failed to save address book")
    
    print(f"\n💡 Usage Tips:")
    print(f"  • For diagnostic mode: python {sys.argv[0]} diagnostic")
    print(f"  • For GAL search: python {sys.argv[0]} search <name_or_email>")
    print(f"  • For GAL only: python {sys.argv[0]} gal-only")
    print(f"  • For full extraction: python {sys.argv[0]} (default)")


if __name__ == "__main__":
    main()
