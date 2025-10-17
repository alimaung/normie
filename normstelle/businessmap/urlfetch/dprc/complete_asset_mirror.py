#!/usr/bin/env python3
"""
Complete asset mirror for Businessmap API documentation.
Downloads main page + all discovered pages + all assets for offline serving.
"""

import os
import time
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse, quote
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import hashlib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup

class CompleteAssetMirror:
    def __init__(self, base_url="https://demo.kanbanize.com/openapi", 
                 links_file="extracted_links.json", 
                 output_dir="complete_offline_mirror",
                 max_workers=3):
        self.base_url = base_url
        self.base_domain = "https://demo.kanbanize.com"
        self.links_file = Path(links_file)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.all_links = []
        self.mirrored_pages = set()
        self.failed_pages = set()
        self.downloaded_assets = set()
        self.asset_url_map = {}  # Maps original URLs to local paths
        self.lock = threading.Lock()
        
        # Chrome instances will be created per thread
        self.chrome_processes = []
        
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
    
    def setup_chrome_for_thread(self, thread_id, debug_port_base=9222):
        """Set up a Chrome instance for a specific thread."""
        import subprocess
        import platform
        import shutil
        
        # Use different port for each thread
        debug_port = debug_port_base + thread_id
        user_data_dir = Path(f"C:/Users/RAVEN/Desktop/chrome_user{thread_id + 1}")
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
            raise Exception("Chrome executable not found!")
        
        # Start Chrome process
        chrome_cmd = [
            chrome_exe,
            f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--disable-default-apps",
            "--disable-popup-blocking",
            "--disable-extensions"
            "--window-size=1920,250"
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
                raise Exception(f"Chrome process exited immediately for thread {thread_id}")
            
            # Connect to Chrome
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"localhost:{debug_port}")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            with self.lock:
                self.chrome_processes.append(chrome_process)
            
            print(f"Thread {thread_id}: Chrome started on port {debug_port}")
            return driver
            
        except Exception as e:
            print(f"Thread {thread_id}: Failed to start Chrome: {e}")
            return None
    
    def wait_for_content_load(self, driver, timeout=10):
        """Wait for basic content loading."""
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)  # Allow for dynamic content
            return True
        except TimeoutException:
            return False
    
    def extract_rendered_html(self, driver):
        """Extract the fully rendered HTML from the current page."""
        try:
            return driver.page_source
        except Exception as e:
            print(f"Error extracting HTML: {e}")
            return None
    
    def download_asset(self, asset_url, local_path):
        """Download a single asset."""
        try:
            if asset_url in self.downloaded_assets:
                return True
            
            print(f"Downloading: {asset_url}")
            
            # Make request with proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': self.base_url
            }
            
            response = requests.get(asset_url, headers=headers, timeout=30)
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
            
            with self.lock:
                self.downloaded_assets.add(asset_url)
                self.asset_url_map[asset_url] = str(local_path.relative_to(self.output_dir))
            
            print(f"✅ Downloaded: {local_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {asset_url}: {e}")
            return False
    
    def extract_and_download_assets(self, html_content, page_url):
        """Extract and download all assets from HTML content."""
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
                        asset_url = urljoin(page_url, asset_url)
                    
                    # Only download from same domain or CDN
                    if any(domain in asset_url for domain in ['demo.kanbanize.com', 'kanbanize.com']):
                        assets_to_download.append(asset_url)
            
            # Download assets
            downloaded_count = 0
            for asset_url in set(assets_to_download):  # Remove duplicates
                if asset_url not in self.downloaded_assets:
                    # Create local path
                    parsed = urlparse(asset_url)
                    local_path = self.output_dir / "assets" / parsed.path.lstrip('/')
                    
                    # Ensure we have a filename
                    if local_path.suffix == '':
                        # Try to determine file type from content-type or URL
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
                    
                    if self.download_asset(asset_url, local_path):
                        downloaded_count += 1
            
            print(f"Downloaded {downloaded_count} new assets for this page")
            return downloaded_count
            
        except Exception as e:
            print(f"Error extracting assets: {e}")
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
                        print(f"Fixed asset link: {original_url} -> {local_path}")
            
            return str(soup)
            
        except Exception as e:
            print(f"Error fixing asset links: {e}")
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
    
    def mirror_single_page_with_assets(self, driver, url, filename, thread_id):
        """Mirror a single page and download all its assets."""
        try:
            with self.lock:
                if url in self.mirrored_pages or url in self.failed_pages:
                    return True
            
            print(f"Thread {thread_id}: Mirroring {filename}")
            
            # Navigate to the page
            driver.get(url)
            
            # Wait for content
            if not self.wait_for_content_load(driver, timeout=10):
                print(f"Thread {thread_id}: Timeout for {url}, but continuing...")
            
            # Extract HTML
            html_content = self.extract_rendered_html(driver)
            if not html_content:
                with self.lock:
                    self.failed_pages.add(url)
                return False
            
            # Extract and download assets
            asset_count = self.extract_and_download_assets(html_content, url)
            
            # Fix asset links in HTML
            fixed_html = self.fix_asset_links_in_html(html_content)
            
            # Save HTML file
            file_path = self.output_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_html)
            
            with self.lock:
                self.mirrored_pages.add(url)
            
            print(f"Thread {thread_id}: ✅ Saved {filename} (with {asset_count} assets)")
            return True
            
        except Exception as e:
            print(f"Thread {thread_id}: ❌ Error mirroring {url}: {e}")
            with self.lock:
                self.failed_pages.add(url)
            return False
    
    def worker_thread(self, thread_id, url_queue, results_queue):
        """Worker thread function to process URLs."""
        driver = None
        try:
            # Set up Chrome for this thread
            driver = self.setup_chrome_for_thread(thread_id)
            if not driver:
                print(f"Thread {thread_id}: Failed to setup Chrome")
                return
            
            processed = 0
            while True:
                try:
                    # Get next URL from queue
                    url, filename = url_queue.get(timeout=10)
                    
                    # Process the URL
                    success = self.mirror_single_page_with_assets(driver, url, filename, thread_id)
                    results_queue.put((url, filename, success))
                    
                    url_queue.task_done()
                    processed += 1
                    
                    # Small delay
                    time.sleep(1)
                    
                except queue.Empty:
                    # No more URLs to process
                    break
                except Exception as e:
                    print(f"Thread {thread_id}: Error in worker: {e}")
                    break
            
            print(f"Thread {thread_id}: Processed {processed} pages")
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
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
            
            # Count stats
            total_links = len(self.all_links) + 1  # +1 for main page
            successful_count = len(self.mirrored_pages)
            failed_count = len(self.failed_pages)
            asset_count = len(self.downloaded_assets)
            
            # Create HTML content
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Businessmap API Documentation - Complete Offline Mirror</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; line-height: 1.6; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; display: block; }}
        .stat-label {{ color: #6c757d; font-size: 0.9em; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        .link-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 10px; margin-left: 20px; }}
        .link-item {{ padding: 8px 12px; border-radius: 4px; transition: background 0.2s; }}
        .link-item:hover {{ background: #f8f9fa; }}
        .method {{ 
            display: inline-block; 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 11px; 
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
        .success {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .main-link {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .main-link a {{ font-size: 1.2em; font-weight: bold; text-decoration: none; color: #1976d2; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Businessmap API Documentation</h1>
            <h2>Complete Offline Mirror with Assets</h2>
            <p>Full offline mirror with all CSS, JavaScript, images and other assets</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <span class="stat-number">{total_links}</span>
                <span class="stat-label">Total Pages</span>
            </div>
            <div class="stat success">
                <span class="stat-number">{successful_count}</span>
                <span class="stat-label">Successfully Mirrored</span>
            </div>
            <div class="stat">
                <span class="stat-number">{asset_count}</span>
                <span class="stat-label">Assets Downloaded</span>
            </div>
            <div class="stat">
                <span class="stat-number">{(successful_count/total_links*100):.1f}%</span>
                <span class="stat-label">Success Rate</span>
            </div>
        </div>
        
        <div class="main-link">
            <a href="index.html">📖 Main API Documentation (Start Here)</a>
            <p>This is the main entry point - start here to browse the full API documentation</p>
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
                    
                    # Check if this page was successfully mirrored
                    status_class = "success" if link['url'] in self.mirrored_pages else "failed"
                    
                    html_content += f"""
                <div class="link-item {status_class}">
                    <span class="method {method}">{method or '?'}</span>
                    <a href="{filename}">{operation_text}</a>
                </div>
"""
                
                html_content += """
            </div>
        </div>
"""
            
            html_content += f"""
        <div class="footer">
            <h3>📋 Mirror Information</h3>
            <p><strong>Source:</strong> <a href="{self.base_url}" target="_blank">{self.base_url}</a></p>
            <p><strong>Mirror Created:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Assets Included:</strong> CSS, JavaScript, Images, Fonts</p>
            <p><strong>Ready for:</strong> Local HTTP server or file:// viewing</p>
        </div>
    </div>
</body>
</html>"""
            
            # Save index file
            index_path = self.output_dir / "mirror_index.html"
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Created complete mirror index: {index_path}")
            return True
            
        except Exception as e:
            print(f"Error creating index page: {e}")
            return False
    
    def mirror_complete_site_with_assets(self):
        """Main method to mirror the complete site with all assets."""
        print("🚀 Starting COMPLETE ASSET MIRROR...")
        start_time = time.time()
        
        # Load discovered links
        if not self.load_discovered_links():
            print("Failed to load discovered links")
            return False
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "assets").mkdir(exist_ok=True)
        print(f"Output directory: {self.output_dir}")
        print(f"Using {self.max_workers} worker threads")
        
        try:
            # Prepare URL queue
            url_queue = queue.Queue()
            results_queue = queue.Queue()
            
            # Add main page first
            url_queue.put((self.base_url, "index.html"))
            
            # Add all discovered links
            for link_info in self.all_links:
                url = link_info['url']
                filename = self.create_filename_from_url(url)
                url_queue.put((url, filename))
            
            total_urls = url_queue.qsize()
            print(f"Queued {total_urls} pages for complete mirroring")
            
            # Start worker threads
            threads = []
            for i in range(self.max_workers):
                thread = threading.Thread(
                    target=self.worker_thread, 
                    args=(i, url_queue, results_queue)
                )
                thread.start()
                threads.append(thread)
                time.sleep(2)  # Stagger thread starts
            
            # Monitor progress
            processed = 0
            while processed < total_urls:
                try:
                    url, filename, success = results_queue.get(timeout=60)
                    processed += 1
                    
                    status = "✅" if success else "❌"
                    print(f"Progress: {processed}/{total_urls} - {status} {filename}")
                    
                except queue.Empty:
                    print("Timeout waiting for results, continuing...")
                    break
            
            # Wait for all threads to complete
            print("Waiting for all threads to complete...")
            for thread in threads:
                thread.join(timeout=30)
            
            # Create index page
            print("\nCreating mirror index...")
            self.create_index_page()
            
            # Calculate timing
            end_time = time.time()
            total_time = end_time - start_time
            
            # Final summary
            successful_count = len(self.mirrored_pages)
            failed_count = len(self.failed_pages)
            asset_count = len(self.downloaded_assets)
            
            print(f"\n🎉 COMPLETE ASSET MIRROR FINISHED! 🎉")
            print(f"⏱️  Total time: {total_time:.1f} seconds")
            print(f"📄 Successfully mirrored: {successful_count} pages")
            print(f"❌ Failed to mirror: {failed_count} pages")
            print(f"🖼️  Downloaded assets: {asset_count}")
            print(f"📊 Success rate: {(successful_count/total_urls*100):.1f}%")
            print(f"📁 Output directory: {self.output_dir}")
            print(f"🌐 Main page: {self.output_dir}/index.html")
            print(f"📋 Index page: {self.output_dir}/mirror_index.html")
            print(f"\n🔥 READY TO SERVE LOCALLY! 🔥")
            print(f"Run: python -m http.server 8000 --directory {self.output_dir}")
            print(f"Then open: http://localhost:8000/index.html")
            
            return True
            
        except Exception as e:
            print(f"Error during complete mirroring: {e}")
            return False
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up all Chrome processes."""
        print("Cleaning up Chrome processes...")
        for process in self.chrome_processes:
            try:
                process.terminate()
                time.sleep(1)
                if process.poll() is None:
                    process.kill()
            except:
                pass
        self.chrome_processes.clear()

def main():
    """Main function to run the complete asset mirror."""
    import sys
    
    # Allow customizing worker count
    max_workers = 3  # Reduced for stability with asset downloads
    if len(sys.argv) > 1:
        try:
            max_workers = int(sys.argv[1])
            max_workers = max(1, min(max_workers, 5))  # Limit between 1-5
        except:
            pass
    
    print(f"🚀 Starting complete asset mirror with {max_workers} worker threads")
    
    mirror = CompleteAssetMirror(max_workers=max_workers)
    success = mirror.mirror_complete_site_with_assets()
    
    if success:
        print("\n🎉 Complete asset mirror finished successfully!")
        print("🌐 Your offline API documentation is ready!")
    else:
        print("\n💥 Asset mirror failed. Check the error messages above.")

if __name__ == "__main__":
    main()


