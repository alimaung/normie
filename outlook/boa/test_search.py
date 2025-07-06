#!/usr/bin/env python3
"""
Test script for the contact search functionality
"""

from search_contacts import ContactSearcher, search_contacts_service, get_contact_by_email_service
import json

def test_search_functionality():
    """Test the search functionality with sample data"""
    
    # Create sample contact data for testing
    sample_contacts = [
        {
            "DisplayName": "Smith, John",
            "SmtpAddress": "john.smith@company.com",
            "GivenName": "John",
            "Surname": "Smith",
            "CompanyName": "Acme Corporation",
            "DepartmentName": "IT Development",
            "Title": "Software Engineer",
            "BusinessTelephoneNumber": "+1 555-123-4567",
            "OfficeLocation": "Building A, Floor 3"
        },
        {
            "DisplayName": "Johnson, Alice",
            "SmtpAddress": "alice.johnson@company.com",
            "GivenName": "Alice",
            "Surname": "Johnson",
            "CompanyName": "Acme Corporation",
            "DepartmentName": "Marketing",
            "Title": "Marketing Manager",
            "BusinessTelephoneNumber": "+1 555-123-4568",
            "MobileTelephoneNumber": "+1 555-987-6543"
        },
        {
            "DisplayName": "Brown, Bob",
            "SmtpAddress": "bob.brown@company.com",
            "GivenName": "Bob",
            "Surname": "Brown",
            "CompanyName": "Acme Corporation",
            "DepartmentName": "IT Development",
            "Title": "Senior Developer",
            "BusinessTelephoneNumber": "+1 555-123-4569"
        }
    ]
    
    # Save sample data to test file
    with open('test_contacts.json', 'w', encoding='utf-8') as f:
        json.dump(sample_contacts, f, indent=2, ensure_ascii=False)
    
    print("📝 Created test contact data")
    print("=" * 50)
    
    # Test the searcher
    searcher = ContactSearcher(contacts_file='test_contacts.json')
    
    # Test 1: Search by name
    print("\n🔍 Test 1: Search by name 'John'")
    results = searcher.search("John")
    print(f"Found {len(results)} results")
    for contact in results:
        print(f"  - {contact['DisplayName']} ({contact.get('SmtpAddress', 'No email')})")
    
    # Test 2: Search by email
    print("\n🔍 Test 2: Search by email 'alice.johnson@company.com'")
    results = searcher.search("alice.johnson@company.com")
    print(f"Found {len(results)} results")
    for contact in results:
        print(f"  - {contact['DisplayName']} ({contact.get('SmtpAddress', 'No email')})")
    
    # Test 3: Search by department
    print("\n🔍 Test 3: Search by department 'IT Development'")
    results = searcher.search("IT Development")
    print(f"Found {len(results)} results")
    for contact in results:
        print(f"  - {contact['DisplayName']} - {contact.get('DepartmentName', 'No dept')}")
    
    # Test 4: Search by specific field
    print("\n🔍 Test 4: Search by Title field 'Manager'")
    results = searcher.search_by_field("Title", "Manager")
    print(f"Found {len(results)} results")
    for contact in results:
        print(f"  - {contact['DisplayName']} - {contact.get('Title', 'No title')}")
    
    # Test 5: Get contact by email
    print("\n🔍 Test 5: Get contact by exact email")
    contact = searcher.get_contact_by_email("john.smith@company.com")
    if contact:
        print(f"Found: {contact['DisplayName']} - {contact.get('Title', 'No title')}")
    else:
        print("No contact found")
    
    # Test 6: Get statistics
    print("\n📊 Test 6: Database statistics")
    stats = searcher.get_statistics()
    print(f"Total contacts: {stats['total_contacts']}")
    print(f"Companies: {len(stats['companies'])}")
    print(f"Departments: {len(stats['departments'])}")
    
    # Test 7: Django service functions
    print("\n🔧 Test 7: Django service functions")
    service_results = search_contacts_service("Software", limit=5)
    print(f"Service search found {len(service_results)} results")
    
    service_contact = get_contact_by_email_service("bob.brown@company.com")
    if service_contact:
        print(f"Service email lookup found: {service_contact['DisplayName']}")
    
    print("\n✅ All tests completed!")
    
    # Clean up test file
    import os
    if os.path.exists('test_contacts.json'):
        os.remove('test_contacts.json')
        print("🧹 Cleaned up test file")

if __name__ == "__main__":
    test_search_functionality() 