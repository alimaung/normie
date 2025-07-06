#!/usr/bin/env python3
"""
Contact Search Tool for OAB Contacts

This script provides search functionality for contacts extracted from OAB files.
Can be used both as a standalone script and as a service in Django applications.

Usage:
    python search_contacts.py "John Smith"
    python search_contacts.py "john.smith@company.com"
    python search_contacts.py "IT Department"
"""

import json
import os
import sys
import re
from typing import List, Dict, Any, Optional, Union
from extract_contacts import extract_contacts_from_oab
from difflib import SequenceMatcher


class ContactSearcher:
    """Contact search service that can be used standalone or in Django"""
    
    def __init__(self, contacts_file: str = 'contacts.json', oab_file: str = 'udetails.oab'):
        """
        Initialize the contact searcher
        
        Args:
            contacts_file: Path to the JSON file containing extracted contacts
            oab_file: Path to the OAB file (used if contacts_file doesn't exist)
        """
        self.contacts_file = contacts_file
        self.oab_file = oab_file
        self.contacts = []
        self.load_contacts()
    
    def load_contacts(self):
        """Load contacts from JSON file or extract from OAB if needed"""
        if os.path.exists(self.contacts_file):
            try:
                with open(self.contacts_file, 'r', encoding='utf-8') as f:
                    self.contacts = json.load(f)
                print(f"Loaded {len(self.contacts)} contacts from {self.contacts_file}")
            except Exception as e:
                print(f"Error loading contacts file: {e}")
                self._extract_from_oab()
        else:
            print(f"Contacts file {self.contacts_file} not found. Extracting from OAB...")
            self._extract_from_oab()
    
    def _extract_from_oab(self):
        """Extract contacts from OAB file"""
        if os.path.exists(self.oab_file):
            print(f"Extracting contacts from {self.oab_file}...")
            self.contacts = extract_contacts_from_oab(self.oab_file)
            if self.contacts:
                # Save extracted contacts for future use
                with open(self.contacts_file, 'w', encoding='utf-8') as f:
                    json.dump(self.contacts, f, indent=2, ensure_ascii=False)
                print(f"Extracted and saved {len(self.contacts)} contacts")
        else:
            print(f"OAB file {self.oab_file} not found. Please provide a valid OAB file.")
            self.contacts = []
    
    def search(self, query: str, fields: Optional[List[str]] = None, 
               fuzzy: bool = True, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search contacts by query string
        
        Args:
            query: Search query string
            fields: List of fields to search in (None = search all text fields)
            fuzzy: Enable fuzzy matching
            limit: Maximum number of results to return
            
        Returns:
            List of matching contact dictionaries with relevance scores
        """
        if not self.contacts:
            return []
        
        # Default searchable fields
        if fields is None:
            fields = [
                'DisplayName', 'EmailAddress', 'SmtpAddress', 'GivenName', 'Surname',
                'CompanyName', 'DepartmentName', 'Title', 'OfficeLocation',
                'BusinessTelephoneNumber', 'MobileTelephoneNumber', 'Account'
            ]
        
        query_lower = query.lower().strip()
        results = []
        
        for contact in self.contacts:
            score = self._calculate_relevance(contact, query_lower, fields, fuzzy)
            if score > 0:
                result = contact.copy()
                result['_relevance_score'] = score
                results.append(result)
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x['_relevance_score'], reverse=True)
        
        return results[:limit]
    
    def _calculate_relevance(self, contact: Dict[str, Any], query: str, 
                           fields: List[str], fuzzy: bool) -> float:
        """Calculate relevance score for a contact"""
        max_score = 0.0
        
        for field in fields:
            if field not in contact:
                continue
            
            value = contact[field]
            if isinstance(value, list):
                # Handle multiple values (like proxy addresses)
                for item in value:
                    score = self._match_score(str(item).lower(), query, fuzzy)
                    max_score = max(max_score, score)
            else:
                score = self._match_score(str(value).lower(), query, fuzzy)
                max_score = max(max_score, score)
        
        return max_score
    
    def _match_score(self, text: str, query: str, fuzzy: bool) -> float:
        """Calculate match score between text and query"""
        if not text or not query:
            return 0.0
        
        # Exact match gets highest score
        if query in text:
            if query == text:
                return 1.0  # Perfect match
            elif text.startswith(query):
                return 0.9  # Prefix match
            else:
                return 0.8  # Contains match
        
        # Fuzzy matching
        if fuzzy:
            # Use SequenceMatcher for fuzzy matching
            similarity = SequenceMatcher(None, text, query).ratio()
            if similarity > 0.6:  # Threshold for fuzzy match
                return similarity * 0.7  # Scale down fuzzy matches
        
        return 0.0
    
    def search_by_field(self, field: str, value: str, exact: bool = False) -> List[Dict[str, Any]]:
        """
        Search contacts by specific field
        
        Args:
            field: Field name to search in
            value: Value to search for
            exact: Whether to use exact matching
            
        Returns:
            List of matching contacts
        """
        results = []
        value_lower = value.lower() if not exact else value
        
        for contact in self.contacts:
            if field not in contact:
                continue
            
            contact_value = contact[field]
            if isinstance(contact_value, list):
                for item in contact_value:
                    item_str = str(item)
                    if exact:
                        if item_str == value:
                            results.append(contact)
                            break
                    else:
                        if value_lower in item_str.lower():
                            results.append(contact)
                            break
            else:
                contact_str = str(contact_value)
                if exact:
                    if contact_str == value:
                        results.append(contact)
                else:
                    if value_lower in contact_str.lower():
                        results.append(contact)
        
        return results
    
    def get_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get contact by email address (exact match)"""
        email_lower = email.lower()
        
        for contact in self.contacts:
            # Check SmtpAddress
            if 'SmtpAddress' in contact and contact['SmtpAddress'].lower() == email_lower:
                return contact
            
            # Check proxy addresses
            if 'AddressBookProxyAddresses' in contact:
                for proxy in contact['AddressBookProxyAddresses']:
                    if proxy.lower().endswith(email_lower):
                        return contact
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the contact database"""
        if not self.contacts:
            return {'total_contacts': 0}
        
        stats = {
            'total_contacts': len(self.contacts),
            'field_coverage': {},
            'companies': set(),
            'departments': set(),
        }
        
        for contact in self.contacts:
            # Field coverage
            for field in contact.keys():
                if field not in stats['field_coverage']:
                    stats['field_coverage'][field] = 0
                stats['field_coverage'][field] += 1
            
            # Companies and departments
            if 'CompanyName' in contact:
                stats['companies'].add(contact['CompanyName'])
            if 'DepartmentName' in contact:
                stats['departments'].add(contact['DepartmentName'])
        
        # Convert sets to lists for JSON serialization
        stats['companies'] = list(stats['companies'])
        stats['departments'] = list(stats['departments'])
        
        # Calculate percentages for field coverage
        for field in stats['field_coverage']:
            count = stats['field_coverage'][field]
            stats['field_coverage'][field] = {
                'count': count,
                'percentage': round((count / len(self.contacts)) * 100, 1)
            }
        
        return stats


def format_contact_output(contact: Dict[str, Any], show_score: bool = False) -> str:
    """Format contact for console output"""
    lines = []
    
    # Header with name and email
    name = contact.get('DisplayName', 'Unknown')
    email = contact.get('SmtpAddress', contact.get('EmailAddress', ''))
    lines.append(f"📧 {name}")
    if email:
        lines.append(f"   Email: {email}")
    
    # Show relevance score if available
    if show_score and '_relevance_score' in contact:
        score = contact['_relevance_score']
        lines.append(f"   Relevance: {score:.2f}")
    
    # Basic info
    if 'GivenName' in contact or 'Surname' in contact:
        given = contact.get('GivenName', '')
        surname = contact.get('Surname', '')
        lines.append(f"   Name: {given} {surname}".strip())
    
    # Work info
    if 'CompanyName' in contact:
        lines.append(f"   Company: {contact['CompanyName']}")
    if 'DepartmentName' in contact:
        lines.append(f"   Department: {contact['DepartmentName']}")
    if 'Title' in contact:
        lines.append(f"   Title: {contact['Title']}")
    if 'OfficeLocation' in contact:
        lines.append(f"   Office: {contact['OfficeLocation']}")
    
    # Phone numbers
    phones = []
    if 'BusinessTelephoneNumber' in contact:
        phones.append(f"Work: {contact['BusinessTelephoneNumber']}")
    if 'MobileTelephoneNumber' in contact:
        phones.append(f"Mobile: {contact['MobileTelephoneNumber']}")
    if 'HomeTelephoneNumber' in contact:
        phones.append(f"Home: {contact['HomeTelephoneNumber']}")
    if phones:
        lines.append(f"   Phone: {', '.join(phones)}")
    
    # Address
    address_parts = []
    for field in ['StreetAddress', 'Locality', 'StateOrProvince', 'PostalCode', 'Country']:
        if field in contact and contact[field]:
            address_parts.append(contact[field])
    if address_parts:
        lines.append(f"   Address: {', '.join(address_parts)}")
    
    # Proxy addresses (additional emails)
    if 'AddressBookProxyAddresses' in contact:
        proxies = contact['AddressBookProxyAddresses']
        if len(proxies) > 1:  # More than just the main email
            lines.append(f"   Additional emails: {', '.join(proxies[1:])}")
    
    return '\n'.join(lines)


def main():
    """Main function for standalone usage"""
    if len(sys.argv) < 2:
        print("Usage: python search_contacts.py <search_query> [--limit N] [--exact] [--field FIELD]")
        print("\nExamples:")
        print("  python search_contacts.py \"John Smith\"")
        print("  python search_contacts.py \"john.smith@company.com\"")
        print("  python search_contacts.py \"IT Department\" --limit 5")
        print("  python search_contacts.py \"Manager\" --field Title")
        print("  python search_contacts.py --stats  # Show database statistics")
        sys.exit(1)
    
    # Parse arguments
    query = sys.argv[1]
    limit = 10
    exact = False
    field = None
    show_stats = False
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--limit' and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--exact':
            exact = True
            i += 1
        elif sys.argv[i] == '--field' and i + 1 < len(sys.argv):
            field = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--stats':
            show_stats = True
            i += 1
        else:
            i += 1
    
    # Initialize searcher
    searcher = ContactSearcher()
    
    if show_stats or query == '--stats':
        # Show statistics
        stats = searcher.get_statistics()
        print(f"\n📊 Contact Database Statistics")
        print(f"{'='*50}")
        print(f"Total contacts: {stats['total_contacts']}")
        print(f"Companies: {len(stats['companies'])}")
        print(f"Departments: {len(stats['departments'])}")
        
        print(f"\n📋 Field Coverage:")
        for field, data in sorted(stats['field_coverage'].items(), 
                                key=lambda x: x[1]['count'], reverse=True):
            print(f"  {field}: {data['count']} contacts ({data['percentage']}%)")
        
        if stats['companies']:
            print(f"\n🏢 Top Companies:")
            for company in sorted(stats['companies'])[:10]:
                print(f"  - {company}")
        
        if stats['departments']:
            print(f"\n🏬 Top Departments:")
            for dept in sorted(stats['departments'])[:10]:
                print(f"  - {dept}")
        
        return
    
    # Perform search
    print(f"🔍 Searching for: '{query}'")
    print(f"{'='*50}")
    
    if field:
        # Search by specific field
        results = searcher.search_by_field(field, query, exact)
        print(f"Found {len(results)} contacts in field '{field}'")
    else:
        # General search
        results = searcher.search(query, fuzzy=not exact, limit=limit)
        print(f"Found {len(results)} contacts")
    
    if not results:
        print("No contacts found.")
        return
    
    # Display results
    for i, contact in enumerate(results, 1):
        print(f"\n{i}. {format_contact_output(contact, show_score=True)}")
        
        if i < len(results):
            print("-" * 50)
    
    if len(results) == limit and not field:
        print(f"\n(Showing top {limit} results. Use --limit to see more)")


# Django service functions
def search_contacts_service(query: str, limit: int = 10, fuzzy: bool = True) -> List[Dict[str, Any]]:
    """
    Django service function for searching contacts
    
    Args:
        query: Search query
        limit: Maximum results to return
        fuzzy: Enable fuzzy matching
        
    Returns:
        List of matching contacts
    """
    searcher = ContactSearcher()
    return searcher.search(query, fuzzy=fuzzy, limit=limit)


def get_contact_by_email_service(email: str) -> Optional[Dict[str, Any]]:
    """
    Django service function for getting contact by email
    
    Args:
        email: Email address to search for
        
    Returns:
        Contact dictionary or None
    """
    searcher = ContactSearcher()
    return searcher.get_contact_by_email(email)


def get_contact_statistics_service() -> Dict[str, Any]:
    """
    Django service function for getting contact statistics
    
    Returns:
        Statistics dictionary
    """
    searcher = ContactSearcher()
    return searcher.get_statistics()


if __name__ == "__main__":
    main() 