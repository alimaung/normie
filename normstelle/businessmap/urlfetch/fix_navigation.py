#!/usr/bin/env python3
"""
Fix navigation in offline mirror by replacing hash-based SPA links 
with direct links to our static HTML files.
"""

import os
import re
import json
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class NavigationFixer:
    def __init__(self, mirror_dir="expand_mirror_optimized", links_file="extracted_links.json"):
        self.mirror_dir = Path(mirror_dir)
        self.links_file = Path(links_file)
        self.url_to_filename_map = {}
        self.all_links = []
        
    def load_url_mappings(self):
        """Load the original URLs and create mapping to filenames."""
        try:
            # Load original links
            with open(self.links_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.all_links = data.get('links', [])
            
            # Create URL to filename mapping
            for link_info in self.all_links:
                original_url = link_info['url']
                parsed = urlparse(original_url)
                
                # Create filename from URL (same logic as mirror script)
                filename = self.create_filename_from_url(original_url)
                
                # Map fragment to filename
                fragment = parsed.fragment.lstrip('/')
                if fragment:
                    self.url_to_filename_map[f"#{fragment}"] = filename
                    self.url_to_filename_map[f"#/{fragment}"] = filename
                    self.url_to_filename_map[f"#//{fragment}"] = filename
                    
                    # Also map without leading slash variations
                    if fragment.startswith('operations/'):
                        op_name = fragment.replace('operations/', '')
                        self.url_to_filename_map[f"#operations/{op_name}"] = filename
                        self.url_to_filename_map[f"#{op_name}"] = filename
                    
                    if fragment.startswith('paths/'):
                        path_name = fragment.replace('paths/', '')
                        self.url_to_filename_map[f"#paths/{path_name}"] = filename
                        self.url_to_filename_map[f"#{path_name}"] = filename
            
            # Add main page mapping
            self.url_to_filename_map["#/"] = "index.html"
            self.url_to_filename_map["#"] = "index.html"
            self.url_to_filename_map[""] = "index.html"
            
            print(f"✅ Created mappings for {len(self.url_to_filename_map)} URL patterns")
            return True
            
        except Exception as e:
            print(f"❌ Error loading URL mappings: {e}")
            return False
    
    def create_filename_from_url(self, url):
        """Create a safe filename from a URL (same logic as mirror script)."""
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
    
    def fix_navigation_in_html(self, html_content):
        """Fix navigation links in HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all links with href attributes
            links = soup.find_all('a', href=True)
            fixed_count = 0
            
            for link in links:
                href = link['href']
                
                # Skip external links and already fixed links
                if href.startswith(('http://', 'https://', 'mailto:', 'tel:')):
                    continue
                    
                if href.endswith('.html'):
                    continue  # Already fixed
                
                # Check if this is a hash-based navigation link
                if href in self.url_to_filename_map:
                    new_href = self.url_to_filename_map[href]
                    link['href'] = new_href
                    fixed_count += 1
                    print(f"  Fixed: {href} → {new_href}")
                
                # Handle some common variations
                elif href.startswith('#/') and href[2:] in self.url_to_filename_map:
                    new_href = self.url_to_filename_map[href[2:]]
                    link['href'] = new_href
                    fixed_count += 1
                    print(f"  Fixed: {href} → {new_href}")
            
            if fixed_count > 0:
                print(f"  ✅ Fixed {fixed_count} navigation links")
            
            return str(soup)
            
        except Exception as e:
            print(f"  ❌ Error fixing navigation: {e}")
            return html_content
    
    def disable_spa_navigation(self, html_content):
        """Disable SPA navigation JavaScript to prevent conflicts."""
        try:
            # Add script to disable hash navigation
            disable_script = """
<script>
// Disable SPA hash navigation for offline use
(function() {
    console.log('🔧 Offline navigation override active');
    
    // Override hash change behavior
    window.addEventListener('hashchange', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Hash change blocked for offline compatibility');
        return false;
    }, true);
    
    // Override pushState/replaceState
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;
    
    history.pushState = function() {
        console.log('pushState blocked for offline compatibility');
        return false;
    };
    
    history.replaceState = function() {
        console.log('replaceState blocked for offline compatibility');
        return false;
    };
    
    console.log('✅ Offline navigation ready');
})();
</script>
"""
            
            # Insert before closing head tag
            if '</head>' in html_content:
                html_content = html_content.replace('</head>', disable_script + '\n</head>')
            else:
                # Fallback: add at end of body
                html_content = html_content.replace('</body>', disable_script + '\n</body>')
            
            return html_content
            
        except Exception as e:
            print(f"  ❌ Error disabling SPA navigation: {e}")
            return html_content
    
    def fix_navigation_in_file(self, file_path):
        """Fix navigation in a single HTML file."""
        try:
            print(f"🔧 Fixing navigation in: {file_path.name}")
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Fix navigation links
            fixed_html = self.fix_navigation_in_html(html_content)
            
            # Disable SPA navigation
            final_html = self.disable_spa_navigation(fixed_html)
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_html)
            
            print(f"  ✅ Navigation fixed in: {file_path.name}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error fixing {file_path}: {e}")
            return False
    
    def fix_all_navigation(self):
        """Fix navigation in all HTML files in the mirror directory."""
        print("🚀 Starting navigation fix for offline mirror...")
        
        # Load URL mappings
        if not self.load_url_mappings():
            print("❌ Failed to load URL mappings")
            return False
        
        # Find all HTML files
        html_files = list(self.mirror_dir.glob('*.html'))
        
        if not html_files:
            print(f"❌ No HTML files found in {self.mirror_dir}")
            return False
        
        print(f"📄 Found {len(html_files)} HTML files to fix")
        
        # Fix navigation in each file
        successful_count = 0
        failed_count = 0
        
        for html_file in html_files:
            if self.fix_navigation_in_file(html_file):
                successful_count += 1
            else:
                failed_count += 1
        
        # Summary
        print(f"\n🎉 Navigation fix completed!")
        print(f"✅ Successfully fixed: {successful_count} files")
        print(f"❌ Failed to fix: {failed_count} files")
        print(f"📁 Directory: {self.mirror_dir}")
        
        if successful_count > 0:
            print(f"\n🌐 Navigation is now fixed for offline use!")
            print(f"🔗 Links will now go directly to the correct HTML files")
            print(f"🚫 SPA JavaScript navigation has been disabled")
            print(f"\nTo test: python -m http.server 8000 --directory {self.mirror_dir}")
            print(f"Then open: http://localhost:8000/index.html")
        
        return successful_count > 0

def main():
    """Main function to fix navigation."""
    print("🔧 Navigation Fixer for Offline Mirror")
    print("=" * 50)
    
    fixer = NavigationFixer()
    success = fixer.fix_all_navigation()
    
    if success:
        print("\n✅ Navigation fix completed successfully!")
        print("🎯 Sidebar navigation should now work properly!")
    else:
        print("\n❌ Navigation fix failed!")

if __name__ == "__main__":
    main()
