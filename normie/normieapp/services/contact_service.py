"""
Fast Contact Autocomplete Service for Django

Uses SQLite database for lightning-fast contact searches suitable for
real-time autocomplete in email compose interface.
"""

import os
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ContactService:
    """Fast contact service using SQLite database"""
    
    def __init__(self):
        """Initialize contact service"""
        # Path to contacts database (relative to project root)
        self.db_path = Path(settings.BASE_DIR).parent / 'outlook' / 'boa' / 'contacts.db'
        self.cache_timeout = 300  # 5 minutes
        
        # Create database if it doesn't exist
        if not self.db_path.exists():
            logger.warning(f"Contact database not found at {self.db_path}")
            logger.info("Run: python outlook/boa/contacts_db.py convert outlook/boa/contacts.json")
        
        logger.debug(f"ContactService initialized with database: {self.db_path}")
    
    def search_contacts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search contacts for autocomplete
        
        Args:
            query: Search query (minimum 2 characters)
            limit: Maximum results (default 10, max 50)
            
        Returns:
            List of contact dictionaries for autocomplete
        """
        # Validate input
        if not query or len(query.strip()) < 2:
            return []
        
        # Limit results to prevent UI overload
        limit = min(max(1, limit), 50)
        query = query.strip()
        
        # Check cache first
        cache_key = f"contact_search:{query}:{limit}"
        cached_results = cache.get(cache_key)
        if cached_results is not None:
            logger.debug(f"Returning cached results for query: {query}")
            return cached_results
        
        # Check if database exists
        if not self.db_path.exists():
            logger.error(f"Contact database not found: {self.db_path}")
            return []
        
        try:
            # Connect to database
            conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            
            # Perform fast search with SQLite indexes
            query_lower = query.lower()
            
            sql = '''
                SELECT display_name, smtp_address, given_name, surname, 
                       company_name, department_name, title
                FROM contacts 
                WHERE 
                    smtp_address LIKE ? COLLATE NOCASE OR
                    display_name LIKE ? COLLATE NOCASE OR
                    given_name LIKE ? COLLATE NOCASE OR
                    surname LIKE ? COLLATE NOCASE
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
            prefix_pattern = f"{query_lower}%"
            
            params = [
                prefix_pattern,     # smtp_address LIKE
                prefix_pattern,     # display_name LIKE  
                prefix_pattern,     # given_name LIKE
                prefix_pattern,     # surname LIKE
                prefix_pattern,     # ORDER BY smtp_address priority
                prefix_pattern,     # ORDER BY display_name priority
                prefix_pattern,     # ORDER BY given_name priority
                prefix_pattern,     # ORDER BY surname priority
                limit
            ]
            
            cursor = conn.execute(sql, params)
            results = []
            
            for row in cursor.fetchall():
                contact = self._format_contact(row)
                results.append(contact)
            
            conn.close()
            
            # Cache results
            cache.set(cache_key, results, self.cache_timeout)
            
            logger.debug(f"Found {len(results)} contacts for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching contacts: {str(e)}")
            return []
    
    def _format_contact(self, row) -> Dict[str, Any]:
        """Format database row for autocomplete response"""
        display_name = row['display_name'] or ''
        smtp_address = row['smtp_address'] or ''
        given_name = row['given_name'] or ''
        surname = row['surname'] or ''
        company_name = row['company_name'] or ''
        department_name = row['department_name'] or ''
        title = row['title'] or ''
        
        # Create display name if not available
        if not display_name and (given_name or surname):
            display_name = f"{given_name} {surname}".strip()
        
        # Format for email recipient field
        if display_name and smtp_address:
            formatted_email = f"{display_name} <{smtp_address}>"
        elif smtp_address:
            formatted_email = smtp_address
        else:
            formatted_email = display_name or "Unknown Contact"
        
        # Create subtitle with company/department info
        subtitle_parts = []
        if title:
            subtitle_parts.append(title)
        if department_name:
            subtitle_parts.append(department_name)
        if company_name and company_name not in subtitle_parts:
            subtitle_parts.append(company_name)
        
        subtitle = " • ".join(subtitle_parts) if subtitle_parts else ""
        
        return {
            'name': display_name,
            'email': smtp_address,
            'formatted': formatted_email,
            'subtitle': subtitle,
            'display_name': display_name,
            'company': company_name,
            'department': department_name,
            'title': title
        }
    
    def get_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get full contact details by email address"""
        if not email or not self.db_path.exists():
            return None
        
        try:
            conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute(
                'SELECT raw_data FROM contacts WHERE smtp_address = ? COLLATE NOCASE LIMIT 1',
                (email,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return json.loads(row['raw_data'])
            return None
            
        except Exception as e:
            logger.error(f"Error getting contact by email {email}: {str(e)}")
            return None
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get contact database statistics"""
        if not self.db_path.exists():
            return {
                'available': False,
                'message': 'Contact database not found',
                'total_contacts': 0
            }
        
        try:
            conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            
            # Get total contacts
            cursor = conn.execute('SELECT COUNT(*) as total FROM contacts')
            total = cursor.fetchone()['total']
            
            # Get contacts with email
            cursor = conn.execute(
                'SELECT COUNT(*) as with_email FROM contacts WHERE smtp_address IS NOT NULL AND smtp_address != ""'
            )
            with_email = cursor.fetchone()['with_email']
            
            # Get database size
            db_size_mb = self.db_path.stat().st_size / 1024 / 1024
            
            conn.close()
            
            return {
                'available': True,
                'total_contacts': total,
                'contacts_with_email': with_email,
                'database_size_mb': round(db_size_mb, 1),
                'database_path': str(self.db_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {
                'available': False,
                'message': f'Database error: {str(e)}',
                'total_contacts': 0
            }
    
    def is_available(self) -> bool:
        """Check if contact service is available"""
        return self.db_path.exists()


# Singleton instance
_contact_service = None

def get_contact_service() -> ContactService:
    """Get singleton contact service instance"""
    global _contact_service
    if _contact_service is None:
        _contact_service = ContactService()
    return _contact_service 