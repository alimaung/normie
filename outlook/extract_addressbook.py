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
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            print("Successfully connected to Outlook")
            return True
        except Exception as e:
            print(f"Error connecting to Outlook: {e}")
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
        
        for outlook_field, json_field in fields_mapping.items():
            try:
                value = getattr(contact, outlook_field, None)
                if value:
                    contact_info[json_field] = str(value).strip()
            except Exception as e:
                print(f"Warning: Could not extract {outlook_field}: {e}")
                continue
        
        # Add creation and modification dates if available
        try:
            if hasattr(contact, 'CreationTime'):
                contact_info['created_date'] = contact.CreationTime.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
            
        try:
            if hasattr(contact, 'LastModificationTime'):
                contact_info['modified_date'] = contact.LastModificationTime.strftime('%Y-%m-%d %H:%M:%S')
        except:
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
            print(f"Processing {items.Count} items in folder: {folder.Name}")
            
            for item in items:
                try:
                    # Check if item is a contact (olContactItem = 2)
                    if item.Class == 40:  # olContact
                        contact_info = self.extract_contact_info(item)
                        if contact_info:  # Only add if we got some info
                            contacts.append(contact_info)
                except Exception as e:
                    print(f"Warning: Could not process contact: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error processing folder {folder.Name}: {e}")
        
        return contacts
    
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
            
            # Try to get Global Address List (GAL) contacts if available
            try:
                address_lists = self.namespace.AddressLists
                for address_list in address_lists:
                    if "Global Address List" in address_list.Name or "GAL" in address_list.Name:
                        print(f"Processing Global Address List: {address_list.Name}")
                        gal_contacts = []
                        
                        try:
                            entries = address_list.AddressEntries
                            print(f"Found {entries.Count} entries in GAL")
                            
                            for entry in entries:
                                try:
                                    # Extract basic info from GAL entry
                                    gal_contact = {
                                        'full_name': entry.Name if hasattr(entry, 'Name') else '',
                                        'email_primary': entry.Address if hasattr(entry, 'Address') else '',
                                        'source': 'Global Address List'
                                    }
                                    
                                    # Try to get additional details if available
                                    try:
                                        details = entry.Details()
                                        if hasattr(details, 'CompanyName'):
                                            gal_contact['company'] = details.CompanyName
                                        if hasattr(details, 'Department'):
                                            gal_contact['department'] = details.Department
                                    except:
                                        pass
                                    
                                    if gal_contact['full_name'] or gal_contact['email_primary']:
                                        gal_contacts.append(gal_contact)
                                        
                                except Exception as e:
                                    continue
                                    
                        except Exception as e:
                            print(f"Warning: Could not fully process GAL: {e}")
                        
                        all_contacts.extend(gal_contacts)
                        folders_processed.append({
                            'name': f"GAL - {address_list.Name}",
                            'count': len(gal_contacts)
                        })
                        break
                        
            except Exception as e:
                print(f"Warning: Could not access Global Address List: {e}")
        
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


def main():
    """
    Main function to extract and save Outlook address book.
    """
    print("Starting Outlook Address Book extraction...")
    
    # Create extractor instance
    extractor = OutlookAddressBookExtractor()
    
    # Extract address book
    address_book_data = extractor.extract_address_book()
    
    if not address_book_data:
        print("Failed to extract address book data")
        return
    
    # Print summary
    extraction_info = address_book_data.get('extraction_info', {})
    print(f"\nExtraction Summary:")
    print(f"Total contacts found: {extraction_info.get('total_contacts', 0)}")
    print(f"Extraction time: {extraction_info.get('timestamp', 'Unknown')}")
    
    folders_info = extraction_info.get('folders_processed', [])
    if folders_info:
        print("\nFolders processed:")
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
                print(f"  {i}. {name} ({email}) - {company}")
    else:
        print("❌ Failed to save address book")


if __name__ == "__main__":
    main()
