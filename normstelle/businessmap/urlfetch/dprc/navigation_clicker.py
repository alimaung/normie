#!/usr/bin/env python3
"""
Navigation clicker for Kanbanize OpenAPI documentation.
Clicks each navigation item to reveal dynamically loaded endpoint links.
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

class NavigationClicker:
    def __init__(self, base_url="https://demo.kanbanize.com/openapi", output_file="complete_links.json"):
        self.base_url = base_url
        self.output_file = Path(output_file)
        self.driver = None
        self.chrome_process = None
        self.all_links = []
        self.clicked_sections = set()
        
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
            
            # Wait for navigation elements
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ElementsTableOfContentsItem"))
            )
            
            time.sleep(5)  # Additional wait for dynamic content
            return True
            
        except TimeoutException:
            print(f"Timeout waiting for content to load after {timeout} seconds")
            return False
    
    def find_navigation_sections(self):
        """Find all navigation sections that can be clicked to reveal content."""
        navigation_sections = []
        seen_titles = set()
        
        try:
            # Look for section headers (not linked but clickable)
            section_selectors = [
                # Sections with chevron icons that can be expanded
                "div[title][class*='sl-flex'][class*='sl-cursor-pointer']:not(a)",
                # Any clickable div with a title that's not an anchor
                "div[title][class*='hover:sl-bg-canvas-200'][class*='sl-cursor-pointer']"
            ]
            
            for selector in section_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        title = element.get_attribute('title')
                        if (title and element.is_displayed() and 
                            title not in seen_titles and 
                            title not in self.clicked_sections):
                            
                            # Check if it's a section header (has chevron icon)
                            chevron = element.find_elements(By.CSS_SELECTOR, "svg[data-icon='chevron-down'], svg[data-icon='chevron-right'], .fa-chevron-down, .fa-chevron-right")
                            if chevron:
                                navigation_sections.append({
                                    'element': element,
                                    'title': title,
                                    'type': 'expandable_section'
                                })
                                seen_titles.add(title)
                                print(f"Found expandable section: {title}")
                    except Exception as e:
                        continue
            
            print(f"Found {len(navigation_sections)} new navigation sections")
            return navigation_sections
            
        except Exception as e:
            print(f"Error finding navigation sections: {e}")
            return []
    
    def click_navigation_section(self, section):
        """Click a navigation section to expand it and reveal endpoint links."""
        try:
            element = section['element']
            title = section['title']
            
            if title in self.clicked_sections:
                print(f"Section '{title}' already clicked, skipping...")
                return False
            
            print(f"Clicking section: {title}")
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)
            
            # Try multiple click methods
            click_success = False
            
            try:
                # Method 1: Direct click
                element.click()
                click_success = True
                print(f"✅ Clicked '{title}' successfully (direct)")
            except ElementClickInterceptedException:
                try:
                    # Method 2: JavaScript click
                    self.driver.execute_script("arguments[0].click();", element)
                    click_success = True
                    print(f"✅ Clicked '{title}' successfully (JavaScript)")
                except Exception as e:
                    try:
                        # Method 3: ActionChains click
                        ActionChains(self.driver).move_to_element(element).click().perform()
                        click_success = True
                        print(f"✅ Clicked '{title}' successfully (ActionChains)")
                    except Exception as e:
                        print(f"❌ Failed to click '{title}': {e}")
            
            if click_success:
                self.clicked_sections.add(title)
                time.sleep(2)  # Wait for content to load after click
                return True
            
            return False
            
        except Exception as e:
            print(f"Error clicking section '{section.get('title', 'unknown')}': {e}")
            return False
    
    def extract_endpoint_links(self):
        """Extract all visible endpoint links from the current page state."""
        links = []
        
        try:
            # Look for ElementsTableOfContentsItem anchor tags
            link_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ElementsTableOfContentsItem[href]")
            
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
                    
                    # Extract section/category (look for parent section)
                    section = "Unknown"
                    try:
                        # Look for the parent section title by traversing up
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
                        "section": section,
                        "source": "navigation_click"
                    }
                    links.append(link_info)
                    print(f"Extracted: [{method}] {operation_text}")
                    
                except Exception as e:
                    print(f"Error extracting link details: {e}")
                    continue
            
            return links
            
        except Exception as e:
            print(f"Error extracting endpoint links: {e}")
            return []
    
    def click_all_navigation_and_extract_links(self):
        """Main method to click all navigation sections and extract all endpoint links."""
        print("Starting comprehensive link extraction...")
        
        # Start Chrome
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
            
            # Extract initially visible links
            print("\n=== Extracting initially visible links ===")
            initial_links = self.extract_endpoint_links()
            self.all_links.extend(initial_links)
            print(f"Found {len(initial_links)} initially visible links")
            
            # Find all navigation sections (limit to prevent infinite loops)
            print("\n=== Finding navigation sections ===")
            navigation_sections = self.find_navigation_sections()
            
            # Limit the number of sections to click to prevent infinite loops
            max_sections = min(len(navigation_sections), 50)  # Limit to 50 sections
            if len(navigation_sections) > max_sections:
                print(f"Limiting to first {max_sections} sections to prevent infinite loops")
                navigation_sections = navigation_sections[:max_sections]
            
            # Click each section and extract new links
            print(f"\n=== Clicking {len(navigation_sections)} navigation sections ===")
            for i, section in enumerate(navigation_sections):
                print(f"\nProcessing section {i+1}/{len(navigation_sections)}: {section['title']}")
                
                if self.click_navigation_section(section):
                    # Extract links after clicking this section
                    new_links = self.extract_endpoint_links()
                    
                    # Add only new links (not already collected)
                    existing_urls = {link['url'] for link in self.all_links}
                    truly_new_links = [link for link in new_links if link['url'] not in existing_urls]
                    
                    if truly_new_links:
                        self.all_links.extend(truly_new_links)
                        print(f"Found {len(truly_new_links)} new links in this section")
                    else:
                        print("No new links found in this section")
                else:
                    print(f"Failed to click section: {section['title']}")
                
                # Small delay between sections
                time.sleep(1)
            
            # Remove any remaining duplicates
            unique_links = []
            seen_urls = set()
            for link in self.all_links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            self.all_links = unique_links
            
            print(f"\n=== EXTRACTION COMPLETE ===")
            print(f"Total unique links extracted: {len(self.all_links)}")
            
            # Save to file
            self.save_links()
            self.print_summary()
            
            return True
            
        except Exception as e:
            print(f"Error during link extraction: {e}")
            return False
        
        finally:
            self.cleanup()
    
    def save_links(self):
        """Save discovered links to JSON file."""
        try:
            output_data = {
                "base_url": self.base_url,
                "extraction_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_links": len(self.all_links),
                "clicked_sections": list(self.clicked_sections),
                "links": self.all_links
            }
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"Links saved to: {self.output_file}")
            
        except Exception as e:
            print(f"Error saving links: {e}")
    
    def print_summary(self):
        """Print a summary of extracted links."""
        print("\n" + "="*70)
        print("COMPREHENSIVE LINK EXTRACTION SUMMARY")
        print("="*70)
        
        # Group by section
        by_section = {}
        for link in self.all_links:
            section = link.get('section', 'Unknown')
            if section not in by_section:
                by_section[section] = []
            by_section[section].append(link)
        
        # Group by HTTP method
        by_method = {}
        for link in self.all_links:
            method = link.get('method', 'Unknown')
            if method not in by_method:
                by_method[method] = []
            by_method[method].append(link)
        
        print(f"\nSections clicked: {len(self.clicked_sections)}")
        for section in self.clicked_sections:
            print(f"  ✅ {section}")
        
        print(f"\nLinks by section:")
        for section, links in by_section.items():
            print(f"  {section}: {len(links)} links")
        
        print(f"\nLinks by HTTP method:")
        for method, links in by_method.items():
            print(f"  {method}: {len(links)} links")
        
        print(f"\nSample links:")
        for i, link in enumerate(self.all_links[:10]):
            method = f"[{link['method']}]" if link['method'] else "[?]"
            print(f"  {i+1:2d}. {method} {link['operation_text'][:50]}...")
            print(f"      → {link['url']}")
        
        if len(self.all_links) > 10:
            print(f"  ... and {len(self.all_links) - 10} more")
        
        print(f"\nTotal unique links: {len(self.all_links)}")
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

def main():
    """Main function to run the navigation clicker."""
    clicker = NavigationClicker()
    success = clicker.click_all_navigation_and_extract_links()
    
    if success:
        print("\n✅ Successfully extracted all endpoint links!")
        print(f"Check {clicker.output_file} for the complete list.")
    else:
        print("\n❌ Link extraction failed. Check the error messages above.")

if __name__ == "__main__":
    main()
