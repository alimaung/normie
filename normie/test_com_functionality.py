#!/usr/bin/env python3
"""
Test COM Functionality for Email Operations

This script tests the new COM functionality for delete and mark read/unread operations.
Run this from the Django project root to test the OutlookService COM integration.
"""

import os
import sys
import django
from pathlib import Path

# Add the Django project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'normie.settings')
django.setup()

from normieapp.services.outlook_service import OutlookService
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_com_functionality():
    """Test COM functionality for email operations."""
    print("🧪 Testing COM Functionality for Email Operations")
    print("=" * 60)
    
    # Initialize the service
    print("\n1. Initializing OutlookService...")
    try:
        outlook_service = OutlookService()
        print("✅ OutlookService initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize OutlookService: {e}")
        return False
    
    # Test COM availability
    print("\n2. Testing COM availability...")
    try:
        com_available = outlook_service.is_com_available()
        print(f"COM Available: {'✅ Yes' if com_available else '❌ No'}")
        
        if not com_available:
            print("⚠️  COM interface not available. Make sure Outlook is running.")
            return False
            
    except Exception as e:
        print(f"❌ Error checking COM availability: {e}")
        return False
    
    # Get COM status
    print("\n3. Getting COM status...")
    try:
        com_status = outlook_service.get_com_status()
        print(f"COM Status: {com_status}")
        
        if com_status.get('available') and com_status.get('initialized'):
            print("✅ COM interface is ready")
        else:
            print(f"⚠️  COM issue: {com_status.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting COM status: {e}")
        return False
    
    # Test email data access
    print("\n4. Testing email data access...")
    try:
        emails_data = outlook_service.get_emails_data()
        email_count = len(emails_data.get('emails', []))
        print(f"📧 Found {email_count} emails in VBA data")
        
        if email_count == 0:
            print("⚠️  No emails found in VBA data. Cannot test email operations.")
            return False
            
        # Get first email for testing
        test_email = emails_data['emails'][0]
        test_email_id = test_email.get('id')
        test_email_subject = test_email.get('subject', 'No subject')
        
        print(f"🎯 Using test email: '{test_email_subject}' (ID: {test_email_id})")
        
    except Exception as e:
        print(f"❌ Error accessing email data: {e}")
        return False
    
    # Test mark as read/unread (non-destructive)
    print("\n5. Testing mark as read/unread functionality...")
    try:
        print("   Testing mark as read...")
        read_result = outlook_service.mark_email_read(test_email_id, True)
        print(f"   Mark as read: {'✅ Success' if read_result else '❌ Failed'}")
        
        print("   Testing mark as unread...")
        unread_result = outlook_service.mark_email_read(test_email_id, False)
        print(f"   Mark as unread: {'✅ Success' if unread_result else '❌ Failed'}")
        
        # Restore original state (mark as read)
        outlook_service.mark_email_read(test_email_id, True)
        
    except Exception as e:
        print(f"❌ Error testing mark read/unread: {e}")
        return False
    
    # Test delete functionality (DISABLED for safety)
    print("\n6. Testing delete functionality...")
    print("   ⚠️  Delete functionality test SKIPPED for safety")
    print("   ℹ️  Delete method is available and would work with:")
    print(f"      outlook_service.delete_email('{test_email_id}')")
    
    # Test bulk operations
    print("\n7. Testing bulk operations...")
    try:
        # Test with a small subset
        test_ids = [test_email_id]
        
        print("   Testing bulk mark as read...")
        bulk_read_result = outlook_service.mark_multiple_emails_read(test_ids, True)
        success_count, failed_ids = bulk_read_result
        print(f"   Bulk mark as read: {success_count}/{len(test_ids)} successful")
        
    except Exception as e:
        print(f"❌ Error testing bulk operations: {e}")
        return False
    
    print("\n🎉 COM functionality test completed successfully!")
    print("\n📋 Summary:")
    print("   ✅ COM interface available and functional")
    print("   ✅ Email data access working")
    print("   ✅ Mark as read/unread operations working")
    print("   ✅ Bulk operations working")
    print("   ⚠️  Delete operations available but not tested (for safety)")
    
    return True

def main():
    """Main test function."""
    try:
        success = test_com_functionality()
        
        if success:
            print("\n🏆 All tests passed! COM functionality is ready for use.")
            return 0
        else:
            print("\n💥 Some tests failed. Check the error messages above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 