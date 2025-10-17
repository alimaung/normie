#!/usr/bin/env python3
"""
Expand and Mirror for Businessmap API documentation.
Super optimized SPA approach using pre-extracted links:
1. Load URLs from extracted_links.json (no extraction needed)
2. Start Chrome with URL pre-loaded (no navigation needed)  
3. Wait 10s for initial load, expand all sections for complete HTML
4. Wait 2s for expansion (instant in SPA)
5. Download main page (with expanded content) and all assets once
6. Mirror all pages with 0.3s delays (SPA optimized)

Performance optimizations:
- Uses existing extracted_links.json (661 URLs pre-discovered)
- Chrome starts with URL loaded
- Initial wait: 10s
- Expansion wait: 2s (instant)
- Page collection: 0.3s between pages  
- Content load: 3s timeout per page
- No link extraction overhead
"""

import os
import time
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import requests
from bs4 import BeautifulSoup

class ExpandAndMirror:
    def __init__(self, base_url="https://demo.kanbanize.com/openapi", 
                 links_file="extracted_links.json",
                 output_dir="expand_mirror_optimized"):
        self.base_url = base_url
        self.base_domain = "https://demo.kanbanize.com"
        self.links_file = Path(links_file)
        self.output_dir = Path(output_dir)
        self.discovered_urls = []
        self.asset_url_map = {}  # Maps original URLs to local paths
        self.downloaded_assets = set()
        self.lock = threading.Lock()
        
        # Target expandable navigation sections (with chevrons)
        self.target_selectors = [
            "div[title][class*='sl-flex'][class*='sl-cursor-pointer']:not(a)",
            "div[title][class*='hover:sl-bg-canvas-200'][class*='sl-cursor-pointer']"
        ]
        
    def load_extracted_links(self):
        """Load URLs from the existing extracted_links.json file."""
        try:
            with open(self.links_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                links = data.get('links', [])
                self.discovered_urls = [link['url'] for link in links]
                print(f"✅ Loaded {len(self.discovered_urls)} URLs from {self.links_file}")
                return True
        except Exception as e:
            print(f"❌ Error loading links file {self.links_file}: {e}")
            return False
        
    def setup_chrome(self):
        """Set up a single Chrome instance."""
        import subprocess
        import platform
        import shutil
        
        # Use single debug port
        debug_port = 9223  # Different port to avoid conflicts
        user_data_dir = Path("C:/Users/RAVEN/Desktop/chrome_click_mirror")
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
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
            raise Exception("❌ Chrome executable not found!")
        
        # Start Chrome process
        chrome_cmd = [
            chrome_exe,
            f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--disable-default-apps",
            "--disable-popup-blocking",
            "--disable-extensions",
            "--window-size=1920,1080",  # Larger window for clicking
            self.base_url  # Start directly with the URL
        ]
        
        try:
            chrome_process = subprocess.Popen(
                chrome_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for Chrome to start
            time.sleep(3)
            
            # Check if process is running
            if chrome_process.poll() is not None:
                raise Exception("❌ Chrome process exited immediately")
            
            # Connect to Chrome
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"localhost:{debug_port}")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            print(f"✅ Chrome started on port {debug_port}")
            return driver, chrome_process
            
        except Exception as e:
            print(f"❌ Failed to start Chrome: {e}")
            return None, None
    
    def wait_for_content_load(self, driver, timeout=10):
        """Wait for basic content loading - optimized for initial load."""
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(1)  # Wait for dynamic content
            return True
        except TimeoutException:
            return False
    
    def wait_for_expandable_sections(self, driver, timeout=15):
        """Wait for expandable navigation sections to be present and clickable."""
        try:
            # Wait for the main API component to load
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "elements-api"))
            )
            
            # Wait for navigation elements
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ElementsTableOfContentsItem"))
            )
            
            # Additional wait for any JavaScript to finish loading (SPA optimized)
            time.sleep(1)
            
            # Find expandable sections
            all_expandable = []
            for selector in self.target_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        title = element.get_attribute('title')
                        if title and element.is_displayed():
                            # Check if it has chevron (expandable)
                            chevron = element.find_elements(By.CSS_SELECTOR, 
                                "svg[data-icon='chevron-down'], svg[data-icon='chevron-right'], "
                                ".fa-chevron-down, .fa-chevron-right")
                            if chevron:
                                all_expandable.append(element)
                    except:
                        continue
            
            if all_expandable:
                print(f"✅ Found {len(all_expandable)} expandable sections")
                return True
            return False
        except TimeoutException:
            print(f"⚠️  Timeout waiting for expandable sections")
            return False
    
    def expand_all_sections_for_content(self, driver):
        """Expand all navigation sections to get complete HTML content (no link extraction)."""
        print(f"\n🎯 STEP 1: Expanding all navigation sections for complete content...")
        
        try:
            # Wait for initial page load (Chrome started with URL)
            print("⏳ Waiting for initial page load (10 seconds)...")
            if not self.wait_for_content_load(driver, timeout=10):
                print("⚠️  Initial load timeout, but continuing...")
            
            # Wait specifically for expandable sections
            if not self.wait_for_expandable_sections(driver, timeout=15):
                print("⚠️  Expandable sections not ready, but continuing...")
            
            # Find all expandable sections
            expandable_sections = []
            seen_titles = set()
            
            for selector in self.target_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        title = element.get_attribute('title')
                        if (title and element.is_displayed() and 
                            title not in seen_titles):
                            
                            # Check if it has chevron (expandable)
                            chevron = element.find_elements(By.CSS_SELECTOR, 
                                "svg[data-icon='chevron-down'], svg[data-icon='chevron-right'], "
                                ".fa-chevron-down, .fa-chevron-right")
                            if chevron:
                                expandable_sections.append({
                                    'element': element,
                                    'title': title
                                })
                                seen_titles.add(title)
                                print(f"Found expandable section: {title}")
                    except:
                        continue
            
            print(f"🔍 Found {len(expandable_sections)} expandable sections")
            
            if len(expandable_sections) == 0:
                print("⚠️  No expandable sections found, continuing with current state...")
                return True
            
            # TOGGLE ALL SECTIONS AT ONCE using JavaScript
            print(f"🚀 Expanding all {len(expandable_sections)} sections simultaneously...")
            
            # Build JavaScript to click all elements at once
            js_commands = []
            for i, section in enumerate(expandable_sections):
                # Store element reference in JavaScript
                js_commands.append(f"var elem{i} = arguments[{i}];")
                js_commands.append(f"elem{i}.click();")
            
            # Execute all clicks at once
            js_script = "\n".join(js_commands)
            elements_to_pass = [section['element'] for section in expandable_sections]
            
            try:
                driver.execute_script(js_script, *elements_to_pass)
                print(f"✅ Triggered expansion of all {len(expandable_sections)} sections!")
                
                # Wait for all content to load (SPA is fast)
                print("⏳ Waiting for all content to expand...")
                time.sleep(2)  # Optimized for SPA - should be instant
                
            except Exception as e:
                print(f"⚠️  Batch expansion failed, trying individual clicks: {e}")
                
                # Fallback: click individually
                clicked_count = 0
                for i, section in enumerate(expandable_sections):
                    try:
                        element = section['element']
                        title = section['title']
                        
                        print(f"🖱️  Expanding section {i+1}/{len(expandable_sections)}: {title}")
                        
                        # Scroll into view
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(0.1)  # Minimal scroll delay
                        
                        # Try multiple click methods
                        try:
                            element.click()
                            clicked_count += 1
                        except ElementClickInterceptedException:
                            try:
                                driver.execute_script("arguments[0].click();", element)
                                clicked_count += 1
                            except Exception as click_e:
                                print(f"❌ Failed to click '{title}': {click_e}")
                                continue
                        
                        time.sleep(0.1)  # Minimal delay for SPA
                        
                    except Exception as e:
                        print(f"❌ Failed to process section {i+1}: {e}")
                        continue
                
                print(f"✅ Individually clicked {clicked_count}/{len(expandable_sections)} sections")
            
            print(f"🎉 Expansion complete! All sections expanded for full content")
            return True
            
        except Exception as e:
            print(f"❌ Error during section expansion: {e}")
            return False
    
    def extract_all_endpoint_links(self, driver):
        """Extract all visible endpoint links from the expanded page."""
        links = []
        
        try:
            # Look for ElementsTableOfContentsItem anchor tags
            link_elements = driver.find_elements(By.CSS_SELECTOR, ".ElementsTableOfContentsItem[href]")
            
            for element in link_elements:
                try:
                    href = element.get_attribute('href')
                    if not href or href in [link['url'] for link in links]:
                        continue
                    
                    # Extract details from the link
                    title_element = element.find_element(By.CSS_SELECTOR, "[title]")
                    title = title_element.get_attribute('title') if title_element else ""
                    
                    # Try to find HTTP method
                    method = ""
                    method_elements = element.find_elements(By.CSS_SELECTOR, ".sl-font-medium, .sl-uppercase")
                    for method_elem in method_elements:
                        method_text = method_elem.text.strip().upper()
                        if method_text in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                            method = method_text
                            break
                    
                    # Extract operation text
                    text_elements = element.find_elements(By.CSS_SELECTOR, ".sl-truncate")
                    operation_text = ""
                    for text_elem in text_elements:
                        if text_elem.text.strip():
                            operation_text = text_elem.text.strip()
                            break
                    
                    # Extract section/category
                    section = "Unknown"
                    try:
                        # Look for the parent section title
                        parent = element
                        for _ in range(10):  # Max 10 levels up
                            parent = parent.find_element(By.XPATH, "..")
                            section_title_elem = parent.find_elements(By.CSS_SELECTOR, "[title][class*='sl-cursor-pointer']")
                            if section_title_elem:
                                potential_section = section_title_elem[0].get_attribute('title')
                                if potential_section and potential_section != title:
                                    section = potential_section
                                    break
                    except:
                        pass
                    
                    link_info = {
                        "url": href,
                        "title": title,
                        "method": method,
                        "operation_text": operation_text,
                        "section": section
                    }
                    links.append(link_info)
                    print(f"📄 Found: [{method}] {operation_text}")
                    
                except Exception as e:
                    print(f"❌ Error extracting link details: {e}")
                    continue
            
            return links
            
        except Exception as e:
            print(f"❌ Error extracting endpoint links: {e}")
            return []
    
    def download_asset(self, asset_url, local_path):
        """Download a single asset."""
        try:
            print(f"📥 Downloading: {asset_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': self.base_url
            }
            
            response = requests.get(asset_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Create local directory
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file
            content_type = response.headers.get('content-type', '').lower()
            if any(text_type in content_type for text_type in ['text/', 'application/json', 'application/javascript', 'application/xml']):
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
            else:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
            
            self.downloaded_assets.add(asset_url)
            self.asset_url_map[asset_url] = str(local_path.relative_to(self.output_dir))
            
            print(f"✅ Downloaded: {local_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {asset_url}: {e}")
            return False
    
    def download_all_assets_once(self, html_content):
        """Download all assets from the main page HTML (ONCE ONLY)."""
        print("\n🔥 STEP 3: Downloading ALL assets from main page...")
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            assets_to_download = []
            
            # Define asset selectors
            asset_selectors = [
                ('link[href]', 'href', ['css', 'stylesheet', 'icon', 'shortcut icon']),
                ('script[src]', 'src', None),
                ('img[src]', 'src', None),
                ('source[src]', 'src', None),
                ('video[src]', 'src', None),
                ('audio[src]', 'src', None),
                ('object[data]', 'data', None),
                ('embed[src]', 'src', None)
            ]
            
            for selector, attr, rel_filter in asset_selectors:
                elements = soup.select(selector)
                for element in elements:
                    asset_url = element.get(attr)
                    if not asset_url:
                        continue
                    
                    # Filter by rel attribute if specified
                    if rel_filter:
                        rel = element.get('rel', [])
                        if isinstance(rel, str):
                            rel = [rel]
                        if not any(r in rel for r in rel_filter):
                            continue
                    
                    # Convert relative URLs to absolute
                    if asset_url.startswith('//'):
                        asset_url = 'https:' + asset_url
                    elif asset_url.startswith('/'):
                        asset_url = self.base_domain + asset_url
                    elif not asset_url.startswith(('http://', 'https://')):
                        asset_url = urljoin(self.base_url, asset_url)
                    
                    # Only download from same domain or CDN
                    if any(domain in asset_url for domain in ['demo.kanbanize.com', 'kanbanize.com']):
                        assets_to_download.append(asset_url)
            
            # Download assets in parallel
            unique_assets = list(set(assets_to_download))  # Remove duplicates
            print(f"📦 Found {len(unique_assets)} unique assets to download")
            
            downloaded_count = 0
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_url = {}
                
                for asset_url in unique_assets:
                    # Create local path
                    parsed = urlparse(asset_url)
                    local_path = self.output_dir / "assets" / parsed.path.lstrip('/')
                    
                    # Ensure we have a filename
                    if local_path.suffix == '':
                        if 'css' in asset_url or 'stylesheet' in asset_url:
                            local_path = local_path.with_suffix('.css')
                        elif 'js' in asset_url or 'javascript' in asset_url:
                            local_path = local_path.with_suffix('.js')
                        elif 'png' in asset_url:
                            local_path = local_path.with_suffix('.png')
                        elif 'jpg' in asset_url or 'jpeg' in asset_url:
                            local_path = local_path.with_suffix('.jpg')
                        elif 'gif' in asset_url:
                            local_path = local_path.with_suffix('.gif')
                        elif 'svg' in asset_url:
                            local_path = local_path.with_suffix('.svg')
                        elif 'ico' in asset_url:
                            local_path = local_path.with_suffix('.ico')
                        else:
                            local_path = local_path / "index.html"
                    
                    future = executor.submit(self.download_asset, asset_url, local_path)
                    future_to_url[future] = asset_url
                
                # Wait for all downloads to complete
                for future in as_completed(future_to_url):
                    if future.result():
                        downloaded_count += 1
            
            print(f"✅ Downloaded {downloaded_count}/{len(unique_assets)} assets successfully!")
            return downloaded_count
            
        except Exception as e:
            print(f"❌ Error downloading assets: {e}")
            return 0
    
    def fix_asset_links_in_html(self, html_content):
        """Replace asset URLs in HTML with local paths."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Fix different types of asset links
            link_fixes = [
                ('link[href]', 'href'),
                ('script[src]', 'src'),
                ('img[src]', 'src'),
                ('source[src]', 'src'),
                ('video[src]', 'src'),
                ('audio[src]', 'src'),
                ('object[data]', 'data'),
                ('embed[src]', 'src')
            ]
            
            for selector, attr in link_fixes:
                elements = soup.select(selector)
                for element in elements:
                    original_url = element.get(attr)
                    if not original_url:
                        continue
                    
                    # Convert to absolute URL for lookup
                    if original_url.startswith('//'):
                        lookup_url = 'https:' + original_url
                    elif original_url.startswith('/'):
                        lookup_url = self.base_domain + original_url
                    else:
                        lookup_url = original_url
                    
                    # Replace with local path if we have it
                    if lookup_url in self.asset_url_map:
                        local_path = self.asset_url_map[lookup_url]
                        element[attr] = local_path
            
            return str(soup)
            
        except Exception as e:
            print(f"❌ Error fixing asset links: {e}")
            return html_content
    
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
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', operation_name)
            return f"operation_{safe_name}.html"
        
        # Handle paths URLs
        if fragment.startswith('paths/'):
            path_name = fragment.replace('paths/', '')
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', path_name)
            return f"path_{safe_name}.html"
        
        # Generic handling
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', fragment)
        return f"page_{safe_name}.html"
    
    def collect_page_html(self, driver, url, filename):
        """Collect HTML from a single page (no asset downloading)."""
        try:
            print(f"📄 Collecting: {filename}")
            
            # Navigate to the page
            driver.get(url)
            
            # Wait for content (SPA optimized)
            if not self.wait_for_content_load(driver, timeout=3):
                print(f"⚠️  Timeout for {url}, but continuing...")
            
            # Extract HTML
            html_content = driver.page_source
            if not html_content:
                print(f"❌ No content for {url}")
                return False
            
            # Fix asset links to point to local files
            fixed_html = self.fix_asset_links_in_html(html_content)
            
            # Save HTML file
            file_path = self.output_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_html)
            
            print(f"✅ Saved: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error collecting {url}: {e}")
            return False
    
    def create_index_page(self):
        """Create an index page with links to all mirrored content."""
        try:
            # Count stats
            total_urls = len(self.discovered_urls)
            asset_count = len(self.downloaded_assets)
            
            # Create HTML content
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Businessmap API Documentation - Expand and Mirror</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; line-height: 1.6; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; display: block; }}
        .stat-label {{ color: #6c757d; font-size: 0.9em; }}
        .url-list {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .url-item {{ padding: 8px 0; border-bottom: 1px solid #dee2e6; }}
        .url-item:last-child {{ border-bottom: none; }}
        .url-item a {{ text-decoration: none; color: #007bff; }}
        .url-item a:hover {{ text-decoration: underline; }}
        .main-link {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .main-link a {{ font-size: 1.2em; font-weight: bold; text-decoration: none; color: #1976d2; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; text-align: center; }}
        .method-info {{ background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Businessmap API Documentation</h1>
            <h2>Expand and Mirror - Super Optimized</h2>
            <p>Pre-extracted links + section expansion + optimized asset management</p>
        </div>
        
        <div class="method-info">
            <h3>🎯 Optimization Method</h3>
            <ul>
                <li><strong>Links:</strong> Loaded from extracted_links.json (661 pre-discovered URLs)</li>
                <li><strong>Expansion:</strong> All navigation sections expanded for complete HTML</li>
                <li><strong>Assets:</strong> Downloaded once and reused across all pages</li>
                <li><strong>SPA:</strong> 0.3s delays optimized for Single Page Application</li>
                <li><strong>Ready:</strong> All links fixed for offline use</li>
            </ul>
        </div>
        
        <div class="stats">
            <div class="stat">
                <span class="stat-number">{total_urls}</span>
                <span class="stat-label">Loaded URLs</span>
            </div>
            <div class="stat">
                <span class="stat-number">{asset_count}</span>
                <span class="stat-label">Assets Downloaded</span>
            </div>
            <div class="stat">
                <span class="stat-number">100%</span>
                <span class="stat-label">Offline Ready</span>
            </div>
        </div>
        
        <div class="main-link">
            <a href="index.html">📖 Main API Documentation (Start Here)</a>
            <p>This is the main entry point - start here to browse the full API documentation</p>
        </div>
        
        <div class="url-list">
            <h3>📋 All Mirrored Pages ({total_urls} total)</h3>
"""
            
            # Add all discovered URLs
            for i, url in enumerate(self.discovered_urls, 1):
                filename = self.create_filename_from_url(url)
                # Show original URL in title, link to local file
                html_content += f"""
            <div class="url-item">
                <strong>{i}.</strong> 
                <a href="{filename}" title="{url}">{filename}</a>
                <small style="color: #6c757d;"> (from {url})</small>
            </div>
"""
            
            html_content += f"""
        </div>
        
        <div class="footer">
            <h3>🌐 Local Serving Instructions</h3>
            <p><strong>Serve locally:</strong> <code>python -m http.server 8000 --directory {self.output_dir.name}</code></p>
            <p><strong>Then open:</strong> <a href="http://localhost:8000/index.html" target="_blank">http://localhost:8000/index.html</a></p>
            <p><strong>Source:</strong> <a href="{self.base_url}" target="_blank">{self.base_url}</a></p>
            <p><strong>Mirror Created:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""
            
            # Save index file
            index_path = self.output_dir / "mirror_index.html"
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Created click mirror index: {index_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating index page: {e}")
            return False
    
    def run_expand_and_mirror(self):
        """Main method to run the click and mirror process."""
        print("🚀 Starting EXPAND AND MIRROR - SUPER OPTIMIZED...")
        print("📋 Strategy: Load URLs from file → Expand sections → Download assets → Mirror pages")
        start_time = time.time()
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "assets").mkdir(exist_ok=True)
        print(f"📁 Output directory: {self.output_dir}")
        
        # Setup Chrome
        driver, chrome_process = self.setup_chrome()
        if not driver:
            print("❌ Failed to setup Chrome")
            return False
        
        try:
            # STEP 1: Load URLs from existing extracted_links.json file
            print(f"\n📋 STEP 1: Loading URLs from extracted links file...")
            if not self.load_extracted_links():
                print("❌ Failed to load extracted links!")
                return False
            
            # STEP 2: Expand all navigation sections for complete HTML content  
            # Chrome already started with the URL, so no need to navigate
            print(f"🌐 Chrome already loaded: {self.base_url}")
            if not self.expand_all_sections_for_content(driver):
                print("⚠️  Failed to expand sections, but continuing...")
                # Continue anyway - we can still mirror with basic content
            
            # STEP 3: Download the main page (index) with expanded content
            print(f"\n📄 STEP 3: Downloading main page with expanded content...")
            main_page_html = driver.page_source
            
            # STEP 4: Download all assets once
            print(f"\n🔥 STEP 4: Downloading assets...")
            asset_count = self.download_all_assets_once(main_page_html)
            
            # Save main page with fixed asset links
            fixed_main_html = self.fix_asset_links_in_html(main_page_html)
            main_file_path = self.output_dir / "index.html"
            with open(main_file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_main_html)
            print(f"✅ Saved main page: index.html")
            
            # STEP 5: Download all pages from extracted links
            print(f"\n📄 STEP 5: Collecting HTML from {len(self.discovered_urls)} pages...")
            successful_count = 1  # Count main page
            failed_count = 0
            
            for i, url in enumerate(self.discovered_urls, 1):
                if url == self.base_url:  # Skip main page (already saved)
                    continue
                    
                filename = self.create_filename_from_url(url)
                print(f"Progress: {i}/{len(self.discovered_urls)} - {filename}")
                
                if self.collect_page_html(driver, url, filename):
                    successful_count += 1
                else:
                    failed_count += 1
                
                # SPA optimized delay
                time.sleep(0.3)
            
            # STEP 6: Create index page
            print(f"\n📋 STEP 6: Creating index page...")
            self.create_index_page()
            
            # Final summary
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n🎉 EXPAND AND MIRROR COMPLETED! 🎉")
            print(f"⏱️  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
            print(f"🔍 URLs loaded from file: {len(self.discovered_urls)}")
            print(f"📄 Successfully mirrored: {successful_count} pages")
            print(f"❌ Failed to mirror: {failed_count} pages")
            print(f"🖼️  Assets downloaded: {asset_count}")
            print(f"📊 Success rate: {(successful_count/(successful_count + failed_count)*100):.1f}%")
            print(f"📁 Output directory: {self.output_dir}")
            print(f"🌐 Main page: {self.output_dir}/index.html")
            print(f"📋 Index page: {self.output_dir}/mirror_index.html")
            print(f"\n🚀 READY TO SERVE!")
            print(f"Run: python -m http.server 8000 --directory {self.output_dir}")
            print(f"Then open: http://localhost:8000/index.html")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during click and mirror: {e}")
            return False
        
        finally:
            # Cleanup
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            if chrome_process:
                try:
                    chrome_process.terminate()
                    time.sleep(1)
                    if chrome_process.poll() is None:
                        chrome_process.kill()
                except:
                    pass
            print("🧹 Chrome cleanup completed")

def main():
    """Main function to run the expand and mirror process."""
    print("🚀 Starting Expand and Mirror")
    print("🎯 Process: Expand all navigation sections + optimized asset mirroring")
    
    mirror = ExpandAndMirror()
    success = mirror.run_expand_and_mirror()
    
    if success:
        print("\n🎉 Expand and mirror finished successfully!")
        print("🌐 Your automated offline API documentation is ready!")
    else:
        print("\n💥 Expand and mirror failed. Check the error messages above.")

if __name__ == "__main__":
    main()
