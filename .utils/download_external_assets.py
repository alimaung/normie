#!/usr/bin/env python3
"""
Script to download external assets for offline use in the Normie Django application.
This script downloads Font Awesome CSS, jQuery JS, and flag images to make the app work offline.
"""

import os
import requests
import re
from urllib.parse import urljoin, urlparse
from pathlib import Path
import time

# Base directories
STATIC_DIR = Path("normieapp/static/normieapp")
CSS_DIR = STATIC_DIR / "css" / "vendor"
JS_DIR = STATIC_DIR / "js" / "vendor"
IMG_DIR = STATIC_DIR / "img" / "flags"
FONTS_DIR = STATIC_DIR / "fonts" / "fontawesome"

# External assets to download
ASSETS = {
    "fontawesome_css": {
        "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
        "local_path": CSS_DIR / "fontawesome.min.css"
    },
    "jquery_js": {
        "url": "https://code.jquery.com/jquery-3.6.4.min.js",
        "local_path": JS_DIR / "jquery-3.6.4.min.js"
    }
}

# Flag images to download (common ones used in the app)
FLAG_IMAGES = [
    {"code": "us", "sizes": ["20x15", "40x30", "60x45"]},
    {"code": "de", "sizes": ["20x15", "40x30", "60x45"]},
    {"code": "fr", "sizes": ["20x15", "40x30", "60x45"]},
    {"code": "es", "sizes": ["20x15", "40x30", "60x45"]},
    {"code": "it", "sizes": ["20x15", "40x30", "60x45"]},
]

def create_directories():
    """Create necessary directories for downloaded assets."""
    directories = [CSS_DIR, JS_DIR, IMG_DIR, FONTS_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def download_file(url, local_path, description=""):
    """Download a file from URL to local path."""
    try:
        print(f"Downloading {description}: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Create parent directory if it doesn't exist
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Downloaded: {local_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {url}: {e}")
        return False

def download_fontawesome_fonts(css_content, css_url):
    """Extract and download Font Awesome font files referenced in CSS."""
    # Find font URLs in the CSS content
    font_urls = re.findall(r'url\(["\']?([^"\']+\.woff2?[^"\']*)["\']?\)', css_content)
    
    for font_url in font_urls:
        # Make absolute URL
        if font_url.startswith('//'):
            font_url = 'https:' + font_url
        elif font_url.startswith('/'):
            font_url = urljoin(css_url, font_url)
        elif not font_url.startswith('http'):
            font_url = urljoin(css_url, font_url)
        
        # Extract filename
        filename = os.path.basename(urlparse(font_url).path)
        if not filename:
            continue
            
        local_font_path = FONTS_DIR / filename
        download_file(font_url, local_font_path, f"Font Awesome font ({filename})")
        
        # Add a small delay to be respectful to the server
        time.sleep(0.1)

def update_css_font_paths(css_content):
    """Update font URLs in CSS to point to local files."""
    # Replace font URLs with local paths and remove fallback TTF references
    def replace_font_url(match):
        original_url = match.group(1)
        filename = os.path.basename(urlparse(original_url).path)
        if filename and filename.endswith('.woff2'):
            # From css/vendor/ to fonts/fontawesome/ we need to go up two levels: ../../fonts/fontawesome/
            return f'url("../../fonts/fontawesome/{filename}") format("woff2")'
        return match.group(0)
    
    # First, replace the WOFF2 URLs with local paths - handle both with and without existing format declarations
    updated_css = re.sub(r'url\(["\']?([^"\']+\.woff2[^"\']*)["\']?\)(?:\s*format\([^)]*\))?', replace_font_url, css_content)
    
    # Remove the fallback TTF references that don't exist locally
    # This removes patterns like: ,url(../webfonts/fa-brands-400.ttf) format("truetype")
    updated_css = re.sub(r',url\([^)]*webfonts/[^)]*\.ttf[^)]*\)[^,}]*', '', updated_css)
    
    # Clean up any duplicate format declarations that might have been created
    updated_css = re.sub(r'format\("woff2"\)\s*format\("woff2"\)', 'format("woff2")', updated_css)
    
    return updated_css

def download_flag_images():
    """Download flag images for language toggle."""
    print("\nDownloading flag images...")
    
    for flag in FLAG_IMAGES:
        code = flag["code"]
        for size in flag["sizes"]:
            url = f"https://flagcdn.com/{size}/{code}.png"
            local_path = IMG_DIR / f"{code}-{size}.png"
            download_file(url, local_path, f"Flag image ({code} {size})")
            time.sleep(0.1)  # Be respectful to the server

def download_main_assets():
    """Download main CSS and JS assets."""
    print("Downloading main assets...")
    
    for asset_name, asset_info in ASSETS.items():
        url = asset_info["url"]
        local_path = asset_info["local_path"]
        
        if download_file(url, local_path, asset_name):
            # Special handling for Font Awesome CSS
            if asset_name == "fontawesome_css":
                print("Processing Font Awesome CSS and downloading fonts...")
                
                # Read the downloaded CSS
                with open(local_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                
                # Download referenced fonts
                download_fontawesome_fonts(css_content, url)
                
                # Update CSS to use local font paths
                updated_css = update_css_font_paths(css_content)
                
                # Write updated CSS
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(updated_css)
                
                print("✓ Updated Font Awesome CSS with local font paths")

def create_offline_base_template():
    """Create an offline version of the base template."""
    offline_template_path = Path("normieapp/templates/normieapp/base_offline.html")
    
    # Read the original template
    with open("normieapp/templates/normieapp/base.html", 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Replace external URLs with local ones
    replacements = {
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css': '{% static "normieapp/css/vendor/fontawesome.min.css" %}',
        'https://code.jquery.com/jquery-3.6.4.min.js': '{% static "normieapp/js/vendor/jquery-3.6.4.min.js" %}',
    }
    
    for external_url, local_url in replacements.items():
        template_content = template_content.replace(external_url, local_url)
    
    # Update flag image URLs to use local files
    # Replace the dynamic flag URLs with a more complex template logic for offline use
    flag_pattern = r'https://flagcdn\.com/(\d+x\d+)/{% if LANGUAGE_CODE == \'en\' %}us{% elif LANGUAGE_CODE == \'de\' %}de{% else %}{{ LANGUAGE_CODE }}{% endif %}\.png'
    flag_replacement = r'{% static "normieapp/img/flags/" %}{% if LANGUAGE_CODE == "en" %}us{% elif LANGUAGE_CODE == "de" %}de{% else %}{{ LANGUAGE_CODE }}{% endif %}-\1.png'
    
    template_content = re.sub(flag_pattern, flag_replacement, template_content)
    
    # Write the offline template
    with open(offline_template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✓ Created offline template: {offline_template_path}")

def main():
    """Main function to download all external assets."""
    print("🚀 Starting download of external assets for offline use...")
    print("=" * 60)
    
    # Create directories
    create_directories()
    
    # Download main assets (CSS, JS)
    download_main_assets()
    
    # Download flag images
    download_flag_images()
    
    # Create offline template
    create_offline_base_template()
    
    print("\n" + "=" * 60)
    print("✅ Download complete!")
    print("\nTo use offline mode:")
    print("1. Rename 'base.html' to 'base_online.html'")
    print("2. Rename 'base_offline.html' to 'base.html'")
    print("3. Your app will now work offline!")
    print("\nDownloaded files:")
    print(f"  - CSS: {CSS_DIR}")
    print(f"  - JS: {JS_DIR}")
    print(f"  - Fonts: {FONTS_DIR}")
    print(f"  - Flags: {IMG_DIR}")

if __name__ == "__main__":
    main() 