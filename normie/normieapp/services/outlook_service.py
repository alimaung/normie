import os
import json
import datetime
import logging
import time
from pathlib import Path
from django.conf import settings
from typing import Dict, List, Optional, Tuple
import hashlib
from logging.handlers import RotatingFileHandler
from datetime import timedelta
import re

# COM interface imports
try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False

# Configure file logging for OutlookService
def setup_outlook_logging():
    """
    Configure file logging for the OutlookService with rotation and proper formatting.
    Creates separate log files for different severity levels.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.BASE_DIR) / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Create outlook-specific log directory
    outlook_log_dir = log_dir / 'outlook'
    outlook_log_dir.mkdir(exist_ok=True)
    
    # Configure the logger
    logger = logging.getLogger('outlook_service')
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Main log file - all messages (with rotation)
    main_handler = RotatingFileHandler(
        outlook_log_dir / 'outlook_service.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    main_handler.setLevel(logging.DEBUG)
    main_handler.setFormatter(detailed_formatter)
    logger.addHandler(main_handler)
    
    # Error log file - only errors and critical messages
    error_handler = RotatingFileHandler(
        outlook_log_dir / 'outlook_errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    # COM operations log - specific to COM interface operations
    com_handler = RotatingFileHandler(
        outlook_log_dir / 'outlook_com.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    com_handler.setLevel(logging.INFO)
    com_handler.setFormatter(simple_formatter)
    
    # Add a filter to only log COM-related messages to this handler
    def com_filter(record):
        return 'COM' in record.getMessage() or 'outlook' in record.funcName.lower()
    
    com_handler.addFilter(com_filter)
    logger.addHandler(com_handler)
    
    # Email operations log - specific to email operations
    email_handler = RotatingFileHandler(
        outlook_log_dir / 'outlook_emails.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    email_handler.setLevel(logging.INFO)
    email_handler.setFormatter(simple_formatter)
    
    # Add a filter to only log email-related messages
    def email_filter(record):
        email_keywords = ['email', 'delete', 'mark', 'read', 'unread', 'search', 'find']
        return any(keyword in record.getMessage().lower() for keyword in email_keywords)
    
    email_handler.addFilter(email_filter)
    logger.addHandler(email_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

# Initialize the file logger
file_logger = setup_outlook_logging()

# Define logger at module level (for backward compatibility)
logger = file_logger

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
        logger.info("=== Initializing OutlookService ===")
        logger.debug(f"Service initialization started at {datetime.datetime.now()}")
        
        try:
            # Dynamic path based on current user
            username = os.environ.get('USERNAME', 'default')
            self.base_path = Path(f"C:/Users/{username}/Desktop/normie/outlook/analyze/mail")
            self.emails_file = self.base_path / "emails.json"
            self.data_folder = self.base_path / "data"
            
            logger.info(f"OutlookService configured for user: {username}")
            logger.debug(f"Base path: {self.base_path}")
            logger.debug(f"Emails file: {self.emails_file}")
            logger.debug(f"Data folder: {self.data_folder}")
            
            # COM interface attributes
            self._outlook_app = None
            self._namespace = None
            self._com_initialized = False
            
            logger.info(f"COM interface availability: {COM_AVAILABLE}")
            
            # Log path existence
            if self.base_path.exists():
                logger.info(f"Base path exists: {self.base_path}")
            else:
                logger.warning(f"Base path does not exist: {self.base_path}")
                
            if self.emails_file.exists():
                logger.info(f"Emails file found: {self.emails_file}")
                logger.debug(f"Emails file size: {self.emails_file.stat().st_size} bytes")
            else:
                logger.info(f"Emails file not found: {self.emails_file}")
            
            logger.info("OutlookService initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Error during OutlookService initialization: {str(e)}", exc_info=True)
            raise

    def _initialize_com(self) -> bool:
        """Initialize COM interface for Outlook operations."""
        logger.debug("=== COM Interface Initialization ===")
        
        if not COM_AVAILABLE:
            logger.warning("COM interface not available (pywin32 not installed)")
            logger.info("To enable COM functionality, install pywin32: pip install pywin32")
            return False
            
        if self._com_initialized:
            logger.debug("COM interface already initialized")
            return True
            
        try:
            logger.info("Starting COM interface initialization...")
            logger.debug("Calling pythoncom.CoInitialize()")
            pythoncom.CoInitialize()
            
            logger.debug("Dispatching Outlook.Application")
            self._outlook_app = win32com.client.Dispatch("Outlook.Application")
            
            logger.debug("Getting MAPI namespace")
            self._namespace = self._outlook_app.GetNamespace("MAPI")
            
            self._com_initialized = True
            logger.info("COM interface initialized successfully")
            
            # Log Outlook version if available
            try:
                version = getattr(self._outlook_app, 'Version', 'Unknown')
                logger.info(f"Connected to Outlook version: {version}")
            except Exception as ver_e:
                logger.debug(f"Could not retrieve Outlook version: {ver_e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize COM interface: {str(e)}", exc_info=True)
            logger.error("Make sure Outlook is installed and you have proper permissions")
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

    def _update_json_files_read_status(self, email_id: str, read: bool) -> bool:
        """
        Update the read/unread status in JSON files for a specific email.
        
        Args:
            email_id: Email ID to update
            read: True to mark as read, False to mark as unread
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if we have multi-file structure
            folder_files = list(self.base_path.glob("emails_*.json"))
            
            if folder_files:
                return self._update_multifile_read_status(email_id, read, folder_files)
            else:
                return self._update_singlefile_read_status(email_id, read)
                
        except Exception as e:
            logger.error(f"Error updating JSON files read status for {email_id}: {str(e)}")
            return False

    def _update_multifile_read_status(self, email_id: str, read: bool, folder_files: List[Path]) -> bool:
        """Update read status in multi-file JSON structure."""
        updated_files = 0
        status = "read" if read else "unread"
        
        for folder_file in folder_files:
            try:
                # Read the file
                encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin-1']
                folder_data = None
                
                for encoding in encodings:
                    try:
                        with open(folder_file, 'r', encoding=encoding) as f:
                            folder_data = json.load(f)
                        break
                    except UnicodeDecodeError:
                        continue
                    except json.JSONDecodeError:
                        continue
                
                if folder_data is None:
                    logger.warning(f"Could not read {folder_file.name}")
                    continue
                
                # Look for the email in this file
                emails = folder_data.get('emails', [])
                email_found = False
                
                for email in emails:
                    # Try multiple ways to match the email ID
                    if (email.get('id') == email_id or 
                        email.get('entry_id') == email_id or 
                        email.get('hash') == email_id):
                        # Update the read status
                        email['unread'] = not read  # unread=True means unread, unread=False means read
                        email_found = True
                        logger.debug(f"Updated email {email_id} to {status} in {folder_file.name}")
                        break
                
                if email_found:
                    # Update timestamp
                    folder_data['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Write back to file
                    with open(folder_file, 'w', encoding='utf-8') as f:
                        json.dump(folder_data, f, indent=2, ensure_ascii=False)
                    
                    updated_files += 1
                    logger.info(f"📝 Updated {folder_file.name} - marked email as {status}")
                    break  # Email found, no need to check other files
                    
            except Exception as e:
                logger.error(f"Error updating {folder_file.name}: {str(e)}")
                continue
        
        if updated_files > 0:
            logger.info(f"✅ Successfully updated read status in {updated_files} JSON file(s)")
            return True
        else:
            logger.warning(f"⚠️ Email {email_id} not found in any JSON files for read status update")
            return False

    def _update_singlefile_read_status(self, email_id: str, read: bool) -> bool:
        """Update read status in single-file JSON structure."""
        try:
            if not self.emails_file.exists():
                logger.warning(f"Emails file not found: {self.emails_file}")
                return False
            
            # Read the file
            encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin-1']
            data = None
            
            for encoding in encodings:
                try:
                    with open(self.emails_file, 'r', encoding=encoding) as f:
                        data = json.load(f)
                    break
                except UnicodeDecodeError:
                    continue
                except json.JSONDecodeError:
                    continue
            
            if data is None:
                logger.error("Failed to read emails file")
                return False
            
            # Look for the email
            emails = data.get('emails', [])
            email_found = False
            status = "read" if read else "unread"
            
            for email in emails:
                # Try multiple ways to match the email ID
                if (email.get('id') == email_id or 
                    email.get('entry_id') == email_id or 
                    email.get('hash') == email_id):
                    # Update the read status
                    email['unread'] = not read  # unread=True means unread, unread=False means read
                    email_found = True
                    logger.debug(f"Updated email {email_id} to {status} in single file")
                    break
            
            if email_found:
                # Update timestamp
                data['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Write back to file
                with open(self.emails_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ Successfully updated single file - marked email as {status}")
                return True
            else:
                logger.warning(f"⚠️ Email {email_id} not found in single file for read status update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating single file read status: {str(e)}")
            return False

    def _remove_email_from_json_files(self, email_id: str) -> bool:
        """
        Remove an email from JSON files after successful deletion.
        
        Args:
            email_id: Email ID to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if we have multi-file structure
            folder_files = list(self.base_path.glob("emails_*.json"))
            
            if folder_files:
                return self._remove_email_from_multifiles(email_id, folder_files)
            else:
                return self._remove_email_from_singlefile(email_id)
                
        except Exception as e:
            logger.error(f"Error removing email from JSON files {email_id}: {str(e)}")
            return False

    def _remove_email_from_multifiles(self, email_id: str, folder_files: List[Path]) -> bool:
        """Remove email from multi-file JSON structure."""
        updated_files = 0
        
        for folder_file in folder_files:
            try:
                # Read the file
                encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin-1']
                folder_data = None
                
                for encoding in encodings:
                    try:
                        with open(folder_file, 'r', encoding=encoding) as f:
                            folder_data = json.load(f)
                        break
                    except UnicodeDecodeError:
                        continue
                    except json.JSONDecodeError:
                        continue
                
                if folder_data is None:
                    logger.warning(f"Could not read {folder_file.name}")
                    continue
                
                # Look for the email in this file
                emails = folder_data.get('emails', [])
                original_count = len(emails)
                
                # Remove the email - try multiple ID fields
                emails = [email for email in emails if not (
                    email.get('id') == email_id or 
                    email.get('entry_id') == email_id or 
                    email.get('hash') == email_id
                )]
                new_count = len(emails)
                
                if new_count < original_count:
                    # Email was found and removed
                    folder_data['emails'] = emails
                    folder_data['total_items'] = new_count
                    folder_data['extracted_count'] = new_count
                    folder_data['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Write back to file
                    with open(folder_file, 'w', encoding='utf-8') as f:
                        json.dump(folder_data, f, indent=2, ensure_ascii=False)
                    
                    updated_files += 1
                    logger.info(f"📝 Removed email from {folder_file.name} (count: {original_count} → {new_count})")
                    break  # Email found and removed, no need to check other files
                    
            except Exception as e:
                logger.error(f"Error updating {folder_file.name}: {str(e)}")
                continue
        
        if updated_files > 0:
            logger.info(f"✅ Successfully removed email from {updated_files} JSON file(s)")
            return True
        else:
            logger.warning(f"⚠️ Email {email_id} not found in any JSON files for removal")
            return False

    def _remove_email_from_singlefile(self, email_id: str) -> bool:
        """Remove email from single-file JSON structure."""
        try:
            if not self.emails_file.exists():
                logger.warning(f"Emails file not found: {self.emails_file}")
                return False
            
            # Read the file
            encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin-1']
            data = None
            
            for encoding in encodings:
                try:
                    with open(self.emails_file, 'r', encoding=encoding) as f:
                        data = json.load(f)
                    break
                except UnicodeDecodeError:
                    continue
                except json.JSONDecodeError:
                    continue
            
            if data is None:
                logger.error("Failed to read emails file")
                return False
            
            # Remove the email - try multiple ID fields  
            emails = data.get('emails', [])
            original_count = len(emails)
            
            emails = [email for email in emails if not (
                email.get('id') == email_id or 
                email.get('entry_id') == email_id or 
                email.get('hash') == email_id
            )]
            new_count = len(emails)
            
            if new_count < original_count:
                # Email was found and removed
                data['emails'] = emails
                data['total_items'] = new_count
                data['extracted_count'] = new_count
                data['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Write back to file
                with open(self.emails_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ Successfully removed email from single file (count: {original_count} → {new_count})")
                return True
            else:
                logger.warning(f"⚠️ Email {email_id} not found in single file for removal")
                return False
                
        except Exception as e:
            logger.error(f"Error removing email from single file: {str(e)}")
            return False

    def delete_email(self, email_id: str) -> bool:
        """
        Delete a specific email using COM interface and update JSON files.
        
        Args:
            email_id: Email ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"=== Attempting to delete email: {email_id} ===")
        
        try:
            # Get email data for logging
            email_data = self.get_email_by_id(email_id)
            if email_data:
                logger.info(f"Email to delete: '{email_data.get('subject', 'N/A')[:50]}...' from {email_data.get('sender_email', 'N/A')}")
            
            logger.debug("Searching for email item in Outlook")
            email_item = self._find_email_by_id(email_id)
            if not email_item:
                logger.error(f"Cannot delete email - not found in Outlook: {email_id}")
                logger.warning(f"Email exists in JSON data but not found in Outlook COM interface")
                return False
                
            # Delete the email from Outlook
            logger.debug("Executing delete operation via COM interface")
            email_item.Delete()
            logger.info(f"✅ Email deleted from Outlook successfully: {email_id}")
            
            # Update JSON files to remove the deleted email
            logger.debug("Updating JSON files to remove deleted email")
            json_updated = self._remove_email_from_json_files(email_id)
            
            if json_updated:
                logger.info(f"🔄 JSON files synchronized - email removed from data files")
            else:
                logger.warning(f"⚠️ JSON files not updated - email may still appear in listings until VBA refresh")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting email {email_id}: {str(e)}", exc_info=True)
            return False

    def mark_email_read(self, email_id: str, read: bool = True) -> bool:
        """
        Mark an email as read or unread using COM interface and update JSON files.
        
        Args:
            email_id: Email ID to mark
            read: True to mark as read, False to mark as unread
            
        Returns:
            bool: True if successful, False otherwise
        """
        status = "read" if read else "unread"
        logger.info(f"=== Attempting to mark email as {status}: {email_id} ===")
        
        try:
            # Get email data for logging
            email_data = self.get_email_by_id(email_id)
            if email_data:
                logger.info(f"Email to mark as {status}: '{email_data.get('subject', 'N/A')[:50]}...' from {email_data.get('sender_email', 'N/A')}")
                current_status = "unread" if email_data.get('unread', False) else "read"
                logger.debug(f"Current email status: {current_status}")
            
            logger.debug("Searching for email item in Outlook")
            email_item = self._find_email_by_id(email_id)
            if not email_item:
                logger.error(f"Cannot mark email - not found in Outlook: {email_id}")
                logger.warning(f"Email exists in JSON data but not found in Outlook COM interface")
                return False
                
            # Set unread status in Outlook (UnRead=False means read, UnRead=True means unread)
            logger.debug(f"Setting UnRead property to {not read}")
            email_item.UnRead = not read
            logger.debug("Saving email changes")
            email_item.Save()
            
            logger.info(f"✅ Email marked as {status} in Outlook successfully: {email_id}")
            
            # Update JSON files to reflect the read status change
            logger.debug("Updating JSON files to reflect read status change")
            json_updated = self._update_json_files_read_status(email_id, read)
            
            if json_updated:
                logger.info(f"🔄 JSON files synchronized - email status updated in data files")
            else:
                logger.warning(f"⚠️ JSON files not updated - email status may not reflect changes until VBA refresh")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error marking email {email_id} as {status}: {str(e)}", exc_info=True)
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

    def flag_email(self, email_id: str, flagged: bool = True) -> bool:
        """
        Flag or unflag an email using COM interface and update JSON files.
        
        Args:
            email_id: Email ID to flag/unflag
            flagged: True to flag the email, False to unflag
            
        Returns:
            bool: True if successful, False otherwise
        """
        status = "flagged" if flagged else "unflagged"
        logger.info(f"=== Attempting to {status} email: {email_id} ===")
        
        try:
            # Get email data for logging
            email_data = self.get_email_by_id(email_id)
            if email_data:
                logger.info(f"Email subject: {email_data.get('subject', 'Unknown')[:50]}...")
            
            # Try COM interface first (if available)
            com_success = False
            com_error = None
            
            try:
                com_success = self._flag_email_via_com(email_id, flagged)
            except Exception as e:
                com_error = str(e)
                logger.warning(f"COM interface failed: {com_error}")
            
            # Update JSON files regardless of COM result
            json_success = False
            json_error = None
            
            try:
                json_success = self._update_email_flag_in_json(email_id, flagged)
            except Exception as e:
                json_error = str(e)
                logger.error(f"JSON update failed: {json_error}")
            
            # Only succeed if BOTH COM and JSON operations work (to keep them in sync)
            if com_success and json_success:
                logger.info(f"✓ Email {status} successfully (COM + JSON in sync)")
                return True
            elif com_success and not json_success:
                logger.error(f"✗ COM succeeded but JSON failed - would cause sync issue! COM: ✓, JSON: {json_error}")
                # TODO: Could attempt to revert COM operation here if needed
                return False
            elif not com_success and json_success:
                logger.error(f"✗ JSON succeeded but COM failed - would cause sync issue! COM: {com_error}, JSON: ✓")
                # TODO: Could attempt to revert JSON operation here if needed
                return False
            else:
                logger.error(f"✗ Both COM and JSON failed - COM: {com_error}, JSON: {json_error}")
                return False
                
        except Exception as e:
            logger.error(f"Error in flag_email: {e}")
            return False

    def flag_multiple_emails(self, email_ids: list, flagged: bool = True) -> tuple:
        """
        Flag or unflag multiple emails.
        
        Args:
            email_ids: List of email IDs to flag/unflag
            flagged: True to flag the emails, False to unflag
            
        Returns:
            tuple: (success_count, failed_ids)
        """
        status = "flagged" if flagged else "unflagged"
        logger.info(f"=== Attempting to {status} {len(email_ids)} emails ===")
        
        success_count = 0
        failed_ids = []
        
        for email_id in email_ids:
            try:
                if self.flag_email(email_id, flagged):
                    success_count += 1
                    logger.info(f"  ✓ Email {email_id} {status}")
                else:
                    failed_ids.append(email_id)
                    logger.warning(f"  ✗ Failed to {status} email {email_id}")
            except Exception as e:
                failed_ids.append(email_id)
                logger.error(f"  ✗ Error with email {email_id}: {e}")
        
        logger.info(f"Batch flag operation complete: {success_count} successful, {len(failed_ids)} failed")
        return success_count, failed_ids

    def _flag_email_via_com(self, email_id: str, flagged: bool) -> bool:
        """
        Flag or unflag email using COM interface.
        
        Args:
            email_id: Email ID (EntryID)
            flagged: True to flag, False to unflag
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use centralized COM initialization
            if not self._initialize_com():
                logger.error("COM interface not available for flagging")
                return False
            
            # Get the mail item by EntryID
            mail_item = self._namespace.GetItemFromID(email_id)
            
            # Add a small delay to prevent COM timing issues
            time.sleep(0.1)
            
            if flagged:
                # Flag the email (use only supported properties)
                mail_item.FlagStatus = 2  # olFlagMarked
                logger.debug(f"COM: Flagged email using FlagStatus only")
            else:
                # Unflag the email
                mail_item.FlagStatus = 0  # olNoFlag
                logger.debug(f"COM: Unflagged email using FlagStatus")
            
            # Save the changes
            mail_item.Save()
            
            logger.info(f"✅ COM flag operation successful for email: {email_id[:20]}...")
            return True
            
        except Exception as e:
            logger.error(f"COM flag operation failed: {e}")
            return False

    def get_json_files(self) -> list:
        """
        Get list of all JSON email files.
        
        Returns:
            list: List of JSON file paths
        """
        json_files = []
        
        # Check for folder-specific files first
        folder_files = list(self.base_path.glob("emails_*.json"))
        if folder_files:
            json_files.extend([str(f) for f in folder_files])
        
        # Also check for single emails.json file
        if self.emails_file.exists():
            json_files.append(str(self.emails_file))
        
        return json_files

    def _repair_json_file(self, json_file_path: str) -> bool:
        """
        Attempt to repair a corrupted JSON file by fixing common syntax issues.
        
        Args:
            json_file_path: Path to the JSON file to repair
            
        Returns:
            bool: True if repair was successful, False otherwise
        """
        try:
            logger.info(f"Attempting to repair JSON file: {json_file_path}")
            
            # Read the raw content with encoding detection
            content = None
            encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(json_file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    logger.info(f"Read file with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                # Last resort - read with errors='ignore'
                with open(json_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                logger.warning(f"Read file with UTF-8 ignoring errors")
            
            # Common JSON repair operations
            original_content = content
            
            # Fix trailing commas in arrays and objects
            
            # Remove trailing commas before closing brackets/braces
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            
            # Fix incomplete objects by adding closing braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces > close_braces:
                content += '}' * (open_braces - close_braces)
            
            # Fix incomplete arrays by adding closing brackets
            open_brackets = content.count('[')
            close_brackets = content.count(']')
            if open_brackets > close_brackets:
                content += ']' * (open_brackets - close_brackets)
            
            # Try to parse the repaired content
            try:
                json.loads(content)
                logger.info(f"JSON repair successful for {json_file_path}")
                
                # Create backup of original
                backup_path = json_file_path + '.corrupt_backup'
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # Write repaired content
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return True
                
            except json.JSONDecodeError:
                logger.warning(f"Could not repair JSON file: {json_file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error repairing JSON file {json_file_path}: {e}")
            return False

    def _update_email_flag_in_json(self, email_id: str, flagged: bool) -> bool:
        """
        Update email flag status in JSON files.
        
        Args:
            email_id: Email ID (hash)
            flagged: True if flagged, False if unflagged
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            success = False
            
            # Check all JSON files for this email
            for json_file in self.get_json_files():
                try:
                    # Try to read the JSON file with multiple encodings
                    data = None
                    encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin-1']
                    
                    for encoding in encodings:
                        try:
                            with open(json_file, 'r', encoding=encoding) as f:
                                data = json.load(f)
                            logger.debug(f"Successfully read {json_file} with encoding: {encoding}")
                            break
                        except UnicodeDecodeError:
                            continue
                        except json.JSONDecodeError as e:
                            if encoding == 'utf-8':  # Only try repair on first encoding
                                logger.warning(f"JSON file corrupted, attempting repair: {json_file}")
                                if self._repair_json_file(json_file):
                                    # Try reading again after repair
                                    try:
                                        with open(json_file, 'r', encoding='utf-8') as f:
                                            data = json.load(f)
                                        break
                                    except:
                                        continue
                            continue
                    
                    if data is None:
                        logger.error(f"Could not read JSON file with any encoding: {json_file}")
                        continue
                    
                    # Find and update the email
                    emails_updated = False
                    for email in data.get('emails', []):
                        # Match by hash, entry_id, or message_id
                        if (email.get('hash') == email_id or 
                            email.get('entry_id') == email_id or 
                            email.get('message_id') == email_id):
                            
                            # Update flag status (match Outlook native behavior)
                            email['flagged'] = flagged
                            email['flag_request'] = ""  # Always empty like Outlook native
                            email['flag_status'] = 2 if flagged else 0
                            
                            if flagged:
                                # Set due date to far future like Outlook native
                                email['flag_due_by'] = "4501-01-01 00:00:00"
                            else:
                                email['flag_due_by'] = ""
                            
                            emails_updated = True
                            logger.info(f"Updated flag status in {json_file}")
                    
                    # Save the updated JSON file
                    if emails_updated:
                        data['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        with open(json_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        
                        success = True
                        logger.info(f"Saved updated JSON file: {json_file}")
                
                except Exception as e:
                    logger.error(f"Error updating JSON file {json_file}: {e}")
                    continue
            
            return success
            
        except Exception as e:
            logger.error(f"Error in _update_email_flag_in_json: {e}")
            return False

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
        logger.debug("=== Loading emails data ===")
        
        try:
            # Check if we have the new multi-file structure (scan for emails_*.json files)
            folder_files = list(self.base_path.glob("emails_*.json"))
            
            if folder_files:
                logger.info(f"Found {len(folder_files)} folder-specific email files")
                logger.debug(f"Folder files: {[f.name for f in folder_files]}")
                return self._get_emails_from_multiple_files()
            else:
                # Fallback to single file (backward compatibility)
                logger.info("Using single email file structure (backward compatibility)")
                return self._get_emails_from_single_file()
                
        except Exception as e:
            logger.error(f"Error reading emails data: {str(e)}", exc_info=True)
            logger.warning("Returning empty data structure due to error")
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
                
                # Use entry_id as the unique identifier if available
                for i, email in enumerate(folder_emails):
                    if 'id' not in email:
                        # Use entry_id from JSON if available, otherwise fall back to hash
                        entry_id = email.get('entry_id')
                        if entry_id:
                            email['id'] = entry_id
                        else:
                            # Fallback: generate hash-based ID if entry_id is missing
                            email_hash = hashlib.md5(
                                f"{email.get('subject', '')}{email.get('sender_email', '')}{email.get('received_time', '')}".encode()
                            ).hexdigest()[:8]
                            email['id'] = f"hash_{email_hash}"
                
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
                
            # Use entry_id as the unique identifier if available
            for i, email in enumerate(data.get('emails', [])):
                if 'id' not in email:
                    # Use entry_id from JSON if available, otherwise fall back to hash
                    entry_id = email.get('entry_id')
                    if entry_id:
                        email['id'] = entry_id
                    else:
                        # Fallback: generate hash-based ID if entry_id is missing
                        email_hash = hashlib.md5(
                            f"{email.get('subject', '')}{email.get('sender_email', '')}{email.get('received_time', '')}".encode()
                        ).hexdigest()[:8]
                        email['id'] = f"hash_{email_hash}"
            
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
                'important_emails': sum(1 for email in emails if 
                                      email.get('importance', 0) > 1 or email.get('flagged', False)),
                'flagged_emails': sum(1 for email in emails if email.get('flagged', False)),
                'emails_with_attachments': sum(1 for email in emails if email.get('attachments', [])),
                'last_updated': data.get('timestamp', 'Never'),
                'folder_name': data.get('folder_name', 'All Folders'),
                'folder_counts': folder_counts,
                'source': data.get('source', 'unknown')
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting folder stats: {str(e)}")
            return {'total_emails': 0, 'unread_emails': 0, 'important_emails': 0, 'flagged_emails': 0, 'emails_with_attachments': 0, 'folder_counts': {}, 'source': 'error'}

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
        
        # Important/Flagged filter - check both importance (legacy) and flagged (new)
        if filter_important:
            filtered_emails = [email for email in filtered_emails if 
                             email.get('importance', 0) > 1 or email.get('flagged', False)]
        
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

    def send_email(self, to_recipients: List[str], subject: str, body: str, 
                   cc_recipients: List[str] = None, bcc_recipients: List[str] = None,
                   attachments: List[str] = None, body_format: str = 'text') -> bool:
        """
        Send an email using COM interface.
        
        Args:
            to_recipients: List of TO recipients
            subject: Email subject
            body: Email body content
            cc_recipients: List of CC recipients (optional)
            bcc_recipients: List of BCC recipients (optional)
            attachments: List of attachment file paths (optional)
            body_format: 'text' or 'html'
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"=== Attempting to send email: '{subject[:50]}...' to {len(to_recipients)} recipients ===")
        
        if not self._initialize_com():
            logger.error("COM interface not available for sending email")
            return False
            
        try:
            # Create a new mail item (0 = olMailItem)
            mail_item = self._outlook_app.CreateItem(0)
            
            # Set recipients
            mail_item.To = '; '.join(to_recipients)
            
            if cc_recipients:
                mail_item.CC = '; '.join(cc_recipients)
                
            if bcc_recipients:
                mail_item.BCC = '; '.join(bcc_recipients)
            
            # Set subject and body
            mail_item.Subject = subject
            
            if body_format.lower() == 'html':
                mail_item.HTMLBody = body
            else:
                mail_item.Body = body
            
            # Add attachments if provided - FAIL if ANY attachment fails
            if attachments:
                for attachment_path in attachments:
                    try:
                        # Normalize the path for Windows
                        normalized_path = os.path.normpath(os.path.abspath(attachment_path))
                        
                        # Check if file exists and is accessible
                        if os.path.exists(normalized_path) and os.path.isfile(normalized_path):
                            # Ensure file is not locked by waiting a moment
                            time.sleep(0.1)
                            
                            # Try to add the attachment
                            mail_item.Attachments.Add(normalized_path)
                            logger.debug(f"Added attachment: {normalized_path}")
                        else:
                            logger.error(f"❌ Attachment not found: {attachment_path}")
                            logger.debug(f"Normalized path: {normalized_path}")
                            logger.debug(f"Path exists: {os.path.exists(normalized_path)}")
                            logger.debug(f"Is file: {os.path.isfile(normalized_path) if os.path.exists(normalized_path) else 'N/A'}")
                            raise FileNotFoundError(f"Attachment not found: {os.path.basename(attachment_path)}")
                    except Exception as attachment_error:
                        logger.error(f"❌ Failed to add attachment {attachment_path}: {str(attachment_error)}")
                        # Re-raise the error to fail the entire email send
                        raise Exception(f"Failed to attach {os.path.basename(attachment_path)}: {str(attachment_error)}")
            
            # Send the email (only if all attachments were successful)
            mail_item.Send()
            
            logger.info(f"✅ Email sent successfully: '{subject[:30]}...' to {len(to_recipients)} recipients" + 
                       (f" with {len(attachments)} attachments" if attachments else ""))
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending email: {str(e)}", exc_info=True)
            return False

    def save_draft(self, to_recipients: List[str], subject: str, body: str,
                   cc_recipients: List[str] = None, bcc_recipients: List[str] = None,
                   attachments: List[str] = None, body_format: str = 'text') -> bool:
        """
        Save an email as draft using COM interface.
        
        Args:
            to_recipients: List of TO recipients
            subject: Email subject
            body: Email body content
            cc_recipients: List of CC recipients (optional)
            bcc_recipients: List of BCC recipients (optional)
            attachments: List of attachment file paths (optional)
            body_format: 'text' or 'html'
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"=== Attempting to save draft: '{subject[:50]}...' ===")
        
        if not self._initialize_com():
            logger.error("COM interface not available for saving draft")
            return False
            
        try:
            # Create a new mail item (0 = olMailItem)
            mail_item = self._outlook_app.CreateItem(0)
            
            # Set recipients
            if to_recipients:
                mail_item.To = '; '.join(to_recipients)
            
            if cc_recipients:
                mail_item.CC = '; '.join(cc_recipients)
                
            if bcc_recipients:
                mail_item.BCC = '; '.join(bcc_recipients)
            
            # Set subject and body
            mail_item.Subject = subject
            
            if body_format.lower() == 'html':
                mail_item.HTMLBody = body
            else:
                mail_item.Body = body
            
            # Add attachments if provided - FAIL if ANY attachment fails
            if attachments:
                for attachment_path in attachments:
                    try:
                        # Normalize the path for Windows
                        normalized_path = os.path.normpath(os.path.abspath(attachment_path))
                        
                        # Check if file exists and is accessible
                        if os.path.exists(normalized_path) and os.path.isfile(normalized_path):
                            # Ensure file is not locked by waiting a moment
                            time.sleep(0.1)
                            
                            # Try to add the attachment
                            mail_item.Attachments.Add(normalized_path)
                            logger.debug(f"Added attachment to draft: {normalized_path}")
                        else:
                            logger.error(f"❌ Attachment not found for draft: {attachment_path}")
                            logger.debug(f"Normalized path: {normalized_path}")
                            logger.debug(f"Path exists: {os.path.exists(normalized_path)}")
                            logger.debug(f"Is file: {os.path.isfile(normalized_path) if os.path.exists(normalized_path) else 'N/A'}")
                            raise FileNotFoundError(f"Attachment not found: {os.path.basename(attachment_path)}")
                    except Exception as attachment_error:
                        logger.error(f"❌ Failed to add attachment to draft {attachment_path}: {str(attachment_error)}")
                        # Re-raise the error to fail the entire draft save
                        raise Exception(f"Failed to attach {os.path.basename(attachment_path)}: {str(attachment_error)}")
            
            # Save as draft (don't send)
            mail_item.Save()
            
            logger.info(f"✅ Draft saved successfully: '{subject[:30]}...'" + 
                       (f" with {len(attachments)} attachments" if attachments else ""))
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving draft: {str(e)}", exc_info=True)
            return False

    def reply_to_email(self, email_id: str, body: str, reply_all: bool = False,
                       body_format: str = 'text') -> bool:
        """
        Reply to an email using COM interface.
        
        Args:
            email_id: ID of the email to reply to
            body: Reply body content
            reply_all: True to reply to all recipients, False for reply to sender only
            body_format: 'text' or 'html'
            
        Returns:
            bool: True if successful, False otherwise
        """
        action = "reply to all" if reply_all else "reply to"
        logger.info(f"=== Attempting to {action} email: {email_id} ===")
        
        try:
            # Find the original email
            original_email_item = self._find_email_by_id(email_id)
            if not original_email_item:
                logger.error(f"Cannot reply - original email not found: {email_id}")
                return False
            
            # Create reply
            if reply_all:
                reply_item = original_email_item.ReplyAll()
            else:
                reply_item = original_email_item.Reply()
            
            # Set body content
            if body_format.lower() == 'html':
                reply_item.HTMLBody = body + reply_item.HTMLBody  # Prepend new content
            else:
                reply_item.Body = body + "\n\n" + reply_item.Body  # Prepend new content
            
            # Send the reply
            reply_item.Send()
            
            logger.info(f"✅ Reply sent successfully to email: {email_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending reply to email {email_id}: {str(e)}", exc_info=True)
            return False

    def forward_email(self, email_id: str, to_recipients: List[str], body: str = "",
                      cc_recipients: List[str] = None, body_format: str = 'text') -> bool:
        """
        Forward an email using COM interface.
        
        Args:
            email_id: ID of the email to forward
            to_recipients: List of recipients to forward to
            body: Additional body content to add (optional)
            cc_recipients: List of CC recipients (optional)
            body_format: 'text' or 'html'
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"=== Attempting to forward email: {email_id} to {len(to_recipients)} recipients ===")
        
        try:
            # Find the original email
            original_email_item = self._find_email_by_id(email_id)
            if not original_email_item:
                logger.error(f"Cannot forward - original email not found: {email_id}")
                return False
            
            # Create forward
            forward_item = original_email_item.Forward()
            
            # Set recipients
            forward_item.To = '; '.join(to_recipients)
            
            if cc_recipients:
                forward_item.CC = '; '.join(cc_recipients)
            
            # Add custom body content if provided
            if body:
                if body_format.lower() == 'html':
                    forward_item.HTMLBody = body + "<br/><br/>" + forward_item.HTMLBody
                else:
                    forward_item.Body = body + "\n\n" + forward_item.Body
            
            # Send the forward
            forward_item.Send()
            
            logger.info(f"✅ Email forwarded successfully: {email_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error forwarding email {email_id}: {str(e)}", exc_info=True)
            return False