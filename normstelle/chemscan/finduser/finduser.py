import requests
import json
import os
import time
from pathlib import Path

def setup_session():
    """Setup the session with cookies and headers for ChemScan"""
    session = requests.Session()
    
    # Set user agent
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    })
    
    # Add cookies (you may need to update these with fresh values)
    session.cookies.update({
        'BAPID': 'dcf4b0c4aec1c98ac98898baba6f196e',
        'https-_csrf': 'rGPiecNFFCCYrsIk1FAdnlvEMeeHVXgAA3sjBmxL8d4'
    })
    
    # Set common headers
    session.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    })
    
    return session

def check_user_id(session, user_id):
    """Check if a user ID exists and return response info"""
    url = f"https://app.chemscan.de/user/view/{user_id}"
    
    try:
        response = session.get(url, timeout=10)
        
        return {
            'id': user_id,
            'status_code': response.status_code,
            'url': url,
            'content_length': len(response.content) if response.content else 0,
            'content_type': response.headers.get('content-type', ''),
            'success': response.status_code == 200
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'id': user_id,
            'status_code': 'ERROR',
            'url': url,
            'error': str(e),
            'success': False
        }

def save_user_html(user_id, response_content):
    """Save user HTML content to file"""
    users_dir = Path('users')
    users_dir.mkdir(exist_ok=True)
    
    filename = f"user_{user_id}.html"
    filepath = users_dir / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response_content)
        return True
    except Exception as e:
        print(f"Error saving user {user_id}: {e}")
        return False

def save_results_json(results, filename='user_scan_results.json'):
    """Save the scan results to JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    """Main function to scan user IDs from 1 to 375"""
    print("Starting ChemScan user discovery...")
    print("Scanning user IDs from 1 to 375")
    print("=" * 50)
    
    # Setup session
    session = setup_session()
    
    # Results storage
    results = {
        'summary': {
            'total_scanned': 0,
            'found_users': 0,
            'not_found': 0,
            'errors': 0,
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'response_codes': [],
        'found_users': [],
        'errors': []
    }
    
    # Scan each user ID
    for user_id in range(372, 376):  # 1 to 375 inclusive
        print(f"Checking user ID {user_id}...", end=' ')
        
        # Check user
        result = check_user_id(session, user_id)
        results['summary']['total_scanned'] += 1
        
        # Record response code
        results['response_codes'].append({
            'id': user_id,
            'code': result['status_code']
        })
        
        if result['success']:
            # User found (HTTP 200)
            results['summary']['found_users'] += 1
            results['found_users'].append(result)
            print(f"✓ FOUND (200) - Content: {result['content_length']} bytes")
            
            # Try to get the actual content and save it
            try:
                response = session.get(result['url'])
                if response.status_code == 200 and response.content:
                    if save_user_html(user_id, response.text):
                        print(f"  → Saved to users/user_{user_id}.html")
                    else:
                        print(f"  → Failed to save HTML")
            except Exception as e:
                print(f"  → Error saving: {e}")
                
        elif result['status_code'] == 404:
            # User not found
            results['summary']['not_found'] += 1
            print("✗ Not found (404)")
            
        elif result['status_code'] == 403:
            # Forbidden - might indicate authentication issues
            results['summary']['errors'] += 1
            results['errors'].append(result)
            print("⚠ Forbidden (403) - Check authentication")
            
        elif result['status_code'] == 'ERROR':
            # Network or other error
            results['summary']['errors'] += 1
            results['errors'].append(result)
            print(f"✗ ERROR - {result.get('error', 'Unknown error')}")
            
        else:
            # Other status code
            results['summary']['errors'] += 1
            results['errors'].append(result)
            print(f"? Unexpected status: {result['status_code']}")
        
        # Rate limiting - be nice to the server
        if user_id % 10 == 0:
            print(f"  → Progress: {user_id}/375 ({user_id/375*100:.1f}%) - Found: {results['summary']['found_users']}")
            time.sleep(1)  # Brief pause every 10 requests
        else:
            time.sleep(0.2)  # Small delay between requests
    
    # Finalize results
    results['summary']['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Save results
    save_results_json(results)
    
    # Print summary
    print("\n" + "=" * 50)
    print("USER DISCOVERY SUMMARY")
    print("=" * 50)
    print(f"Total IDs scanned: {results['summary']['total_scanned']}")
    print(f"Users found (200): {results['summary']['found_users']}")
    print(f"Not found (404): {results['summary']['not_found']}")
    print(f"Errors/Other: {results['summary']['errors']}")
    print(f"Success rate: {results['summary']['found_users']/results['summary']['total_scanned']*100:.1f}%")
    
    if results['found_users']:
        print(f"\n✓ FOUND USER IDs:")
        for user in results['found_users']:
            print(f"  - ID {user['id']}: {user['content_length']} bytes")
    
    if results['errors']:
        print(f"\n⚠ ERRORS/ISSUES:")
        for error in results['errors'][:10]:  # Show first 10 errors
            print(f"  - ID {error['id']}: {error['status_code']} - {error.get('error', 'No details')}")
        if len(results['errors']) > 10:
            print(f"  ... and {len(results['errors']) - 10} more errors")
    
    print(f"\nResults saved to user_scan_results.json")
    if results['summary']['found_users'] > 0:
        print(f"User HTML files saved to users/ directory")

if __name__ == "__main__":
    main()
