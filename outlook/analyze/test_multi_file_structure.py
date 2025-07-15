#!/usr/bin/env python3
"""
Test script for the new multi-file email structure.
This script tests the updated OutlookService to ensure it correctly reads
from multiple folder-specific JSON files.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'normie'))

from normie.normieapp.services.outlook_service import OutlookService

def test_multi_file_structure():
    """Test the multi-file email structure functionality."""
    
    print("=" * 60)
    print("TESTING MULTI-FILE EMAIL STRUCTURE")
    print("=" * 60)
    
    # Initialize the service
    service = OutlookService()
    
    # Test data availability
    print("\n1. Testing data availability...")
    is_available = service.is_data_available()
    print(f"   Data available: {is_available}")
    
    # Test data status
    print("\n2. Testing data status...")
    status = service.get_data_status()
    print(f"   Status: {status}")
    
    # Test email data loading
    print("\n3. Testing email data loading...")
    try:
        data = service.get_emails_data()
        print(f"   Source: {data.get('source', 'unknown')}")
        print(f"   Total emails: {len(data.get('emails', []))}")
        print(f"   Folder counts: {data.get('folder_counts', {})}")
        print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
        
        # Show sample emails from different folders
        emails = data.get('emails', [])
        if emails:
            print("\n   Sample emails by folder:")
            folder_samples = {}
            for email in emails:
                folder = email.get('folder', 'Unknown')
                if folder not in folder_samples:
                    folder_samples[folder] = []
                if len(folder_samples[folder]) < 2:  # Max 2 samples per folder
                    folder_samples[folder].append({
                        'subject': email.get('subject', 'No Subject')[:50],
                        'sender': email.get('sender_email', 'Unknown'),
                        'id': email.get('id', 'No ID')
                    })
            
            for folder, samples in folder_samples.items():
                print(f"     {folder}:")
                for sample in samples:
                    print(f"       - {sample['subject']} (from: {sample['sender']}) [ID: {sample['id']}]")
        
    except Exception as e:
        print(f"   ERROR loading email data: {e}")
    
    # Test folder statistics
    print("\n4. Testing folder statistics...")
    try:
        stats = service.get_folder_stats()
        print(f"   Total emails: {stats.get('total_emails', 0)}")
        print(f"   Unread emails: {stats.get('unread_emails', 0)}")
        print(f"   Important emails: {stats.get('important_emails', 0)}")
        print(f"   Emails with attachments: {stats.get('emails_with_attachments', 0)}")
        print(f"   Last updated: {stats.get('last_updated', 'N/A')}")
        print(f"   Source: {stats.get('source', 'unknown')}")
        print(f"   Folder counts: {stats.get('folder_counts', {})}")
        
    except Exception as e:
        print(f"   ERROR getting folder stats: {e}")
    
    # Test folder-specific email retrieval
    print("\n5. Testing folder-specific email retrieval...")
    try:
        # Test inbox emails
        inbox_emails, inbox_pagination = service.get_inbox_emails(per_page=5)
        print(f"   Inbox emails: {len(inbox_emails)} (total: {inbox_pagination.get('total_count', 0)})")
        
        # Test deleted emails
        deleted_emails, deleted_pagination = service.get_deleted_emails(per_page=5)
        print(f"   Deleted emails: {len(deleted_emails)} (total: {deleted_pagination.get('total_count', 0)})")
        
        # Test sent emails
        sent_emails, sent_pagination = service.get_sent_emails(per_page=5)
        print(f"   Sent emails: {len(sent_emails)} (total: {sent_pagination.get('total_count', 0)})")
        
        # Test draft emails
        draft_emails, draft_pagination = service.get_draft_emails(per_page=5)
        print(f"   Draft emails: {len(draft_emails)} (total: {draft_pagination.get('total_count', 0)})")
        
    except Exception as e:
        print(f"   ERROR testing folder-specific retrieval: {e}")
    
    # Test email search
    print("\n6. Testing email search...")
    try:
        search_results, search_pagination = service.get_emails_list(
            search="Security", per_page=3
        )
        print(f"   Search results for 'Security': {len(search_results)} (total: {search_pagination.get('total_count', 0)})")
        
        for result in search_results:
            print(f"     - {result.get('subject', 'No Subject')[:50]} (from: {result.get('sender_email', 'Unknown')})")
        
    except Exception as e:
        print(f"   ERROR testing search: {e}")
    
    # Test COM interface status
    print("\n7. Testing COM interface status...")
    try:
        com_status = service.get_com_status()
        print(f"   COM available: {com_status.get('available', False)}")
        print(f"   COM message: {com_status.get('message', 'N/A')}")
        
    except Exception as e:
        print(f"   ERROR testing COM interface: {e}")
    
    print("\n" + "=" * 60)
    print("MULTI-FILE STRUCTURE TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_multi_file_structure() 