# URL Cleanup Tools for Verzeichnis.json

This directory contains tools to fix and analyze URLs in the Verzeichnis.json file.

## Scripts

### 1. main.py (Recommended)
**Complete URL processing pipeline** that chains together cleanup and extraction.

**Features:**
- Runs URL cleanup automatically
- Extracts URLs from both original and cleaned versions
- Compares before/after results
- Generates comprehensive reports
- Creates timestamped files for tracking

**Usage:**
```bash
cd normstelle/excelmigration/Verzeichnis/testing/urls_cleanup/
python main.py                    # Run full pipeline
python main.py --cleanup-only     # Only run URL cleanup
python main.py --extract-only     # Only extract URLs
python main.py -i myfile.json     # Use different input file
```

**Output files:**
- `Verzeichnis_backup_TIMESTAMP.json` - Backup of original
- `Verzeichnis_cleaned_TIMESTAMP.json` - Cleaned version
- `urls_original_TIMESTAMP.txt` - URLs from original file
- `urls_cleaned_TIMESTAMP.txt` - URLs from cleaned file
- `url_processing_report_TIMESTAMP.json` - Detailed analysis report

### 2. url_cleanup.py
Main script that fixes URLs in Verzeichnis.json based on replacement rules.

**Features:**
- Reads replacement rules from the `replace` file
- Applies URL transformations to fix broken paths
- Ignores URLs specified in ignore lists
- Creates automatic backup before processing
- Provides detailed statistics on changes made

**Usage:**
```bash
cd normstelle/excelmigration/Verzeichnis/testing/urls_cleanup/
python url_cleanup.py
```

**What it does:**
- Replaces old server paths with new ones:
  - `\\Dehesdna-a009a\projekte\k-z\ofs\Dokumentenservice\TeileundStoffe` → `\\deberdna-c010a\GlobalDE\DocumentManagement\Ofs\obl\Dokumentenservice\TeileundStoffe\`
  - Similar replacements for other old server paths
  - Relative paths (`../`, `..\`) → new base path
- Ignores HTTP URLs and dead file paths
- Creates `Verzeichnis_backup.json` before making changes

### 2. url_test_analyzer.py
Analysis script that provides detailed statistics on URL fix success rates.

**Features:**
- Analyzes URLs before and after cleanup
- Categorizes URLs by type (needs fixing, already fixed, ignored, etc.)
- Calculates success rates including and excluding ignored URLs
- Provides detailed breakdowns by column and URL type
- Compares before/after statistics if backup exists

**Usage:**
```bash
python url_test_analyzer.py
```

**Reports:**
- Total URLs processed
- Fix rates (including and excluding ignored URLs)
- URL categories breakdown
- Column-wise statistics
- Before/after comparison
- Sample URLs for each category

## Files

- `replace` - Contains replacement rules and ignore patterns
- `urls_dead.txt` - List of dead URLs to ignore during processing
- `Verzeichnis.json` - Main data file (large, don't open directly)
- `Verzeichnis_backup.json` - Backup created before cleanup

## Replacement Rules

From the `replace` file:

**Replace these patterns:**
- `\\Dehesdna-a009a\projekte\k-z\ofs\Dokumentenservice\TeileundStoffe`
- `\\Dehesdna-a007a\projekte\k-z\ofs\Dokumentenservice\TeileundStoffe`
- `\\Dehesdna-a0079a\projekte\k-z\ofs\Dokumentenservice\TeileundStoffe`
- `\\Deberdna-a018a\projekte\k-z\ofs\Dokumentenservice\TeileundStoffe`
- `../`
- `..\`

**With:**
- `\\deberdna-c010a\GlobalDE\DocumentManagement\Ofs\obl\Dokumentenservice\TeileundStoffe\`

**Ignore:**
- HTTP/HTTPS URLs
- Dead file paths listed in `urls_dead.txt`
- Specific problematic URLs listed in `replace` file

## Workflow

### Recommended (Using main.py):
```bash
# Run complete pipeline - cleanup, extraction, and analysis
python main.py
```

### Manual (Step by step):

1. **First run the analyzer** to see current state:
   ```bash
   python url_test_analyzer.py
   ```

2. **Run the cleanup** to fix URLs:
   ```bash
   python url_cleanup.py
   ```

3. **Extract URLs from both versions**:
   ```bash
   python url_extract.py -o urls_original.txt  # Before cleanup
   # Copy cleaned file to main location, then:
   python url_extract.py -o urls_cleaned.txt   # After cleanup
   ```

4. **Run analyzer again** to see results and success rates:
   ```bash
   python url_test_analyzer.py
   ```

## Expected Results

### Using main.py pipeline:
- **Automated processing**: Complete cleanup and analysis in one command
- **Timestamped outputs**: All files include timestamps to prevent overwrites
- **Comprehensive comparison**: Before/after URL analysis with change detection
- **Detailed reporting**: JSON report with complete statistics and sample changes
- **Success rates**: Typically above 80% for fixable URLs

### Individual cleanup process:
- Fix broken network paths by updating server names
- Convert relative paths to absolute paths
- Leave ignored URLs unchanged
- Provide success rates typically above 80% for fixable URLs

## Safety Features

- **Automatic timestamped backups**: Creates `Verzeichnis_backup_TIMESTAMP.json` before any changes
- **No overwriting**: Original files are preserved, new cleaned files are created
- **Ignore lists**: Won't modify URLs that should be left alone
- **Detailed logging**: Shows exactly what was changed
- **Comprehensive reporting**: JSON reports with complete statistics and analysis
- **Change tracking**: Detailed before/after comparisons
