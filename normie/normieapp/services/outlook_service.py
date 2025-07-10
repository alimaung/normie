import os
import win32com.client
import pythoncom
import datetime
import base64
from django.conf import settings
from pathlib import Path
import json
import uuid
import logging
import traceback
import sys
import time

# Define logger at module level
logger = logging.getLogger(__name__)

# Set up debug logging to file
def setup_debug_logging():
    """Set up a separate debug log file for the Outlook service."""
    try:
        # Create logs directory if it doesn't exist
        log_dir = Path(settings.BASE_DIR) / 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up a file handler for debug logging
        debug_handler = logging.FileHandler(log_dir / 'outlook_debug.log')
        debug_handler.setLevel(logging.DEBUG)
        
        # Add formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        debug_handler.setFormatter(formatter)
        
        # Add handler to logger
        outlook_logger = logging.getLogger(__name__)
        outlook_logger.setLevel(logging.DEBUG)
        
        # Check if handler already exists to avoid duplicates
        handler_exists = False
        for handler in outlook_logger.handlers:
            if isinstance(handler, logging.FileHandler) and handler.baseFilename.endswith('outlook_debug.log'):
                handler_exists = True
                break
        
        if not handler_exists:
            outlook_logger.addHandler(debug_handler)
            
        return log_dir / 'outlook_debug.log'
    except Exception as e:
        print(f"Error setting up debug logging: {str(e)}")
        return None

# Set up debug logging
debug_log_path = setup_debug_logging()

