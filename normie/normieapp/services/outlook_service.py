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

logger = logging.getLogger(__name__)

class OutlookService:
    """
    Service for interacting with Microsoft Outlook via win32com.
    Provides email functionality for specific accounts.
    """
    
    ALLOWED_ACCOUNTS = [
        'irm-standardisation-office@rolls-royce.com',
        'microfilm.rollsroyce@outlook.com'  # Only for testing
    ]
    
    def __init__(self):
        """Initialize the Outlook service."""
        # Initialize COM in the current thread
        pythoncom.CoInitialize()
        
        # Store email cache directory
        self.cache_dir = Path(settings.BASE_DIR) / 'normieapp' / 'static' / 'normieapp' / 'data' / 'email_cache'
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_outlook_application(self):
        """Get the Outlook application COM object."""
        try:
            return win32com.client.Dispatch("Outlook.Application")
        except Exception as e:
            logger.error(f"Failed to connect to Outlook: {str(e)}")
            raise ConnectionError("Could not connect to Microsoft Outlook. Please ensure Outlook is installed and running.")
    
    def _get_namespace(self):
        """Get the MAPI namespace from Outlook."""
        app = self._get_outlook_application()
        return app.GetNamespace("MAPI")
    
    def _get_account(self, email_address):
        """
        Get the specific account object by email address.
        Only allows access to pre-approved email addresses.
        Falls back to testing email if primary email is not found.
        """
        if email_address not in self.ALLOWED_ACCOUNTS:
            raise ValueError(f"Access to email account '{email_address}' is not allowed.")
        
        namespace = self._get_namespace()
        
        # Try to find the account
        for account in namespace.Accounts:
            if account.SmtpAddress.lower() == email_address.lower():
                return account
        
        # If the requested account is the primary one and not found, try the testing account
        if email_address == self.ALLOWED_ACCOUNTS[0]:
            logger.warning(f"Primary email account '{email_address}' not found. Trying fallback account.")
            fallback_email = self.ALLOWED_ACCOUNTS[1]  # Use testing email as fallback
            
            for account in namespace.Accounts:
                if account.SmtpAddress.lower() == fallback_email.lower():
                    logger.info(f"Using fallback email account: {fallback_email}")
                    return account
        
        raise ValueError(f"Email account '{email_address}' not found in Outlook, and no fallback account is available.")
    
    def _get_folder(self, namespace, folder_type='inbox'):
        """
        Get the specified folder from Outlook.
        
        Args:
            namespace: The Outlook namespace
            folder_type: The type of folder to get (inbox, drafts, sent, deleted, junk, archive)
            
        Returns:
            The folder object
        """
        # Map folder types to Outlook constants
        folder_map = {
            'inbox': 6,      # olFolderInbox
            'drafts': 16,    # olFolderDrafts
            'sent': 5,       # olFolderSentMail
            'deleted': 3,    # olFolderDeletedItems
            'junk': 23,      # olFolderJunk
            'archive': 1000  # Custom value, will handle differently
        }
        
        try:
            if folder_type.lower() == 'archive':
                # Try to find the Archive folder by name
                try:
                    root_folders = namespace.Folders
                    for i in range(1, root_folders.Count + 1):
                        root_folder = root_folders.Item(i)
                        for j in range(1, root_folder.Folders.Count + 1):
                            folder = root_folder.Folders.Item(j)
                            if folder.Name.lower() == 'archive':
                                return folder
                    
                    # If not found, return inbox as fallback
                    return namespace.GetDefaultFolder(6)  # olFolderInbox
                except:
                    # If any error occurs, return inbox as fallback
                    return namespace.GetDefaultFolder(6)  # olFolderInbox
            else:
                # Get the folder using the mapped constant
                folder_constant = folder_map.get(folder_type.lower(), 6)  # Default to inbox
                return namespace.GetDefaultFolder(folder_constant)
        except Exception as e:
            logger.error(f"Error getting folder {folder_type}: {str(e)}")
            # Default to inbox if there's an error
            return namespace.GetDefaultFolder(6)  # olFolderInbox
    
    def get_inbox_folder(self, email_address):
        """Get the inbox folder for the specified account."""
        account = self._get_account(email_address)
        return account.DeliveryStore.GetDefaultFolder(6)  # 6 = olFolderInbox
    
    def get_sent_folder(self, email_address):
        """Get the sent items folder for the specified account."""
        account = self._get_account(email_address)
        return account.DeliveryStore.GetDefaultFolder(5)  # 5 = olFolderSentMail
    
    def get_drafts_folder(self, email_address):
        """Get the drafts folder for the specified account."""
        account = self._get_account(email_address)
        return account.DeliveryStore.GetDefaultFolder(16)  # 16 = olFolderDrafts
    
    def get_emails(self, email_address, folder_type='inbox', limit=50, offset=0, search_term=None, category=None):
        """
        Get emails from the specified folder.
        
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
        try:
            # Get the account
            account = self._get_account(email_address)
            namespace = self._get_namespace()
            
            # Get the folder
            folder = self._get_folder(namespace, folder_type)
            
            # Get emails from folder
            emails = []
            items = folder.Items
            
            # Sort by received time (newest first)
            items.Sort("[ReceivedTime]", True)
            
            # Apply search filter if provided
            if search_term:
                items = items.Restrict(f"@SQL=\"urn:schemas:httpmail:subject\" LIKE '%{search_term}%' OR \"urn:schemas:httpmail:textdescription\" LIKE '%{search_term}%' OR \"urn:schemas:httpmail:fromname\" LIKE '%{search_term}%' OR \"urn:schemas:httpmail:fromemail\" LIKE '%{search_term}%'")
            
            # Apply category filter if provided
            if category:
                items = items.Restrict(f"[Categories] = '{category}'")
            
            # Apply pagination
            count = 0
            skipped = 0
            
            for item in items:
                # Skip items until we reach the offset
                if skipped < offset:
                    skipped += 1
                    continue
                
                # Stop if we've reached the limit
                if count >= limit:
                    break
                
                try:
                    # Check if this email belongs to an allowed account
                    if item.Parent.Store.DisplayName not in [acc.DisplayName for acc in namespace.Accounts if acc.SmtpAddress in self.ALLOWED_ACCOUNTS]:
                        continue
                    
                    # Get email details
                    email = self._extract_email_details(item)
                    emails.append(email)
                    count += 1
                except Exception as e:
                    logger.error(f"Error processing email: {str(e)}")
            
            return emails
            
        except Exception as e:
            logger.error(f"Error getting emails: {str(e)}")
            raise
    
    def _extract_email_details(self, item):
        """
        Extract email details from an Outlook item.
        
        Args:
            item: The Outlook item
            
        Returns:
            Dictionary with email details
        """
        try:
            # Get sender email address
            sender_email = ""
            if hasattr(item, "SenderEmailAddress"):
                sender_email = item.SenderEmailAddress
            
            # Get recipient email addresses
            to_list = []
            if hasattr(item, "To") and item.To:
                to_list = [recipient.strip() for recipient in item.To.split(';')]
            
            # Get CC email addresses
            cc_list = []
            if hasattr(item, "CC") and item.CC:
                cc_list = [recipient.strip() for recipient in item.CC.split(';')]
            
            # Get attachments
            attachments = []
            if hasattr(item, "Attachments") and item.Attachments.Count > 0:
                for i in range(1, item.Attachments.Count + 1):
                    attachment = item.Attachments.Item(i)
                    attachments.append({
                        'name': attachment.FileName,
                        'size': attachment.Size,
                        'id': i  # Use index as ID for now
                    })
            
            # Get body
            body = ""
            if hasattr(item, "Body"):
                body = item.Body
            
            # Get HTML body if available
            html_body = ""
            if hasattr(item, "HTMLBody"):
                html_body = item.HTMLBody
            
            # Get categories as list
            categories = []
            if hasattr(item, "Categories") and item.Categories:
                categories = [category.strip() for category in item.Categories.split(',')]
            
            # Create email dictionary
            email = {
                'id': item.EntryID,
                'subject': item.Subject or "(No Subject)",
                'sender': item.SenderName if hasattr(item, "SenderName") else "",
                'sender_email': sender_email,
                'to': "; ".join(to_list),
                'cc': "; ".join(cc_list),
                'received_time': item.ReceivedTime.strftime('%Y-%m-%d %H:%M:%S') if hasattr(item, 'ReceivedTime') else None,
                'sent_time': item.SentOn.strftime('%Y-%m-%d %H:%M:%S') if hasattr(item, 'SentOn') else None,
                'has_attachments': len(attachments) > 0,
                'attachments': attachments,
                'body': body,
                'html_body': html_body,
                'unread': item.UnRead if hasattr(item, 'UnRead') else False,
                'importance': item.Importance if hasattr(item, 'Importance') else 1,  # 0=Low, 1=Normal, 2=High
                'categories': categories,
                'preview': body[:200] + '...' if len(body) > 200 else body
            }
            
            return email
            
        except Exception as e:
            logger.error(f"Error extracting email details: {str(e)}")
            # Return minimal email details on error
            return {
                'id': item.EntryID if hasattr(item, 'EntryID') else "",
                'subject': item.Subject if hasattr(item, 'Subject') else "(Error)",
                'sender': item.SenderName if hasattr(item, 'SenderName') else "",
                'preview': "Error extracting email details"
            }
    
    def get_email(self, email_address, message_id):
        """
        Get a specific email by ID.
        
        Args:
            email_address: The email address of the account
            message_id: The EntryID of the email
            
        Returns:
            Dictionary with email details
        """
        try:
            namespace = self._get_namespace()
            item = namespace.GetItemFromID(message_id)
            
            # Check if this email belongs to an allowed account
            if item.Parent.Store.DisplayName not in [acc.DisplayName for acc in namespace.Accounts if acc.SmtpAddress in self.ALLOWED_ACCOUNTS]:
                raise ValueError("Attempting to access email from unauthorized account")
            
            # Extract email details
            return self._extract_email_details(item)
            
        except Exception as e:
            logger.error(f"Error getting email: {str(e)}")
            raise
    
    def send_email(self, email_address, to, subject, body, cc=None, bcc=None, attachments=None, html_body=None, importance=1):
        """
        Send an email from the specified account.
        
        Args:
            email_address: The email address to send from
            to: Recipient email address(es)
            subject: Email subject
            body: Plain text email body
            cc: Carbon copy recipient(s)
            bcc: Blind carbon copy recipient(s)
            attachments: List of file paths to attach
            html_body: HTML version of the email body
            importance: Email importance (0=Low, 1=Normal, 2=High)
            
        Returns:
            True if successful
        """
        try:
            app = self._get_outlook_application()
            mail = app.CreateItem(0)  # 0 = olMailItem
            
            # Set the sending account
            account = self._get_account(email_address)
            mail._oleobj_.Invoke(*(64209, 0, 8, 0, account))
            
            # Set email properties
            mail.To = to
            mail.Subject = subject
            mail.Body = body
            
            if html_body:
                mail.HTMLBody = html_body
            
            if cc:
                mail.CC = cc
            
            if bcc:
                mail.BCC = bcc
            
            mail.Importance = importance
            
            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    if os.path.exists(attachment_path):
                        mail.Attachments.Add(attachment_path)
            
            # Send the email
            mail.Send()
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise
    
    def save_draft(self, email_address, to, subject, body, cc=None, bcc=None, attachments=None, html_body=None, importance=1):
        """
        Save an email as draft.
        
        Args:
            email_address: The email address to save draft for
            to: Recipient email address(es)
            subject: Email subject
            body: Plain text email body
            cc: Carbon copy recipient(s)
            bcc: Blind carbon copy recipient(s)
            attachments: List of file paths to attach
            html_body: HTML version of the email body
            importance: Email importance (0=Low, 1=Normal, 2=High)
            
        Returns:
            EntryID of the saved draft
        """
        try:
            app = self._get_outlook_application()
            mail = app.CreateItem(0)  # 0 = olMailItem
            
            # Set the sending account
            account = self._get_account(email_address)
            mail._oleobj_.Invoke(*(64209, 0, 8, 0, account))
            
            # Set email properties
            mail.To = to
            mail.Subject = subject
            mail.Body = body
            
            if html_body:
                mail.HTMLBody = html_body
            
            if cc:
                mail.CC = cc
            
            if bcc:
                mail.BCC = bcc
            
            mail.Importance = importance
            
            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    if os.path.exists(attachment_path):
                        mail.Attachments.Add(attachment_path)
            
            # Save the draft
            mail.Save()
            return mail.EntryID
        
        except Exception as e:
            logger.error(f"Error saving draft: {str(e)}")
            raise
    
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
            
            # Check if this email belongs to an allowed account
            if item.Parent.Store.DisplayName not in [acc.DisplayName for acc in namespace.Accounts if acc.SmtpAddress in self.ALLOWED_ACCOUNTS]:
                raise ValueError("Attempting to access email from unauthorized account")
            
            # Delete the item
            item.Delete()
            return True
        
        except Exception as e:
            logger.error(f"Error deleting email: {str(e)}")
            raise
    
    def categorize_email(self, email_address, message_id, category):
        """
        Apply a category to an email.
        
        Args:
            email_address: The email address of the account
            message_id: The EntryID of the email
            category: The category to apply
            
        Returns:
            True if successful
        """
        try:
            namespace = self._get_namespace()
            item = namespace.GetItemFromID(message_id)
            
            # Check if this email belongs to an allowed account
            if item.Parent.Store.DisplayName not in [acc.DisplayName for acc in namespace.Accounts if acc.SmtpAddress in self.ALLOWED_ACCOUNTS]:
                raise ValueError("Attempting to access email from unauthorized account")
            
            # Apply the category
            item.Categories = category
            item.Save()
            return True
        
        except Exception as e:
            logger.error(f"Error categorizing email: {str(e)}")
            raise
    
    def get_categories(self, email_address):
        """
        Get all available categories for the specified account.
        
        Args:
            email_address: The email address of the account
            
        Returns:
            List of category dictionaries with name and color
        """
        try:
            # Get the account
            account = self._get_account(email_address)
            namespace = self._get_namespace()
            
            # Try to get categories from the store
            categories = []
            
            # Default categories if we can't get them from Outlook
            default_categories = [
                {"name": "Important", "color": "#FF0000"},
                {"name": "Work", "color": "#FFA500"},
                {"name": "Personal", "color": "#0000FF"},
                {"name": "Follow-up", "color": "#008000"},
                {"name": "Project", "color": "#800080"}
            ]
            
            try:
                # Try to access the Categories collection (this might not work in all Outlook versions)
                store = account.DeliveryStore
                
                # This is a bit tricky as the API for categories varies by Outlook version
                # Try to access categories through the store's Master Category List
                try:
                    category_list = namespace.Categories
                    if category_list and category_list.Count > 0:
                        for i in range(1, category_list.Count + 1):
                            cat = category_list.Item(i)
                            categories.append({
                                "name": cat.Name,
                                "color": self._convert_outlook_color_to_hex(cat.Color)
                            })
                except:
                    # Fall back to default categories if we can't get them from Outlook
                    categories = default_categories
                    logger.warning("Could not access Outlook categories, using default categories")
            except:
                # Fall back to default categories if we can't access the store
                categories = default_categories
                logger.warning("Could not access Outlook store categories, using default categories")
            
            # If no categories were found, use default categories
            if not categories:
                categories = default_categories
                
            return categories
            
        except Exception as e:
            logger.error(f"Error retrieving categories: {str(e)}")
            # Return default categories on error
            return [
                {"name": "Important", "color": "#FF0000"},
                {"name": "Work", "color": "#FFA500"},
                {"name": "Personal", "color": "#0000FF"},
                {"name": "Follow-up", "color": "#008000"},
                {"name": "Project", "color": "#800080"}
            ]
    
    def _convert_outlook_color_to_hex(self, outlook_color):
        """Convert Outlook category color to hex color."""
        # Outlook color mapping (approximate)
        color_map = {
            0: "#000000",  # None
            1: "#FF0000",  # Red
            2: "#0000FF",  # Blue
            3: "#008000",  # Green
            4: "#800080",  # Purple
            5: "#FFA500",  # Orange
            6: "#800000",  # Maroon
            7: "#008080",  # Teal
            8: "#FFFF00",  # Yellow
            9: "#808000",  # Olive
            10: "#000080", # Navy
            11: "#FF00FF", # Magenta
            12: "#00FFFF", # Cyan
            13: "#A52A2A", # Brown
            14: "#808080", # Gray
            15: "#C0C0C0", # Silver
            16: "#FF69B4", # Pink
            17: "#00FF00", # Bright Green
            18: "#9370DB", # Medium Purple
            19: "#87CEEB", # Sky Blue
            20: "#FFD700", # Gold
            21: "#FF6347", # Tomato
            22: "#8A2BE2", # Blue Violet
            23: "#00FA9A", # Medium Spring Green
            24: "#4682B4", # Steel Blue
            25: "#D2691E"  # Chocolate
        }
        return color_map.get(outlook_color, "#777777")  # Default to gray if color not found
    
    def _guess_content_type(self, filename):
        """Guess the content type based on file extension."""
        ext = os.path.splitext(filename)[1].lower()
        
        content_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.7z': 'application/x-7z-compressed',
        }
        
        return content_types.get(ext, 'application/octet-stream')
    
    def __del__(self):
        """Clean up COM resources."""
        try:
            pythoncom.CoUninitialize()
        except:
            pass 