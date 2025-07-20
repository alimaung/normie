import requests
from datetime import datetime
import os
import re
import time
import pickle
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ChemScanClient:
    def __init__(self, cookies_file='chemscan_cookies.pkl', session_file='chemscan_session.json'):
        self.session = requests.Session()
        self.base_url = "https://app.chemscan.de"
        self.is_authenticated = False
        self.cookies_file = cookies_file
        self.session_file = session_file
        self.username = os.getenv('CHEMSCAN_USER')
        self.password = os.getenv('CHEMSCAN_KEY')
        
        # Set common headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Try to load existing session
        self.load_session()
    
    def save_session(self):
        """
        Save cookies and session info to files
        """
        try:
            # Save cookies
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(self.session.cookies, f)
            
            # Save session metadata
            session_data = {
                'is_authenticated': self.is_authenticated,
                'last_login': datetime.now().isoformat(),
                'base_url': self.base_url
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            print(f"✓ Session saved to {self.cookies_file} and {self.session_file}")
            
        except Exception as e:
            print(f"⚠ Failed to save session: {e}")
    
    def load_session(self):
        """
        Load cookies and session info from files
        """
        try:
            # Load cookies if they exist
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                    self.session.cookies.update(cookies)
                print(f"✓ Loaded cookies from {self.cookies_file}")
            
            # Load session metadata
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                    self.is_authenticated = session_data.get('is_authenticated', False)
                    last_login = session_data.get('last_login')
                    
                    if last_login:
                        print(f"✓ Last login: {last_login}")
                
                print(f"✓ Loaded session metadata from {self.session_file}")
            
        except Exception as e:
            print(f"⚠ Failed to load session: {e}")
            self.is_authenticated = False
    
    def clear_session(self):
        """
        Clear saved session files
        """
        try:
            if os.path.exists(self.cookies_file):
                os.remove(self.cookies_file)
                print(f"✓ Removed {self.cookies_file}")
            
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
                print(f"✓ Removed {self.session_file}")
                
            self.is_authenticated = False
            self.session.cookies.clear()
            
        except Exception as e:
            print(f"⚠ Failed to clear session: {e}")

    def is_session_valid(self):
        """
        Check if current session is still authenticated
        """
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            # If we get redirected to login page, session is invalid
            if '/user/login' in response.url:
                self.is_authenticated = False
                return False
            self.is_authenticated = True
            return True
        except:
            return False
    
    def fetch_login_page(self):
        """
        Fetch the login page and extract CSRF token
        """
        print("Fetching login page...")
        
        try:
            response = self.session.get(f"{self.base_url}/user/login", timeout=30)
            response.raise_for_status()
            
            # Save the login page HTML
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chemscan_login_page_{timestamp}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"✓ Login page saved to: {filename}")
            
            # Extract CSRF token with multiple strategies
            csrf_token = self._extract_csrf_token(response.text)
            
            if csrf_token:
                print(f"✓ CSRF token extracted: {csrf_token[:20]}...")
            else:
                print("⚠ CSRF token not found - login might still work")
            
            return csrf_token, response.text
            
        except Exception as e:
            print(f"✗ Error fetching login page: {e}")
            return None, None
    
    def _extract_csrf_token(self, html):
        """
        Extract CSRF token using multiple strategies
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Strategy 1: Look for _csrf_token input field
        csrf_input = soup.find('input', {'name': '_csrf_token'})
        if csrf_input and csrf_input.get('value'):
            return csrf_input.get('value')
        
        # Strategy 2: Look for csrf-token meta tag
        csrf_meta = soup.find('meta', {'name': 'csrf-token'})
        if csrf_meta and csrf_meta.get('content'):
            return csrf_meta.get('content')
        
        # Strategy 3: Look for token in script tags (common pattern)
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for common CSRF token patterns
                token_match = re.search(r'["\']_token["\']:\s*["\']([^"\']+)["\']', script.string)
                if token_match:
                    return token_match.group(1)
                
                token_match = re.search(r'csrf[_-]?token["\']:\s*["\']([^"\']+)["\']', script.string, re.IGNORECASE)
                if token_match:
                    return token_match.group(1)
        
        return None
    
    def login(self, username, password, max_retries=3):
        """
        Perform automatic login with retry logic
        """
        print("Starting automatic login process...")
        
        for attempt in range(max_retries):
            if attempt > 0:
                print(f"Retry attempt {attempt + 1}/{max_retries}")
                time.sleep(2)  # Wait before retry
            
            # First, get the login page and CSRF token
            csrf_token, login_html = self.fetch_login_page()
            
            if login_html is None:
                print("✗ Failed to fetch login page")
                continue
            
            # Prepare login data
            login_data = {
                '_username': username,
                '_password': password,
                '_remember_me': 'on',
                '_target_path': '',
            }
            
            # Add CSRF token if found
            if csrf_token:
                login_data['_csrf_token'] = csrf_token
            
            # Update headers for POST request
            self.session.headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': self.base_url,
                'Referer': f"{self.base_url}/user/login",
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            })
            
            try:
                print("Submitting login form...")
                response = self.session.post(
                    f"{self.base_url}/user/login-check",
                    data=login_data,
                    allow_redirects=False,  # Don't follow redirects automatically
                    timeout=30
                )
                
                print(f"✓ Login response status: {response.status_code}")
                
                # Check if login was successful
                if response.status_code == 302:
                    redirect_location = response.headers.get('location', '')
                    print(f"✓ Login successful! Redirecting to: {redirect_location}")
                    
                    # Verify session is actually valid
                    if self.is_session_valid():
                        print("✓ Session validation successful!")
                        self.is_authenticated = True
                        
                        # Save session for persistence
                        self.save_session()
                        
                        # Show cookies for debugging
                        print("✓ Session cookies:")
                        for cookie in self.session.cookies:
                            print(f"  - {cookie.name}: {cookie.value[:20]}...")
                        
                        return True
                    else:
                        print("⚠ Login appeared successful but session validation failed")
                        continue
                        
                elif response.status_code == 200:
                    # Login form returned - likely failed
                    print("✗ Login failed - returned to login form")
                    if "error" in response.text.lower() or "invalid" in response.text.lower():
                        print("✗ Detected error message in response")
                    continue
                    
                else:
                    print(f"✗ Unexpected response status: {response.status_code}")
                    continue
                    
            except Exception as e:
                print(f"✗ Error during login attempt {attempt + 1}: {e}")
                continue
        
        print(f"✗ Login failed after {max_retries} attempts")
        return False
    
    def fetch_authenticated_page(self, path="", auto_login_if_needed=True):
        """
        Fetch a page after successful login, with automatic re-authentication
        """
        # Check if we need to re-authenticate
        if auto_login_if_needed and not self.is_session_valid():
            print("⚠ Session expired, attempting re-login...")
            
            if self.username and self.password:
                print("✓ Found stored credentials, attempting automatic re-login...")
                if not self.login(self.username, self.password):
                    print("✗ Automatic re-login failed")
                    return None, None
            else:
                print("✗ No stored credentials available for automatic re-login")
                print("  Please set CHEMSCAN_USER and CHEMSCAN_KEY environment variables")
                return None, None
        
        try:
            url = f"{self.base_url}/{path}" if path else self.base_url
            print(f"Fetching authenticated page: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if we got redirected to login (session expired)
            if '/user/login' in response.url:
                print("✗ Session expired - redirected to login page")
                self.is_authenticated = False
                return None, None
            
            # Save the authenticated page
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page_name = path.replace('/', '_') if path else 'dashboard'
            filename = f"chemscan_{page_name}_{timestamp}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"✓ Authenticated page saved to: {filename}")
            print(f"✓ Page size: {len(response.text)} characters")
            
            return filename, response.text
            
        except Exception as e:
            print(f"✗ Error fetching authenticated page: {e}")
            return None, None
    
    def fetch_all_grid_data(self):
        """
        Fetch all data from the hazardous substance grid (all pages)
        """
        print("Fetching all grid data...")
        
        if not self.is_session_valid():
            print("✗ Session not valid for grid data fetching")
            return None
        
        # Get CSRF token from cookies for API requests
        csrf_token = None
        for cookie in self.session.cookies:
            if cookie.name == 'https-_csrf':
                csrf_token = cookie.value
                break
        
        if not csrf_token:
            print("✗ CSRF token not found in cookies")
            return None
        
        # Set up headers for API requests
        api_headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache, no-store",
            "Referer": f"{self.base_url}/cadaster/organization/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "X-Csrf-Header": csrf_token,
            "X-Requested-With": "XMLHttpRequest"
        }
        
        # API endpoint
        api_url = f"{self.base_url}/datagrid/uub-hazard-substance-organization-with-actions-grid"
        
        all_data = []
        page = 1
        total_pages = 13  # We know there are 13 pages
        
        print(f"Fetching {total_pages} pages of data...")
        
        while page <= total_pages:
            print(f"Fetching page {page}/{total_pages}...")
            
            # Parameters for the API request
            params = {
                "uub-hazard-substance-organization-with-actions-grid[originalRoute]": "uub_cadaster_organization_index",
                "appearanceType": "grid",
                "uub-hazard-substance-organization-with-actions-grid[_pager][_page]": page,
                "uub-hazard-substance-organization-with-actions-grid[_pager][_per_page]": 100,  # Max items per page
                "uub-hazard-substance-organization-with-actions-grid[_parameters][view]": "__all__",
                "uub-hazard-substance-organization-with-actions-grid[_appearance][_type]": "grid",
                "uub-hazard-substance-organization-with-actions-grid[_columns]": "active1.hsSds1.hsHa1.internalName1.name1.alternativeName1.manufacturerName1.symbolSigns1.catalogRRates1.substanceName1.hazardSubstanceAssessmentBU1.responsibleUserGroup1.hsNumber0.additionalInfo10.additionalInfo20.hsWaterHazardClass1.catalogWarehouseClass0.catalogUnNumber0.hsForm0.hsBoilingPoint0.hsFlamePoint0.sdsRequested0.sdsPrinted0.hsVocAmount0"
            }
            
            try:
                response = self.session.get(
                    api_url,
                    headers=api_headers,
                    params=params,
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"✗ Failed to fetch page {page}: HTTP {response.status_code}")
                    if response.status_code == 401:
                        print("✗ Authentication failed - session may have expired")
                        return None
                    page += 1
                    continue
                
                try:
                    page_data = response.json()
                    items = page_data.get('data', [])
                    
                    if not items:
                        print(f"⚠ No data found on page {page}")
                        break
                    
                    print(f"✓ Page {page}: Found {len(items)} items")
                    all_data.extend(items)
                    
                    # Check if we've reached the end
                    total_records = page_data.get('options', {}).get('totalRecords', 0)
                    if total_records > 0:
                        actual_total_pages = (total_records + 99) // 100  # Calculate actual pages
                        if actual_total_pages != total_pages:
                            print(f"✓ Updated total pages: {actual_total_pages} (was {total_pages})")
                            total_pages = actual_total_pages
                    
                except json.JSONDecodeError:
                    print(f"✗ Failed to parse JSON response for page {page}")
                    print(f"Response content: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"✗ Error fetching page {page}: {e}")
            
            page += 1
            time.sleep(0.5)  # Small delay to be respectful
        
        print(f"✓ Completed fetching all pages. Total items: {len(all_data)}")
        
        # Save the complete dataset
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"chemscan_all_data_{timestamp}.json"
        
        try:
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'total_items': len(all_data),
                        'total_pages': total_pages,
                        'fetched_at': datetime.now().isoformat(),
                        'source': 'ChemScan Cadaster Organization Grid'
                    },
                    'data': all_data
                }, f, indent=2, ensure_ascii=False)
            
            print(f"✓ All data saved to: {json_filename}")
            print(f"✓ Total records: {len(all_data)}")
            
            # Show sample of first few items
            if all_data:
                print("\n--- Sample of first item ---")
                first_item = all_data[0]
                for key, value in list(first_item.items())[:5]:
                    print(f"{key}: {value}")
                print("...")
            
            return json_filename, all_data
            
        except Exception as e:
            print(f"✗ Failed to save JSON file: {e}")
            return None, all_data

def main():
    print("ChemScan Automatic Login")
    print("=" * 40)
    
    # Initialize client
    client = ChemScanClient()
    
    # Check if credentials are available
    if not client.username or not client.password:
        print("✗ Missing credentials!")
        print("  Please set environment variables:")
        print("  CHEMSCAN_USER=your_email@domain.com")
        print("  CHEMSCAN_KEY=your_password")
        return
    
    print(f"✓ Using credentials for: {client.username}")
    
    # Check if we already have a valid session
    if client.is_session_valid():
        print("✓ Found valid existing session, skipping login")
    else:
        print("⚠ No valid session found, performing login...")
        # Perform login with retries
        if not client.login(client.username, client.password, max_retries=3):
            print("\n✗ Login failed after all retry attempts!")
            return
    
        # Continue with the authenticated request
    print("\n" + "=" * 40)
    print("Fetching ALL hazardous substance data...")
    
    # Fetch all grid data from all pages
    json_filename, all_data = client.fetch_all_grid_data()
    
    if json_filename and all_data:
        print(f"✓ All data successfully fetched and saved!")
        print(f"✓ JSON file: {json_filename}")
        print(f"✓ Total records: {len(all_data)}")
        
        # Show some statistics
        if all_data:
            print("\n--- Data Statistics ---")
            
            # Count active vs inactive
            active_count = sum(1 for item in all_data if item.get('active') == '1')
            inactive_count = len(all_data) - active_count
            print(f"Active substances: {active_count}")
            print(f"Inactive substances: {inactive_count}")
            
            # Show unique manufacturers (first 10)
            manufacturers = set()
            for item in all_data:
                if item.get('manufacturerName'):
                    manufacturers.add(item['manufacturerName'])
            print(f"Unique manufacturers: {len(manufacturers)}")
            if manufacturers:
                print("Sample manufacturers:", list(manufacturers)[:5])
            
            # Show sample internal names
            internal_names = [item.get('internalName', 'N/A') for item in all_data[:5]]
            print(f"Sample internal names: {internal_names}")
            
    else:
        print("✗ Failed to fetch all grid data")
    
    print("\n✓ Process completed successfully!")

if __name__ == "__main__":
    main()
