#!/usr/bin/env python3
"""
Web scraper to download Kanbanize OpenAPI demo for offline viewing.
Downloads all HTML, CSS, JS, images and other assets to an 'openapi' folder.
"""

import os
import requests
from urllib.parse import urljoin, urlparse, unquote
from pathlib import Path
import re
from bs4 import BeautifulSoup
import time
import mimetypes

class KanbanizeMirror:
    def __init__(self, base_url="https://demo.kanbanize.com/openapi", output_dir="openapi"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.downloaded_files = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def create_directory_structure(self):
        """Create the output directory structure."""
        self.output_dir.mkdir(exist_ok=True)
        print(f"Created output directory: {self.output_dir}")
        
    def sanitize_filename(self, filename):
        """Sanitize filename for cross-platform compatibility."""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return filename.strip()
        
    def get_local_path(self, url):
        """Convert URL to local file path."""
        parsed = urlparse(url)
        path = unquote(parsed.path)
        
        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]
            
        # If no file extension, assume it's HTML
        if not Path(path).suffix and not path.endswith('/'):
            path += '.html'
        elif path.endswith('/'):
            path += 'index.html'
            
        return self.output_dir / self.sanitize_filename(path)
        
    def download_file(self, url, local_path=None):
        """Download a file from URL to local path."""
        if url in self.downloaded_files:
            return True
            
        try:
            if local_path is None:
                local_path = self.get_local_path(url)
                
            # Create directory if it doesn't exist
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"Downloading: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Write file
            if response.headers.get('content-type', '').startswith('text/'):
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
            else:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                    
            self.downloaded_files.add(url)
            print(f"Saved: {local_path}")
            return True
            
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False
            
    def process_html(self, html_content, base_url):
        """Process HTML content and extract asset URLs."""
        soup = BeautifulSoup(html_content, 'html.parser')
        assets = []
        
        # Find all assets: CSS, JS, images, etc.
        selectors = [
            ('link[href]', 'href'),
            ('script[src]', 'src'),
            ('img[src]', 'src'),
            ('a[href]', 'href'),
            ('iframe[src]', 'src')
        ]
        
        for selector, attr in selectors:
            elements = soup.select(selector)
            for element in elements:
                url = element.get(attr)
                if url:
                    full_url = urljoin(base_url, url)
                    assets.append(full_url)
                    
        return assets, soup
        
    def fix_html_links(self, soup, base_url):
        """Convert absolute URLs to relative paths for offline viewing."""
        selectors = [
            ('link[href]', 'href'),
            ('script[src]', 'src'),
            ('img[src]', 'src'),
            ('a[href]', 'href'),
            ('iframe[src]', 'src')
        ]
        
        for selector, attr in selectors:
            elements = soup.select(selector)
            for element in elements:
                url = element.get(attr)
                if url and url.startswith(('http://', 'https://')):
                    # Convert to relative path
                    parsed = urlparse(url)
                    if parsed.netloc == urlparse(base_url).netloc:
                        relative_path = parsed.path
                        if relative_path.startswith('/'):
                            relative_path = relative_path[1:]
                        if not Path(relative_path).suffix and not relative_path.endswith('/'):
                            relative_path += '.html'
                        elif relative_path.endswith('/'):
                            relative_path += 'index.html'
                        element[attr] = relative_path
                        
        return soup
        
    def mirror_site(self):
        """Download the entire site for offline viewing."""
        print("Starting Kanbanize OpenAPI mirror...")
        
        # Create directory structure
        self.create_directory_structure()
        
        # Start with the main page
        main_url = self.base_url
        urls_to_process = [main_url]
        processed_urls = set()
        
        while urls_to_process:
            current_url = urls_to_process.pop(0)
            
            if current_url in processed_urls:
                continue
                
            processed_urls.add(current_url)
            
            try:
                print(f"Processing: {current_url}")
                response = self.session.get(current_url, timeout=30)
                response.raise_for_status()
                
                # Determine if it's HTML content
                content_type = response.headers.get('content-type', '')
                
                if 'text/html' in content_type:
                    # Process HTML
                    assets, soup = self.process_html(response.text, current_url)
                    
                    # Fix links for offline viewing
                    fixed_soup = self.fix_html_links(soup, self.base_url)
                    
                    # Save the fixed HTML
                    local_path = self.get_local_path(current_url)
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(local_path, 'w', encoding='utf-8') as f:
                        f.write(str(fixed_soup))
                    
                    print(f"Saved HTML: {local_path}")
                    
                    # Add new URLs to process (only from same domain)
                    for asset_url in assets:
                        parsed_asset = urlparse(asset_url)
                        parsed_base = urlparse(self.base_url)
                        
                        if parsed_asset.netloc == parsed_base.netloc:
                            if asset_url not in processed_urls:
                                urls_to_process.append(asset_url)
                        
                    # Download assets
                    for asset_url in assets:
                        parsed_asset = urlparse(asset_url)
                        parsed_base = urlparse(self.base_url)
                        
                        if parsed_asset.netloc == parsed_base.netloc:
                            self.download_file(asset_url)
                            
                else:
                    # Download non-HTML files directly
                    self.download_file(current_url)
                    
                # Small delay to be respectful
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing {current_url}: {e}")
                
        print(f"\nMirroring complete! Files saved to: {self.output_dir}")
        print(f"Open {self.output_dir}/index.html in your browser to view offline.")

def main():
    """Main function to run the mirror."""
    mirror = KanbanizeMirror()
    mirror.mirror_site()

if __name__ == "__main__":
    main()
