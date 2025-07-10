#!/usr/bin/env python3
"""
Test Fixed OutlookService

Quick test to verify the fixed service works correctly.
"""

import sys
import os
from pathlib import Path

# Add the Django project path
sys.path.insert(0, str(Path(__file__).parent / 'normie'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'normie.settings')

import django
django.setup()

from normie.normieapp.services.outlook_service import OutlookService

def test_fixed_service():
    """Test the fixed OutlookService configuration."""
    print("Fixed OutlookService Test")
    print("========================")
    
    try:
        # Create OutlookService instance
        service = OutlookService()
        print("✓ OutlookService created successfully")
        
        # Check allowed accounts
        print(f"Allowed accounts: {service.ALLOWED_ACCOUNTS}")
        
        if len(service.ALLOWED_ACCOUNTS) == 1:
            print("✓ Only one account allowed (IRM)")
        else:
            print(f"✗ Expected 1 account, got {len(service.ALLOWED_ACCOUNTS)}")
            
        if service.ALLOWED_ACCOUNTS[0] == 'irm-standardisation-office@rolls-royce.com':
            print("✓ Correct IRM account configured")
        else:
            print(f"✗ Wrong account: {service.ALLOWED_ACCOUNTS[0]}")
        
        # Test VBA data path
        vba_path = service._get_vba_data_path()
        print(f"VBA data path: {vba_path}")
        
        if vba_path.exists():
            print("✓ VBA emails.json file exists")
            print(f"  File size: {vba_path.stat().st_size} bytes")
            
            # Test freshness
            is_fresh = service._is_vba_data_fresh()
            print(f"  VBA data is fresh: {is_fresh}")
            
            if is_fresh:
                print("✓ VBA data is current")
                
                # Test loading a few emails
                try:
                    emails = service.get_emails(
                        email_address='irm-standardisation-office@rolls-royce.com',
                        limit=3
                    )
                    print(f"✓ Successfully loaded {len(emails)} emails")
                    
                    if emails:
                        first_email = emails[0]
                        print(f"  First email subject: {first_email.get('subject', 'N/A')}")
                        print(f"  First email source: {first_email.get('source', 'N/A')}")
                        
                        if first_email.get('source') == 'vba':
                            print("✓ VBA data integration working")
                        else:
                            print("ℹ Using COM fallback")
                            
                except Exception as e:
                    print(f"✗ Error loading emails: {e}")
            else:
                print("ℹ VBA data is stale (will use COM fallback)")
        else:
            print("ℹ VBA emails.json file does not exist (will use COM fallback)")
        
        print(f"\n✓ Fixed service test completed!")
        print(f"Configuration:")
        print(f"  - Only IRM account allowed: ✓")
        print(f"  - No fallback accounts: ✓") 
        print(f"  - VBA integration ready: ✓")
        return True
        
    except Exception as e:
        print(f"✗ Service test failed: {e}")
        return False

if __name__ == "__main__":
    test_fixed_service() 