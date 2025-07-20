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
import win32com.client.gencache
import pythoncom
import json
import os
import datetime
import traceback
import sys
import shutil
from pathlib import Path

class OutlookAnalyzer:
    """Comprehensive Outlook COM application analyzer."""
    
    def __init__(self, debug=False):
        """Initialize the analyzer."""
        self.app = None
        self.namespace = None
        self.debug = debug
        self.results = {
            'timestamp': datetime.datetime.now().isoformat(),
            'folders': {},
            'emails': {},
            'calendar_info': {},
            'statistics': {},
            'errors': []
        }
    
    def clear_win32com_cache(self):
        """Clear the win32com cache to prevent CLSIDToClassMap errors."""
        try:
            print("Clearing win32com cache to prevent COM errors...")
            
            # Get the cache directory
            cache_dir = win32com.client.gencache.GetGeneratePath()
            
            if os.path.exists(cache_dir):
                print(f"  Cache directory: {cache_dir}")
                
                # Remove the entire cache directory
                shutil.rmtree(cache_dir, ignore_errors=True)
                print("  ✓ Cache directory cleared successfully")
                
                # Recreate the directory structure
                os.makedirs(cache_dir, exist_ok=True)
                print("  ✓ Cache directory recreated")
            else:
                print("  ✓ Cache directory doesn't exist, nothing to clear")
                
        except Exception as e:
            error_msg = f"Warning: Could not clear win32com cache: {str(e)}"
            print(f"  ⚠️  {error_msg}")
            # Don't add to errors as this is not critical
    
    def connect_to_outlook(self):
        """Connect to the Outlook COM application."""
        try:
            print("Connecting to Outlook COM application...")
            pythoncom.CoInitialize()
            self.app = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.app.GetNamespace("MAPI")
            
            # Test basic access
            print("Testing basic Outlook access...")
            try:
                version = getattr(self.app, 'Version', 'Unknown')
                print(f"  Outlook Version: {version}")
                
                # Test namespace access
                default_profile = getattr(self.namespace, 'DefaultProfileName', 'Unknown')
                print(f"  Default Profile: {default_profile}")
                
                # Test store access
                stores = self.namespace.Stores
                print(f"  Available Stores: {stores.Count}")
                
                for i in range(1, min(stores.Count + 1, 3)):  # Show first 3 stores
                    store = stores.Item(i)
                    store_name = getattr(store, 'DisplayName', f'Store_{i}')
                    print(f"    Store {i}: {store_name}")
                
            except Exception as e:
                print(f"  Warning: Error during basic access test: {e}")
            
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
                    debug_context = f"Email {i} in {account_name}"
                    
                    if self.debug:
                        print(f"    DEBUG: Processing {debug_context}")
                        print(f"    DEBUG: Item type: {type(item).__name__}")
                        print(f"    DEBUG: Item class: {self._safe_get_property(item, 'Class', 'Unknown', debug_context if self.debug else '')}")
                    
                    # Extract email details with detailed debugging
                    email_info = {
                        'index': i,
                        'debug_info': {
                            'item_type': str(type(item)),
                            'item_class': self._safe_get_property(item, 'Class', 'Unknown', debug_context),
                            'available_properties': []
                        }
                    }
                    
                    # Try to list available properties
                    if self.debug:
                        try:
                            available_props = [prop for prop in dir(item) if not prop.startswith('_')]
                            email_info['debug_info']['available_properties'] = available_props[:20]  # First 20 properties
                            print(f"    DEBUG: Available properties: {len(available_props)}")
                        except:
                            pass
                    
                    # Extract basic properties with debugging
                    email_info.update({
                        'subject': self._safe_get_property(item, 'Subject', 'No Subject', debug_context),
                        'sender_name': self._safe_get_property(item, 'SenderName', 'Unknown', debug_context),
                        'sender_email': self._safe_get_property(item, 'SenderEmailAddress', 'Unknown', debug_context),
                        'received_time': str(self._safe_get_property(item, 'ReceivedTime', 'Unknown', debug_context)),
                        'sent_on': str(self._safe_get_property(item, 'SentOn', 'Unknown', debug_context)),
                        'size': self._safe_get_property(item, 'Size', 0, debug_context),
                        'importance': self._safe_get_property(item, 'Importance', 1, debug_context),
                        'unread': self._safe_get_property(item, 'UnRead', False, debug_context),
                        'categories': self._safe_get_property(item, 'Categories', '', debug_context),
                        'body': '',
                        'body_format': self._safe_get_property(item, 'BodyFormat', 'Unknown', debug_context),
                        'html_body': '',
                        'recipients': [],
                        'attachments': []
                    })
                    
                    # Try alternative sender properties
                    if email_info['sender_name'] == 'Unknown':
                        if self.debug:
                            print(f"    DEBUG: Trying alternative sender properties...")
                        email_info['sender_name'] = self._safe_get_property(item, 'SentOnBehalfOfName', 'Unknown', debug_context if self.debug else '')
                        if email_info['sender_name'] == 'Unknown':
                            # Try to get from SenderEmailAddress property differently
                            try:
                                sender_obj = getattr(item, 'Sender', None)
                                if sender_obj:
                                    email_info['sender_name'] = self._safe_get_property(sender_obj, 'Name', 'Unknown', f"{debug_context} Sender" if self.debug else '')
                                    email_info['sender_email'] = self._safe_get_property(sender_obj, 'Address', 'Unknown', f"{debug_context} Sender" if self.debug else '')
                            except Exception as e:
                                if self.debug:
                                    print(f"    DEBUG: Error accessing Sender object: {e}")
                    
                    # Try to get body with different approaches
                    if self.debug:
                        print(f"    DEBUG: Attempting to get email body...")
                    body_attempts = [
                        ('Body', 'body'),
                        ('HTMLBody', 'html_body'),
                        ('RTFBody', 'rtf_body')
                    ]
                    
                    for prop_name, result_key in body_attempts:
                        try:
                            if hasattr(item, prop_name):
                                body_content = getattr(item, prop_name)
                                if body_content and len(str(body_content).strip()) > 0:
                                    if result_key == 'body' or result_key == 'html_body':
                                        # Store full email content (no truncation)
                                        email_info[result_key] = str(body_content)
                                    if self.debug:
                                        print(f"    DEBUG: Successfully got {prop_name} ({len(str(body_content))} chars)")
                                else:
                                    if self.debug:
                                        print(f"    DEBUG: {prop_name} is empty or None")
                            else:
                                if self.debug:
                                    print(f"    DEBUG: {prop_name} property not available")
                        except Exception as e:
                            if self.debug:
                                print(f"    DEBUG: Error getting {prop_name}: {e}")
                            email_info[f'{result_key}_error'] = str(e)
                    
                    # Get recipients with detailed debugging
                    print(f"    DEBUG: Attempting to get recipients...")
                    try:
                        if hasattr(item, 'Recipients'):
                            recipients_obj = getattr(item, 'Recipients')
                            recipients_count = getattr(recipients_obj, 'Count', 0)
                            print(f"    DEBUG: Found {recipients_count} recipients")
                            
                            for j in range(1, min(recipients_count + 1, 11)):  # Max 10 recipients
                                try:
                                    recipient = recipients_obj.Item(j)
                                    recipient_info = {
                                        'name': self._safe_get_property(recipient, 'Name', 'Unknown', f"{debug_context} Recipient {j}"),
                                        'address': self._safe_get_property(recipient, 'Address', 'Unknown', f"{debug_context} Recipient {j}"),
                                        'type': self._safe_get_property(recipient, 'Type', 'Unknown', f"{debug_context} Recipient {j}")
                                    }
                                    email_info['recipients'].append(recipient_info)
                                    print(f"    DEBUG: Got recipient {j}: {recipient_info['name']}")
                                except Exception as e:
                                    print(f"    DEBUG: Error getting recipient {j}: {e}")
                                    email_info['recipients'].append({'error': str(e), 'index': j})
                        else:
                            print(f"    DEBUG: No Recipients property available")
                    except Exception as e:
                        print(f"    DEBUG: Error accessing recipients: {e}")
                        email_info['recipients_error'] = str(e)
                    
                    # Get attachments with detailed debugging
                    print(f"    DEBUG: Attempting to get attachments...")
                    try:
                        if hasattr(item, 'Attachments'):
                            attachments_obj = getattr(item, 'Attachments')
                            attachments_count = getattr(attachments_obj, 'Count', 0)
                            print(f"    DEBUG: Found {attachments_count} attachments")
                            
                            for j in range(1, min(attachments_count + 1, 11)):  # Max 10 attachments
                                try:
                                    attachment = attachments_obj.Item(j)
                                    attachment_info = {
                                        'filename': self._safe_get_property(attachment, 'FileName', 'Unknown', f"{debug_context} Attachment {j}"),
                                        'size': self._safe_get_property(attachment, 'Size', 0, f"{debug_context} Attachment {j}"),
                                        'type': self._safe_get_property(attachment, 'Type', 'Unknown', f"{debug_context} Attachment {j}")
                                    }
                                    email_info['attachments'].append(attachment_info)
                                    print(f"    DEBUG: Got attachment {j}: {attachment_info['filename']}")
                                except Exception as e:
                                    print(f"    DEBUG: Error getting attachment {j}: {e}")
                                    email_info['attachments'].append({'error': str(e), 'index': j})
                        else:
                            print(f"    DEBUG: No Attachments property available")
                    except Exception as e:
                        print(f"    DEBUG: Error accessing attachments: {e}")
                        email_info['attachments_error'] = str(e)
                    
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
    
    def _safe_get_property(self, obj, property_name, default_value, debug_context=""):
        """Safely get a property from an Outlook object with detailed error logging."""
        try:
            if hasattr(obj, property_name):
                value = getattr(obj, property_name)
                return value
            else:
                if debug_context and self.debug:
                    print(f"    DEBUG: {debug_context} - Property '{property_name}' not found on object")
                return default_value
        except Exception as e:
            error_msg = f"Error accessing {property_name}: {str(e)} (Type: {type(e).__name__})"
            if debug_context and self.debug:
                print(f"    DEBUG: {debug_context} - {error_msg}")
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
    
    def save_results(self, output_file="debug\outlook_analysis.json"):
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
    
    # Enable debug mode if requested
    debug_mode = len(sys.argv) > 1 and sys.argv[1] == '--debug'
    if debug_mode:
        print("DEBUG MODE ENABLED")
    
    analyzer = OutlookAnalyzer(debug=debug_mode)
    
    try:
        # Clear win32com cache first to prevent COM errors
        analyzer.clear_win32com_cache()
        
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
