import os
import json
import datetime
import logging
from pathlib import Path
from django.conf import settings
from typing import Dict, List, Optional, Tuple
import hashlib

# COM interface imports
try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False

# Define logger at module level
logger = logging.getLogger(__name__)

class OutlookService:
    """
    Clean Outlook service for email management.
    Reads VBA-extracted JSON data and provides email functionality.
    Now includes COM interface for email operations like delete and mark read/unread.
    """
    
    # Account configuration with fallback support
    # Will try TARGET_ACCOUNT first, then DEBUG_ACCOUNT if not found
    TARGET_ACCOUNT = "IRM-Standardisation-Office"
    DEBUG_ACCOUNT = "microfilm.development@gmail.com"
    
    def __init__(self):
        """Initialize the Outlook service."""
        logger.debug("Initializing OutlookService")
        
        # Dynamic path based on current user
        self.base_path = Path(f"C:/Users/{os.environ.get('USERNAME', 'default')}/Desktop/normie/outlook/analyze/mail")
        self.emails_file = self.base_path / "emails.json"
        self.data_folder = self.base_path / "data"
        
        # COM interface attributes
        self._outlook_app = None
        self._namespace = None
        self._com_initialized = False
        
        logger.debug(f"Base path: {self.base_path}")
        logger.debug(f"Emails file: {self.emails_file}")
        logger.debug(f"COM Available: {COM_AVAILABLE}")

    def _initialize_com(self) -> bool:
        """Initialize COM interface for Outlook operations."""
        if not COM_AVAILABLE:
            logger.warning("COM interface not available (pywin32 not installed)")
            return False
            
        if self._com_initialized:
            return True
            
        try:
            logger.debug("Initializing COM interface...")
            pythoncom.CoInitialize()
            self._outlook_app = win32com.client.Dispatch("Outlook.Application")
            self._namespace = self._outlook_app.GetNamespace("MAPI")
            self._com_initialized = True
            logger.debug("COM interface initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize COM interface: {str(e)}")
            return False

    def _cleanup_com(self):
        """Cleanup COM interface resources."""
        if self._com_initialized:
            try:
                if self._namespace:
                    self._namespace = None
                if self._outlook_app:
                    self._outlook_app = None
                pythoncom.CoUninitialize()
                self._com_initialized = False
                logger.debug("COM interface cleaned up")
            except Exception as e:
                logger.warning(f"Error during COM cleanup: {str(e)}")

    def _get_account_priority_list(self) -> List[str]:
        """Get list of accounts to try in priority order."""
        return [self.TARGET_ACCOUNT, self.DEBUG_ACCOUNT]

    def _find_target_store_with_fallback(self) -> Optional[object]:
        """
        Find target Outlook store with fallback accounts.
        
        Returns:
            Outlook store object if found, None otherwise
        """
        if not self._initialize_com():
            return None
            
        try:
            stores = self._namespace.Stores
            accounts = self._get_account_priority_list()
            
            # Try each account in priority order
            for account in accounts:
                logger.debug(f"Searching for account: {account}")
                
                for i in range(1, stores.Count + 1):
                    store = stores.Item(i)
                    if account.upper() in store.DisplayName.upper():
                        logger.info(f"Found target store: {store.DisplayName} (Account: {account})")
                        return store
                
                logger.debug(f"Account '{account}' not found, trying next...")
            
            # If we get here, no accounts were found
            logger.error("No target accounts found. Available stores:")
            for i in range(1, stores.Count + 1):
                store = stores.Item(i)
                logger.error(f"  - {store.DisplayName}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding target store: {str(e)}")
            return None

    def _find_email_by_id(self, email_id: str) -> Optional[object]:
        """
        Find an email in Outlook by its ID using native Outlook identifiers.
        
        Args:
            email_id: The email ID to search for (VBA-generated format)
            
        Returns:
            Outlook mail item if found, None otherwise
        """
        if not self._initialize_com():
            logger.warning("COM interface not available for email search")
            return None
            
        try:
            # Get the email data to extract Outlook identifiers
            email_data = self.get_email_by_id(email_id)
            if not email_data:
                logger.warning(f"Email data not found for ID: {email_id}")
                return None
            
            # Extract Outlook native identifiers
            entry_id = email_data.get('entry_id', '').strip()
            message_id = email_data.get('message_id', '').strip()
            conversation_id = email_data.get('conversation_id', '').strip()
            
            logger.debug(f"Searching for email using native identifiers:")
            logger.debug(f"  EntryID: {entry_id[:50]}..." if entry_id else "  EntryID: (empty)")
            logger.debug(f"  MessageID: {message_id[:50]}..." if message_id else "  MessageID: (empty)")
            logger.debug(f"  ConversationID: {conversation_id[:20]}..." if conversation_id else "  ConversationID: (empty)")
            
            # Method 1: Try GetItemFromID with EntryID (most direct approach)
            if entry_id:
                try:
                    logger.debug("Attempting direct EntryID lookup...")
                    item = self._namespace.GetItemFromID(entry_id)
                    if item:
                        logger.info(f"Found email using EntryID: {email_data.get('subject', 'N/A')[:30]}...")
                        return item
                except Exception as e:
                    logger.debug(f"EntryID lookup failed: {str(e)}")
            
            # Method 2: Search using AdvancedSearch with MessageID
            if message_id:
                try:
                    logger.debug("Attempting MessageID search...")
                    # Look for the email using fallback account logic
                    target_store = self._find_target_store_with_fallback()
                    
                    if target_store:
                        # Get inbox folder
                        root_folder = target_store.GetRootFolder()
                        inbox = None
                        
                        for i in range(1, root_folder.Folders.Count + 1):
                            folder = root_folder.Folders.Item(i)
                            if folder.Name.lower() == "inbox":
                                inbox = folder
                                break
                        
                        if inbox:
                            # Search through recent emails by MessageID
                            items = inbox.Items
                            search_limit = min(items.Count, 500)
                            
                            for i in range(1, search_limit + 1):
                                try:
                                    item = items.Item(i)
                                    if hasattr(item, 'PropertyAccessor'):
                                        item_msg_id = item.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x1035001E")
                                        if item_msg_id and item_msg_id.strip() == message_id:
                                            logger.info(f"Found email using MessageID: {email_data.get('subject', 'N/A')[:30]}...")
                                            return item
                                except Exception:
                                    continue
                except Exception as e:
                    logger.debug(f"MessageID search failed: {str(e)}")
            
            # Method 3: Fallback to content-based search
            logger.debug("Falling back to content-based search...")
            return self._find_email_by_content(email_data)
            
        except Exception as e:
            logger.error(f"Error finding email by ID {email_id}: {str(e)}")
            return None

    def _find_email_by_content(self, email_data: Dict) -> Optional[object]:
        """
        Fallback method to find email by content when native identifiers fail.
        
        Args:
            email_data: Email data dictionary with subject, sender, etc.
            
        Returns:
            Outlook mail item if found, None otherwise
        """
        try:
            # Look for the email using fallback account logic
            target_store = self._find_target_store_with_fallback()
            
            if not target_store:
                logger.error("No target accounts found for content-based email search")
                return None
                
            # Get inbox folder
            root_folder = target_store.GetRootFolder()
            inbox = None
            
            for i in range(1, root_folder.Folders.Count + 1):
                folder = root_folder.Folders.Item(i)
                if folder.Name.lower() == "inbox":
                    inbox = folder
                    break
                    
            if not inbox:
                logger.error("Inbox folder not found")
                return None
            
            # Extract search criteria from email data
            email_subject = email_data.get('subject', '').strip()
            email_sender = email_data.get('sender_email', '').strip()
            email_received_time = email_data.get('received_time', '')
            email_size = email_data.get('size', 0)
            
            logger.debug(f"Content search for subject: '{email_subject[:50]}...', sender: '{email_sender}'")
            
            # Search through inbox items with multiple criteria
            items = inbox.Items
            found_candidates = []
            
            # Limit search to recent emails to improve performance
            search_limit = min(items.Count, 200)  # Reduced limit for fallback
            logger.debug(f"Searching through {search_limit} recent emails")
            
            for i in range(1, search_limit + 1):
                try:
                    item = items.Item(i)
                    
                    # Skip non-mail items
                    if not hasattr(item, 'Subject') or not hasattr(item, 'SenderEmailAddress'):
                        continue
                    
                    # Primary match: subject and sender
                    subject_match = item.Subject and item.Subject.strip() == email_subject
                    sender_match = item.SenderEmailAddress and item.SenderEmailAddress.strip().lower() == email_sender.lower()
                    
                    if subject_match and sender_match:
                        # Additional verification by size if available
                        if email_size > 0 and hasattr(item, 'Size'):
                            size_diff = abs(item.Size - email_size)
                            size_match = size_diff <= (email_size * 0.1)
                        else:
                            size_match = True
                        
                        if size_match:
                            logger.debug(f"Found content match for email: {email_subject[:30]}...")
                            return item
                        else:
                            # Store as candidate if subject and sender match but size doesn't
                            found_candidates.append((item, f"size_mismatch: {item.Size} vs {email_size}"))
                            
                except Exception as e:
                    logger.debug(f"Error checking email item {i}: {str(e)}")
                    continue
            
            # If no exact match, try the best candidate
            if found_candidates:
                best_candidate, match_info = found_candidates[0]
                logger.warning(f"No exact match found, using best candidate: {match_info}")
                return best_candidate
                    
            logger.warning(f"Email not found using content search")
            return None
            
        except Exception as e:
            logger.error(f"Error in content-based email search: {str(e)}")
            return None

    def delete_email(self, email_id: str) -> bool:
        """
        Delete a specific email using COM interface.
        
        Args:
            email_id: Email ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            email_item = self._find_email_by_id(email_id)
            if not email_item:
                logger.error(f"Cannot delete email - not found: {email_id}")
                return False
                
            # Delete the email
            email_item.Delete()
            logger.info(f"Email deleted successfully: {email_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting email {email_id}: {str(e)}")
            return False

    def mark_email_read(self, email_id: str, read: bool = True) -> bool:
        """
        Mark an email as read or unread using COM interface.
        
        Args:
            email_id: Email ID to mark
            read: True to mark as read, False to mark as unread
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            email_item = self._find_email_by_id(email_id)
            if not email_item:
                logger.error(f"Cannot mark email - not found: {email_id}")
                return False
                
            # Set unread status (UnRead=False means read, UnRead=True means unread)
            email_item.UnRead = not read
            email_item.Save()
            
            status = "read" if read else "unread"
            logger.info(f"Email marked as {status} successfully: {email_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking email {email_id} as {'read' if read else 'unread'}: {str(e)}")
            return False

    def delete_multiple_emails(self, email_ids: List[str]) -> Tuple[int, List[str]]:
        """
        Delete multiple emails using COM interface.
        
        Args:
            email_ids: List of email IDs to delete
            
        Returns:
            Tuple[int, List[str]]: (success_count, failed_ids)
        """
        success_count = 0
        failed_ids = []
        
        for email_id in email_ids:
            if self.delete_email(email_id):
                success_count += 1
            else:
                failed_ids.append(email_id)
                
        logger.info(f"Bulk delete completed: {success_count}/{len(email_ids)} successful")
        return success_count, failed_ids

    def mark_multiple_emails_read(self, email_ids: List[str], read: bool = True) -> Tuple[int, List[str]]:
        """
        Mark multiple emails as read or unread using COM interface.
        
        Args:
            email_ids: List of email IDs to mark
            read: True to mark as read, False to mark as unread
            
        Returns:
            Tuple[int, List[str]]: (success_count, failed_ids)
        """
        success_count = 0
        failed_ids = []
        
        for email_id in email_ids:
            if self.mark_email_read(email_id, read):
                success_count += 1
            else:
                failed_ids.append(email_id)
                
        status = "read" if read else "unread"
        logger.info(f"Bulk mark as {status} completed: {success_count}/{len(email_ids)} successful")
        return success_count, failed_ids

    def is_com_available(self) -> bool:
        """
        Check if COM interface is available and functional.
        
        Returns:
            bool: True if COM interface can be initialized
        """
        return COM_AVAILABLE and self._initialize_com()

    def get_com_status(self) -> Dict:
        """
        Get COM interface status information.
        
        Returns:
            Dict: Status information about COM interface
        """
        if not COM_AVAILABLE:
            return {
                'available': False,
                'message': 'COM interface not available (pywin32 not installed)',
                'initialized': False
            }
            
        if self._initialize_com():
            try:
                version = getattr(self._outlook_app, 'Version', 'Unknown')
                return {
                    'available': True,
                    'initialized': True,
                    'message': f'COM interface ready (Outlook {version})',
                    'outlook_version': version
                }
            except Exception as e:
                return {
                    'available': True,
                    'initialized': False,
                    'message': f'COM interface error: {str(e)}'
                }
        else:
            return {
                'available': True,
                'initialized': False,
                'message': 'Failed to initialize COM interface'
            }

    def __del__(self):
        """Cleanup COM interface on object destruction."""
        self._cleanup_com()

    def get_emails_data(self) -> Dict:
        """
        Read and return emails data from VBA JSON files (multiple folder files).
        
        Returns:
            Dict: Consolidated email data structure from all folders
        """
        try:
            # Check if we have the new multi-file structure (scan for emails_*.json files)
            folder_files = list(self.base_path.glob("emails_*.json"))
            
            if folder_files:
                return self._get_emails_from_multiple_files()
            else:
                # Fallback to single file (backward compatibility)
                return self._get_emails_from_single_file()
                
        except Exception as e:
            logger.error(f"Error reading emails data: {str(e)}")
            return self._get_empty_data_structure()

    def _get_emails_from_multiple_files(self) -> Dict:
        """
        Read emails from multiple folder-specific JSON files.
        
        Returns:
            Dict: Consolidated email data structure
        """
        try:
            # Scan for all emails_*.json files
            folder_files = list(self.base_path.glob("emails_*.json"))
            
            # Consolidate emails from all folder files
            all_emails = []
            folder_counts = {}
            latest_timestamp = None
            
            for folder_file in folder_files:
                filename = folder_file.name
                
                # Extract folder name from filename (emails_inbox.json -> inbox)
                folder_name = filename[7:-5]  # Remove "emails_" prefix and ".json" suffix
                folder_name = folder_name.replace('_', ' ').title()  # Convert to readable name
                
                # Try multiple encodings to handle Windows-generated files
                encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin-1']
                folder_data = None
                
                for encoding in encodings:
                    try:
                        with open(folder_file, 'r', encoding=encoding) as f:
                            folder_data = json.load(f)
                        logger.debug(f"Successfully read {filename} with encoding: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error in {filename} with encoding {encoding}: {str(e)}")
                        continue
                
                if folder_data is None:
                    logger.error(f"Failed to read {filename} with any encoding")
                    continue
                
                # Use folder_name from JSON data if available, otherwise use extracted name
                json_folder_name = folder_data.get('folder_name', folder_name)
                
                # Add emails from this folder
                folder_emails = folder_data.get('emails', [])
                folder_counts[json_folder_name] = len(folder_emails)
                
                # Add unique IDs to emails if not present
                for i, email in enumerate(folder_emails):
                    if 'id' not in email:
                        # Generate unique ID based on index and content hash
                        email_hash = hashlib.md5(
                            f"{email.get('subject', '')}{email.get('sender_email', '')}{email.get('received_time', '')}".encode()
                        ).hexdigest()[:8]
                        email['id'] = f"vba_{len(all_emails)+i+1}_{email_hash}"
                
                all_emails.extend(folder_emails)
                
                # Track latest timestamp
                file_timestamp = folder_data.get('timestamp', '')
                if not latest_timestamp or file_timestamp > latest_timestamp:
                    latest_timestamp = file_timestamp
                
                logger.debug(f"Loaded {len(folder_emails)} emails from {json_folder_name} folder")
            
            # Create consolidated data structure
            consolidated_data = {
                'timestamp': latest_timestamp or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'folder_name': 'All Folders',
                'folder_path': '/All',
                'total_items': len(all_emails),
                'emails': all_emails,
                'extracted_count': len(all_emails),
                'folder_counts': folder_counts,
                'source': 'multi_file'
            }
            
            logger.debug(f"Consolidated {len(all_emails)} emails from {len(folder_counts)} folders")
            return consolidated_data
            
        except Exception as e:
            logger.error(f"Error reading emails from multiple files: {str(e)}")
            return self._get_empty_data_structure()

    def _get_emails_from_single_file(self) -> Dict:
        """
        Read emails from single JSON file (backward compatibility).
        
        Returns:
            Dict: Email data structure from single file
        """
        try:
            if not self.emails_file.exists():
                logger.warning(f"Emails file not found: {self.emails_file}")
                return self._get_empty_data_structure()
            
            # Try multiple encodings to handle Windows-generated files
            encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin-1']
            data = None
            
            for encoding in encodings:
                try:
                    with open(self.emails_file, 'r', encoding=encoding) as f:
                        data = json.load(f)
                    logger.debug(f"Successfully read file with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error with encoding {encoding}: {str(e)}")
                    continue
            
            if data is None:
                logger.error("Failed to read file with any encoding")
                return self._get_empty_data_structure()
                
            # Add unique IDs to emails if not present
            for i, email in enumerate(data.get('emails', [])):
                if 'id' not in email:
                    # Generate unique ID based on index and content hash
                    email_hash = hashlib.md5(
                        f"{email.get('subject', '')}{email.get('sender_email', '')}{email.get('received_time', '')}".encode()
                    ).hexdigest()[:8]
                    email['id'] = f"vba_{i+1}_{email_hash}"
            
            # Add source indicator
            data['source'] = 'single_file'
            
            logger.debug(f"Loaded {len(data.get('emails', []))} emails from single JSON file")
            return data
            
        except Exception as e:
            logger.error(f"Error reading single file emails data: {str(e)}")
            return self._get_empty_data_structure()

    def get_emails_list(self, 
                       page: int = 1, 
                       per_page: int = 25,
                       search: str = None,
                       filter_unread: bool = None,
                       filter_important: bool = None,
                       filter_attachments: bool = None,
                       filter_folder: str = None,
                       sort_by: str = 'received_time',
                       sort_order: str = 'desc') -> Tuple[List[Dict], Dict]:
        """
        Get paginated and filtered list of emails.
        
        Args:
            page: Page number (1-based)
            per_page: Number of emails per page
            search: Search query for sender, subject, or body
            filter_unread: Filter for unread emails only
            filter_important: Filter for important emails only
            filter_attachments: Filter for emails with attachments
            sort_by: Field to sort by
            sort_order: 'asc' or 'desc'
            
        Returns:
            Tuple[List[Dict], Dict]: (emails_list, pagination_info)
        """
        try:
            data = self.get_emails_data()
            emails = data.get('emails', [])
            
            # Apply filters
            filtered_emails = self._apply_filters(
                emails, search, filter_unread, filter_important, filter_attachments, filter_folder
            )
            
            # Apply sorting
            sorted_emails = self._apply_sorting(filtered_emails, sort_by, sort_order)
            
            # Apply pagination
            total_count = len(sorted_emails)
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            paginated_emails = sorted_emails[start_index:end_index]
            
            # Prepare pagination info
            total_pages = (total_count + per_page - 1) // per_page
            pagination_info = {
                'current_page': page,
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_previous': page > 1,
                'has_next': page < total_pages,
                'start_index': start_index + 1 if total_count > 0 else 0,
                'end_index': min(end_index, total_count),
                'page_range': list(range(max(1, page - 2), min(total_pages + 1, page + 3)))
            }
            
            logger.debug(f"Returning {len(paginated_emails)} emails (page {page}/{pagination_info['total_pages']})")
            return paginated_emails, pagination_info
            
        except Exception as e:
            logger.error(f"Error getting emails list: {str(e)}")
            return [], {
                'current_page': 1, 
                'per_page': per_page, 
                'total_count': 0, 
                'total_pages': 0,
                'has_previous': False,
                'has_next': False,
                'start_index': 0,
                'end_index': 0,
                'page_range': []
            }

    def get_email_by_id(self, email_id: str) -> Optional[Dict]:
        """
        Get a specific email by its ID.
        
        Args:
            email_id: Email ID to retrieve
            
        Returns:
            Dict or None: Email data if found, None otherwise
        """
        try:
            data = self.get_emails_data()
            emails = data.get('emails', [])
            
            for email in emails:
                if email.get('id') == email_id:
                    return email
                    
            logger.warning(f"Email not found with ID: {email_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting email by ID {email_id}: {str(e)}")
            return None

    def get_folder_stats(self) -> Dict:
        """
        Get statistics about the email folder.
        
        Returns:
            Dict: Folder statistics
        """
        try:
            data = self.get_emails_data()
            emails = data.get('emails', [])
            
            # Use folder_counts from data if available (multi-file structure)
            folder_counts = data.get('folder_counts', {})
            
            # If not available, calculate from emails (single-file structure)
            if not folder_counts:
                for email in emails:
                    folder = email.get('folder', 'Inbox')
                    folder_counts[folder] = folder_counts.get(folder, 0) + 1
            
            stats = {
                'total_emails': len(emails),
                'unread_emails': sum(1 for email in emails if email.get('unread', False)),
                'important_emails': sum(1 for email in emails if email.get('importance', 0) > 1),
                'emails_with_attachments': sum(1 for email in emails if email.get('attachments', [])),
                'last_updated': data.get('timestamp', 'Never'),
                'folder_name': data.get('folder_name', 'All Folders'),
                'folder_counts': folder_counts,
                'source': data.get('source', 'unknown')
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting folder stats: {str(e)}")
            return {'total_emails': 0, 'unread_emails': 0, 'important_emails': 0, 'emails_with_attachments': 0, 'folder_counts': {}, 'source': 'error'}

    def _apply_filters(self, emails: List[Dict], search: str, filter_unread: bool, 
                      filter_important: bool, filter_attachments: bool, filter_folder: str) -> List[Dict]:
        """Apply filters to email list."""
        filtered_emails = emails.copy()
        
        # Search filter
        if search:
            search_lower = search.lower()
            filtered_emails = [
                email for email in filtered_emails
                if (search_lower in email.get('subject', '').lower() or
                    search_lower in email.get('sender_name', '').lower() or
                    search_lower in email.get('sender_email', '').lower() or
                    search_lower in email.get('body', '').lower())
            ]
        
        # Unread filter
        if filter_unread:
            filtered_emails = [email for email in filtered_emails if email.get('unread', False)]
        
        # Important filter
        if filter_important:
            filtered_emails = [email for email in filtered_emails if email.get('importance', 0) > 1]
        
        # Attachments filter
        if filter_attachments:
            filtered_emails = [email for email in filtered_emails if email.get('attachments', [])]
        
        # Folder filter (handle both Outlook and Gmail folder names)
        if filter_folder:
            # Gmail folder name mapping
            folder_alternatives = {
                'sent items': ['sent items', 'sent mail'],
                'sent mail': ['sent items', 'sent mail'],
                'deleted items': ['deleted items', 'trash'],
                'trash': ['deleted items', 'trash']
            }
            
            filter_lower = filter_folder.lower()
            possible_names = folder_alternatives.get(filter_lower, [filter_lower])
            
            filtered_emails = [
                email for email in filtered_emails 
                if email.get('folder', '').lower() in possible_names
            ]
        
        return filtered_emails

    def _apply_sorting(self, emails: List[Dict], sort_by: str, sort_order: str) -> List[Dict]:
        """Apply sorting to email list."""
        reverse = sort_order == 'desc'
        
        if sort_by == 'received_time':
            return sorted(emails, key=lambda x: x.get('received_time', ''), reverse=reverse)
        elif sort_by == 'sender_name':
            return sorted(emails, key=lambda x: x.get('sender_name', '').lower(), reverse=reverse)
        elif sort_by == 'subject':
            return sorted(emails, key=lambda x: x.get('subject', '').lower(), reverse=reverse)
        elif sort_by == 'size':
            return sorted(emails, key=lambda x: x.get('size', 0), reverse=reverse)
        else:
            return emails

    def _get_empty_data_structure(self) -> Dict:
        """Return empty data structure when no emails are available."""
        return {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'folder_name': 'Inbox',
            'folder_path': '/Inbox',
            'total_items': 0,
            'emails': [],
            'extracted_count': 0
        }

    def get_attachment_path(self, email_id: str, filename: str) -> Optional[str]:
        """
        Get the full path to an email attachment.
        
        Args:
            email_id: Email ID
            filename: Attachment filename
            
        Returns:
            str or None: Full path to attachment if it exists
        """
        try:
            email = self.get_email_by_id(email_id)
            if not email:
                return None
                
            # Look for attachment in email data
            for attachment in email.get('attachments', []):
                if attachment.get('filename') == filename:
                    filepath = attachment.get('filepath', '')
                    if filepath.startswith('data/'):
                        # Convert relative path to absolute
                        full_path = self.base_path / filepath
                        if full_path.exists():
                            return str(full_path)
                            
            return None
            
        except Exception as e:
            logger.error(f"Error getting attachment path: {str(e)}")
            return None

    def is_data_available(self) -> bool:
        """
        Check if VBA data is available.
        
        Returns:
            bool: True if data files exist and are readable
        """
        try:
            # Check for new multi-file structure first
            folder_files = list(self.base_path.glob("emails_*.json"))
            if folder_files:
                return True
                
            # Fallback to single file check
            return self.emails_file.exists() and self.emails_file.is_file()
        except Exception:
            return False

    def get_data_status(self) -> Dict:
        """
        Get status information about the data source.
        
        Returns:
            Dict: Status information
        """
        try:
            # Check for new multi-file structure first
            folder_files = list(self.base_path.glob("emails_*.json"))
            
            if folder_files:
                # Multi-file structure
                try:
                    total_files = len(folder_files)
                    total_size = sum(f.stat().st_size for f in folder_files)
                    
                    # Get the most recent modification time
                    latest_mtime = max(f.stat().st_mtime for f in folder_files)
                    last_modified = datetime.datetime.fromtimestamp(latest_mtime)
                    
                    return {
                        'available': True,
                        'message': f'VBA multi-file data available ({total_files} folder files)',
                        'path': str(self.base_path),
                        'last_modified': last_modified.strftime('%Y-%m-%d %H:%M:%S'),
                        'file_size': total_size,
                        'structure': 'multi_file',
                        'folder_files': total_files
                    }
                    
                except Exception as e:
                    return {
                        'available': False,
                        'message': f'Error reading multi-file structure: {str(e)}',
                        'path': str(self.base_path),
                        'last_modified': None,
                        'structure': 'multi_file_error'
                    }
            
            # Fallback to single file check
            elif self.emails_file.exists():
                stat = self.emails_file.stat()
                last_modified = datetime.datetime.fromtimestamp(stat.st_mtime)
                
                return {
                    'available': True,
                    'message': 'VBA single-file data available',
                    'path': str(self.emails_file),
                    'last_modified': last_modified.strftime('%Y-%m-%d %H:%M:%S'),
                    'file_size': stat.st_size,
                    'structure': 'single_file'
                }
            
            else:
                return {
                    'available': False,
                    'message': 'VBA data files not found. Please ensure the VBA extractor is running.',
                    'path': str(self.emails_file),
                    'last_modified': None,
                    'structure': 'none'
                }
            
        except Exception as e:
            return {
                'available': False,
                'message': f'Error checking data status: {str(e)}',
                'path': str(self.emails_file),
                'last_modified': None,
                'structure': 'error'
            }

    def test_account_fallback(self) -> Dict:
        """
        Test the account fallback logic.
        
        Returns:
            Dict: Test results showing which accounts were found
        """
        result = {
            'com_available': COM_AVAILABLE,
            'com_initialized': False,
            'accounts_found': [],
            'target_store': None,
            'available_stores': [],
            'test_successful': False
        }
        
        if not self._initialize_com():
            result['message'] = 'COM interface not available'
            return result
            
        result['com_initialized'] = True
        
        try:
            stores = self._namespace.Stores
            accounts = self._get_account_priority_list()
            
            # List all available stores
            for i in range(1, stores.Count + 1):
                store = stores.Item(i)
                result['available_stores'].append(store.DisplayName)
            
            # Check which target accounts are available
            for account in accounts:
                for i in range(1, stores.Count + 1):
                    store = stores.Item(i)
                    if account.upper() in store.DisplayName.upper():
                        result['accounts_found'].append({
                            'account': account,
                            'store_name': store.DisplayName
                        })
                        break
            
            # Test the fallback logic
            target_store = self._find_target_store_with_fallback()
            if target_store:
                result['target_store'] = target_store.DisplayName
                result['test_successful'] = True
                result['message'] = f'Fallback logic successful - found {target_store.DisplayName}'
            else:
                result['message'] = 'Fallback logic failed - no accounts found'
                
        except Exception as e:
            result['message'] = f'Error testing fallback logic: {str(e)}'
            
        return result

    def debug_email_data(self, email_id: str) -> Dict:
        """
        Debug method to show email data structure and COM search details.
        
        Args:
            email_id: The VBA-generated email ID to debug
            
        Returns:
            Dict: Debug information about the email and search process
        """
        debug_info = {
            'email_id': email_id,
            'json_email_found': False,
            'json_email_data': None,
            'com_available': COM_AVAILABLE,
            'com_initialized': False,
            'account_search': [],
            'search_criteria': {},
            'search_results': []
        }
        
        try:
            # Get email data from JSON
            email_data = self.get_email_by_id(email_id)
            if email_data:
                debug_info['json_email_found'] = True
                debug_info['json_email_data'] = {
                    'subject': email_data.get('subject', ''),
                    'sender_email': email_data.get('sender_email', ''),
                    'sender_name': email_data.get('sender_name', ''),
                    'received_time': email_data.get('received_time', ''),
                    'size': email_data.get('size', 0),
                    'hash': email_data.get('hash', ''),
                    'index': email_data.get('index', 0),
                    'entry_id': email_data.get('entry_id', ''),
                    'message_id': email_data.get('message_id', ''),
                    'conversation_id': email_data.get('conversation_id', ''),
                    'folder': email_data.get('folder', ''),
                    'folder_path': email_data.get('folder_path', '')
                }
                
                debug_info['search_criteria'] = {
                    'subject': email_data.get('subject', '').strip(),
                    'sender_email': email_data.get('sender_email', '').strip(),
                    'received_time': email_data.get('received_time', ''),
                    'size': email_data.get('size', 0)
                }
            
            # Test COM interface
            if self._initialize_com():
                debug_info['com_initialized'] = True
                
                # Test account finding
                stores = self._namespace.Stores
                accounts = self._get_account_priority_list()
                
                debug_info['available_stores'] = []
                for i in range(1, stores.Count + 1):
                    store = stores.Item(i)
                    debug_info['available_stores'].append(store.DisplayName)
                
                # Test account search
                for account in accounts:
                    account_info = {'account': account, 'found': False, 'store_name': None}
                    
                    for i in range(1, stores.Count + 1):
                        store = stores.Item(i)
                        if account.upper() in store.DisplayName.upper():
                            account_info['found'] = True
                            account_info['store_name'] = store.DisplayName
                            break
                    
                    debug_info['account_search'].append(account_info)
                
                # If we have email data, try searching for it
                if email_data and debug_info['account_search']:
                    target_store = self._find_target_store_with_fallback()
                    if target_store:
                        debug_info['target_store_found'] = target_store.DisplayName
                        
                        # Get inbox
                        root_folder = target_store.GetRootFolder()
                        inbox = None
                        
                        for i in range(1, root_folder.Folders.Count + 1):
                            folder = root_folder.Folders.Item(i)
                            if folder.Name.lower() == "inbox":
                                inbox = folder
                                break
                        
                        if inbox:
                            debug_info['inbox_found'] = True
                            debug_info['inbox_item_count'] = inbox.Items.Count
                            
                            # Search for matching emails (limited sample)
                            items = inbox.Items
                            search_limit = min(items.Count, 50)  # Small sample for debugging
                            
                            subject_to_find = email_data.get('subject', '').strip()
                            sender_to_find = email_data.get('sender_email', '').strip()
                            
                            for i in range(1, search_limit + 1):
                                try:
                                    item = items.Item(i)
                                    if hasattr(item, 'Subject') and hasattr(item, 'SenderEmailAddress'):
                                        item_subject = item.Subject.strip() if item.Subject else ''
                                        item_sender = item.SenderEmailAddress.strip() if item.SenderEmailAddress else ''
                                        
                                        match_info = {
                                            'index': i,
                                            'subject': item_subject[:50] + '...' if len(item_subject) > 50 else item_subject,
                                            'sender': item_sender,
                                            'subject_match': item_subject == subject_to_find,
                                            'sender_match': item_sender.lower() == sender_to_find.lower(),
                                            'both_match': item_subject == subject_to_find and item_sender.lower() == sender_to_find.lower()
                                        }
                                        
                                        if match_info['subject_match'] or match_info['sender_match'] or match_info['both_match']:
                                            debug_info['search_results'].append(match_info)
                                            
                                except Exception as e:
                                    continue
                        else:
                            debug_info['inbox_found'] = False
                    else:
                        debug_info['target_store_found'] = False
            
        except Exception as e:
            debug_info['error'] = str(e)
        
        return debug_info
    
    def get_inbox_emails(self, **kwargs) -> Tuple[List[Dict], Dict]:
        """Get emails from Inbox folder."""
        return self.get_emails_list(filter_folder='Inbox', **kwargs)
    
    def get_deleted_emails(self, **kwargs) -> Tuple[List[Dict], Dict]:
        """Get emails from Deleted Items folder."""
        return self.get_emails_list(filter_folder='Deleted Items', **kwargs)
    
    def get_sent_emails(self, **kwargs) -> Tuple[List[Dict], Dict]:
        """Get emails from Sent Items folder."""
        return self.get_emails_list(filter_folder='Sent Items', **kwargs)
    
    def get_draft_emails(self, **kwargs) -> Tuple[List[Dict], Dict]:
        """Get emails from Drafts folder."""
        return self.get_emails_list(filter_folder='Drafts', **kwargs)
    
    def get_outbox_emails(self, **kwargs) -> Tuple[List[Dict], Dict]:
        """Get emails from Outbox folder."""
        return self.get_emails_list(filter_folder='Outbox', **kwargs)