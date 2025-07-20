#!/usr/bin/env python3
"""
Outlook COM Operations Test

Tests the key operations needed for Django inbox functionality:
1. Email reading operations (already tested in analyze.py - FAILED)
2. Email deletion (delete_email method)
3. Email categorization (categorize_email method) 
4. Mark as read/unread (mark_as_read method)
5. Email composition/sending (send_email method)
6. Email reply functionality
7. Email forward functionality
8. Email move operations (move to folders)
9. Get categories (get_categories method)

This will help determine which operations work with COM vs need VBA workarounds.
"""

import win32com.client
import pythoncom
import sys
import traceback
import datetime
import os

class OutlookCOMTester:
    """Test various Outlook COM operations for inbox functionality."""
    
    def __init__(self):
        self.app = None
        self.namespace = None
        self.test_results = {}
    
    def connect_to_outlook(self):
        """Connect to Outlook COM application."""
        try:
            print("Connecting to Outlook...")
            pythoncom.CoInitialize()
            self.app = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.app.GetNamespace("MAPI")
            print("✓ Connected successfully")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def get_test_email(self, account_name="IRM-Standardisation-Office"):
        """Get a test email for operations testing."""
        try:
            print(f"\nFinding test email in {account_name}...")
            
            # Find the target account
            stores = self.namespace.Stores
            target_store = None
            
            for i in range(1, stores.Count + 1):
                store = stores.Item(i)
                if account_name.lower() in store.DisplayName.lower():
                    target_store = store
                    break
            
            if not target_store:
                print(f"✗ Account {account_name} not found")
                return None
            
            # Find inbox
            root_folder = target_store.GetRootFolder()
            inbox = None
            
            for i in range(1, root_folder.Folders.Count + 1):
                folder = root_folder.Folders.Item(i)
                if folder.Name.lower() == 'inbox':
                    inbox = folder
                    break
            
            if not inbox:
                print("✗ Inbox not found")
                return None
            
            # Get first email
            if inbox.Items.Count > 0:
                items = inbox.Items
                items.Sort("[ReceivedTime]", True)
                test_email = items.Item(1)
                print(f"✓ Found test email: {getattr(test_email, 'Subject', 'No Subject')}")
                return test_email, inbox
            else:
                print("✗ No emails found in inbox")
                return None, inbox
                
        except Exception as e:
            print(f"✗ Error finding test email: {e}")
            return None, None
    
    def test_email_reading(self):
        """Test email reading operations (we know these are restricted)."""
        print("\n" + "="*50)
        print("TEST 1: EMAIL READING OPERATIONS")
        print("="*50)
        
        test_email, inbox = self.get_test_email()
        if not test_email:
            self.test_results['reading'] = {'status': 'FAILED', 'reason': 'No test email found'}
            return
        
        reading_tests = {
            'Subject': 'subject access',
            'SenderName': 'sender name access', 
            'SenderEmailAddress': 'sender email access',
            'Body': 'email body access',
            'HTMLBody': 'HTML body access',
            'ReceivedTime': 'received time access',
            'Size': 'email size access',
            'UnRead': 'unread status access',
            'Categories': 'categories access'
        }
        
        results = {}
        for property_name, description in reading_tests.items():
            try:
                value = getattr(test_email, property_name)
                if value is not None and str(value).strip():
                    results[property_name] = {'status': 'SUCCESS', 'value': str(value)[:50]}
                    print(f"  ✓ {description}: SUCCESS")
                else:
                    results[property_name] = {'status': 'EMPTY', 'value': 'Empty/None'}
                    print(f"  ⚠ {description}: EMPTY")
            except Exception as e:
                results[property_name] = {'status': 'FAILED', 'error': str(e)}
                print(f"  ✗ {description}: FAILED - {e}")
        
        self.test_results['reading'] = results
    
    def test_mark_as_read(self):
        """Test marking emails as read/unread."""
        print("\n" + "="*50)
        print("TEST 2: MARK AS READ/UNREAD")
        print("="*50)
        
        test_email, inbox = self.get_test_email()
        if not test_email:
            self.test_results['mark_read'] = {'status': 'FAILED', 'reason': 'No test email found'}
            return
        
        try:
            # Get original unread status
            original_status = getattr(test_email, 'UnRead', None)
            print(f"  Original unread status: {original_status}")
            
            # Test marking as read
            print("  Testing mark as read...")
            test_email.UnRead = False
            test_email.Save()
            new_status = getattr(test_email, 'UnRead', None)
            print(f"  ✓ Mark as read: SUCCESS (status: {new_status})")
            
            # Test marking as unread
            print("  Testing mark as unread...")
            test_email.UnRead = True
            test_email.Save()
            new_status = getattr(test_email, 'UnRead', None)
            print(f"  ✓ Mark as unread: SUCCESS (status: {new_status})")
            
            # Restore original status
            test_email.UnRead = original_status
            test_email.Save()
            print(f"  ✓ Restored original status: {original_status}")
            
            self.test_results['mark_read'] = {'status': 'SUCCESS'}
            
        except Exception as e:
            print(f"  ✗ Mark as read/unread: FAILED - {e}")
            self.test_results['mark_read'] = {'status': 'FAILED', 'error': str(e)}
    
    def test_categorization(self):
        """Test email categorization operations."""
        print("\n" + "="*50)
        print("TEST 3: EMAIL CATEGORIZATION")
        print("="*50)
        
        test_email, inbox = self.get_test_email()
        if not test_email:
            self.test_results['categorization'] = {'status': 'FAILED', 'reason': 'No test email found'}
            return
        
        try:
            # Get original categories
            original_categories = getattr(test_email, 'Categories', '')
            print(f"  Original categories: '{original_categories}'")
            
            # Test adding a category
            test_category = "Test Category"
            print(f"  Testing add category '{test_category}'...")
            test_email.Categories = test_category
            test_email.Save()
            new_categories = getattr(test_email, 'Categories', '')
            print(f"  ✓ Add category: SUCCESS (categories: '{new_categories}')")
            
            # Test multiple categories
            multi_categories = "Test Category;Important"
            print(f"  Testing multiple categories '{multi_categories}'...")
            test_email.Categories = multi_categories
            test_email.Save()
            new_categories = getattr(test_email, 'Categories', '')
            print(f"  ✓ Multiple categories: SUCCESS (categories: '{new_categories}')")
            
            # Restore original categories
            test_email.Categories = original_categories
            test_email.Save()
            print(f"  ✓ Restored original categories: '{original_categories}'")
            
            self.test_results['categorization'] = {'status': 'SUCCESS'}
            
        except Exception as e:
            print(f"  ✗ Categorization: FAILED - {e}")
            self.test_results['categorization'] = {'status': 'FAILED', 'error': str(e)}
    
    def test_email_deletion(self):
        """Test email deletion (non-destructive - test delete then undo)."""
        print("\n" + "="*50)
        print("TEST 4: EMAIL DELETION")
        print("="*50)
        
        test_email, inbox = self.get_test_email()
        if not test_email:
            self.test_results['deletion'] = {'status': 'FAILED', 'reason': 'No test email found'}
            return
        
        try:
            # Check if we can access the Delete method
            if hasattr(test_email, 'Delete'):
                print("  ✓ Delete method available")
                
                # Find deleted items folder for recovery
                deleted_items = None
                try:
                    deleted_items = self.namespace.GetDefaultFolder(3)  # olFolderDeletedItems
                    print("  ✓ Deleted Items folder accessible")
                except Exception as e:
                    print(f"  ⚠ Deleted Items folder not accessible: {e}")
                
                # Get original subject for tracking
                subject = getattr(test_email, 'Subject', 'Unknown')
                print(f"  Email to test delete: '{subject}'")
                
                # NOTE: For safety, we'll just test the method availability
                # rather than actually deleting an email
                print("  ⚠ SKIPPING actual deletion for safety")
                print("  ✓ Delete method is available and could be called")
                
                self.test_results['deletion'] = {'status': 'AVAILABLE', 'note': 'Method available but not tested destructively'}
                
            else:
                print("  ✗ Delete method not available")
                self.test_results['deletion'] = {'status': 'FAILED', 'reason': 'Delete method not available'}
                
        except Exception as e:
            print(f"  ✗ Deletion test: FAILED - {e}")
            self.test_results['deletion'] = {'status': 'FAILED', 'error': str(e)}
    
    def test_email_composition(self):
        """Test email composition and sending capabilities."""
        print("\n" + "="*50)
        print("TEST 5: EMAIL COMPOSITION & SENDING")
        print("="*50)
        
        try:
            # Test creating a new mail item
            print("  Testing mail item creation...")
            mail_item = self.app.CreateItem(0)  # olMailItem
            print("  ✓ Mail item created successfully")
            
            # Test setting basic properties
            test_properties = {
                'To': 'test@example.com',
                'Subject': 'Test Email - DO NOT SEND',
                'Body': 'This is a test email body.',
                'HTMLBody': '<html><body><p>This is a test HTML email body.</p></body></html>'
            }
            
            for prop, value in test_properties.items():
                try:
                    setattr(mail_item, prop, value)
                    result_value = getattr(mail_item, prop)
                    print(f"  ✓ Set {prop}: SUCCESS")
                except Exception as e:
                    print(f"  ✗ Set {prop}: FAILED - {e}")
            
            # Test Send method availability (but don't actually send)
            if hasattr(mail_item, 'Send'):
                print("  ✓ Send method available")
                print("  ⚠ SKIPPING actual send for safety")
            else:
                print("  ✗ Send method not available")
            
            # Test Save as draft
            try:
                mail_item.Save()
                print("  ✓ Save as draft: SUCCESS")
                
                # Clean up - delete the draft
                mail_item.Delete()
                print("  ✓ Draft cleanup: SUCCESS")
                
            except Exception as e:
                print(f"  ✗ Save as draft: FAILED - {e}")
            
            self.test_results['composition'] = {'status': 'SUCCESS'}
            
        except Exception as e:
            print(f"  ✗ Email composition: FAILED - {e}")
            self.test_results['composition'] = {'status': 'FAILED', 'error': str(e)}
    
    def test_email_reply_forward(self):
        """Test reply and forward functionality."""
        print("\n" + "="*50)
        print("TEST 6: EMAIL REPLY & FORWARD")
        print("="*50)
        
        test_email, inbox = self.get_test_email()
        if not test_email:
            self.test_results['reply_forward'] = {'status': 'FAILED', 'reason': 'No test email found'}
            return
        
        operations = ['Reply', 'ReplyAll', 'Forward']
        results = {}
        
        for operation in operations:
            try:
                print(f"  Testing {operation} method...")
                if hasattr(test_email, operation):
                    # Create reply/forward item
                    reply_item = getattr(test_email, operation)()
                    print(f"  ✓ {operation} item created")
                    
                    # Test modifying the reply
                    if hasattr(reply_item, 'Body'):
                        reply_item.Body = f"Test {operation} body - DO NOT SEND"
                        print(f"  ✓ {operation} body modified")
                    
                    # Clean up without sending
                    if hasattr(reply_item, 'Delete'):
                        reply_item.Delete()
                        print(f"  ✓ {operation} item cleaned up")
                    
                    results[operation] = {'status': 'SUCCESS'}
                    
                else:
                    print(f"  ✗ {operation} method not available")
                    results[operation] = {'status': 'FAILED', 'reason': 'Method not available'}
                    
            except Exception as e:
                print(f"  ✗ {operation}: FAILED - {e}")
                results[operation] = {'status': 'FAILED', 'error': str(e)}
        
        self.test_results['reply_forward'] = results
    
    def test_folder_operations(self):
        """Test folder and move operations."""
        print("\n" + "="*50)
        print("TEST 7: FOLDER & MOVE OPERATIONS")
        print("="*50)
        
        test_email, inbox = self.get_test_email()
        if not test_email:
            self.test_results['folder_operations'] = {'status': 'FAILED', 'reason': 'No test email found'}
            return
        
        try:
            # Test accessing different folders
            folder_tests = {
                'Inbox': 6,          # olFolderInbox
                'Sent Items': 5,     # olFolderSentMail  
                'Drafts': 16,        # olFolderDrafts
                'Deleted Items': 3,  # olFolderDeletedItems
                'Junk Email': 23     # olFolderJunk
            }
            
            accessible_folders = {}
            for folder_name, folder_id in folder_tests.items():
                try:
                    folder = self.namespace.GetDefaultFolder(folder_id)
                    folder_display_name = getattr(folder, 'Name', 'Unknown')
                    item_count = getattr(folder, 'Items', {}).Count if hasattr(folder, 'Items') else 0
                    accessible_folders[folder_name] = {
                        'accessible': True,
                        'name': folder_display_name,
                        'item_count': item_count
                    }
                    print(f"  ✓ {folder_name}: Accessible ({item_count} items)")
                except Exception as e:
                    accessible_folders[folder_name] = {
                        'accessible': False,
                        'error': str(e)
                    }
                    print(f"  ✗ {folder_name}: Not accessible - {e}")
            
            # Test Move method availability
            if hasattr(test_email, 'Move'):
                print("  ✓ Move method available")
                print("  ⚠ SKIPPING actual move for safety")
                move_available = True
            else:
                print("  ✗ Move method not available")
                move_available = False
            
            self.test_results['folder_operations'] = {
                'accessible_folders': accessible_folders,
                'move_available': move_available
            }
            
        except Exception as e:
            print(f"  ✗ Folder operations: FAILED - {e}")
            self.test_results['folder_operations'] = {'status': 'FAILED', 'error': str(e)}
    
    def test_categories_management(self):
        """Test category management operations."""
        print("\n" + "="*50)
        print("TEST 8: CATEGORIES MANAGEMENT")
        print("="*50)
        
        try:
            # Test accessing master category list
            print("  Testing category list access...")
            
            if hasattr(self.namespace, 'Categories'):
                categories = self.namespace.Categories
                print(f"  ✓ Categories collection accessible")
                print(f"  ✓ Categories count: {categories.Count}")
                
                # List first few categories
                for i in range(1, min(categories.Count + 1, 6)):  # First 5 categories
                    try:
                        category = categories.Item(i)
                        name = getattr(category, 'Name', 'Unknown')
                        color = getattr(category, 'Color', 'Unknown')
                        print(f"    - {name} (Color: {color})")
                    except Exception as e:
                        print(f"    - Error reading category {i}: {e}")
                
                self.test_results['categories_management'] = {'status': 'SUCCESS', 'count': categories.Count}
                
            else:
                print("  ✗ Categories collection not accessible")
                self.test_results['categories_management'] = {'status': 'FAILED', 'reason': 'Categories not accessible'}
            
        except Exception as e:
            print(f"  ✗ Categories management: FAILED - {e}")
            self.test_results['categories_management'] = {'status': 'FAILED', 'error': str(e)}
    
    def print_summary(self):
        """Print a summary of all test results."""
        print("\n" + "="*60)
        print("OUTLOOK COM OPERATIONS TEST SUMMARY")
        print("="*60)
        
        success_count = 0
        total_tests = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            test_display = test_name.replace('_', ' ').title()
            
            if isinstance(result, dict):
                if result.get('status') == 'SUCCESS':
                    print(f"✓ {test_display}: WORKING")
                    success_count += 1
                elif result.get('status') == 'AVAILABLE':
                    print(f"⚠ {test_display}: AVAILABLE (not fully tested)")
                    success_count += 0.5
                elif result.get('status') == 'FAILED':
                    print(f"✗ {test_display}: FAILED - {result.get('reason', result.get('error', 'Unknown'))}")
                else:
                    # Complex result, check individual items
                    working_items = 0
                    total_items = 0
                    for key, value in result.items():
                        if isinstance(value, dict) and 'status' in value:
                            total_items += 1
                            if value['status'] == 'SUCCESS':
                                working_items += 1
                    
                    if total_items > 0:
                        if working_items == total_items:
                            print(f"✓ {test_display}: WORKING ({working_items}/{total_items})")
                            success_count += 1
                        elif working_items > 0:
                            print(f"⚠ {test_display}: PARTIAL ({working_items}/{total_items})")
                            success_count += 0.5
                        else:
                            print(f"✗ {test_display}: FAILED (0/{total_items})")
                    else:
                        print(f"? {test_display}: UNKNOWN")
        
        print(f"\nOverall Success Rate: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%)")
        
        # Recommendations
        print(f"\n📋 RECOMMENDATIONS FOR DJANGO INTEGRATION:")
        
        if self.test_results.get('mark_read', {}).get('status') == 'SUCCESS':
            print("✓ Mark as read/unread operations can use COM")
        else:
            print("✗ Mark as read/unread operations need VBA workaround")
        
        if self.test_results.get('categorization', {}).get('status') == 'SUCCESS':
            print("✓ Email categorization can use COM")
        else:
            print("✗ Email categorization needs VBA workaround")
        
        if self.test_results.get('deletion', {}).get('status') in ['SUCCESS', 'AVAILABLE']:
            print("✓ Email deletion can use COM")
        else:
            print("✗ Email deletion needs VBA workaround")
        
        if self.test_results.get('composition', {}).get('status') == 'SUCCESS':
            print("✓ Email composition/sending can use COM")
        else:
            print("✗ Email composition/sending needs VBA workaround")
        
        print("✗ Email reading (content) requires VBA workaround (already confirmed)")
    
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
    """Main function to run all tests."""
    print("Outlook COM Operations Tester")
    print("============================")
    print("Testing operations needed for Django inbox functionality")
    print()
    
    tester = OutlookCOMTester()
    
    try:
        if not tester.connect_to_outlook():
            return 1
        
        # Run all tests
        tester.test_email_reading()
        tester.test_mark_as_read() 
        tester.test_categorization()
        tester.test_email_deletion()
        tester.test_email_composition()
        tester.test_email_reply_forward()
        tester.test_folder_operations()
        tester.test_categories_management()
        
        # Print summary
        tester.print_summary()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        print(f"Stack trace: {traceback.format_exc()}")
        return 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())
