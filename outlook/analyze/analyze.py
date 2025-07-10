#!/usr/bin/env python3
"""
Outlook COM Application Analyzer

This script analyzes the Outlook COM application to extract comprehensive information about:
- Email accounts (Exchange)
- Folder structure and statistics
- Groups and distribution lists
- Calendar information
- Contact information
- Application settings and configuration

Requires: pywin32 (pip install pywin32)
"""

import win32com.client
import pythoncom
import json
import os
import datetime
import traceback
import sys
from pathlib import Path

class OutlookAnalyzer:
    """Comprehensive Outlook COM application analyzer."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.app = None
        self.namespace = None
        self.results = {
            'timestamp': datetime.datetime.now().isoformat(),
            'accounts': [],
            'folders': {},
            'groups': [],
            'contacts': [],
            'calendar_info': {},
            'statistics': {},
            'errors': []
        }
    
    def connect_to_outlook(self):
        """Connect to the Outlook COM application."""
        try:
            print("Connecting to Outlook COM application...")
            pythoncom.CoInitialize()
            self.app = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.app.GetNamespace("MAPI")
            print("✓ Successfully connected to Outlook")
            return True
        except Exception as e:
            error_msg = f"Failed to connect to Outlook: {str(e)}"
            print(f"✗ {error_msg}")
            self.results['errors'].append(error_msg)
            return False
    
    def analyze_accounts(self):
        """Analyze all email accounts in Outlook."""
        try:
            print("\nAnalyzing email accounts...")
            accounts = self.namespace.Accounts
            print(f"Found {accounts.Count} account(s)")
            
            for i in range(1, accounts.Count + 1):
                account = accounts.Item(i)
                account_info = {
                    'index': i,
                    'display_name': getattr(account, 'DisplayName', 'Unknown'),
                    'smtp_address': getattr(account, 'SmtpAddress', 'Unknown'),
                    'account_type': self._get_account_type(account),
                    'current_user': getattr(account, 'CurrentUser', {}).Name if hasattr(account, 'CurrentUser') and account.CurrentUser else 'Unknown',
                    'delivery_store': {},
                    'session': {}
                }
                
                # Get delivery store information
                try:
                    if hasattr(account, 'DeliveryStore') and account.DeliveryStore:
                        store = account.DeliveryStore
                        account_info['delivery_store'] = {
                            'display_name': getattr(store, 'DisplayName', 'Unknown'),
                            'file_path': getattr(store, 'FilePath', 'Unknown'),
                            'size': getattr(store, 'Size', 0),
                            'categories': self._get_store_categories(store)
                        }
                except Exception as e:
                    account_info['delivery_store']['error'] = str(e)
                
                # Get session information
                try:
                    if hasattr(account, 'Session'):
                        session = account.Session
                        account_info['session'] = {
                            'current_user': getattr(session, 'CurrentUser', {}).Name if hasattr(session, 'CurrentUser') and session.CurrentUser else 'Unknown',
                            'default_store': getattr(session, 'DefaultStore', {}).DisplayName if hasattr(session, 'DefaultStore') and session.DefaultStore else 'Unknown'
                        }
                except Exception as e:
                    account_info['session']['error'] = str(e)
                
                self.results['accounts'].append(account_info)
                print(f"  ✓ {account_info['display_name']} ({account_info['smtp_address']})")
            
        except Exception as e:
            error_msg = f"Error analyzing accounts: {str(e)}"
            print(f"✗ {error_msg}")
            self.results['errors'].append(error_msg)
    
    def analyze_folders(self):
        """Analyze folder structure and statistics."""
        try:
            print("\nAnalyzing folder structure...")
            
            # Get default folders
            default_folders = {
                'inbox': (6, 'olFolderInbox'),
                'sent_items': (5, 'olFolderSentMail'),
                'drafts': (16, 'olFolderDrafts'),
                'deleted_items': (3, 'olFolderDeletedItems'),
                'outbox': (4, 'olFolderOutbox'),
                'junk': (23, 'olFolderJunk'),
                'calendar': (9, 'olFolderCalendar'),
                'contacts': (10, 'olFolderContacts'),
                'tasks': (13, 'olFolderTasks'),
                'notes': (12, 'olFolderNotes'),
                'journal': (11, 'olFolderJournal')
            }
            
            for folder_name, (folder_id, folder_constant) in default_folders.items():
                try:
                    folder = self.namespace.GetDefaultFolder(folder_id)
                    folder_info = self._analyze_folder(folder, folder_name)
                    self.results['folders'][folder_name] = folder_info
                    print(f"  ✓ {folder_name}: {folder_info['name']} ({folder_info['total_items']} items)")
                except Exception as e:
                    error_msg = f"Error accessing {folder_name}: {str(e)}"
                    print(f"  ✗ {error_msg}")
                    self.results['folders'][folder_name] = {'error': str(e)}
            
            # Analyze custom folders
            self._analyze_custom_folders()
            
        except Exception as e:
            error_msg = f"Error analyzing folders: {str(e)}"
            print(f"✗ {error_msg}")
            self.results['errors'].append(error_msg)
    
    def _analyze_folder(self, folder, folder_type):
        """Analyze a specific folder."""
        folder_info = {
            'name': getattr(folder, 'Name', 'Unknown'),
            'entry_id': getattr(folder, 'EntryID', 'Unknown'),
            'store_id': getattr(folder, 'StoreID', 'Unknown'),
            'total_items': getattr(folder, 'Items', {}).Count if hasattr(folder, 'Items') else 0,
            'unread_items': getattr(folder, 'UnReadItemCount', 0),
            'folder_path': getattr(folder, 'FolderPath', 'Unknown'),
            'default_item_type': getattr(folder, 'DefaultItemType', 'Unknown'),
            'subfolders': [],
            'recent_items': []
        }
        
        # Get subfolders
        try:
            if hasattr(folder, 'Folders') and folder.Folders.Count > 0:
                for i in range(1, min(folder.Folders.Count + 1, 11)):  # Limit to first 10 subfolders
                    subfolder = folder.Folders.Item(i)
                    subfolder_info = {
                        'name': getattr(subfolder, 'Name', 'Unknown'),
                        'total_items': getattr(subfolder, 'Items', {}).Count if hasattr(subfolder, 'Items') else 0,
                        'unread_items': getattr(subfolder, 'UnReadItemCount', 0)
                    }
                    folder_info['subfolders'].append(subfolder_info)
        except Exception as e:
            folder_info['subfolders_error'] = str(e)
        
        # Get recent items (for email folders)
        if folder_type in ['inbox', 'sent_items', 'drafts']:
            try:
                items = folder.Items
                items.Sort("[ReceivedTime]", True)  # Sort by received time, descending
                
                for i in range(1, min(items.Count + 1, 6)):  # Get up to 5 recent items
                    item = items.Item(i)
                    item_info = {
                        'subject': getattr(item, 'Subject', 'No Subject'),
                        'sender': getattr(item, 'SenderName', 'Unknown'),
                        'received_time': str(getattr(item, 'ReceivedTime', 'Unknown')),
                        'size': getattr(item, 'Size', 0),
                        'unread': getattr(item, 'UnRead', False),
                        'importance': getattr(item, 'Importance', 1)
                    }
                    folder_info['recent_items'].append(item_info)
            except Exception as e:
                folder_info['recent_items_error'] = str(e)
        
        return folder_info
    
    def _analyze_custom_folders(self):
        """Analyze custom folders in all stores."""
        try:
            print("  Analyzing custom folders...")
            stores = self.namespace.Stores
            
            for i in range(1, stores.Count + 1):
                store = stores.Item(i)
                store_name = getattr(store, 'DisplayName', f'Store_{i}')
                
                try:
                    root_folder = store.GetRootFolder()
                    custom_folders = self._get_custom_folders(root_folder, max_depth=2)
                    
                    if custom_folders:
                        if 'custom_folders' not in self.results['folders']:
                            self.results['folders']['custom_folders'] = {}
                        self.results['folders']['custom_folders'][store_name] = custom_folders
                        print(f"    ✓ {store_name}: {len(custom_folders)} custom folders")
                except Exception as e:
                    print(f"    ✗ Error analyzing store {store_name}: {str(e)}")
        
        except Exception as e:
            print(f"  ✗ Error analyzing custom folders: {str(e)}")
    
    def _get_custom_folders(self, parent_folder, max_depth=2, current_depth=0):
        """Recursively get custom folders."""
        if current_depth >= max_depth:
            return []
        
        custom_folders = []
        try:
            if hasattr(parent_folder, 'Folders'):
                for i in range(1, parent_folder.Folders.Count + 1):
                    folder = parent_folder.Folders.Item(i)
                    folder_info = {
                        'name': getattr(folder, 'Name', 'Unknown'),
                        'total_items': getattr(folder, 'Items', {}).Count if hasattr(folder, 'Items') else 0,
                        'unread_items': getattr(folder, 'UnReadItemCount', 0),
                        'path': getattr(folder, 'FolderPath', 'Unknown')
                    }
                    
                    # Get subfolders recursively
                    subfolders = self._get_custom_folders(folder, max_depth, current_depth + 1)
                    if subfolders:
                        folder_info['subfolders'] = subfolders
                    
                    custom_folders.append(folder_info)
        except Exception as e:
            pass  # Ignore errors for individual folders
        
        return custom_folders
    
    def analyze_groups(self):
        """Analyze groups and distribution lists."""
        try:
            print("\nAnalyzing groups and distribution lists...")
            
            # Try to get address lists (which include distribution lists)
            try:
                address_lists = self.namespace.AddressLists
                
                for i in range(1, address_lists.Count + 1):
                    address_list = address_lists.Item(i)
                    list_info = {
                        'name': getattr(address_list, 'Name', 'Unknown'),
                        'address_list_type': getattr(address_list, 'AddressListType', 'Unknown'),
                        'is_read_only': getattr(address_list, 'IsReadOnly', True),
                        'entry_count': 0,
                        'entries': []
                    }
                    
                    try:
                        entries = address_list.AddressEntries
                        list_info['entry_count'] = entries.Count
                        
                        # Get first few entries for sample
                        for j in range(1, min(entries.Count + 1, 6)):
                            entry = entries.Item(j)
                            entry_info = {
                                'name': getattr(entry, 'Name', 'Unknown'),
                                'address': getattr(entry, 'Address', 'Unknown'),
                                'type': getattr(entry, 'Type', 'Unknown')
                            }
                            list_info['entries'].append(entry_info)
                    
                    except Exception as e:
                        list_info['entries_error'] = str(e)
                    
                    self.results['groups'].append(list_info)
                    print(f"  ✓ {list_info['name']}: {list_info['entry_count']} entries")
            
            except Exception as e:
                print(f"  ✗ Error accessing address lists: {str(e)}")
                self.results['groups'].append({'error': str(e)})
            
        except Exception as e:
            error_msg = f"Error analyzing groups: {str(e)}"
            print(f"✗ {error_msg}")
            self.results['errors'].append(error_msg)
    
    def analyze_contacts(self):
        """Analyze contact information."""
        try:
            print("\nAnalyzing contacts...")
            
            contacts_folder = self.namespace.GetDefaultFolder(10)  # olFolderContacts
            contacts = contacts_folder.Items
            
            contact_summary = {
                'total_contacts': contacts.Count,
                'sample_contacts': [],
                'contact_fields': set()
            }
            
            # Get sample contacts
            for i in range(1, min(contacts.Count + 1, 6)):
                contact = contacts.Item(i)
                contact_info = {
                    'full_name': getattr(contact, 'FullName', 'Unknown'),
                    'email1_address': getattr(contact, 'Email1Address', ''),
                    'company_name': getattr(contact, 'CompanyName', ''),
                    'job_title': getattr(contact, 'JobTitle', ''),
                    'business_telephone_number': getattr(contact, 'BusinessTelephoneNumber', '')
                }
                
                # Collect field names for analysis
                try:
                    for prop in dir(contact):
                        if not prop.startswith('_') and not callable(getattr(contact, prop)):
                            contact_summary['contact_fields'].add(prop)
                except:
                    pass
                
                contact_summary['sample_contacts'].append(contact_info)
            
            # Convert set to list for JSON serialization
            contact_summary['contact_fields'] = list(contact_summary['contact_fields'])
            
            self.results['contacts'] = contact_summary
            print(f"  ✓ Found {contact_summary['total_contacts']} contacts")
            
        except Exception as e:
            error_msg = f"Error analyzing contacts: {str(e)}"
            print(f"✗ {error_msg}")
            self.results['errors'].append(error_msg)
    
    def analyze_calendar(self):
        """Analyze calendar information."""
        try:
            print("\nAnalyzing calendar...")
            
            calendar_folder = self.namespace.GetDefaultFolder(9)  # olFolderCalendar
            appointments = calendar_folder.Items
            
            calendar_info = {
                'total_appointments': appointments.Count,
                'upcoming_appointments': [],
                'calendar_name': getattr(calendar_folder, 'Name', 'Unknown')
            }
            
            # Get upcoming appointments
            try:
                appointments.Sort("[Start]")
                appointments.IncludeRecurrences = True
                
                # Filter for upcoming appointments (next 30 days)
                start_date = datetime.datetime.now()
                end_date = start_date + datetime.timedelta(days=30)
                
                filter_string = f"[Start] >= '{start_date.strftime('%m/%d/%Y')}' AND [Start] <= '{end_date.strftime('%m/%d/%Y')}'"
                filtered_appointments = appointments.Restrict(filter_string)
                
                for i in range(1, min(filtered_appointments.Count + 1, 11)):
                    appointment = filtered_appointments.Item(i)
                    appointment_info = {
                        'subject': getattr(appointment, 'Subject', 'No Subject'),
                        'start': str(getattr(appointment, 'Start', 'Unknown')),
                        'end': str(getattr(appointment, 'End', 'Unknown')),
                        'location': getattr(appointment, 'Location', ''),
                        'organizer': getattr(appointment, 'Organizer', 'Unknown'),
                        'is_recurring': getattr(appointment, 'IsRecurring', False)
                    }
                    calendar_info['upcoming_appointments'].append(appointment_info)
            
            except Exception as e:
                calendar_info['appointments_error'] = str(e)
            
            self.results['calendar_info'] = calendar_info
            print(f"  ✓ Calendar: {calendar_info['total_appointments']} total appointments")
            
        except Exception as e:
            error_msg = f"Error analyzing calendar: {str(e)}"
            print(f"✗ {error_msg}")
            self.results['errors'].append(error_msg)
    
    def generate_statistics(self):
        """Generate overall statistics."""
        try:
            print("\nGenerating statistics...")
            
            stats = {
                'total_accounts': len(self.results['accounts']),
                'total_folders_analyzed': len(self.results['folders']),
                'total_groups': len(self.results['groups']),
                'inbox_stats': {},
                'overall_email_count': 0,
                'overall_unread_count': 0
            }
            
            # Calculate email statistics
            for folder_name, folder_info in self.results['folders'].items():
                if isinstance(folder_info, dict) and 'total_items' in folder_info:
                    stats['overall_email_count'] += folder_info['total_items']
                    stats['overall_unread_count'] += folder_info.get('unread_items', 0)
                    
                    if folder_name == 'inbox':
                        stats['inbox_stats'] = {
                            'total_items': folder_info['total_items'],
                            'unread_items': folder_info['unread_items'],
                            'subfolders_count': len(folder_info.get('subfolders', []))
                        }
            
            self.results['statistics'] = stats
            print(f"  ✓ Statistics generated")
            print(f"    - Accounts: {stats['total_accounts']}")
            print(f"    - Total emails: {stats['overall_email_count']}")
            print(f"    - Unread emails: {stats['overall_unread_count']}")
            
        except Exception as e:
            error_msg = f"Error generating statistics: {str(e)}"
            print(f"✗ {error_msg}")
            self.results['errors'].append(error_msg)
    
    def _get_account_type(self, account):
        """Determine the account type."""
        try:
            if hasattr(account, 'AccountType'):
                return account.AccountType
            elif hasattr(account, 'DeliveryStore') and account.DeliveryStore:
                store = account.DeliveryStore
                if hasattr(store, 'ExchangeStoreType'):
                    return f"Exchange ({store.ExchangeStoreType})"
            return "Unknown"
        except:
            return "Unknown"
    
    def _get_store_categories(self, store):
        """Get categories from a store."""
        try:
            if hasattr(store, 'Categories'):
                categories = []
                for i in range(1, store.Categories.Count + 1):
                    category = store.Categories.Item(i)
                    categories.append({
                        'name': getattr(category, 'Name', 'Unknown'),
                        'color': getattr(category, 'Color', 'Unknown')
                    })
                return categories
        except:
            pass
        return []
    
    def save_results(self, output_file="outlook_analysis.json"):
        """Save analysis results to a JSON file."""
        try:
            output_path = Path(__file__).parent / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n✓ Results saved to: {output_path}")
            return output_path
        except Exception as e:
            print(f"✗ Error saving results: {str(e)}")
            return None
    
    def print_summary(self):
        """Print a summary of the analysis."""
        print("\n" + "="*60)
        print("OUTLOOK ANALYSIS SUMMARY")
        print("="*60)
        
        if self.results['accounts']:
            print(f"\n📧 EMAIL ACCOUNTS ({len(self.results['accounts'])})")
            for account in self.results['accounts']:
                print(f"  • {account['display_name']}")
                print(f"    Email: {account['smtp_address']}")
                print(f"    Type: {account['account_type']}")
        
        if self.results['folders']:
            print(f"\n📁 FOLDER ANALYSIS")
            for folder_name, folder_info in self.results['folders'].items():
                if isinstance(folder_info, dict) and 'total_items' in folder_info:
                    print(f"  • {folder_name.title()}: {folder_info['total_items']} items ({folder_info.get('unread_items', 0)} unread)")
        
        if self.results['statistics']:
            stats = self.results['statistics']
            print(f"\n📊 STATISTICS")
            print(f"  • Total Emails: {stats['overall_email_count']}")
            print(f"  • Unread Emails: {stats['overall_unread_count']}")
            print(f"  • Groups/Lists: {stats['total_groups']}")
        
        if self.results['contacts']:
            print(f"\n👥 CONTACTS")
            print(f"  • Total Contacts: {self.results['contacts']['total_contacts']}")
        
        if self.results['calendar_info']:
            print(f"\n📅 CALENDAR")
            print(f"  • Total Appointments: {self.results['calendar_info']['total_appointments']}")
            print(f"  • Upcoming Appointments: {len(self.results['calendar_info'].get('upcoming_appointments', []))}")
        
        if self.results['errors']:
            print(f"\n⚠️  ERRORS ({len(self.results['errors'])})")
            for error in self.results['errors'][:5]:  # Show first 5 errors
                print(f"  • {error}")
    
    def cleanup(self):
        """Cleanup COM objects."""
        try:
            if self.namespace:
                self.namespace = None
            if self.app:
                self.app = None
            pythoncom.CoUninitialize()
        except:
            pass

def main():
    """Main function to run the analysis."""
    print("Outlook COM Application Analyzer")
    print("================================")
    
    analyzer = OutlookAnalyzer()
    
    try:
        # Connect to Outlook
        if not analyzer.connect_to_outlook():
            return 1
        
        # Run analysis modules
        analyzer.analyze_accounts()
        analyzer.analyze_folders()
        analyzer.analyze_groups()
        analyzer.analyze_contacts()
        analyzer.analyze_calendar()
        analyzer.generate_statistics()
        
        # Save and display results
        analyzer.save_results()
        analyzer.print_summary()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")
        return 1
    finally:
        analyzer.cleanup()

if __name__ == "__main__":
    sys.exit(main())
