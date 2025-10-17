#!/usr/bin/env python3
"""
Focused link extractor for Kanbanize OpenAPI documentation.
Discovers all API operation links and endpoints for comprehensive mirroring.
"""

import os
import time
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

class KanbanizeLinkFetcher:
    def __init__(self, base_url="https://demo.kanbanize.com/openapi", output_file="discovered_links.json"):
        self.base_url = base_url
        self.output_file = Path(output_file)
        self.driver = None
        self.chrome_process = None
        self.discovered_links = []
        
    def setup_chrome_remote(self, debug_port=9222):
        """Connect to existing Chrome instance with remote debugging."""
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"localhost:{debug_port}")
        
        try:
            print(f"Connecting to Chrome on port {debug_port}...")
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Successfully connected to Chrome!")
            return True
        except Exception as e:
            print(f"Failed to connect to Chrome: {e}")
            return False
    
    def start_chrome_with_debugging(self, debug_port=9222, user_data_dir=r"C:\Users\RAVEN\Desktop\user1"):
        """Start Chrome with remote debugging enabled."""
        import subprocess
        import platform
        import shutil
        
        user_data_path = Path(user_data_dir)
        user_data_path.mkdir(parents=True, exist_ok=True)
        print(f"Using user data directory: {user_data_path}")
        
        # Find Chrome executable
        chrome_exe = None
        if platform.system() == "Windows":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe"
            ]
            
            for path in chrome_paths:
                if Path(path).exists():
                    chrome_exe = str(path)
                    break
            
            if not chrome_exe:
                chrome_exe = shutil.which("chrome") or shutil.which("chrome.exe")
        else:
            chrome_exe = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")
        
        if not chrome_exe:
            print("Chrome executable not found!")
            return False
        
        print(f"Found Chrome at: {chrome_exe}")
        
        chrome_cmd = [
            chrome_exe,
            f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={user_data_path}",
            "--no-first-run",
            "--disable-default-apps",
            "--disable-popup-blocking",
            "--disable-translate",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-device-discovery-notifications"
        ]
        
        try:
            print(f"Starting Chrome with command:")
            print(" ".join(f'"{arg}"' if " " in arg else arg for arg in chrome_cmd))
            
            # Start Chrome process with some output for debugging
            self.chrome_process = subprocess.Popen(
                chrome_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print(f"Chrome started with PID: {self.chrome_process.pid}")
            
            # Wait for Chrome to start
            max_retries = 15
            for i in range(max_retries):
                time.sleep(2)
                
                # Check if Chrome process is still running
                if self.chrome_process.poll() is not None:
                    stdout, stderr = self.chrome_process.communicate()
                    print(f"Chrome process exited with code: {self.chrome_process.returncode}")
                    if stdout:
                        print(f"Chrome stdout: {stdout}")
                    if stderr:
                        print(f"Chrome stderr: {stderr}")
                    return False
                
                try:
                    import urllib.request
                    urllib.request.urlopen(f"http://localhost:{debug_port}/json", timeout=5)
                    print("Chrome debugging port is ready!")
                    break
                except Exception as e:
                    if i == max_retries - 1:
                        print(f"Chrome took too long to start or debugging port not accessible: {e}")
                        return False
                    print(f"Waiting for Chrome... ({i+1}/{max_retries})")
            
            return self.setup_chrome_remote(debug_port)
            
        except Exception as e:
            print(f"Failed to start Chrome: {e}")
            return False
    
    def wait_for_content_load(self, timeout=30):
        """Wait for the API documentation content to fully load."""
        try:
            print("Waiting for API content to load...")
            
            # Wait for the main elements-api component
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "elements-api"))
            )
            
            # Wait for table of contents or navigation to load
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: any([
                        driver.find_elements(By.CSS_SELECTOR, ".ElementsTableOfContentsItem"),
                        driver.find_elements(By.CSS_SELECTOR, "[class*='toc']"),
                        driver.find_elements(By.CSS_SELECTOR, "a[href*='operations']"),
                        driver.find_elements(By.CSS_SELECTOR, "[data-testid*='operation']")
                    ])
                )
                print("Navigation elements detected!")
            except TimeoutException:
                print("Navigation elements not found, checking for other content...")
            
            # Additional wait for dynamic content
            time.sleep(5)
            return True
            
        except TimeoutException:
            print(f"Timeout waiting for content to load after {timeout} seconds")
            return False
    
    def discover_api_operation_links(self):
        """Discover all API operation links using multiple strategies."""
        links = []
        
        print("Discovering API operation links...")
        
        # Strategy 1: Look for ElementsTableOfContentsItem links (like the example)
        try:
            toc_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ElementsTableOfContentsItem")
            print(f"Found {len(toc_elements)} table of contents items")
            
            for element in toc_elements:
                try:
                    href = element.get_attribute('href')
                    if href:
                        # Extract operation info
                        title_element = element.find_element(By.CSS_SELECTOR, "[title]")
                        title = title_element.get_attribute('title') if title_element else ""
                        
                        # Extract HTTP method
                        method_element = element.find_element(By.CSS_SELECTOR, ".sl-font-medium")
                        method = method_element.text.upper() if method_element else ""
                        
                        # Extract operation text
                        text_element = element.find_element(By.CSS_SELECTOR, ".sl-truncate")
                        operation_text = text_element.text if text_element else ""
                        
                        link_info = {
                            "url": href,
                            "title": title,
                            "method": method,
                            "operation_text": operation_text,
                            "source": "ElementsTableOfContentsItem"
                        }
                        links.append(link_info)
                        print(f"Found: {method} - {operation_text}")
                        
                except Exception as e:
                    print(f"Error extracting from TOC element: {e}")
                    
        except Exception as e:
            print(f"Error finding TOC elements: {e}")
        
        # Strategy 2: Look for operation-related links with href containing 'operations'
        try:
            operation_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='operations']")
            print(f"Found {len(operation_links)} operation-related links")
            
            for element in operation_links:
                try:
                    href = element.get_attribute('href')
                    text = element.text.strip()
                    
                    # Skip if we already have this link
                    if any(link['url'] == href for link in links):
                        continue
                    
                    link_info = {
                        "url": href,
                        "title": text,
                        "method": "",
                        "operation_text": text,
                        "source": "operations_href"
                    }
                    links.append(link_info)
                    print(f"Found operation link: {text}")
                    
                except Exception as e:
                    print(f"Error extracting operation link: {e}")
                    
        except Exception as e:
            print(f"Error finding operation links: {e}")
        
        # Strategy 3: Look for testid operation elements
        try:
            testid_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid*='operation']")
            print(f"Found {len(testid_elements)} testid operation elements")
            
            for element in testid_elements:
                try:
                    # Look for links within these elements
                    link_elements = element.find_elements(By.TAG_NAME, "a")
                    for link_elem in link_elements:
                        href = link_elem.get_attribute('href')
                        text = link_elem.text.strip()
                        
                        if href and not any(link['url'] == href for link in links):
                            link_info = {
                                "url": href,
                                "title": text,
                                "method": "",
                                "operation_text": text,
                                "source": "testid_operation"
                            }
                            links.append(link_info)
                            print(f"Found testid operation: {text}")
                            
                except Exception as e:
                    print(f"Error extracting from testid element: {e}")
                    
        except Exception as e:
            print(f"Error finding testid elements: {e}")
        
        # Strategy 4: Look for any links with fragments that might be API operations
        try:
            fragment_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='#']")
            print(f"Found {len(fragment_links)} fragment links")
            
            for element in fragment_links:
                try:
                    href = element.get_attribute('href')
                    text = element.text.strip()
                    
                    # Filter for likely API operation fragments
                    if (href and 
                        any(keyword in href.lower() for keyword in ['operation', 'get', 'post', 'put', 'delete', 'patch']) and
                        not any(link['url'] == href for link in links)):
                        
                        link_info = {
                            "url": href,
                            "title": text,
                            "method": "",
                            "operation_text": text,
                            "source": "fragment_link"
                        }
                        links.append(link_info)
                        print(f"Found fragment link: {text}")
                        
                except Exception as e:
                    print(f"Error extracting fragment link: {e}")
                    
        except Exception as e:
            print(f"Error finding fragment links: {e}")
        
        return links
    
    def expand_navigation_sections(self):
        """Try to expand any collapsed navigation sections to reveal more links."""
        try:
            print("Looking for expandable navigation sections...")
            
            # Look for common expansion elements
            expand_selectors = [
                "[aria-expanded='false']",
                ".collapsed",
                "[class*='expand']",
                "[class*='collapse']",
                "button[class*='chevron']",
                ".sl-chevron"
            ]
            
            expanded_count = 0
            for selector in expand_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        try:
                            # Try to click to expand
                            if element.is_displayed() and element.is_enabled():
                                self.driver.execute_script("arguments[0].click();", element)
                                expanded_count += 1
                                time.sleep(0.5)  # Small delay between clicks
                        except Exception as e:
                            continue
                except Exception as e:
                    continue
            
            if expanded_count > 0:
                print(f"Expanded {expanded_count} navigation sections")
                time.sleep(2)  # Wait for content to load after expansion
            else:
                print("No expandable sections found")
                
        except Exception as e:
            print(f"Error expanding navigation: {e}")
    
    def scroll_to_load_content(self):
        """Scroll through the page to trigger any lazy-loaded content."""
        try:
            print("Scrolling to load any lazy content...")
            
            # Get page height
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Scroll in chunks
            scroll_position = 0
            while scroll_position < total_height:
                scroll_position += viewport_height
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                time.sleep(1)  # Wait for content to load
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            print("Completed scrolling")
            
        except Exception as e:
            print(f"Error during scrolling: {e}")
    
    def fetch_all_links(self):
        """Main method to fetch all API operation links."""
        print("Starting Kanbanize API link discovery...")
        
        # Start Chrome with debugging (always start fresh instance)
        if not self.start_chrome_with_debugging():
            print("Failed to start Chrome")
            return False
        
        try:
            # Navigate to main page
            print(f"Navigating to {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for content to load
            if not self.wait_for_content_load():
                print("Content loading timeout, but continuing...")
            
            # Try to expand navigation sections
            self.expand_navigation_sections()
            
            # Scroll to load any lazy content
            self.scroll_to_load_content()
            
            # Discover all links
            self.discovered_links = self.discover_api_operation_links()
            
            # Remove duplicates based on URL
            unique_links = []
            seen_urls = set()
            for link in self.discovered_links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            self.discovered_links = unique_links
            
            print(f"\nDiscovered {len(self.discovered_links)} unique API operation links!")
            
            # Save to JSON file
            self.save_links()
            
            # Print summary
            self.print_summary()
            
            return True
            
        except Exception as e:
            print(f"Error during link discovery: {e}")
            return False
        
        finally:
            self.cleanup()
    
    def save_links(self):
        """Save discovered links to JSON file."""
        try:
            output_data = {
                "base_url": self.base_url,
                "discovery_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_links": len(self.discovered_links),
                "links": self.discovered_links
            }
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"Links saved to: {self.output_file}")
            
        except Exception as e:
            print(f"Error saving links: {e}")
    
    def print_summary(self):
        """Print a summary of discovered links."""
        print("\n" + "="*60)
        print("LINK DISCOVERY SUMMARY")
        print("="*60)
        
        # Group by source
        by_source = {}
        for link in self.discovered_links:
            source = link.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(link)
        
        for source, links in by_source.items():
            print(f"\n{source.upper()} ({len(links)} links):")
            for link in links[:5]:  # Show first 5 of each type
                method = f"[{link['method']}]" if link['method'] else ""
                print(f"  {method} {link['operation_text'][:60]}...")
                print(f"    → {link['url']}")
            if len(links) > 5:
                print(f"  ... and {len(links) - 5} more")
        
        print(f"\nTotal unique links: {len(self.discovered_links)}")
        print(f"Output file: {self.output_file}")
    
    def cleanup(self):
        """Clean up Chrome driver and process."""
        try:
            if self.driver:
                print("Closing Chrome driver...")
                self.driver.quit()
                self.driver = None
        except Exception as e:
            print(f"Error closing driver: {e}")
        
        try:
            if self.chrome_process:
                print("Terminating Chrome process...")
                self.chrome_process.terminate()
                time.sleep(2)
                if self.chrome_process.poll() is None:
                    print("Force killing Chrome process...")
                    self.chrome_process.kill()
                self.chrome_process = None
        except Exception as e:
            print(f"Error terminating Chrome process: {e}")

def test_chrome_startup():
    """Test function to verify Chrome startup without full link discovery."""
    fetcher = KanbanizeLinkFetcher()
    print("Testing Chrome startup...")
    
    if fetcher.start_chrome_with_debugging():
        print("✅ Chrome started successfully!")
        if fetcher.driver:
            print("✅ Selenium driver connected successfully!")
            try:
                print("Testing navigation to Google...")
                fetcher.driver.get("https://www.google.com")
                print("✅ Navigation test successful!")
            except Exception as e:
                print(f"❌ Navigation test failed: {e}")
        fetcher.cleanup()
        return True
    else:
        print("❌ Chrome startup failed!")
        return False

def main():
    """Main function to run the link fetcher."""
    import sys
    
    # Check if user wants to test Chrome startup only
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        return test_chrome_startup()
    
    fetcher = KanbanizeLinkFetcher()
    success = fetcher.fetch_all_links()
    
    if success:
        print("\n✅ Successfully discovered all API operation links!")
        print(f"Check {fetcher.output_file} for the complete list.")
    else:
        print("\n❌ Link discovery failed. Check the error messages above.")

if __name__ == "__main__":
    main()
