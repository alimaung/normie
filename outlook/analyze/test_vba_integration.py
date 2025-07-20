#!/usr/bin/env python3
"""
Test VBA Integration

Simple test to verify the hybrid VBA-COM integration works.
This script tests the VBA file reading functionality without Django.
"""

import sys
import os
import json
from pathlib import Path

# Add the Django project path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'normie'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'normie.settings')

import django
django.setup()

from normie.normieapp.services.outlook_service import OutlookService

def test_vba_integration():
    """Test the VBA integration functionality."""
    print("VBA Integration Test")
    print("===================")
    
    try:
        # Create OutlookService instance
        service = OutlookService()
        print("✓ OutlookService created successfully")
        
        # Test VBA data path
        vba_path = service._get_vba_data_path()
        print(f"VBA data path: {vba_path}")
        
        # Check if VBA file exists
        if vba_path.exists():
            print("✓ VBA emails.json file exists")
            print(f"  File size: {vba_path.stat().st_size} bytes")
            print(f"  Modified: {vba_path.stat().st_mtime}")
        else:
            print("✗ VBA emails.json file does not exist")
            print("  Make sure the VBA script is running and has created the file")
            return False
        
        # Test if VBA data is fresh
        is_fresh = service._is_vba_data_fresh()
        print(f"VBA data is fresh: {is_fresh}")
        
        if not is_fresh:
            print("⚠ VBA data is not fresh (older than 2 minutes)")
            print("  Start the VBA script in Outlook to generate fresh data")
        
        # Test loading VBA emails
        print("\nTesting VBA email loading...")
        try:
            vba_emails = service._get_emails_from_vba(limit=5)
            print(f"✓ Loaded {len(vba_emails)} emails from VBA")
            
            if vba_emails:
                # Show first email details
                first_email = vba_emails[0]
                print(f"\nFirst email details:")
                print(f"  ID: {first_email.get('id', 'Unknown')}")
                print(f"  Subject: {first_email.get('subject', 'Unknown')}")
                print(f"  Sender: {first_email.get('sender', 'Unknown')}")
                print(f"  Source: {first_email.get('source', 'Unknown')}")
                print(f"  Has attachments: {first_email.get('has_attachments', False)}")
                print(f"  Body preview: {first_email.get('preview', 'No preview')[:100]}...")
                
                # Test getting specific email
                print(f"\nTesting specific email retrieval...")
                specific_email = service._get_email_from_vba(first_email['id'])
                if specific_email:
                    print("✓ Successfully retrieved specific email from VBA")
                else:
                    print("✗ Failed to retrieve specific email from VBA")
                
            else:
                print("⚠ No emails found in VBA data")
                
        except Exception as e:
            print(f"✗ Error loading VBA emails: {e}")
            return False
        
        # Test hybrid get_emails method
        print(f"\nTesting hybrid get_emails method...")
        try:
            emails = service.get_emails(
                email_address='irm-standardisation-office@rolls-royce.com',
                folder_type='inbox',
                limit=3
            )
            print(f"✓ Hybrid method returned {len(emails)} emails")
            
            if emails:
                sources = [email.get('source', 'com') for email in emails]
                vba_count = sources.count('vba')
                com_count = sources.count('com')
                print(f"  VBA emails: {vba_count}")
                print(f"  COM emails: {com_count}")
                
                if vba_count > 0:
                    print("✓ VBA integration is working!")
                else:
                    print("⚠ No VBA emails returned (using COM fallback)")
            
        except Exception as e:
            print(f"✗ Error with hybrid method: {e}")
            return False
        
        print(f"\n✓ VBA integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ VBA integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_vba_integration()
    sys.exit(0 if success else 1) 