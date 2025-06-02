# Offline Assets Download Script

This script downloads external dependencies (CSS, JavaScript, and images) used in the Normie Django application to enable offline functionality.

## What it downloads

1. **Font Awesome CSS** (6.4.0) - Icons used throughout the application
2. **Font Awesome Fonts** - WOFF/WOFF2 font files referenced by the CSS
3. **jQuery JavaScript** (3.6.4) - JavaScript library
4. **Flag Images** - Country flag images for language toggle (US, DE, FR, ES, IT)

## Prerequisites

Install the required Python package:

```bash
pip install -r requirements_download.txt
```

Or install manually:

```bash
pip install requests
```

## Usage

1. **Run the download script:**
   ```bash
   python download_external_assets.py
   ```

2. **The script will:**
   - Create necessary directories in `normieapp/static/normieapp/`
   - Download all external assets
   - Update Font Awesome CSS to use local font paths
   - Create an offline version of the base template (`base_offline.html`)

3. **To switch to offline mode:**
   ```bash
   # Backup the original template
   mv normieapp/templates/normieapp/base.html normieapp/templates/normieapp/base_online.html
   
   # Use the offline template
   mv normieapp/templates/normieapp/base_offline.html normieapp/templates/normieapp/base.html
   ```

4. **To switch back to online mode:**
   ```bash
   # Restore the original template
   mv normieapp/templates/normieapp/base.html normieapp/templates/normieapp/base_offline.html
   mv normieapp/templates/normieapp/base_online.html normieapp/templates/normieapp/base.html
   ```

## Directory Structure

After running the script, the following directories will be created:

```
normieapp/static/normieapp/
├── css/vendor/
│   └── fontawesome.min.css
├── js/vendor/
│   └── jquery-3.6.4.min.js
├── fonts/fontawesome/
│   ├── fa-brands-400.woff2
│   ├── fa-regular-400.woff2
│   ├── fa-solid-900.woff2
│   └── ... (other font files)
└── img/flags/
    ├── us-20x15.png
    ├── us-40x30.png
    ├── us-60x45.png
    ├── de-20x15.png
    └── ... (other flag images)
```

## Template Changes

The offline template (`base_offline.html`) includes the following changes:

1. **Font Awesome CSS:** Points to local file instead of CDN
2. **jQuery:** Points to local file instead of CDN
3. **Flag Images:** Uses local flag images with proper Django template logic

## Benefits

- **Offline functionality:** Application works without internet connection
- **Faster loading:** No external requests needed
- **Reliability:** No dependency on external CDNs
- **Privacy:** No external requests to third-party services

## Notes

- The script is respectful to external servers and includes delays between requests
- Font Awesome fonts are automatically detected and downloaded from the CSS
- Flag images are downloaded for common languages (US, DE, FR, ES, IT)
- You can add more flag images by modifying the `FLAG_IMAGES` list in the script

## Troubleshooting

If downloads fail:
1. Check your internet connection
2. Verify that the external URLs are still valid
3. Check if any firewall is blocking the requests
4. Run the script again (it will skip already downloaded files)

## Updating Assets

To update to newer versions:
1. Modify the URLs in the `ASSETS` dictionary in the script
2. Run the script again
3. Test the application to ensure compatibility 