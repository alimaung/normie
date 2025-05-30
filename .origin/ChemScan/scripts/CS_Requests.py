import requests
import json
import logging
from bs4 import BeautifulSoup
import chromedriver
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import re
from selenium import webdriver
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://app.chemscan.de"
COOKIE_FILE = Path('cookie1.json')
OUTPUT_DIR = Path('data1')

class ChemScanClient:
    def __init__(self):
        self.cookies = None
        self.headers = None
        self.session = requests.Session()
        
        # Create output directory if it doesn't exist
        OUTPUT_DIR.mkdir(exist_ok=True)
        
    def initialize(self) -> bool:
        """Initialize the client with valid cookies."""
        try:
            self.cookies = self._load_cookies()
            if not self._validate_cookies():
                logger.info("Cookies invalid or expired. Getting new cookies...")
                self.cookies = self._get_new_cookies()
                self._save_cookies(self.cookies)
            
            self._setup_headers()
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            return False
    
    def _load_cookies(self) -> Optional[List[Dict]]:
        """Load cookies from file if it exists."""
        try:
            if COOKIE_FILE.exists():
                with open(COOKIE_FILE, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.warning(f"Failed to load cookies: {str(e)}")
            return None
    
    def _save_cookies(self, cookies: List[Dict]) -> None:
        """Save cookies to file."""
        try:
            with open(COOKIE_FILE, 'w') as f:
                json.dump(cookies, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cookies: {str(e)}")
    
    def _get_new_cookies(self) -> List[Dict]:
        """Get new cookies using Selenium."""
        logger.info("Initializing Selenium to get new cookies...")

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=chrome_options)
        driver.switch_to.window(driver.window_handles[-1])
        #driver = chromedriver.init_driver()
        
        try:
            driver.get(f"{BASE_URL}/cadaster/organization/")
            cookies = driver.get_cookies()
            return cookies
        finally:
            driver.quit()
    
    def _validate_cookies(self) -> bool:
        """Check if current cookies are valid."""
        if not self.cookies:
            return False
        
        # Extract required cookies
        cookie_dict = self._format_cookies_for_requests()
        test_url = f"{BASE_URL}/cadaster/organization/"
        
        try:
            response = self.session.get(test_url, cookies=cookie_dict, timeout=10, verify=False)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def _format_cookies_for_requests(self) -> Dict[str, str]:
        """Convert cookie list to dictionary format for requests."""
        if not self.cookies:
            return {}
        
        cookie_dict = {}
        required_cookies = ['https-_csrf', 'BAPID', 'BAPRM']
        
        for cookie in self.cookies:
            if cookie.get('name') in required_cookies:
                cookie_dict[cookie['name']] = cookie['value']
        
        return cookie_dict
    
    def _setup_headers(self) -> None:
        """Set up request headers based on cookies."""
        cookie_dict = self._format_cookies_for_requests()
        csrf_token = cookie_dict.get('https-_csrf', '')
        
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache, no-store",
            "Referer": f"{BASE_URL}/cadaster/organization/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "X-Csrf-Header": csrf_token,
            "X-Requested-With": "XMLHttpRequest"
        }
    
    def fetch_data(self, internal_name_value: str) -> Optional[Dict]:
        """Fetch data for a given internal name."""
        if not self.cookies or not self.headers:
            if not self.initialize():
                return None
        
        url = f"{BASE_URL}/datagrid/uub-hazard-substance-organization-with-actions-grid"
        
        params = {
            "uub-hazard-substance-organization-with-actions-grid[originalRoute]": "uub_cadaster_organization_index",
            "appearanceType": "grid",
            "uub-hazard-substance-organization-with-actions-grid[_pager][_page]": 1,
            "uub-hazard-substance-organization-with-actions-grid[_pager][_per_page]": 25,
            "uub-hazard-substance-organization-with-actions-grid[_parameters][view]": "__all__",
            "uub-hazard-substance-organization-with-actions-grid[_appearance][_type]": "grid",
            "uub-hazard-substance-organization-with-actions-grid[_filter][internalName][value]": internal_name_value,
            "uub-hazard-substance-organization-with-actions-grid[_filter][internalName][type]": 1,
            "uub-hazard-substance-organization-with-actions-grid[_columns]": "active1.hsSds1.hsHa1.internalName1.name1.manufacturerName1.symbolSigns1.catalogRRates1.substanceName1.hazardSubstanceAssessmentBU1.hsNumber0.additionalInfo10.additionalInfo20.hsWaterHazardClass0.catalogWarehouseClass0.catalogUnNumber0.hsForm0.hsBoilingPoint0.hsFlamePoint0.sdsRequested0.sdsPrinted0.hsVocAmount0"
        }
        
        try:
            response = self.session.get(
                url, 
                headers=self.headers, 
                params=params, 
                cookies=self._format_cookies_for_requests(),
                timeout=30,
                verify=False
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch data: HTTP {response.status_code}")
                if response.status_code == 401:
                    # Try to refresh cookies and retry once
                    self.initialize()
                    return self.fetch_data(internal_name_value)
                return None
            
            data = response.json().get('data', [])
            if not data:
                logger.warning(f"No data found for internal name: {internal_name_value}")
                return None
            
            return self._process_data(data)
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return None
        except json.JSONDecodeError:
            logger.error("Failed to parse response as JSON")
            return None
    
    def _process_data(self, data: List[Dict]) -> Optional[Dict]:
        """Process the data returned from the API."""
        if not data:
            return None
        
        try:
            # Extract the view link from the first item
            link = data[0].get('view_link')
            if not link:
                logger.warning("View link not found in response data")
                return None
            
            full_url = f"{BASE_URL}{link}"
            logger.info(f"Fetching details from: {full_url}")
            
            response = self.session.get(
                full_url,
                cookies=self._format_cookies_for_requests(),
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch detail page: HTTP {response.status_code}")
                return None
            
            # Save raw HTML for debugging if needed
            with open(OUTPUT_DIR / 'last_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            return self._extract_file_data(response.text)
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return None
    
    def _extract_file_data(self, html_content: str) -> Optional[List[Dict]]:
        """Extract file information from the detail page HTML."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            widget_div = soup.find('div', {'class': 'widget-content'})
            
            if not widget_div:
                logger.warning("No 'widget-content' div found")
                return None
            
            data_options = widget_div.find('div', {'data-page-component-options': True})
            if not data_options:
                logger.warning("No 'data-page-component-options' found")
                return None
            
            # Get and parse the JSON data
            data_options_value = data_options.get('data-page-component-options')
            decoded_options = json.loads(data_options_value.replace("&quot;", "\""))
            data_items = decoded_options.get('data', {})
            
            if not data_items or 'data' not in data_items:
                logger.warning("No file data found in component options")
                return None
            
            processed_items = []
            
            for item in data_items["data"]:
                if 'originalFilename' not in item:
                    continue
                
                # Parse the embedded HTML
                original_filename = item["originalFilename"]
                file_soup = BeautifulSoup(original_filename, "html.parser")
                link_tag = file_soup.find("a")
                
                if not link_tag:
                    continue
                
                # Extract file information
                new_data = {
                    "link": link_tag.get("href", ""),
                    "filename": link_tag.get("data-filename", ""),
                    "display": link_tag.text.strip(),
                    "fileSize": item.get("fileSize", "").strip(),
                    "createdAt": item.get("createdAt", ""),
                    "comment": item.get("comment", ""),
                    "id": item.get("id", "")
                }
                
                processed_items.append(new_data)
            
            # Save processed data
            with open(OUTPUT_DIR / 'processed_items.json', 'w', encoding='utf-8') as f:
                json.dump(processed_items, f, indent=4)
            self.check_files(processed_items)
            #return processed_items
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error extracting file data: {str(e)}")
            return None

    def check_files(self, processed_items: List[Dict]) -> None:
        """Check if filename and comments have a common format and assign them."""
        print(f"Found {len(processed_items)} attachments")
        ats_count = 0
        chem_count = 0
        unrecognized_count = 0

        for item in processed_items:
            # assign files and comments to either to AT&S or ChemScan
            # comment format for AT&S is "AT&S_ID/YYYY_TKZ_LOC-CODE" * global seperator = _, AT&S = Anträge Teile und Stoffe (fixed prefix), ID/YYYY = ID number (3 digits, e.g. 087) and year (2017) seperated by / (e.g 087/2017), TKZ = Teilekennzahl (8 digits, e.g. 01042842), * LOC-CODE = either OU, DW, HH
            # filename format for AT&S is "ID-YYYY_TKZ.pdf" * global seperator = _, ID-YYYY = ID number (3 digits, e.g. 087) and year (2017) seperated by - (e.g 087-2017), TKZ = Teilekennzahl (8 digits, e.g. 01042842), .pdf file extension
            # comment format for ChemScan is "ChemScan_ID-YYYY_TKZ_LOC_CODE" * global seperator = _, ID-YYYY = ID number (3 digits, e.g. 087) and year (2017) seperated by - (e.g 087-2017), TKZ = Teilekennzahl (8 digits, e.g. 01042842), LOC-CODE = either OU, DW, HH
            # filename format for ChemScan is "ID-YYYY_NAME.pdf" * global seperator = _, ID-YYYY = ID number (3 digits, e.g. 087) and year (2017) seperated by - (e.g 087-2017), NAME = any string, .pdf file extension ** ID-YYYY is weighted more
            filename = item['filename']
            comment = item['comment']
            
            # Check for AT&S format (comment format: AT&S_087-2017_01043022_DW)
            if re.match(r"^AT&S_\d{3}-\d{4}_\d{8}_(OU|DW|HH)$", comment):#and re.match(r"^\d{3}-\d{4}_\d{8}\.pdf$", filename):
                ats_code = f"\033[38;2;16;6;159m"
                print(f"{ats_code}AT&S: {filename} ({comment})\033[0m")
                ats_count += 1

            # Check for ChemScan format (comment format: ChemScan_087-2017_01043022_DW)
            elif re.match(r"^ChemScan_\d{3}-\d{4}_\d{8}_(OU|DW|HH)$", comment): #and re.match(r"^\d{8}_.+\.pdf$", filename):
                chem_code = f"\033[38;2;134;188;36m"
                print(f"{chem_code}ChemScan: {filename} ({comment})\033[0m")
                chem_count += 1
            
            else:
                print(f"Unrecognized format: \033[31m{filename} ({comment})\033[0m")
                unrecognized_count += 1

        # Print final summary of the counts
        print(f"\nSummary: {ats_count} AT&S, {chem_count} ChemScan, {unrecognized_count} Unrecognized from {len(processed_items)} total")

def main():
    client = ChemScanClient()
    if not client.initialize():
        logger.error("Failed to initialize ChemScan client")
        return
    
    internal_name_value = input("Enter the internalName value: ")
    result = client.fetch_data(internal_name_value)
    
    if result:
        logger.info(f"Found {len(result)} items for {internal_name_value}")
        for item in result:
            print(f"File: {item['filename']} ({item['comment']})")
    else:
        logger.warning(f"No results found for {internal_name_value}")

if __name__ == "__main__":
    main()