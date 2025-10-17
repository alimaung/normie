#!/usr/bin/env python3
"""
Complete Selenium-based mirror for Kanbanize OpenAPI documentation.
Captures the main page and all discovered API endpoint pages for offline use.
"""

import os
import time
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse, quote
import re
import hashlib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup

class CompleteMirror:
    def __init__(self, base_url="https://demo.kanbanize.com/openapi", 
                 links_file="complete_links.json", 
                 output_dir="complete_mirror"):
        self.base_url = base_url
        self.links_file = Path(links_file)
        self.output_dir = Path(output_dir)
        self.driver = None
        self.chrome_process = None
        self.downloaded_assets = set()
        self.all_links = []
        self.mirrored_pages = set()
        
    def load_discovered_links(self):
        """Load the discovered links from the JSON file."""
        try:
            with open(self.links_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.all_links = data.get('links', [])
                print(f"Loaded {len(self.all_links)} discovered links from {self.links_file}")
                return True
        except Exception as e:
            print(f"Error loading links file {self.links_file}: {e}")
            return False
    
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
            "--disable-popup-blocking"
        ]
        
        try:
            print(f"Starting Chrome...")
            
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
                
                if self.chrome_process.poll() is not None:
                    stdout, stderr = self.chrome_process.communicate()
                    print(f"Chrome process exited with code: {self.chrome_process.returncode}")
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
                        print(f"Chrome took too long to start: {e}")
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
            
            # Additional wait for dynamic content
            time.sleep(5)
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
                    if full_url not in self.downloaded_assets and full_url not in assets:
                        assets.append(full_url)
        
        # Download assets (limit to avoid too many requests)
        downloaded_count = 0
        max_assets = 20  # Limit asset downloads
        
        for asset_url in assets[:max_assets]:
            try:
                if asset_url in self.downloaded_assets:
                    continue
                    
                print(f"Downloading asset: {asset_url}")
                response = requests.get(asset_url, timeout=10)
                response.raise_for_status()
                
                # Create local path
                parsed = urlparse(asset_url)
                local_path = self.output_dir / "assets" / parsed.path.lstrip('/')
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save file
                if response.headers.get('content-type', '').startswith('text/'):
                    with open(local_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                else:
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                
                self.downloaded_assets.add(asset_url)
                downloaded_count += 1
                print(f"Saved asset: {local_path}")
                
            except Exception as e:
                print(f"Error downloading asset {asset_url}: {e}")
        
        print(f"Downloaded {downloaded_count} assets")
    
    def create_filename_from_url(self, url):
        """Create a safe filename from a URL."""
        parsed = urlparse(url)
        
        # Handle main page
        if parsed.fragment == "/" or not parsed.fragment:
            return "index.html"
        
        # Extract operation name from fragment
        fragment = parsed.fragment.lstrip('/')
        
        # Handle operations URLs
        if fragment.startswith('operations/'):
            operation_name = fragment.replace('operations/', '')
            # Clean the name for filesystem
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', operation_name)
            return f"operation_{safe_name}.html"
        
        # Handle paths URLs
        if fragment.startswith('paths/'):
            path_name = fragment.replace('paths/', '')
            # Clean the name for filesystem
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', path_name)
            return f"path_{safe_name}.html"
        
        # Generic handling
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', fragment)
        return f"page_{safe_name}.html"
    
    def mirror_single_page(self, url, filename=None, skip_assets=False):
        """Mirror a single page and save it to disk."""
        try:
            if url in self.mirrored_pages:
                print(f"Already mirrored: {url}")
                return True
            
            print(f"Mirroring: {url}")
            
            # Navigate to the page
            self.driver.get(url)
            
            # Wait for content to load
            if not self.wait_for_content_load(timeout=20):
                print(f"Content loading timeout for {url}, but continuing...")
            
            # Extract rendered HTML
            html_content = self.extract_rendered_html()
            if not html_content:
                print(f"Failed to extract HTML for {url}")
                return False
            
            # Create filename if not provided
            if not filename:
                filename = self.create_filename_from_url(url)
            
            # Save HTML file
            file_path = self.output_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Saved: {file_path}")
            
            # Download assets for main page only to avoid duplicates
            if not skip_assets and (url == self.base_url or filename == "index.html"):
                print("Downloading assets for main page...")
                self.download_assets(html_content, self.base_url)
            
            self.mirrored_pages.add(url)
            return True
            
        except Exception as e:
            print(f"Error mirroring page {url}: {e}")
            return False
    
    def create_index_page(self):
        """Create an index page with links to all mirrored content."""
        try:
            # Group links by section and method
            links_by_section = {}
            for link in self.all_links:
                section = link.get('section', 'Unknown')
                if section not in links_by_section:
                    links_by_section[section] = []
                links_by_section[section].append(link)
            
            # Create HTML content
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Businessmap API Documentation - Offline Mirror</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 5px; }}
        .link-list {{ margin-left: 20px; }}
        .link-item {{ margin: 5px 0; }}
        .method {{ 
            display: inline-block; 
            padding: 2px 6px; 
            border-radius: 3px; 
            font-size: 12px; 
            font-weight: bold; 
            min-width: 50px; 
            text-align: center; 
            margin-right: 10px; 
        }}
        .method.GET {{ background-color: #d4edda; color: #155724; }}
        .method.POST {{ background-color: #fff3cd; color: #856404; }}
        .method.PUT {{ background-color: #cce5ff; color: #004085; }}
        .method.PATCH {{ background-color: #e2e3e5; color: #383d41; }}
        .method.DELETE {{ background-color: #f8d7da; color: #721c24; }}
        .stats {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>Businessmap API Documentation - Offline Mirror</h1>
    
    <div class="stats">
        <h3>Mirror Statistics</h3>
        <ul>
            <li>Total API Endpoints: {len(self.all_links)}</li>
            <li>Mirrored Pages: {len(self.mirrored_pages)}</li>
            <li>Mirror Created: {time.strftime('%Y-%m-%d %H:%M:%S')}</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>Main Documentation</h2>
        <div class="link-list">
            <div class="link-item">
                <a href="index.html">📖 Main API Documentation</a>
            </div>
        </div>
    </div>
"""
            
            # Add sections
            for section, links in sorted(links_by_section.items()):
                if section == "Unknown":
                    continue
                    
                html_content += f"""
    <div class="section">
        <h2>{section} ({len(links)} endpoints)</h2>
        <div class="link-list">
"""
                
                for link in sorted(links, key=lambda x: (x.get('method', ''), x.get('operation_text', ''))):
                    method = link.get('method', '')
                    operation_text = link.get('operation_text', '')
                    filename = self.create_filename_from_url(link['url'])
                    
                    html_content += f"""
            <div class="link-item">
                <span class="method {method}">{method or '?'}</span>
                <a href="{filename}">{operation_text}</a>
            </div>
"""
                
                html_content += """
        </div>
    </div>
"""
            
            html_content += """
    <div class="section">
        <h2>About This Mirror</h2>
        <p>This is an offline mirror of the Businessmap API documentation. All pages have been rendered and saved for offline use.</p>
        <p>Original documentation: <a href="https://demo.kanbanize.com/openapi">https://demo.kanbanize.com/openapi</a></p>
    </div>
    
</body>
</html>"""
            
            # Save index file
            index_path = self.output_dir / "mirror_index.html"
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Created index page: {index_path}")
            return True
            
        except Exception as e:
            print(f"Error creating index page: {e}")
            return False
    
    def mirror_complete_documentation(self):
        """Main method to mirror the complete documentation."""
        print("Starting complete documentation mirror...")
        
        # Load discovered links
        if not self.load_discovered_links():
            print("Failed to load discovered links")
            return False
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        print(f"Output directory: {self.output_dir}")
        
        # Start Chrome
        if not self.start_chrome_with_debugging():
            print("Failed to start Chrome")
            return False
        
        try:
            mirrored_count = 0
            failed_count = 0
            
            # Mirror main page first
            print("\n=== Mirroring main page ===")
            if self.mirror_single_page(self.base_url, "index.html"):
                mirrored_count += 1
                print("✅ Main page mirrored successfully")
            else:
                failed_count += 1
                print("❌ Failed to mirror main page")
            
            # Mirror all discovered endpoint pages
            print(f"\n=== Mirroring {len(self.all_links)} endpoint pages ===")
            for i, link_info in enumerate(self.all_links):
                url = link_info['url']
                operation_text = link_info.get('operation_text', '')
                method = link_info.get('method', '')
                
                print(f"\nProgress: {i+1}/{len(self.all_links)}")
                print(f"Operation: [{method}] {operation_text}")
                
                filename = self.create_filename_from_url(url)
                
                if self.mirror_single_page(url, filename, skip_assets=True):
                    mirrored_count += 1
                    print(f"✅ Mirrored: {filename}")
                else:
                    failed_count += 1
                    print(f"❌ Failed: {filename}")
                
                # Small delay between requests
                time.sleep(1)
            
            # Create index page
            print("\n=== Creating index page ===")
            if self.create_index_page():
                print("✅ Index page created")
            else:
                print("❌ Failed to create index page")
            
            # Summary
            print(f"\n=== MIRROR COMPLETE ===")
            print(f"Successfully mirrored: {mirrored_count} pages")
            print(f"Failed to mirror: {failed_count} pages")
            print(f"Total pages processed: {mirrored_count + failed_count}")
            print(f"Output directory: {self.output_dir}")
            print(f"Main page: {self.output_dir}/index.html")
            print(f"Index page: {self.output_dir}/mirror_index.html")
            
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
    """Main function to run the complete mirror."""
    mirror = CompleteMirror()
    success = mirror.mirror_complete_documentation()
    
    if success:
        print("\n✅ Successfully created complete offline mirror!")
        print(f"Open {mirror.output_dir}/mirror_index.html to browse the mirror")
    else:
        print("\n❌ Mirroring failed. Check the error messages above.")

if __name__ == "__main__":
    main()
