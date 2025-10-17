#!/usr/bin/env python3
"""
Fast, threaded Selenium-based mirror for Businessmap API documentation.
Optimized for speed with minimal wait times and parallel processing.
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

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

class FastMirror:
    def __init__(self, base_url="https://demo.kanbanize.com/openapi", 
                 links_file="extracted_links.json", 
                 output_dir="fast_mirror",
                 max_workers=4):
        self.base_url = base_url
        self.links_file = Path(links_file)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.all_links = []
        self.mirrored_pages = set()
        self.failed_pages = set()
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
        user_data_dir = Path(f"C:/Users/RAVEN/Desktop/user{thread_id + 1}")
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
            "--disable-extensions",
            "--disable-plugins",
            "--disable-images",  # Speed up loading
            "--disable-javascript",  # We don't need JS for static content
            "--headless"  # Run headless for speed
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
    
    def fast_wait_for_content(self, driver, timeout=5):
        """Fast wait for basic content loading."""
        try:
            # Just wait for body tag - much faster than complex elements
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(1)  # Minimal additional wait
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
    
    def mirror_single_page_fast(self, driver, url, filename, thread_id):
        """Mirror a single page quickly."""
        try:
            with self.lock:
                if url in self.mirrored_pages or url in self.failed_pages:
                    return True
            
            print(f"Thread {thread_id}: Mirroring {filename}")
            
            # Navigate to the page
            driver.get(url)
            
            # Fast content wait
            if not self.fast_wait_for_content(driver, timeout=3):
                print(f"Thread {thread_id}: Fast timeout for {url}, but continuing...")
            
            # Extract HTML quickly
            html_content = self.extract_rendered_html(driver)
            if not html_content:
                with self.lock:
                    self.failed_pages.add(url)
                return False
            
            # Save HTML file
            file_path = self.output_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            with self.lock:
                self.mirrored_pages.add(url)
            
            print(f"Thread {thread_id}: ✅ Saved {filename}")
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
                    url, filename = url_queue.get(timeout=5)
                    
                    # Process the URL
                    success = self.mirror_single_page_fast(driver, url, filename, thread_id)
                    results_queue.put((url, filename, success))
                    
                    url_queue.task_done()
                    processed += 1
                    
                    # Small delay to avoid overwhelming the server
                    time.sleep(0.5)
                    
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
            
            # Count successful vs failed
            total_links = len(self.all_links)
            successful_count = len(self.mirrored_pages)
            failed_count = len(self.failed_pages)
            
            # Create HTML content
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Businessmap API Documentation - Fast Mirror</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .stats {{ display: flex; gap: 20px; margin: 15px 0; }}
        .stat {{ background: #e9ecef; padding: 10px; border-radius: 3px; text-align: center; flex: 1; }}
        .section {{ margin-bottom: 25px; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 5px; }}
        .link-list {{ margin-left: 20px; }}
        .link-item {{ margin: 3px 0; }}
        .method {{ 
            display: inline-block; 
            padding: 2px 6px; 
            border-radius: 3px; 
            font-size: 11px; 
            font-weight: bold; 
            min-width: 45px; 
            text-align: center; 
            margin-right: 8px; 
        }}
        .method.GET {{ background-color: #d4edda; color: #155724; }}
        .method.POST {{ background-color: #fff3cd; color: #856404; }}
        .method.PUT {{ background-color: #cce5ff; color: #004085; }}
        .method.PATCH {{ background-color: #e2e3e5; color: #383d41; }}
        .method.DELETE {{ background-color: #f8d7da; color: #721c24; }}
        .success {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Businessmap API Documentation - Fast Mirror</h1>
        <div class="stats">
            <div class="stat">
                <strong>Total Endpoints</strong><br>
                {total_links}
            </div>
            <div class="stat success">
                <strong>Successfully Mirrored</strong><br>
                {successful_count}
            </div>
            <div class="stat failed">
                <strong>Failed</strong><br>
                {failed_count}
            </div>
            <div class="stat">
                <strong>Success Rate</strong><br>
                {(successful_count/total_links*100):.1f}%
            </div>
        </div>
        <p><strong>Mirror Created:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>📖 Main Documentation</h2>
        <div class="link-list">
            <div class="link-item">
                <a href="index.html">Main API Documentation</a>
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
    <div class="section">
        <h2>📊 Mirror Information</h2>
        <ul>
            <li><strong>Source:</strong> <a href="{self.base_url}">{self.base_url}</a></li>
            <li><strong>Links Source:</strong> {self.links_file}</li>
            <li><strong>Mirror Method:</strong> Fast Selenium with Threading</li>
            <li><strong>Total Processing Time:</strong> See console output</li>
        </ul>
    </div>
    
</body>
</html>"""
            
            # Save index file
            index_path = self.output_dir / "fast_mirror_index.html"
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Created fast mirror index: {index_path}")
            return True
            
        except Exception as e:
            print(f"Error creating index page: {e}")
            return False
    
    def mirror_complete_documentation_fast(self):
        """Main method to mirror documentation with threading."""
        print("Starting fast threaded documentation mirror...")
        start_time = time.time()
        
        # Load discovered links
        if not self.load_discovered_links():
            print("Failed to load discovered links")
            return False
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
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
            print(f"Queued {total_urls} pages for mirroring")
            
            # Start worker threads
            threads = []
            for i in range(self.max_workers):
                thread = threading.Thread(
                    target=self.worker_thread, 
                    args=(i, url_queue, results_queue)
                )
                thread.start()
                threads.append(thread)
                time.sleep(1)  # Stagger thread starts
            
            # Monitor progress
            processed = 0
            while processed < total_urls:
                try:
                    url, filename, success = results_queue.get(timeout=30)
                    processed += 1
                    
                    status = "✅" if success else "❌"
                    print(f"Progress: {processed}/{total_urls} - {status} {filename}")
                    
                except queue.Empty:
                    print("Timeout waiting for results, continuing...")
                    break
            
            # Wait for all threads to complete
            print("Waiting for all threads to complete...")
            for thread in threads:
                thread.join(timeout=10)
            
            # Create index page
            print("\nCreating index page...")
            self.create_index_page()
            
            # Calculate timing
            end_time = time.time()
            total_time = end_time - start_time
            
            # Final summary
            successful_count = len(self.mirrored_pages)
            failed_count = len(self.failed_pages)
            
            print(f"\n🎉 FAST MIRROR COMPLETE 🎉")
            print(f"⏱️  Total time: {total_time:.1f} seconds")
            print(f"✅ Successfully mirrored: {successful_count} pages")
            print(f"❌ Failed to mirror: {failed_count} pages")
            print(f"📊 Success rate: {(successful_count/total_urls*100):.1f}%")
            print(f"⚡ Average speed: {total_urls/total_time:.1f} pages/second")
            print(f"📁 Output directory: {self.output_dir}")
            print(f"🌐 Main page: {self.output_dir}/index.html")
            print(f"📋 Index page: {self.output_dir}/fast_mirror_index.html")
            
            return True
            
        except Exception as e:
            print(f"Error during fast mirroring: {e}")
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
    """Main function to run the fast mirror."""
    import sys
    
    # Allow customizing worker count
    max_workers = 4
    if len(sys.argv) > 1:
        try:
            max_workers = int(sys.argv[1])
            max_workers = max(1, min(max_workers, 8))  # Limit between 1-8
        except:
            pass
    
    print(f"Starting fast mirror with {max_workers} worker threads")
    
    mirror = FastMirror(max_workers=max_workers)
    success = mirror.mirror_complete_documentation_fast()
    
    if success:
        print("\n🚀 Fast mirror completed successfully!")
    else:
        print("\n💥 Fast mirror failed. Check the error messages above.")

if __name__ == "__main__":
    main()
