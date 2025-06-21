import win32com.client
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class SimpleOutlookExtractor:
    """
    Simple and reliable Outlook contact extractor based on proven working code.
    Uses GetGlobalAddressList() and GetExchangeUser() methods.
    """
    
    def __init__(self):
        self.outlook = None
        
    def connect_to_outlook(self) -> bool:
        """Establish connection to Outlook application."""
        try:
            print("🔗 Connecting to Outlook...")
            # Use gencache.EnsureDispatch for better COM object handling
            self.outlook = win32com.client.gencache.EnsureDispatch("Outlook.Application")
            print("✅ Successfully connected to Outlook")
            return True
        except Exception as e:
            print(f"❌ Error connecting to Outlook: {e}")
            print("💡 Troubleshooting tips:")
            print("   • Make sure Microsoft Outlook is installed and running")
            print("   • Ensure you're connected to Exchange server")
            print("   • Check if Outlook is running in safe mode")
            return False
    
    def extract_gal_contacts(self) -> List[Dict[str, Any]]:
        """
        Extract contacts from Global Address List using the proven working method.
        """
        contacts = []
        
        try:
            print("🌐 Accessing Global Address List...")
            
            # Get Global Address List - this is the proven working method
            gal = self.outlook.Session.GetGlobalAddressList()
            entries = gal.AddressEntries
            total_entries = entries.Count
            
            print(f"📊 Found {total_entries} entries in Global Address List")
            
            if total_entries == 0:
                print("⚠️ No entries found in Global Address List")
                return contacts
            
            processed = 0
            successful = 0
            
            # Iterate through GAL entries
            for entry in entries:
                try:
                    processed += 1
                    
                    # Show progress for large GALs
                    if processed % 100 == 0 or processed == total_entries:
                        print(f"  Progress: {processed}/{total_entries} entries processed, {successful} contacts extracted...")
                    
                    # Check if entry type is Exchange (EX)
                    if entry.Type == "EX":
                        # Get Exchange User - this is the key method that works
                        user = entry.GetExchangeUser()
                        
                        if user is not None:
                            contact = {
                                'source': 'Global Address List',
                                'entry_type': 'Exchange'
                            }
                            
                            # Extract basic information
                            try:
                                if hasattr(user, 'FirstName') and user.FirstName:
                                    contact['first_name'] = str(user.FirstName).strip()
                                
                                if hasattr(user, 'LastName') and user.LastName:
                                    contact['last_name'] = str(user.LastName).strip()
                                
                                # Create full name
                                if 'first_name' in contact and 'last_name' in contact:
                                    contact['full_name'] = f"{contact['first_name']} {contact['last_name']}"
                                elif 'first_name' in contact:
                                    contact['full_name'] = contact['first_name']
                                elif 'last_name' in contact:
                                    contact['full_name'] = contact['last_name']
                                
                                # Primary SMTP Address - this is the reliable email field
                                if hasattr(user, 'PrimarySmtpAddress') and user.PrimarySmtpAddress:
                                    contact['email_primary'] = str(user.PrimarySmtpAddress).strip()
                                
                                # Additional Exchange User properties
                                exchange_fields = {
                                    'CompanyName': 'company',
                                    'Department': 'department', 
                                    'JobTitle': 'job_title',
                                    'BusinessTelephoneNumber': 'phone_business',
                                    'MobileTelephoneNumber': 'phone_mobile',
                                    'OfficeLocation': 'office_location',
                                    'ManagerName': 'manager_name',
                                    'AssistantName': 'assistant_name'
                                }
                                
                                for ex_field, json_field in exchange_fields.items():
                                    try:
                                        if hasattr(user, ex_field):
                                            value = getattr(user, ex_field, None)
                                            if value and str(value).strip():
                                                contact[json_field] = str(value).strip()
                                    except Exception:
                                        continue
                                
                                # Only add contact if it has meaningful information
                                # Require at least a name or email
                                if (contact.get('full_name') or 
                                    contact.get('first_name') or 
                                    contact.get('last_name') or 
                                    contact.get('email_primary')):
                                    
                                    contacts.append(contact)
                                    successful += 1
                                    
                            except Exception as extract_error:
                                print(f"  Warning: Could not extract data from Exchange user: {extract_error}")
                                continue
                                
                except Exception as entry_error:
                    print(f"  Warning: Could not process GAL entry {processed}: {entry_error}")
                    continue
            
            print(f"✅ Successfully extracted {successful} contacts from {processed} GAL entries")
            
        except Exception as e:
            print(f"❌ Error accessing Global Address List: {e}")
            print("💡 This might mean:")
            print("   • Outlook is not connected to Exchange server")
            print("   • You don't have permission to access GAL")
            print("   • Outlook is running in offline mode")
        
        return contacts
    
    def extract_local_contacts(self) -> List[Dict[str, Any]]:
        """
        Extract contacts from local Contacts folder using safe property access.
        """
        contacts = []
        
        try:
            print("📁 Accessing local Contacts folder...")
            
            # Get default contacts folder
            namespace = self.outlook.GetNamespace("MAPI")
            contacts_folder = namespace.GetDefaultFolder(10)  # olFolderContacts
            items = contacts_folder.Items
            
            total_items = items.Count
            print(f"📊 Found {total_items} items in local Contacts folder")
            
            if total_items == 0:
                print("⚠️ No items found in local Contacts folder")
                return contacts
            
            processed = 0
            successful = 0
            
            for item in items:
                try:
                    processed += 1
                    
                    # Show progress
                    if processed % 25 == 0 or processed == total_items:
                        print(f"  Progress: {processed}/{total_items} items processed, {successful} contacts extracted...")
                    
                    # Check if item is a contact
                    if hasattr(item, 'Class') and item.Class == 40:  # olContact
                        contact = {
                            'source': 'Local Contacts',
                            'entry_type': 'Contact'
                        }
                        
                        # Extract basic fields that we know work from the debug analysis
                        safe_fields = {
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
                            'BusinessAddress': 'address_business',
                            'HomeAddress': 'address_home'
                        }
                        
                        for outlook_field, json_field in safe_fields.items():
                            try:
                                if hasattr(item, outlook_field):
                                    value = getattr(item, outlook_field, None)
                                    if value and str(value).strip():
                                        contact[json_field] = str(value).strip()
                            except Exception:
                                continue
                        
                        # Try to extract email using PropertyAccessor (safer method)
                        try:
                            property_accessor = item.PropertyAccessor
                            
                            # Try different MAPI property tags for email
                            email_tags = [
                                'http://schemas.microsoft.com/mapi/proptag/0x8083001E',  # Email1Address Unicode
                                'http://schemas.microsoft.com/mapi/proptag/0x8083001F',  # Email1Address ANSI
                            ]
                            
                            for tag in email_tags:
                                try:
                                    email_value = property_accessor.GetProperty(tag)
                                    if email_value and str(email_value).strip():
                                        contact['email_primary'] = str(email_value).strip()
                                        break
                                except Exception:
                                    continue
                                    
                        except Exception:
                            pass
                        
                        # Only add contact if it has meaningful information
                        if (contact.get('full_name') or 
                            contact.get('first_name') or 
                            contact.get('last_name') or 
                            contact.get('email_primary') or
                            contact.get('company')):
                            
                            contacts.append(contact)
                            successful += 1
                            
                except Exception as item_error:
                    print(f"  Warning: Could not process local contact {processed}: {item_error}")
                    continue
            
            print(f"✅ Successfully extracted {successful} contacts from {processed} local items")
            
        except Exception as e:
            print(f"❌ Error accessing local contacts: {e}")
        
        return contacts
    
    def extract_all_contacts(self) -> Dict[str, Any]:
        """
        Extract contacts from both GAL and local contacts.
        """
        if not self.connect_to_outlook():
            return {}
        
        all_contacts = []
        extraction_summary = []
        
        # Extract GAL contacts (Exchange)
        print("\n" + "="*60)
        print("EXTRACTING GLOBAL ADDRESS LIST (GAL) CONTACTS")
        print("="*60)
        
        gal_contacts = self.extract_gal_contacts()
        if gal_contacts:
            all_contacts.extend(gal_contacts)
            extraction_summary.append({
                'source': 'Global Address List',
                'count': len(gal_contacts)
            })
        
        # Extract local contacts
        print("\n" + "="*60)
        print("EXTRACTING LOCAL CONTACTS")
        print("="*60)
        
        local_contacts = self.extract_local_contacts()
        if local_contacts:
            all_contacts.extend(local_contacts)
            extraction_summary.append({
                'source': 'Local Contacts',
                'count': len(local_contacts)
            })
        
        # Create result structure
        result = {
            'extraction_info': {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_contacts': len(all_contacts),
                'extraction_method': 'Simplified GAL + Local extraction',
                'sources_processed': extraction_summary
            },
            'contacts': all_contacts
        }
        
        return result
    
    def save_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """Save contacts to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"outlook_contacts_simple_{timestamp}.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Contacts saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving to JSON: {e}")
            return ""


def main():
    """Main function using the simple, proven approach."""
    print("🚀 Simple Outlook Contact Extractor")
    print("=" * 50)
    print("Based on proven working code for GAL + Local contacts")
    print("=" * 50)
    
    extractor = SimpleOutlookExtractor()
    
    # Extract all contacts
    contacts_data = extractor.extract_all_contacts()
    
    if not contacts_data:
        print("❌ Failed to extract contacts")
        return
    
    # Print summary
    extraction_info = contacts_data.get('extraction_info', {})
    total_contacts = extraction_info.get('total_contacts', 0)
    
    print(f"\n📊 EXTRACTION SUMMARY")
    print("=" * 30)
    print(f"Total contacts extracted: {total_contacts}")
    print(f"Extraction time: {extraction_info.get('timestamp', 'Unknown')}")
    
    sources = extraction_info.get('sources_processed', [])
    if sources:
        print("\nSources processed:")
        for source in sources:
            print(f"  • {source['source']}: {source['count']} contacts")
    
    # Save to JSON
    saved_file = extractor.save_to_json(contacts_data)
    
    if saved_file and total_contacts > 0:
        print(f"\n✅ SUCCESS! Contacts extracted and saved")
        
        # Show sample contacts
        contacts = contacts_data.get('contacts', [])
        print(f"\n📋 Sample of extracted contacts (first 5):")
        
        for i, contact in enumerate(contacts[:5], 1):
            name = contact.get('full_name', 
                             f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip() or 
                             'No name')
            email = contact.get('email_primary', 'No email')
            company = contact.get('company', 'No company')
            source = contact.get('source', 'Unknown source')
            
            print(f"  {i}. {name}")
            print(f"     Email: {email}")
            print(f"     Company: {company}")
            print(f"     Source: {source}")
            print()
        
        # Statistics
        gal_count = sum(1 for c in contacts if c.get('source') == 'Global Address List')
        local_count = sum(1 for c in contacts if c.get('source') == 'Local Contacts')
        with_email = sum(1 for c in contacts if c.get('email_primary'))
        
        print(f"📈 Statistics:")
        print(f"  • GAL contacts: {gal_count}")
        print(f"  • Local contacts: {local_count}")
        print(f"  • Contacts with email: {with_email}/{total_contacts}")
        
    else:
        print("❌ No contacts were extracted or saved")


if __name__ == "__main__":
    main() 