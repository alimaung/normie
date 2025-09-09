#!/usr/bin/env python3
"""
Test script to verify URL cleanup functionality works correctly
"""

from continuous_updater import ContinuousExcelUpdater

def test_url_cleanup():
    """Test the URL cleanup rules with sample data"""
    
    print("Testing URL cleanup functionality...")
    
    # Create updater instance
    updater = ContinuousExcelUpdater()
    
    # Test data with URLs that should be fixed
    test_data = {
        'metadata': {
            'hyperlink_columns': ['Antrag', 'Datenblatt', 'SDB MSDS']
        },
        'data': [
            {
                'Antrag-nummer': '001',
                'Antrag': {
                    'display_text': 'Application Form',
                    'url': '\\\\Dehesdna-a009a\\projekte\\k-z\\ofs\\Dokumentenservice\\TeileundStoffe\\applications\\app001.pdf',
                    'tooltip': 'Test tooltip'
                },
                'Datenblatt': {
                    'display_text': 'Data Sheet',
                    'url': '\\\\Dehesdna-a007a\\projekte\\k-z\\ofs\\Dokumentenservice\\TeileundStoffe\\datasheets\\sheet001.pdf',
                    'tooltip': ''
                },
                'SDB MSDS': {
                    'display_text': 'Safety Sheet',
                    'url': '../datasheets/msds001.pdf',
                    'tooltip': None
                },
                'Regular_Column': 'Some text data'
            },
            {
                'Antrag-nummer': '002', 
                'Antrag': {
                    'display_text': 'HTTP Link',
                    'url': 'https://example.com/should-be-ignored',
                    'tooltip': 'This should be ignored'
                },
                'Datenblatt': None,
                'SDB MSDS': {
                    'display_text': 'Already correct', 
                    'url': '\\\\deberdna-c010a\\GlobalDE\\DocumentManagement\\Ofs\\obl\\Dokumentenservice\\TeileundStoffe\\safety\\already-correct.pdf',
                    'tooltip': 'Should not change'
                }
            }
        ]
    }
    
    print("\nOriginal URLs:")
    for i, entry in enumerate(test_data['data']):
        print(f"Entry {i+1}:")
        for col in ['Antrag', 'Datenblatt', 'SDB MSDS']:
            if col in entry and entry[col] and isinstance(entry[col], dict):
                print(f"  {col}: {entry[col]['url']}")
    
    # Run URL cleanup
    changes = updater.cleanup_urls_in_json(test_data)
    
    print(f"\nURL cleanup completed with {changes} changes")
    
    print("\nFixed URLs:")
    for i, entry in enumerate(test_data['data']):
        print(f"Entry {i+1}:")
        for col in ['Antrag', 'Datenblatt', 'SDB MSDS']:
            if col in entry and entry[col] and isinstance(entry[col], dict):
                print(f"  {col}: {entry[col]['url']}")
    
    # Check stats
    print(f"\nStatistics:")
    print(f"  Total URLs: {updater.stats['total_urls']}")
    print(f"  Fixed URLs: {updater.stats['fixed_urls']}")
    print(f"  Ignored URLs: {updater.stats['ignored_urls']}")
    print(f"  Unchanged URLs: {updater.stats['unchanged_urls']}")
    
    return changes > 0

if __name__ == "__main__":
    success = test_url_cleanup()
    if success:
        print("\n✅ URL cleanup test PASSED - URLs were fixed!")
    else:
        print("\n❌ URL cleanup test FAILED - No URLs were fixed!")
