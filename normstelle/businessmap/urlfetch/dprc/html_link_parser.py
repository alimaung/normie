#!/usr/bin/env python3
"""
BeautifulSoup-based link parser for offline Businessmap API Documentation.
Extracts all API endpoint links directly from the HTML file.
"""

import json
import time
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class HTMLLinkParser:
    def __init__(self, html_file="Businessmap API Documentation.html", output_file="extracted_links.json"):
        self.html_file = Path(html_file)
        self.output_file = Path(output_file)
        self.base_url = "https://demo.kanbanize.com/openapi"
        self.all_links = []
        
    def load_html_file(self):
        """Load and parse the HTML file."""
        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.soup = BeautifulSoup(content, 'html.parser')
            print(f"Successfully loaded HTML file: {self.html_file}")
            return True
            
        except Exception as e:
            print(f"Error loading HTML file {self.html_file}: {e}")
            return False
    
    def extract_api_links(self):
        """Extract all API operation links from the HTML."""
        links = []
        
        # Strategy 1: Find all anchor tags with href containing operations
        print("Extracting links with 'operations' in href...")
        operation_links = self.soup.find_all('a', href=re.compile(r'#/operations/'))
        for link in operation_links:
            href = link.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                link_info = self.extract_link_details(link, full_url, "operations_href")
                if link_info:
                    links.append(link_info)
        
        print(f"Found {len(operation_links)} operation links")
        
        # Strategy 2: Find all anchor tags with href containing paths
        print("Extracting links with 'paths' in href...")
        path_links = self.soup.find_all('a', href=re.compile(r'#/paths/'))
        for link in path_links:
            href = link.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                link_info = self.extract_link_details(link, full_url, "paths_href")
                if link_info:
                    links.append(link_info)
        
        print(f"Found {len(path_links)} path links")
        
        # Strategy 3: Find all anchor tags with fragment identifiers
        print("Extracting all fragment links...")
        fragment_links = self.soup.find_all('a', href=re.compile(r'#/'))
        for link in fragment_links:
            href = link.get('href')
            if href and not any(existing['url'] == urljoin(self.base_url, href) for existing in links):
                full_url = urljoin(self.base_url, href)
                link_info = self.extract_link_details(link, full_url, "fragment_href")
                if link_info:
                    links.append(link_info)
        
        print(f"Found {len(fragment_links)} total fragment links")
        
        # Strategy 4: Look for ElementsTableOfContentsItem class
        print("Extracting ElementsTableOfContentsItem links...")
        toc_links = self.soup.find_all('a', class_='ElementsTableOfContentsItem')
        for link in toc_links:
            href = link.get('href')
            if href and not any(existing['url'] == urljoin(self.base_url, href) for existing in links):
                full_url = urljoin(self.base_url, href)
                link_info = self.extract_link_details(link, full_url, "toc_item")
                if link_info:
                    links.append(link_info)
        
        print(f"Found {len(toc_links)} table of contents links")
        
        # Strategy 5: Look for any links in the sidebar or navigation
        print("Extracting sidebar navigation links...")
        nav_elements = self.soup.find_all(['nav', 'aside']) + self.soup.find_all(class_=re.compile(r'nav|sidebar|toc', re.I))
        nav_link_count = 0
        for nav in nav_elements:
            nav_links = nav.find_all('a', href=re.compile(r'#/'))
            for link in nav_links:
                href = link.get('href')
                if href and not any(existing['url'] == urljoin(self.base_url, href) for existing in links):
                    full_url = urljoin(self.base_url, href)
                    link_info = self.extract_link_details(link, full_url, "nav_sidebar")
                    if link_info:
                        links.append(link_info)
                        nav_link_count += 1
        
        print(f"Found {nav_link_count} additional navigation links")
        
        return links
    
    def extract_link_details(self, link_element, url, source):
        """Extract detailed information from a link element."""
        try:
            # Extract text content
            text = link_element.get_text(strip=True)
            
            # Extract title attribute
            title = link_element.get('title', '')
            
            # Try to find HTTP method
            method = ""
            method_patterns = [
                r'\b(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\b',
                r'method["\']?\s*:\s*["\']?(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)["\']?'
            ]
            
            # Look in the link text
            for pattern in method_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    method = match.group(1).upper()
                    break
            
            # Look in nearby elements for method indication
            if not method:
                parent = link_element.parent
                if parent:
                    parent_text = parent.get_text()
                    for pattern in method_patterns:
                        match = re.search(pattern, parent_text, re.I)
                        if match:
                            method = match.group(1).upper()
                            break
            
            # Look for method in class names or data attributes
            if not method:
                for elem in [link_element] + list(link_element.find_all()):
                    classes = elem.get('class', [])
                    for cls in classes:
                        if isinstance(cls, str):
                            for m in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                                if m.lower() in cls.lower():
                                    method = m
                                    break
                    if method:
                        break
            
            # Try to find operation ID or endpoint name from URL
            parsed = urlparse(url)
            operation_id = ""
            if parsed.fragment:
                if '/operations/' in parsed.fragment:
                    operation_id = parsed.fragment.split('/operations/')[-1]
                elif '/paths/' in parsed.fragment:
                    operation_id = parsed.fragment.split('/paths/')[-1]
            
            # Extract section/category
            section = "Unknown"
            try:
                # Look for parent sections
                current = link_element.parent
                for _ in range(10):  # Max 10 levels up
                    if not current:
                        break
                    
                    # Look for section headers
                    section_headers = current.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    for header in section_headers:
                        header_text = header.get_text(strip=True)
                        if header_text and header_text != text and len(header_text) < 100:
                            section = header_text
                            break
                    
                    if section != "Unknown":
                        break
                    
                    current = current.parent
            except:
                pass
            
            link_info = {
                "url": url,
                "title": title,
                "method": method,
                "operation_text": text,
                "operation_id": operation_id,
                "section": section,
                "source": source
            }
            
            return link_info
            
        except Exception as e:
            print(f"Error extracting details for link {url}: {e}")
            return None
    
    def remove_duplicates(self, links):
        """Remove duplicate links based on URL."""
        seen_urls = set()
        unique_links = []
        
        for link in links:
            url = link['url']
            if url not in seen_urls:
                unique_links.append(link)
                seen_urls.add(url)
        
        return unique_links
    
    def save_links(self, links):
        """Save extracted links to JSON file."""
        try:
            output_data = {
                "source_file": str(self.html_file),
                "base_url": self.base_url,
                "extraction_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_links": len(links),
                "links": links
            }
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"Links saved to: {self.output_file}")
            return True
            
        except Exception as e:
            print(f"Error saving links: {e}")
            return False
    
    def print_summary(self, links):
        """Print a summary of extracted links."""
        print("\n" + "="*70)
        print("LINK EXTRACTION SUMMARY")
        print("="*70)
        
        # Group by source
        by_source = {}
        for link in links:
            source = link.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(link)
        
        # Group by method
        by_method = {}
        for link in links:
            method = link.get('method', 'Unknown')
            if method not in by_method:
                by_method[method] = []
            by_method[method].append(link)
        
        # Group by section
        by_section = {}
        for link in links:
            section = link.get('section', 'Unknown')
            if section not in by_section:
                by_section[section] = []
            by_section[section].append(link)
        
        print(f"\nTotal unique links: {len(links)}")
        
        print(f"\nLinks by source:")
        for source, source_links in by_source.items():
            print(f"  {source}: {len(source_links)} links")
        
        print(f"\nLinks by HTTP method:")
        for method, method_links in by_method.items():
            print(f"  {method}: {len(method_links)} links")
        
        print(f"\nTop sections:")
        sorted_sections = sorted(by_section.items(), key=lambda x: len(x[1]), reverse=True)
        for section, section_links in sorted_sections[:10]:
            print(f"  {section}: {len(section_links)} links")
        
        print(f"\nSample links:")
        for i, link in enumerate(links[:15]):
            method = f"[{link['method']}]" if link['method'] else "[?]"
            text = link['operation_text'][:60] + "..." if len(link['operation_text']) > 60 else link['operation_text']
            print(f"  {i+1:2d}. {method} {text}")
            print(f"      → {link['url']}")
        
        if len(links) > 15:
            print(f"  ... and {len(links) - 15} more")
        
        print(f"\nOutput file: {self.output_file}")
    
    def extract_all_links(self):
        """Main method to extract all links from the HTML file."""
        print("Starting HTML link extraction...")
        
        # Load HTML file
        if not self.load_html_file():
            return False
        
        # Extract all API links
        print("\nExtracting API links...")
        links = self.extract_api_links()
        
        # Remove duplicates
        print(f"\nRemoving duplicates from {len(links)} links...")
        unique_links = self.remove_duplicates(links)
        
        print(f"Found {len(unique_links)} unique links!")
        
        # Save to file
        if self.save_links(unique_links):
            print("✅ Links saved successfully")
        else:
            print("❌ Failed to save links")
        
        # Print summary
        self.print_summary(unique_links)
        
        return True

def main():
    """Main function to run the HTML link parser."""
    parser = HTMLLinkParser()
    success = parser.extract_all_links()
    
    if success:
        print("\n✅ Successfully extracted all links from HTML file!")
    else:
        print("\n❌ Link extraction failed. Check the error messages above.")

if __name__ == "__main__":
    main()
