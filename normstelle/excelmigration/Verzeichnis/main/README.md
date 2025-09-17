# Continuous Excel Updater for Django App

This consolidated script combines the functionality of three separate scripts to provide continuous updates of Excel data for your Django application.

## Features

- **Automatic Excel Fetching**: Retrieves the latest `Verzeichnis.xlsb` from network or local sources
- **Format Conversion**: Converts `.xlsb` to `.xlsx` using Excel COM automation
- **Ultra-Fast Data Extraction**: Uses `openpyxl` for rapid data extraction with hyperlinks and colors
- **URL Cleanup**: Applies replacement rules to normalize file paths and URLs
- **Continuous Updates**: Runs on a schedule to keep data current
- **Django Integration**: Outputs directly to Django static data directory

## Requirements

Install dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- `openpyxl` - For Excel file processing
- `pywin32` - For Excel COM automation (Windows only)

## Usage

### Single Update (Run Once)
```bash
py run_updater.py
# or
py run_updater.py --once
```

### Continuous Updates
```bash
# Run every 30 minutes (default)
py run_updater.py --continuous

# Run every 60 minutes
py run_updater.py --continuous 60

# Run every 15 minutes
py run_updater.py --continuous 15
```

## File Structure

The script expects this Django directory structure:
```
normie/
├── normieapp/
│   └── static/
│       └── normieapp/
│           ├── temp/           # Temporary files during processing
│           └── data/           # Final output location
│               └── Verzeichnis.json
```

## Source Files

The script will attempt to fetch Excel files from:

1. **Primary (Live)**: `\\deberdna-c010a\GlobalDE\DocumentManagement\Ofs\obl\Dokumentenservice\TeileundStoffe\Datei\Verzeichnis.xlsb`
2. **Fallback (Test)**: `D:\GlobalDE\DocumentManagement\Ofs\obl\Dokumentenservice\TeileundStoffe\Datei\Verzeichnis.xlsb`

## URL Cleanup Rules

The script loads URL replacement rules from the `replace` file in the same directory. The file format:

```
replace:
\\Dehesdna-a009a\projekte\k-z\ofs\Dokumentenservice\TeileundStoffe
\\Dehesdna-a007a\projekte\k-z\ofs\Dokumentenservice\TeileundStoffe
../
..\

with:
\\deberdna-c010a\GlobalDE\DocumentManagement\Ofs\obl\Dokumentenservice\TeileundStoffe\

ignore:
http://edm1.dw.brr.de/cgi-bin/DirectShow.pl?doc_name=LBR3044
https://www.ansell.com/de/de/products/alphatec-02-100
+contents of: C:\path\to\dead_urls.txt
```

Features:
- **Replace section**: Patterns to find and replace
- **With section**: Target replacement path
- **Ignore section**: URLs to skip (including external file references)
- **Dead URLs file**: Additional URLs to ignore loaded from external file

## Output

The final JSON file contains:
- **Data**: All Excel rows with extracted values
- **Colors**: Cell background colors mapped to approval statuses
- **Hyperlinks**: Document links with normalized URLs
- **Metadata**: Processing statistics and performance metrics

Example approval status mapping:
- `#FFCC99` → "not approved"
- `#CCFFCC` → "approved"
- `#CCFF99` → "approved for first order"
- `#FFFFFF` → "processing"

## Error Handling

- Automatic cleanup of temporary files on success or failure
- Backup creation before overwriting existing JSON files
- Detailed logging with timestamps
- Graceful handling of missing source files

## Performance

The script is optimized for speed:
- Uses `openpyxl` for direct file reading (no Excel application needed)
- Bulk data operations for maximum throughput
- Selective column processing for hyperlinks
- Memory-efficient processing for large datasets

## Stopping Continuous Updates

Press `Ctrl+C` to stop continuous updates gracefully.

## Troubleshooting

1. **Missing Dependencies**: Install with `pip install -r requirements.txt`
2. **Excel File Not Found**: Check network connectivity and file paths
3. **Permission Errors**: Ensure write access to Django static directories
4. **COM Errors**: Make sure Excel is properly installed (for .xlsb conversion)

## Integration with Django

Once the script is running, your Django app can read the updated JSON data from:
```python
import json
from django.conf import settings

json_path = settings.STATIC_ROOT / 'normieapp' / 'data' / 'Verzeichnis.json'
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
```

The JSON structure includes metadata for cache invalidation:
```python
last_updated = data['metadata']['url_cleanup']['applied']
total_rows = data['metadata']['total_rows']
```
