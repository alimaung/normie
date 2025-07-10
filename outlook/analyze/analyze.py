#!/usr/bin/env python3
"""
Outlook COM Application Analyzer

This script analyzes the Outlook COM application to extract comprehensive information about:
- Folder structure and statistics
- Email content from both accounts
- Calendar information

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
            'folders': {},
            'emails': {},
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
            'subfolders': []
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
    
    def extract_emails(self):
        """Extract first 5 emails from both accounts' inboxes."""
        try:
            print("\nExtracting emails from both accounts...")
            
            # Get all stores (accounts)
            stores = self.namespace.Stores
            
            for i in range(1, stores.Count + 1):
                store = stores.Item(i)
                store_name = getattr(store, 'DisplayName', f'Store_{i}')
                
                try:
                    print(f"  Processing account: {store_name}")
                    
                    # Get the inbox for this store
                    root_folder = store.GetRootFolder()
                    inbox = self._find_inbox_in_store(root_folder)
                    
                    if inbox and hasattr(inbox, 'Items'):
                        emails = self._extract_emails_from_folder(inbox, store_name, 5)
                        if emails:
                            self.results['emails'][store_name] = emails
                            print(f"    ✓ Extracted {len(emails)} emails from {store_name}")
                        else:
                            print(f"    ✗ No emails extracted from {store_name}")
                    else:
                        print(f"    ✗ Could not find inbox for {store_name}")
                        
                except Exception as e:
                    error_msg = f"Error processing {store_name}: {str(e)}"
                    print(f"    ✗ {error_msg}")
                    self.results['errors'].append(error_msg)
            
        except Exception as e:
            error_msg = f"Error extracting emails: {str(e)}"
            print(f"✗ {error_msg}")
            self.results['errors'].append(error_msg)
    
    def _find_inbox_in_store(self, root_folder):
        """Find the Inbox folder in a store."""
        try:
            if hasattr(root_folder, 'Folders'):
                for i in range(1, root_folder.Folders.Count + 1):
                    folder = root_folder.Folders.Item(i)
                    folder_name = getattr(folder, 'Name', '').lower()
                    if folder_name == 'inbox':
                        return folder
            return None
        except:
            return None
    
    def _extract_emails_from_folder(self, folder, account_name, limit=5):
        """Extract emails from a specific folder."""
        emails = []
        try:
            items = folder.Items
            items.Sort("[ReceivedTime]", True)  # Sort by received time, descending
            
            for i in range(1, min(items.Count + 1, limit + 1)):
                try:
                    item = items.Item(i)
                    
                    # Extract email details
                    email_info = {
                        'index': i,
                        'subject': self._safe_get_property(item, 'Subject', 'No Subject'),
                        'sender_name': self._safe_get_property(item, 'SenderName', 'Unknown'),
                        'sender_email': self._safe_get_property(item, 'SenderEmailAddress', 'Unknown'),
                        'received_time': str(self._safe_get_property(item, 'ReceivedTime', 'Unknown')),
                        'sent_on': str(self._safe_get_property(item, 'SentOn', 'Unknown')),
                        'size': self._safe_get_property(item, 'Size', 0),
                        'importance': self._safe_get_property(item, 'Importance', 1),
                        'unread': self._safe_get_property(item, 'UnRead', False),
                        'categories': self._safe_get_property(item, 'Categories', ''),
                        'body': self._safe_get_property(item, 'Body', ''),
                        'body_format': self._safe_get_property(item, 'BodyFormat', 'Unknown'),
                        'html_body': '',
                        'recipients': [],
                        'attachments': []
                    }
                    
                    # Try to get HTML body
                    try:
                        email_info['html_body'] = self._safe_get_property(item, 'HTMLBody', '')
                    except:
                        email_info['html_body'] = 'Error accessing HTML body'
                    
                    # Get recipients
                    try:
                        if hasattr(item, 'Recipients'):
                            for j in range(1, min(item.Recipients.Count + 1, 11)):  # Max 10 recipients
                                recipient = item.Recipients.Item(j)
                                recipient_info = {
                                    'name': self._safe_get_property(recipient, 'Name', 'Unknown'),
                                    'address': self._safe_get_property(recipient, 'Address', 'Unknown'),
                                    'type': self._safe_get_property(recipient, 'Type', 'Unknown')
                                }
                                email_info['recipients'].append(recipient_info)
                    except Exception as e:
                        email_info['recipients_error'] = str(e)
                    
                    # Get attachments
                    try:
                        if hasattr(item, 'Attachments'):
                            for j in range(1, min(item.Attachments.Count + 1, 11)):  # Max 10 attachments
                                attachment = item.Attachments.Item(j)
                                attachment_info = {
                                    'filename': self._safe_get_property(attachment, 'FileName', 'Unknown'),
                                    'size': self._safe_get_property(attachment, 'Size', 0),
                                    'type': self._safe_get_property(attachment, 'Type', 'Unknown')
                                }
                                email_info['attachments'].append(attachment_info)
                    except Exception as e:
                        email_info['attachments_error'] = str(e)
                    
                    # Truncate body if too long (for JSON storage)
                    if len(email_info['body']) > 2000:
                        email_info['body'] = email_info['body'][:2000] + "... [TRUNCATED]"
                    if len(email_info['html_body']) > 3000:
                        email_info['html_body'] = email_info['html_body'][:3000] + "... [TRUNCATED]"
                    
                    emails.append(email_info)
                    
                except Exception as e:
                    error_info = {
                        'index': i,
                        'error': f"Error extracting email {i}: {str(e)}"
                    }
                    emails.append(error_info)
            
        except Exception as e:
            print(f"    ✗ Error accessing items in folder: {str(e)}")
        
        return emails
    
    def _safe_get_property(self, obj, property_name, default_value):
        """Safely get a property from an Outlook object."""
        try:
            return getattr(obj, property_name, default_value)
        except:
            return default_value
    
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
                        'subject': self._safe_get_property(appointment, 'Subject', 'No Subject'),
                        'start': str(self._safe_get_property(appointment, 'Start', 'Unknown')),
                        'end': str(self._safe_get_property(appointment, 'End', 'Unknown')),
                        'location': self._safe_get_property(appointment, 'Location', ''),
                        'organizer': self._safe_get_property(appointment, 'Organizer', 'Unknown'),
                        'is_recurring': self._safe_get_property(appointment, 'IsRecurring', False),
                        'body': self._safe_get_property(appointment, 'Body', '')[:500]  # Truncate body
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
                'total_folders_analyzed': len(self.results['folders']),
                'total_accounts_with_emails': len(self.results['emails']),
                'inbox_stats': {},
                'overall_email_count': 0,
                'overall_unread_count': 0,
                'emails_extracted': 0
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
            
            # Count extracted emails
            for account_name, emails in self.results['emails'].items():
                stats['emails_extracted'] += len(emails)
            
            self.results['statistics'] = stats
            print(f"  ✓ Statistics generated")
            print(f"    - Accounts with emails: {stats['total_accounts_with_emails']}")
            print(f"    - Total emails: {stats['overall_email_count']}")
            print(f"    - Unread emails: {stats['overall_unread_count']}")
            print(f"    - Emails extracted: {stats['emails_extracted']}")
            
        except Exception as e:
            error_msg = f"Error generating statistics: {str(e)}"
            print(f"✗ {error_msg}")
            self.results['errors'].append(error_msg)
    
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
        
        if self.results['emails']:
            print(f"\n📧 EMAIL EXTRACTION")
            for account_name, emails in self.results['emails'].items():
                print(f"  • {account_name}: {len(emails)} emails extracted")
                for email in emails[:2]:  # Show first 2 emails
                    if 'subject' in email:
                        print(f"    - {email['subject'][:50]}{'...' if len(email['subject']) > 50 else ''}")
                        print(f"      From: {email['sender_name']} ({email['received_time'][:10]})")
        
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
            print(f"  • Emails Extracted: {stats['emails_extracted']}")
        
        if self.results['calendar_info']:
            print(f"\n📅 CALENDAR")
            print(f"  • Total Appointments: {self.results['calendar_info']['total_appointments']}")
            print(f"  • Upcoming Appointments: {len(self.results['calendar_info'].get('upcoming_appointments', []))}")
        
        if self.results['errors']:
            print(f"\n⚠️  ERRORS ({len(self.results['errors'])})")
            for error in self.results['errors'][:3]:  # Show first 3 errors
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
        analyzer.analyze_folders()
        analyzer.extract_emails()
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
