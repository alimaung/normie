#!/usr/bin/env python3
"""
SQLite-based Contact Database for Fast Autocomplete

Converts large JSON contact files to SQLite database with proper indexing
for fast autocomplete searches.
"""

import sqlite3
import json
import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path
import time
import re


class ContactDatabase:
    """Fast SQLite-based contact database for autocomplete functionality"""
    
    def __init__(self, db_path: str = 'contacts.db'):
        """Initialize the contact database"""
        self.db_path = Path(db_path)
        self.conn = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize SQLite database with proper schema and indexes"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        
        # Create contacts table with optimized schema
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                display_name TEXT,
                smtp_address TEXT,
                email_address TEXT,
                given_name TEXT,
                surname TEXT,
                company_name TEXT,
                department_name TEXT,
                title TEXT,
                business_phone TEXT,
                mobile_phone TEXT,
                office_location TEXT,
                search_text TEXT,  -- Combined searchable text
                raw_data JSON      -- Full contact data as JSON
            )
        ''')
        
        # Create indexes for fast autocomplete searches
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_display_name ON contacts(display_name)',
            'CREATE INDEX IF NOT EXISTS idx_smtp_address ON contacts(smtp_address)',
            'CREATE INDEX IF NOT EXISTS idx_given_name ON contacts(given_name)',
            'CREATE INDEX IF NOT EXISTS idx_surname ON contacts(surname)',
            'CREATE INDEX IF NOT EXISTS idx_search_text ON contacts(search_text)',
            'CREATE INDEX IF NOT EXISTS idx_company ON contacts(company_name)',
            'CREATE INDEX IF NOT EXISTS idx_department ON contacts(department_name)',
        ]
        
        for index_sql in indexes:
            self.conn.execute(index_sql)
        
        self.conn.commit()
    
    def import_from_json(self, json_file: str, progress_callback=None):
        """Import contacts from JSON file with progress tracking"""
        print(f"Importing contacts from {json_file}...")
        
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"JSON file not found: {json_file}")
        
        # Clear existing data
        self.conn.execute('DELETE FROM contacts')
        
        start_time = time.time()
        
        with open(json_file, 'r', encoding='utf-8') as f:
            contacts = json.load(f)
        
        total_contacts = len(contacts)
        print(f"Processing {total_contacts} contacts...")
        
        # Batch insert for better performance
        batch_size = 1000
        batch = []
        
        for i, contact in enumerate(contacts):
            # Extract key fields
            display_name = contact.get('DisplayName', '')
            smtp_address = contact.get('SmtpAddress', '')
            email_address = contact.get('EmailAddress', '')
            given_name = contact.get('GivenName', '')
            surname = contact.get('Surname', '')
            company_name = contact.get('CompanyName', '')
            department_name = contact.get('DepartmentName', '')
            title = contact.get('Title', '')
            business_phone = contact.get('BusinessTelephoneNumber', '')
            mobile_phone = contact.get('MobileTelephoneNumber', '')
            office_location = contact.get('OfficeLocation', '')
            
            # Create searchable text (lowercased for case-insensitive search)
            search_parts = [
                display_name, smtp_address, given_name, surname,
                company_name, department_name, title
            ]
            search_text = ' '.join(filter(None, search_parts)).lower()
            
            # Store raw data as JSON string
            raw_data = json.dumps(contact, ensure_ascii=False)
            
            batch.append((
                display_name, smtp_address, email_address, given_name, surname,
                company_name, department_name, title, business_phone, mobile_phone,
                office_location, search_text, raw_data
            ))
            
            # Insert batch when full
            if len(batch) >= batch_size:
                self._insert_batch(batch)
                batch = []
                
                if progress_callback:
                    progress_callback(i + 1, total_contacts)
                elif i % 5000 == 0:
                    print(f"Processed {i + 1}/{total_contacts} contacts...")
        
        # Insert remaining contacts
        if batch:
            self._insert_batch(batch)
        
        self.conn.commit()
        
        elapsed = time.time() - start_time
        print(f"✅ Imported {total_contacts} contacts in {elapsed:.2f} seconds")
        print(f"📊 Database size: {self.db_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    def _insert_batch(self, batch):
        """Insert a batch of contacts"""
        self.conn.executemany('''
            INSERT INTO contacts (
                display_name, smtp_address, email_address, given_name, surname,
                company_name, department_name, title, business_phone, mobile_phone,
                office_location, search_text, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', batch)
    
    def search_for_autocomplete(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fast autocomplete search optimized for recipient fields
        
        Args:
            query: Search query (partial name/email)
            limit: Maximum results to return
            
        Returns:
            List of contact dictionaries suitable for autocomplete
        """
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip().lower()
        
        # Use LIKE with indexes for fast prefix matching
        sql = '''
            SELECT display_name, smtp_address, given_name, surname, 
                   company_name, department_name, title
            FROM contacts 
            WHERE 
                display_name LIKE ? COLLATE NOCASE OR
                smtp_address LIKE ? COLLATE NOCASE OR
                given_name LIKE ? COLLATE NOCASE OR
                surname LIKE ? COLLATE NOCASE OR
                search_text LIKE ? COLLATE NOCASE
            ORDER BY 
                CASE 
                    WHEN smtp_address LIKE ? COLLATE NOCASE THEN 1
                    WHEN display_name LIKE ? COLLATE NOCASE THEN 2
                    WHEN given_name LIKE ? COLLATE NOCASE THEN 3
                    WHEN surname LIKE ? COLLATE NOCASE THEN 4
                    ELSE 5
                END,
                display_name
            LIMIT ?
        '''
        
        # Create search patterns
        prefix_pattern = f"{query}%"
        contains_pattern = f"%{query}%"
        
        params = [
            prefix_pattern,     # display_name LIKE
            prefix_pattern,     # smtp_address LIKE  
            prefix_pattern,     # given_name LIKE
            prefix_pattern,     # surname LIKE
            contains_pattern,   # search_text LIKE
            prefix_pattern,     # ORDER BY smtp_address priority
            prefix_pattern,     # ORDER BY display_name priority
            prefix_pattern,     # ORDER BY given_name priority
            prefix_pattern,     # ORDER BY surname priority
            limit
        ]
        
        cursor = self.conn.execute(sql, params)
        results = []
        
        for row in cursor.fetchall():
            # Format for autocomplete dropdown
            contact = {
                'display_name': row['display_name'] or '',
                'email': row['smtp_address'] or '',
                'name': row['display_name'] or f"{row['given_name']} {row['surname']}".strip(),
                'company': row['company_name'] or '',
                'department': row['department_name'] or '',
                'title': row['title'] or '',
                'formatted': self._format_contact_for_display(row)
            }
            results.append(contact)
        
        return results
    
    def _format_contact_for_display(self, row) -> str:
        """Format contact for autocomplete display"""
        name = row['display_name'] or f"{row['given_name']} {row['surname']}".strip()
        email = row['smtp_address'] or ''
        
        if name and email:
            return f"{name} <{email}>"
        elif email:
            return email
        elif name:
            return name
        else:
            return "Unknown Contact"
    
    def get_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get full contact details by email address"""
        cursor = self.conn.execute(
            'SELECT raw_data FROM contacts WHERE smtp_address = ? COLLATE NOCASE LIMIT 1',
            (email,)
        )
        row = cursor.fetchone()
        
        if row:
            return json.loads(row['raw_data'])
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        cursor = self.conn.execute('SELECT COUNT(*) as total FROM contacts')
        total = cursor.fetchone()['total']
        
        cursor = self.conn.execute('SELECT COUNT(*) as with_email FROM contacts WHERE smtp_address IS NOT NULL AND smtp_address != ""')
        with_email = cursor.fetchone()['with_email']
        
        cursor = self.conn.execute('SELECT COUNT(*) as with_phone FROM contacts WHERE business_phone IS NOT NULL AND business_phone != ""')
        with_phone = cursor.fetchone()['with_phone']
        
        return {
            'total_contacts': total,
            'contacts_with_email': with_email,
            'contacts_with_phone': with_phone,
            'database_size_mb': self.db_path.stat().st_size / 1024 / 1024 if self.db_path.exists() else 0
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()


def convert_json_to_db(json_file: str, db_file: str = 'contacts.db'):
    """Convert JSON contact file to SQLite database"""
    print(f"Converting {json_file} to SQLite database {db_file}")
    
    # Remove existing database
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Removed existing database: {db_file}")
    
    # Create new database and import
    db = ContactDatabase(db_file)
    
    def progress_callback(current, total):
        if current % 5000 == 0 or current == total:
            percentage = (current / total) * 100
            print(f"Progress: {current}/{total} ({percentage:.1f}%)")
    
    db.import_from_json(json_file, progress_callback)
    
    # Show statistics
    stats = db.get_stats()
    print(f"\n📊 Database Statistics:")
    print(f"  Total contacts: {stats['total_contacts']:,}")
    print(f"  With email: {stats['contacts_with_email']:,}")
    print(f"  With phone: {stats['contacts_with_phone']:,}")
    print(f"  Database size: {stats['database_size_mb']:.1f} MB")
    
    db.close()
    return db_file


def test_autocomplete_performance(db_file: str = 'contacts.db'):
    """Test autocomplete performance"""
    print(f"\n🚀 Testing autocomplete performance...")
    
    db = ContactDatabase(db_file)
    
    test_queries = ['john', 'smith', 'alice', 'bob', 'dev', 'manager', 'IT']
    
    for query in test_queries:
        start_time = time.time()
        results = db.search_for_autocomplete(query, limit=10)
        elapsed = time.time() - start_time
        
        print(f"Query '{query}': {len(results)} results in {elapsed*1000:.2f}ms")
        
        # Show first few results
        for i, contact in enumerate(results[:3]):
            print(f"  {i+1}. {contact['formatted']}")
        
        if len(results) > 3:
            print(f"  ... and {len(results) - 3} more")
        print()
    
    db.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  {sys.argv[0]} convert <json_file> [db_file]")
        print(f"  {sys.argv[0]} test [db_file]")
        print(f"  {sys.argv[0]} search <query> [db_file]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'convert':
        json_file = sys.argv[2]
        db_file = sys.argv[3] if len(sys.argv) > 3 else 'contacts.db'
        convert_json_to_db(json_file, db_file)
    
    elif command == 'test':
        db_file = sys.argv[2] if len(sys.argv) > 2 else 'contacts.db'
        test_autocomplete_performance(db_file)
    
    elif command == 'search':
        query = sys.argv[2]
        db_file = sys.argv[3] if len(sys.argv) > 3 else 'contacts.db'
        
        db = ContactDatabase(db_file)
        results = db.search_for_autocomplete(query, limit=20)
        
        print(f"Search results for '{query}':")
        for i, contact in enumerate(results, 1):
            print(f"{i:2}. {contact['formatted']}")
            if contact['company']:
                print(f"     {contact['company']} - {contact['department']}")
        
        db.close()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1) 