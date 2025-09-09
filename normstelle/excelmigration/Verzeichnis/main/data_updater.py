#!/usr/bin/env python3
"""
Consolidated Data Updater for Django App
========================================

This script continuously fetches the latest Excel file, processes it, and updates
the JSON data for the Django application.

Features:
- Fetches latest Excel from network (live/test paths)
- Converts xlsb → xlsx in temp directory  
- Extracts data with hyperlinks and approval statuses
- Applies URL cleanup rules
- Saves final JSON to Django static data directory
- Continuous update loop with configurable intervals
- Comprehensive error handling and logging
"""

import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataUpdater:
    """Consolidated data updater for Excel → JSON pipeline."""
    
    def __init__(self, 
                 temp_dir: str = r"C:\Users\RAVEN\Desktop\normie\normie\normieapp\static\normieapp\temp",
                 data_file: str = r"C:\Users\RAVEN\Desktop\normie\normie\normieapp\static\normieapp\data\Verzeichnis.json"):
        
        self.temp_dir = Path(temp_dir)
        self.data_file = Path(data_file)
        
        # Source paths
        self.live_src = r"\\deberdna-c010a\GlobalDE\DocumentManagement\Ofs\obl\Dokumentenservice\TeileundStoffe\Datei\Verzeichnis.xlsb"
        self.test_src = r"D:\GlobalDE\DocumentManagement\Ofs\obl\Dokumentenservice\TeileundStoffe\Datei\Verzeichnis.xlsb"
        
        # URL cleanup configuration
        self.replacement_rules = []
        self.ignore_patterns = set()
        self.dead_urls = set()
        self.target_replacement = ""
        
        # Statistics
        self.stats = {
            'updates_completed': 0,
            'last_update': None,
            'last_error': None,
            'total_errors': 0
        }
        
        # Ensure directories exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DataUpdater initialized")
        logger.info(f"Temp directory: {self.temp_dir}")
        logger.info(f"Data file: {self.data_file}")

    def pick_source_path(self) -> Path:
        """Return the first available source path (live first, then testing)."""
        live = Path(self.live_src)
        if live.exists():
            logger.info(f"Using live source: {live}")
            return live
            
        test = Path(self.test_src)
        if test.exists():
            logger.info(f"Using test source: {test}")
            return test
            
        raise FileNotFoundError(
            f"Neither live nor testing source file was found.\n"
            f"Live: {self.live_src}\n"
            f"Test: {self.test_src}"
        )

    def copy_and_convert_excel(self, src_path: Path) -> Path:
        """Copy Excel file to temp directory and convert xlsb → xlsx."""
        try:
            import win32com.client  # type: ignore
            import pythoncom
        except ImportError as exc:
            raise RuntimeError(
                "pywin32 is required. Install with: pip install pywin32"
            ) from exc

        # Copy to temp directory
        temp_xlsb = self.temp_dir / "Verzeichnis.xlsb"
        temp_xlsx = self.temp_dir / "Verzeichnis.xlsx"
        
        logger.info(f"Copying {src_path} → {temp_xlsb}")
        shutil.copy2(src_path, temp_xlsb)
        
        # Remove existing xlsx if it exists
        if temp_xlsx.exists():
            temp_xlsx.unlink()

        excel = None
        workbook = None
        try:
            logger.info("Converting xlsb → xlsx using Excel COM")
            pythoncom.CoInitialize()
            
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False

            # Open with read-only and no link updates for speed
            workbook = excel.Workbooks.Open(str(temp_xlsb), UpdateLinks=0, ReadOnly=1)
            
            # Save as xlsx (FileFormat=51)
            workbook.SaveAs(str(temp_xlsx), FileFormat=51)
            workbook.Close(SaveChanges=False)
            
            logger.info(f"Conversion completed: {temp_xlsx}")
            
        finally:
            # Cleanup COM objects
            try:
                if workbook is not None:
                    workbook.Close(SaveChanges=False)
                if excel is not None:
                    excel.Quit()
                pythoncom.CoUninitialize()
            except Exception as e:
                logger.warning(f"COM cleanup warning: {e}")

        # Remove temporary xlsb file
        try:
            temp_xlsb.unlink()
            logger.info(f"Removed temporary file: {temp_xlsb}")
        except Exception as e:
            logger.warning(f"Could not remove temp file {temp_xlsb}: {e}")

        return temp_xlsx

    def extract_excel_data(self, xlsx_path: Path) -> Dict:
        """Extract data and hyperlinks from Excel file."""
        try:
            import win32com.client as win32
            import pythoncom
        except ImportError as exc:
            raise RuntimeError("pywin32 is required for data extraction") from exc

        excel_app = None
        workbook = None
        
        try:
            logger.info(f"Extracting data from: {xlsx_path}")
            
            pythoncom.CoInitialize()
            excel_app = win32.Dispatch("Excel.Application")
            excel_app.Visible = False
            excel_app.DisplayAlerts = False
            
            workbook = excel_app.Workbooks.Open(str(xlsx_path))
            worksheet = workbook.ActiveSheet
            
            # Get data bounds
            used_range = worksheet.UsedRange
            max_col = min(used_range.Columns.Count, 27)  # Limit to AA
            max_row = min(used_range.Rows.Count, 5000)   # Reasonable limit
            
            logger.info(f"Processing {max_row} rows and {max_col} columns")
            
            # Extract headers
            headers = []
            for col in range(1, max_col + 1):
                cell_value = worksheet.Cells(1, col).Value
                headers.append(cell_value if cell_value else f"Column_{chr(ord('A') + col - 1)}")
            
            # Identify hyperlink columns (M to U = 13 to 21)
            hyperlink_col_indices = list(range(13, min(22, max_col + 1)))
            hyperlink_col_names = [headers[i-1] for i in hyperlink_col_indices if i <= len(headers)]
            
            logger.info(f"Hyperlink columns: {hyperlink_col_names}")
            
            # Extract data
            data_rows = []
            hyperlink_count = 0
            color_count = 0
            
            for row_num in range(2, max_row + 1):
                row_data = {}
                
                # Extract color from column A for approval status
                cell_a = worksheet.Cells(row_num, 1)
                try:
                    rgb_value = cell_a.Interior.Color
                    cell_color = self.rgb_to_hex(rgb_value)
                    
                    if cell_color and cell_color != "#FFFFFF":
                        row_data['color'] = cell_color
                        row_data['status'] = self.map_color_to_status(cell_color)
                        color_count += 1
                    else:
                        row_data['color'] = "#FFFFFF"
                        row_data['status'] = "processing"
                        
                except Exception as e:
                    logger.warning(f"Color extraction error row {row_num}: {e}")
                    row_data['color'] = None
                    row_data['status'] = "unknown"
                
                # Process each column
                for col_idx, header in enumerate(headers):
                    col_num = col_idx + 1
                    if col_num > max_col:
                        break
                        
                    cell = worksheet.Cells(row_num, col_num)
                    
                    # Handle hyperlink columns
                    if col_num in hyperlink_col_indices:
                        try:
                            if cell.Hyperlinks.Count > 0:
                                hyperlink = cell.Hyperlinks(1)
                                target = hyperlink.Address
                                subaddress = hyperlink.SubAddress if hasattr(hyperlink, 'SubAddress') else None
                                
                                if target and subaddress:
                                    full_target = f"{target}#{subaddress}"
                                else:
                                    full_target = target or subaddress
                                
                                # Initial URL normalization
                                normalized_target = self.normalize_url(full_target)
                                
                                row_data[header] = {
                                    'display_text': cell.Value,
                                    'url': normalized_target,
                                    'original_url': full_target if full_target != normalized_target else None,
                                    'tooltip': hyperlink.ScreenTip if hasattr(hyperlink, 'ScreenTip') else None
                                }
                                hyperlink_count += 1
                                
                            elif cell.Value:
                                # Handle file paths in cells without hyperlinks
                                cell_value = str(cell.Value).strip()
                                if self.looks_like_file_path(cell_value):
                                    normalized_path = self.normalize_url(cell_value)
                                    row_data[header] = {
                                        'display_text': cell.Value,
                                        'url': normalized_path,
                                        'original_url': cell_value if cell_value != normalized_path else None,
                                        'tooltip': None,
                                        'type': 'inferred_file_path'
                                    }
                                else:
                                    row_data[header] = {
                                        'display_text': cell.Value,
                                        'url': None,
                                        'tooltip': None
                                    }
                            else:
                                row_data[header] = None
                                
                        except Exception as e:
                            logger.warning(f"Hyperlink processing error row {row_num}, col {header}: {e}")
                            row_data[header] = {
                                'display_text': cell.Value,
                                'url': None,
                                'tooltip': None,
                                'error': str(e)
                            }
                    else:
                        # Regular data column
                        try:
                            row_data[header] = cell.Value
                        except Exception as e:
                            logger.warning(f"Cell read error row {row_num}, col {header}: {e}")
                            row_data[header] = None
                
                data_rows.append(row_data)
                
                if row_num % 500 == 0:
                    logger.info(f"Processed {row_num - 1} rows...")
            
            logger.info(f"Extraction completed: {len(data_rows)} rows, {hyperlink_count} hyperlinks, {color_count} colors")
            
            # Create final data structure
            data_dict = {
                'metadata': {
                    'total_rows': len(data_rows),
                    'total_columns': len(headers),
                    'columns': headers,
                    'source_file': xlsx_path.name,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'hyperlinks_extracted': True,
                    'hyperlink_columns': hyperlink_col_names,
                    'colors_extracted': True,
                    'color_mapping': {
                        '#FFCC99': 'not approved',
                        '#CCFFCC': 'approved',
                        '#CCFF99': 'approved for first order',
                        '#FFFFFF': 'processing'
                    },
                    'extraction_method': 'win32com'
                },
                'data': data_rows
            }
            
            return data_dict
            
        finally:
            try:
                if workbook:
                    workbook.Close(SaveChanges=False)
                if excel_app:
                    excel_app.Quit()
                pythoncom.CoUninitialize()
            except Exception as e:
                logger.warning(f"COM cleanup error: {e}")

    def load_replacement_rules(self, replace_file: str = "replace"):
        """Load URL replacement rules from file."""
        replace_path = Path(replace_file)
        
        if not replace_path.exists():
            logger.warning(f"Replace file not found: {replace_path}")
            return
            
        try:
            with open(replace_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.lower() == 'replace:':
                    current_section = 'replace'
                elif line.lower() == 'with:':
                    current_section = 'with'
                elif line.lower() == 'ignore:':
                    current_section = 'ignore'
                elif line.startswith('+contents of:'):
                    ignore_file = line.split(':', 1)[1].strip()
                    self.load_ignore_file(ignore_file)
                elif current_section == 'replace':
                    self.replacement_rules.append(line)
                elif current_section == 'with':
                    self.target_replacement = line
                elif current_section == 'ignore':
                    self.ignore_patterns.add(line)
            
            logger.info(f"Loaded {len(self.replacement_rules)} replacement rules")
            
        except Exception as e:
            logger.error(f"Error loading replacement rules: {e}")

    def load_ignore_file(self, file_path: str):
        """Load URLs to ignore from separate file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.dead_urls.add(line)
            logger.info(f"Loaded {len(self.dead_urls)} dead URLs from {file_path}")
        except FileNotFoundError:
            logger.warning(f"Ignore file not found: {file_path}")
        except Exception as e:
            logger.error(f"Error loading ignore file: {e}")

    def cleanup_urls(self, data: Dict) -> int:
        """Apply URL cleanup rules to the data."""
        if not self.replacement_rules:
            logger.info("No replacement rules loaded, skipping URL cleanup")
            return 0
            
        changes = 0
        total_urls = 0
        
        hyperlink_columns = [
            "Antrag", "Datenblatt", "Produkt-zulassung", "SDB MSDS",
            "Gefährdungsprüfungeurteilung", "Gefährdungsprüfung", 
            "Sonstiges", "Schriftverkehr", "Änd. Historie"
        ]
        
        for entry in data.get('data', []):
            for column in hyperlink_columns:
                if column in entry and entry[column] and isinstance(entry[column], dict):
                    url_obj = entry[column]
                    if 'url' in url_obj and url_obj['url']:
                        total_urls += 1
                        original_url = url_obj['url']
                        
                        if not self.should_ignore_url(original_url):
                            fixed_url, was_changed = self.fix_url(original_url)
                            if was_changed:
                                url_obj['url'] = fixed_url
                                changes += 1
        
        logger.info(f"URL cleanup completed: {changes} URLs fixed out of {total_urls} total")
        return changes

    def normalize_url(self, url: str) -> str:
        """Normalize URLs by replacing relative paths with full network paths."""
        if not url:
            return url
        
        if url.startswith("../.docs"):
            relative_part = url[8:]  # Remove "../.docs"
            relative_part = relative_part.replace('/', '\\')
            normalized_url = f"file:///\\\\Dehesdna-a009a\\projekte\\k-z\\ofs\\Dokumentenservice\\TeileundStoffe{relative_part}"
            return normalized_url
        
        return url

    def looks_like_file_path(self, value: str) -> bool:
        """Check if a string looks like a file path."""
        return (value.startswith(('C:', 'D:', 'E:', '\\\\', './', '../')) or 
                '\\' in value or 
                value.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')))

    def should_ignore_url(self, url: str) -> bool:
        """Check if URL should be ignored."""
        if not url:
            return True
            
        for pattern in self.ignore_patterns:
            if pattern in url:
                return True
                
        if url in self.dead_urls:
            return True
            
        if url.startswith(('http://', 'https://')):
            return True
            
        return False

    def fix_url(self, url: str) -> Tuple[str, bool]:
        """Fix a URL based on replacement rules."""
        if not url or self.should_ignore_url(url):
            return url, False
            
        original_url = url
        
        for old_pattern in self.replacement_rules:
            if old_pattern in url:
                url = url.replace(old_pattern, self.target_replacement)
                
        if url.startswith('\\\\'):
            url = url.replace('/', '\\')
            
        return url, url != original_url

    def rgb_to_hex(self, rgb_value) -> Optional[str]:
        """Convert RGB value to hex color code."""
        if rgb_value is None:
            return None
        
        try:
            rgb_int = int(rgb_value)
            red = rgb_int & 255
            green = (rgb_int >> 8) & 255
            blue = (rgb_int >> 16) & 255
            return f"#{red:02X}{green:02X}{blue:02X}"
        except (ValueError, TypeError):
            return None

    def map_color_to_status(self, color: str) -> str:
        """Map color codes to status descriptions."""
        color_mapping = {
            "#FFCC99": "not approved",
            "#CCFFCC": "approved", 
            "#CCFF99": "approved for first order",
            "#FFFFFF": "processing"
        }
        return color_mapping.get(color, "unknown")

    def update_data(self) -> bool:
        """Complete data update cycle."""
        try:
            logger.info("Starting data update cycle...")
            
            # Step 1: Get source file
            src_path = self.pick_source_path()
            
            # Step 2: Copy and convert
            xlsx_path = self.copy_and_convert_excel(src_path)
            
            # Step 3: Extract data
            data = self.extract_excel_data(xlsx_path)
            
            # Step 4: Load cleanup rules and apply
            self.load_replacement_rules()
            url_changes = self.cleanup_urls(data)
            
            # Step 5: Update metadata
            if 'metadata' in data:
                data['metadata'].update({
                    'update_timestamp': datetime.now().isoformat(),
                    'url_cleanup_applied': True,
                    'url_changes': url_changes,
                    'source_path': str(src_path)
                })
            
            # Step 6: Save to Django data directory
            logger.info(f"Saving data to: {self.data_file}")
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Step 7: Cleanup temp file
            try:
                xlsx_path.unlink()
                logger.info(f"Removed temp file: {xlsx_path}")
            except Exception as e:
                logger.warning(f"Could not remove temp file: {e}")
            
            # Update statistics
            self.stats['updates_completed'] += 1
            self.stats['last_update'] = datetime.now().isoformat()
            
            logger.info(f"Data update completed successfully!")
            logger.info(f"Total rows: {data['metadata']['total_rows']}")
            logger.info(f"URL changes: {url_changes}")
            
            return True
            
        except Exception as e:
            self.stats['total_errors'] += 1
            self.stats['last_error'] = str(e)
            logger.error(f"Data update failed: {e}")
            return False

    def run_continuous(self, interval_minutes: int = 30):
        """Run continuous updates at specified interval."""
        logger.info(f"Starting continuous update loop (interval: {interval_minutes} minutes)")
        
        while True:
            try:
                success = self.update_data()
                if success:
                    logger.info(f"Update successful. Next update in {interval_minutes} minutes.")
                else:
                    logger.warning(f"Update failed. Retrying in {interval_minutes} minutes.")
                
                # Log statistics
                logger.info(f"Statistics - Updates: {self.stats['updates_completed']}, "
                           f"Errors: {self.stats['total_errors']}")
                
                # Wait for next cycle
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Continuous update stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in continuous loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


def main():
    """Main function with command line options."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Updater for Django App")
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--interval', type=int, default=30, help='Update interval in minutes (default: 30)')
    parser.add_argument('--temp-dir', type=str, help='Custom temp directory')
    parser.add_argument('--data-file', type=str, help='Custom data file path')
    
    args = parser.parse_args()
    
    # Initialize updater
    kwargs = {}
    if args.temp_dir:
        kwargs['temp_dir'] = args.temp_dir
    if args.data_file:
        kwargs['data_file'] = args.data_file
        
    updater = DataUpdater(**kwargs)
    
    try:
        if args.once:
            logger.info("Running single update...")
            success = updater.update_data()
            sys.exit(0 if success else 1)
        else:
            logger.info("Starting continuous update mode...")
            updater.run_continuous(args.interval)
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