class OutlookService:
    """
    Service for interacting with Microsoft Outlook via win32com.
    Provides email functionality for specific accounts.
    Uses hybrid approach: VBA files for content, COM for actions.
    """
    
    ALLOWED_ACCOUNTS = [
        'irm-standardisation-office@rolls-royce.com',
        'ali.maung@rolls-royce.com',  # Ali Maung's account (belongs to the IRM group)
        'microfilm.rollsroyce@outlook.com'  # Only for testing
    ]
    
    def __init__(self):
        """Initialize the Outlook service."""
        logger.debug("Initializing OutlookService")
        # Initialize COM in the current thread
        try:
            pythoncom.CoInitialize()
            logger.debug("COM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize COM: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
        
        # Store email cache directory
        self.cache_dir = Path(settings.BASE_DIR) / 'normieapp' / 'static' / 'normieapp' / 'data' / 'email_cache'
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.debug(f"Email cache directory: {self.cache_dir}")
        
        # Log debug file location
        if debug_log_path:
            logger.info(f"Debug logs are being written to: {debug_log_path}")
    
    def _get_outlook_application(self):
        """Get the Outlook application COM object."""
        logger.debug("Getting Outlook application object")
        try:
            app = win32com.client.Dispatch("Outlook.Application")
            logger.debug("Successfully got Outlook application")
            return app
        except Exception as e:
            logger.error(f"Failed to connect to Outlook: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise ConnectionError("Could not connect to Microsoft Outlook. Please ensure Outlook is installed and running.")
    
    def _get_namespace(self):
        """Get the MAPI namespace from Outlook."""
        logger.debug("Getting MAPI namespace")
        try:
            app = self._get_outlook_application()
            namespace = app.GetNamespace("MAPI")
            logger.debug("Successfully got MAPI namespace")
            return namespace
        except Exception as e:
            logger.error(f"Failed to get MAPI namespace: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise
    
    def get_emails(self, email_address, folder_type='inbox', limit=50, offset=0, search_term=None, category=None):
        """
        Get emails from the specified folder using hybrid approach.
        
        Args:
            email_address: The email address of the account
            folder_type: The type of folder to get emails from (inbox, drafts, sent)
            limit: Maximum number of emails to return
            offset: Number of emails to skip
            search_term: Optional search term to filter emails
            category: Optional category to filter emails
            
        Returns:
            List of email dictionaries
        """
        logger.debug(f"Getting emails for {email_address}, folder: {folder_type}, limit: {limit}, offset: {offset}, search: {search_term}, category: {category}")
        
        # Try VBA data first if it's fresh and we're requesting inbox
        if folder_type == 'inbox' and self._is_vba_data_fresh():
            logger.info("Using VBA data for email content")
            vba_emails = self._get_emails_from_vba(folder_type, limit, offset, search_term, category)
            if vba_emails:
                return vba_emails
            else:
                logger.warning("VBA data failed, falling back to COM")
        else:
            logger.debug(f"Using COM for emails (folder: {folder_type}, VBA fresh: {self._is_vba_data_fresh()})")
        
        # Fallback to COM (with restricted content)
        return self._get_emails_from_com(email_address, folder_type, limit, offset, search_term, category)
    
    def get_email(self, email_address, message_id):
        """
        Get a specific email by ID using hybrid approach.
        
        Args:
            email_address: The email address of the account
            message_id: The EntryID of the email (or VBA format ID)
            
        Returns:
            Dictionary with email details
        """
        logger.debug(f"Getting email: {message_id}")
        
        # Check if this is a VBA email ID
        if message_id.startswith('vba_') and self._is_vba_data_fresh():
            logger.info("Getting email from VBA data")
            vba_email = self._get_email_from_vba(message_id)
            if vba_email:
                return vba_email
            else:
                logger.warning("Email not found in VBA data, trying COM")
        
        # Fallback to COM
        return self._get_email_from_com(email_address, message_id)
    
    def delete_email(self, email_address, message_id):
        """
        Delete an email by its ID.
        
        Args:
            email_address: The email address of the account
            message_id: The EntryID of the email
            
        Returns:
            True if successful
        """
        try:
            namespace = self._get_namespace()
            item = namespace.GetItemFromID(message_id)
            item.Delete()
            logger.debug(f"Successfully deleted email: {message_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting email: {str(e)}")
            raise
    
    def mark_as_read(self, email_address, message_id):
        """
        Mark an email as read.
        
        Args:
            email_address: The email address of the account
            message_id: The EntryID of the email
            
        Returns:
            True if successful
        """
        try:
            namespace = self._get_namespace()
            item = namespace.GetItemFromID(message_id)
            if hasattr(item, 'UnRead') and item.UnRead:
                item.UnRead = False
                item.Save()
                logger.debug(f"Successfully marked email as read: {message_id}")
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {str(e)}")
            raise

    # VBA Integration Methods
    def _get_vba_data_path(self):
        """Get path to VBA-exported emails.json file."""
        username = os.environ.get('USERNAME', 'user')
        vba_path = Path(f"C:/Users/{username}/Desktop/normie/outlook/analyze/mail/emails.json")
        return vba_path
    
    def _is_vba_data_fresh(self, max_age_minutes=2):
        """Check if VBA data is recent enough to use."""
        vba_file = self._get_vba_data_path()
        if not vba_file.exists():
            logger.debug(f"VBA file does not exist: {vba_file}")
            return False
        
        file_age = time.time() - vba_file.stat().st_mtime
        is_fresh = file_age < (max_age_minutes * 60)
        logger.debug(f"VBA file age: {file_age:.1f} seconds, fresh: {is_fresh}")
        return is_fresh
    
    def _get_emails_from_vba(self, folder_type='inbox', limit=50, offset=0, search_term=None, category=None):
        """
        Get emails from VBA-exported JSON files.
        """
        logger.debug(f"Getting emails from VBA files: folder={folder_type}, limit={limit}, offset={offset}")
        
        vba_file = self._get_vba_data_path()
        
        try:
            with open(vba_file, 'r', encoding='utf-8') as f:
                vba_data = json.load(f)
            
            logger.debug(f"Loaded VBA data: {len(vba_data.get('emails', []))} emails")
            
            # Get emails from VBA data
            emails = vba_data.get('emails', [])
            
            # Convert VBA format to our expected format
            converted_emails = []
            for email in emails:
                try:
                    converted_email = self._convert_vba_email_format(email)
                    
                    # Apply search filter
                    if search_term:
                        search_lower = search_term.lower()
                        if not (search_lower in converted_email.get('subject', '').lower() or 
                               search_lower in converted_email.get('sender', '').lower() or 
                               search_lower in converted_email.get('body', '').lower()):
                            continue
                    
                    # Apply category filter
                    if category:
                        email_categories = converted_email.get('categories', [])
                        if isinstance(email_categories, str):
                            email_categories = [cat.strip() for cat in email_categories.split(',') if cat.strip()]
                        if category not in email_categories:
                            continue
                    
                    converted_emails.append(converted_email)
                    
                except Exception as e:
                    logger.warning(f"Error converting VBA email: {e}")
                    continue
            
            # Apply pagination
            total_emails = len(converted_emails)
            paginated_emails = converted_emails[offset:offset + limit]
            
            logger.debug(f"Returning {len(paginated_emails)} emails from VBA data (total: {total_emails})")
            return paginated_emails
            
        except Exception as e:
            logger.error(f"Error reading VBA emails: {e}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return []
    
    def _convert_vba_email_format(self, vba_email):
        """Convert VBA email format to our expected format."""
        # Extract attachment info
        attachments = []
        for attachment in vba_email.get('attachments', []):
            # Fix filepath escaping and convert to forward slashes
            filepath = attachment.get('filepath', '').replace('\\', '/')
            
            attachments.append({
                'name': attachment.get('filename', 'Unknown'),
                'filename': attachment.get('filename', 'Unknown'),  # Template expects this
                'size': attachment.get('size', 0),
                'id': len(attachments) + 1,
                'filepath': filepath,
                'path': filepath,  # Template expects this for download links
                'content_type': self._guess_content_type(attachment.get('filename', ''))  # Template expects this
            })
        
        # Parse recipients
        recipients = vba_email.get('recipients', [])
        to_list = []
        cc_list = []
        
        for recipient in recipients:
            if recipient.get('type') == 1:  # TO recipient
                to_list.append(recipient.get('address', ''))
            elif recipient.get('type') == 2:  # CC recipient
                cc_list.append(recipient.get('address', ''))
        
        # Convert categories
        categories = []
        vba_categories = vba_email.get('categories', '')
        if vba_categories:
            categories = [cat.strip() for cat in vba_categories.split(';') if cat.strip()]
        
        # Generate unique ID from VBA data
        email_id = f"vba_{vba_email.get('index', 0)}_{hash(vba_email.get('subject', '') + vba_email.get('received_time', ''))}"
        
        return {
            'id': email_id,
            'subject': vba_email.get('subject', '(No Subject)'),
            'sender': vba_email.get('sender_name', ''),
            'sender_email': vba_email.get('sender_email', ''),
            'to': '; '.join(to_list),
            'cc': '; '.join(cc_list),
            'received_time': vba_email.get('received_time', ''),
            'sent_time': vba_email.get('sent_on', ''),
            'has_attachments': len(attachments) > 0,
            'attachments': attachments,
            'body': vba_email.get('body', ''),
            'body_text': vba_email.get('body', ''),  # Template expects this
            'html_body': vba_email.get('html_body', ''),
            'body_html': vba_email.get('html_body', ''),  # Template expects this
            'unread': vba_email.get('unread', False),
            'importance': vba_email.get('importance', 1),
            'categories': categories,
            'preview': vba_email.get('body', '')[:200] + '...' if len(vba_email.get('body', '')) > 200 else vba_email.get('body', ''),
            'msg_file': vba_email.get('msg_file', '').replace('\\', '/'),  # Fix escape characters
            'source': 'vba'
        }
    
    def _guess_content_type(self, filename):
        """Guess content type from filename extension."""
        if not filename:
            return 'application/octet-stream'
        
        filename_lower = filename.lower()
        
        if filename_lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            return 'image/' + filename_lower.split('.')[-1]
        elif filename_lower.endswith('.pdf'):
            return 'application/pdf'
        elif filename_lower.endswith(('.doc', '.docx')):
            return 'application/msword'
        elif filename_lower.endswith(('.xls', '.xlsx')):
            return 'application/vnd.ms-excel'
        elif filename_lower.endswith(('.ppt', '.pptx')):
            return 'application/vnd.ms-powerpoint'
        elif filename_lower.endswith(('.zip', '.rar', '.7z')):
            return 'application/zip'
        elif filename_lower.endswith('.txt'):
            return 'text/plain'
        else:
            return 'application/octet-stream'
    
    def _get_email_from_vba(self, email_id):
        """Get a specific email by ID from VBA files."""
        logger.debug(f"Getting email from VBA files: {email_id}")
        
        vba_file = self._get_vba_data_path()
        
        try:
            with open(vba_file, 'r', encoding='utf-8') as f:
                vba_data = json.load(f)
            
            emails = vba_data.get('emails', [])
            
            for email in emails:
                converted_email = self._convert_vba_email_format(email)
                if converted_email['id'] == email_id:
                    logger.debug(f"Found email in VBA data: {converted_email['subject']}")
                    return converted_email
            
            logger.warning(f"Email not found in VBA data: {email_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error reading VBA email: {e}")
            return None
    
    # COM Fallback Methods (simplified)
    def _get_emails_from_com(self, email_address, folder_type='inbox', limit=50, offset=0, search_term=None, category=None):
        """Get emails from COM (fallback with restricted content)."""
        logger.debug(f"Getting emails via COM fallback for folder: {folder_type}")
        try:
            namespace = self._get_namespace()
            folder = namespace.GetDefaultFolder(6)  # Default to inbox
            
            items = folder.Items
            items.Sort("[ReceivedTime]", True)
            
            emails = []
            count = 0
            skipped = 0
            
            for item in items:
                if skipped < offset:
                    skipped += 1
                    continue
                
                if count >= limit:
                    break
                
                try:
                    email = self._extract_email_details(item)
                    emails.append(email)
                    count += 1
                except Exception as e:
                    logger.debug(f"Error processing email: {str(e)}")
                    continue
            
            logger.debug(f"Retrieved {len(emails)} emails from COM")
            return emails
            
        except Exception as e:
            logger.error(f"Error getting emails from COM: {str(e)}")
            return []
    
    def _extract_email_details(self, item):
        """Extract email details from Outlook item (with restrictions)."""
        try:
            # Note: Many fields will be restricted, but we can get basic info
            email = {
                'id': item.EntryID if hasattr(item, 'EntryID') else "",
                'subject': item.Subject if hasattr(item, 'Subject') else "(No Subject)",
                'sender': "(Restricted)",  # Corporate restriction
                'sender_email': "",
                'received_time': item.ReceivedTime.strftime('%Y-%m-%d %H:%M:%S') if hasattr(item, 'ReceivedTime') else "",
                'body': "(Restricted)",  # Corporate restriction
                'html_body': "",
                'unread': item.UnRead if hasattr(item, 'UnRead') else False,
                'has_attachments': False,
                'attachments': [],
                'categories': [],
                'preview': "Content restricted by corporate policy",
                'source': 'com'
            }
            return email
        except Exception as e:
            logger.error(f"Error extracting email details: {str(e)}")
            return {
                'id': "",
                'subject': "(Error)",
                'sender': "",
                'preview': "Error extracting email details",
                'source': 'com'
            }
    
    def _get_email_from_com(self, email_address, message_id):
        """Get a specific email by ID from COM."""
        try:
            namespace = self._get_namespace()
            item = namespace.GetItemFromID(message_id)
            return self._extract_email_details(item)
        except Exception as e:
            logger.error(f"Error getting email from COM: {str(e)}")
            raise

    def __del__(self):
        """Clean up COM resources."""
        try:
            pythoncom.CoUninitialize()
        except:
            pass