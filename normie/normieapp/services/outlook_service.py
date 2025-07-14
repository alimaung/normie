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

    def _find_email_by_id(self, email_id: str) -> Optional[object]:
        """
        Find an email in Outlook by its ID.
        
        Args:
            email_id: The email ID to search for
            
        Returns:
            Outlook mail item if found, None otherwise
        """
        if not self._initialize_com():
            return None
            
        try:
            # Get the email data to find additional identifiers
            email_data = self.get_email_by_id(email_id)
            if not email_data:
                logger.warning(f"Email data not found for ID: {email_id}")
                return None
            
            # Look for the email in the IRM-Standardisation-Office account
            target_account = "IRM-Standardisation-Office"
            stores = self._namespace.Stores
            
            target_store = None
            for i in range(1, stores.Count + 1):
                store = stores.Item(i)
                if target_account.upper() in store.DisplayName.upper():
                    target_store = store
                    break
            
            if not target_store:
                logger.error(f"Target account '{target_account}' not found")
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
            
            # Search for email by subject and sender
            email_subject = email_data.get('subject', '')
            email_sender = email_data.get('sender_email', '')
            email_received_time = email_data.get('received_time', '')
            
            # Search through inbox items
            items = inbox.Items
            for i in range(1, min(items.Count + 1, 500)):  # Limit search to recent 500 emails
                try:
                    item = items.Item(i)
                    
                    # Match by subject and sender
                    if (hasattr(item, 'Subject') and hasattr(item, 'SenderEmailAddress') and
                        item.Subject == email_subject and 
                        item.SenderEmailAddress == email_sender):
                        
                        # Additional verification by received time if available
                        if hasattr(item, 'ReceivedTime'):
                            item_time = item.ReceivedTime.strftime('%Y-%m-%d %H:%M:%S')
                            if email_received_time and item_time == email_received_time:
                                return item
                        else:
                            return item
                            
                except Exception as e:
                    logger.debug(f"Error checking item {i}: {str(e)}")
                    continue
                    
            logger.warning(f"Email not found in Outlook for ID: {email_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding email by ID {email_id}: {str(e)}")
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
        Read and return emails data from VBA JSON file.
        
        Returns:
            Dict: Email data structure or empty structure if file not found
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
                    
            logger.debug(f"Loaded {len(data.get('emails', []))} emails from JSON")
            return data
            
        except Exception as e:
            logger.error(f"Error reading emails data: {str(e)}")
            return self._get_empty_data_structure()

    def get_emails_list(self, 
                       page: int = 1, 
                       per_page: int = 25,
                       search: str = None,
                       filter_unread: bool = None,
                       filter_important: bool = None,
                       filter_attachments: bool = None,
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
                emails, search, filter_unread, filter_important, filter_attachments
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
            
            stats = {
                'total_emails': len(emails),
                'unread_emails': sum(1 for email in emails if email.get('unread', False)),
                'important_emails': sum(1 for email in emails if email.get('importance', 0) > 1),
                'emails_with_attachments': sum(1 for email in emails if email.get('attachments', [])),
                'last_updated': data.get('timestamp', 'Never'),
                'folder_name': data.get('folder_name', 'Inbox')
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting folder stats: {str(e)}")
            return {'total_emails': 0, 'unread_emails': 0, 'important_emails': 0, 'emails_with_attachments': 0}

    def _apply_filters(self, emails: List[Dict], search: str, filter_unread: bool, 
                      filter_important: bool, filter_attachments: bool) -> List[Dict]:
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
            bool: True if data file exists and is readable
        """
        try:
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
            if not self.is_data_available():
                return {
                    'available': False,
                    'message': 'VBA data file not found. Please ensure the VBA extractor is running.',
                    'path': str(self.emails_file),
                    'last_modified': None
                }
            
            stat = self.emails_file.stat()
            last_modified = datetime.datetime.fromtimestamp(stat.st_mtime)
            
            return {
                'available': True,
                'message': 'VBA data available',
                'path': str(self.emails_file),
                'last_modified': last_modified.strftime('%Y-%m-%d %H:%M:%S'),
                'file_size': stat.st_size
            }
            
        except Exception as e:
            return {
                'available': False,
                'message': f'Error checking data status: {str(e)}',
                'path': str(self.emails_file),
                'last_modified': None
            }