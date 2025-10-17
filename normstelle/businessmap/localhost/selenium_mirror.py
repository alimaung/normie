#!/usr/bin/env python3
"""
Selenium-based web scraper to capture fully rendered Kanbanize OpenAPI documentation.
Uses existing Chrome instance with remote debugging on port 9222.
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
import requests
from bs4 import BeautifulSoup

class SeleniumKanbanizeMirror:
    def __init__(self, base_url="https://demo.kanbanize.com/openapi", output_dir="openapi_rendered"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.driver = None
        self.chrome_process = None
        self.downloaded_assets = set()
        
    def setup_chrome_remote(self, debug_port=9222, user_data_dir=r"C:\Users\RAVEN\Desktop\user1"):
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
        
        # Use the provided user data directory directly
        user_data_path = Path(user_data_dir)
        
        user_data_path.mkdir(parents=True, exist_ok=True)
        print(f"Using user data directory: {user_data_path}")
        
        # Find Chrome executable
        chrome_exe = None
        if platform.system() == "Windows":
            # Common Chrome installation paths on Windows
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe"
            ]
            
            for path in chrome_paths:
                if Path(path).exists():
                    chrome_exe = str(path)
                    break
            
            # Also try finding chrome in PATH
            if not chrome_exe:
                chrome_exe = shutil.which("chrome") or shutil.which("chrome.exe")
        else:
            # Linux/Mac
            chrome_exe = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")
        
        if not chrome_exe:
            print("Chrome executable not found!")
            print("Please make sure Chrome is installed in one of these locations:")
            if platform.system() == "Windows":
                print("- C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
                print("- C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe")
            else:
                print("- google-chrome (in PATH)")
                print("- chromium (in PATH)")
            return False
        
        print(f"Found Chrome at: {chrome_exe}")
        
        # Build Chrome command - keep it simple
        chrome_cmd = [
            chrome_exe,
            f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={user_data_path}"
        ]
        
        try:
            print(f"Starting Chrome with command:")
            print(" ".join(f'"{arg}"' if " " in arg else arg for arg in chrome_cmd))
            
            # Start Chrome process
            self.chrome_process = subprocess.Popen(
                chrome_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            print(f"Chrome started with PID: {self.chrome_process.pid}")
            print(f"Waiting for Chrome to initialize on port {debug_port}...")
            
            # Wait for Chrome to start and be ready
            max_retries = 15
            for i in range(max_retries):
                time.sleep(2)
                try:
                    # Test if Chrome debugging port is ready
                    import urllib.request
                    urllib.request.urlopen(f"http://localhost:{debug_port}/json", timeout=5)
                    print("Chrome debugging port is ready!")
                    break
                except:
                    if i == max_retries - 1:
                        print("Chrome took too long to start or debugging port not accessible")
                        return False
                    print(f"Waiting for Chrome... ({i+1}/{max_retries})")
            
            # Now connect to Chrome
            return self.setup_chrome_remote(debug_port, user_data_dir)
            
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
            
            # Wait a bit more for dynamic content
            time.sleep(5)
            
            # Try to wait for specific API content indicators
            try:
                # Look for common API documentation elements
                WebDriverWait(self.driver, 10).until(
                    lambda driver: any([
                        driver.find_elements(By.CSS_SELECTOR, "[data-testid*='operation']"),
                        driver.find_elements(By.CSS_SELECTOR, ".sl-stack"),
                        driver.find_elements(By.CSS_SELECTOR, "[class*='endpoint']"),
                        driver.find_elements(By.CSS_SELECTOR, "[class*='method']")
                    ])
                )
                print("API content elements detected!")
            except TimeoutException:
                print("Specific API elements not found, but proceeding...")
            
            # Additional wait for any async loading
            time.sleep(3)
            return True
            
        except TimeoutException:
            print(f"Timeout waiting for content to load after {timeout} seconds")
            return False
    
    def extract_rendered_html(self):
        """Extract the fully rendered HTML from the current page."""
        try:
            # Get the page source after all JavaScript has executed
            html_content = self.driver.page_source
            
            # Parse with BeautifulSoup for cleaning
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script tags that might cause issues offline
            for script in soup.find_all('script'):
                if script.get('src') and 'http' in script.get('src'):
                    # Keep local scripts, remove external ones
                    if not any(domain in script.get('src') for domain in ['demo.kanbanize.com']):
                        script.decompose()
            
            return str(soup)
            
        except Exception as e:
            print(f"Error extracting HTML: {e}")
            return None
    
    def download_assets(self, html_content, base_url):
        """Download CSS, JS, and other assets referenced in the HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        assets = []
        selectors = [
            ('link[href]', 'href'),
            ('script[src]', 'src'),
            ('img[src]', 'src'),
            ('source[src]', 'src')
        ]
        
        for selector, attr in selectors:
            elements = soup.select(selector)
            for element in elements:
                url = element.get(attr)
                if url and url.startswith(('http://', 'https://', '/')):
                    full_url = urljoin(base_url, url)
                    if full_url not in self.downloaded_assets:
                        assets.append(full_url)
        
        # Download assets
        for asset_url in assets:
            try:
                if asset_url in self.downloaded_assets:
                    continue
                    
                print(f"Downloading asset: {asset_url}")
                response = requests.get(asset_url, timeout=30)
                response.raise_for_status()
                
                # Create local path
                parsed = urlparse(asset_url)
                local_path = self.output_dir / parsed.path.lstrip('/')
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save file
                if response.headers.get('content-type', '').startswith('text/'):
                    with open(local_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                else:
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                
                self.downloaded_assets.add(asset_url)
                print(f"Saved asset: {local_path}")
                
            except Exception as e:
                print(f"Error downloading asset {asset_url}: {e}")
    
    def discover_api_pages(self):
        """Discover different API endpoint pages to render."""
        pages = [self.base_url]  # Start with main page
        
        try:
            # Look for navigation links or API endpoints
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='#']")
            for element in nav_elements:
                href = element.get_attribute('href')
                if href and href not in pages:
                    pages.append(href)
            
            # Also check for any operation links
            operation_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid*='operation'] a")
            for element in operation_elements:
                href = element.get_attribute('href')
                if href and href not in pages:
                    pages.append(href)
                    
        except Exception as e:
            print(f"Error discovering pages: {e}")
        
        return pages[:10]  # Limit to first 10 pages to avoid too many
    
    def mirror_site(self):
        """Main method to mirror the entire site with full rendering."""
        print("Starting Selenium-based Kanbanize OpenAPI mirror...")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        print(f"Output directory: {self.output_dir}")
        
        # Start Chrome with remote debugging
        if not self.start_chrome_with_debugging():
            print("Failed to start Chrome with remote debugging.")
            return False
        
        try:
            # Navigate to main page
            print(f"Navigating to {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for content to load
            if not self.wait_for_content_load():
                print("Content loading timeout, but continuing...")
            
            # Discover all pages/sections
            pages = self.discover_api_pages()
            print(f"Found {len(pages)} pages to render")
            
            # Process each page
            for i, page_url in enumerate(pages):
                try:
                    print(f"\nProcessing page {i+1}/{len(pages)}: {page_url}")
                    
                    if page_url != self.driver.current_url:
                        self.driver.get(page_url)
                        self.wait_for_content_load(timeout=15)
                    
                    # Extract rendered HTML
                    html_content = self.extract_rendered_html()
                    if html_content:
                        # Save HTML file
                        if page_url == self.base_url:
                            filename = "index.html"
                        else:
                            # Create filename from URL hash or path
                            parsed = urlparse(page_url)
                            if parsed.fragment:
                                filename = f"{parsed.fragment}.html"
                            else:
                                filename = f"page_{i}.html"
                        
                        file_path = self.output_dir / filename
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        
                        print(f"Saved rendered HTML: {file_path}")
                        
                        # Download assets for this page
                        self.download_assets(html_content, self.base_url)
                
                except Exception as e:
                    print(f"Error processing page {page_url}: {e}")
            
            print(f"\nSelenium mirroring complete!")
            print(f"Files saved to: {self.output_dir}")
            print(f"Open {self.output_dir}/index.html to view offline")
            
            return True
            
        except Exception as e:
            print(f"Error during mirroring: {e}")
            return False
        
        finally:
            self.cleanup()
    
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

def main():
    """Main function to run the Selenium mirror."""
    mirror = SeleniumKanbanizeMirror()
    success = mirror.mirror_site()
    
    if success:
        print("\n✅ Successfully created offline mirror with Selenium!")
    else:
        print("\n❌ Mirroring failed. Check the error messages above.")

if __name__ == "__main__":
    main()