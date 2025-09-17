"""
Directory service for updating and optimizing Verzeichnis data.
Combines background updating with JSON optimization.
"""

import json
import logging
import os
import threading
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from django.conf import settings

logger = logging.getLogger(__name__)


class JSONOptimizer:
    """Optimizes JSON file size by compressing data structure."""
    
    def __init__(self):
        # Common base URL that appears in all file paths
        self.base_url = "file:///\\\\deberdna-c010a\\GlobalDE\\DocumentManagement\\NormstelleShare\\TeileundStoffe\\\\"
        
        # Column name mappings (long -> short)
        self.column_map = {
            "Antrag-nummer": "an",
            "Teile-nummer": "tn", 
            "Freigabe": "fr",
            "relevant für Luftfahrtteile": "rl",
            "Benennung": "bn",
            "Produktname / Normkurzbezeichnung": "pn",
            "Produktzulassungs-spezifikation": "ps",
            "Eingang": "ein",
            "Abschluss": "ab",
            "Abteilung": "abt",
            "Einsatzort": "eo",
            "Antragsteller": "as",
            "Antrag": "ant",
            "Datenblatt": "db",
            "Produkt-zulassung": "pz",
            "SDB MSDS": "sdb",
            "Gefährdungsprüfungeurteilung": "gpu",
            "Gefährdungsprüfung": "gp",
            "Sonstiges": "so",
            "Schriftverkehr": "sv",
            "Änd. Historie": "ah",
            "Datum": "dt",
            "Bearbeiter": "bb",
            "=CONCATENATE(\"Bemerkung \n(\",COUNTIF(C:C,\"TBD\"),\" offene Anträge)\")": "bem",
            "GSK-Nr.": "gsk",
            "Lieferant": "lf",
            "Hersteller": "hs",
            "color": "c",
            "status": "s"
        }
        
        # Reverse mapping for decompression
        self.reverse_map = {v: k for k, v in self.column_map.items()}

    def compress_url(self, url: str) -> str:
        """Compress URL by removing base path"""
        if not url or not url.startswith(self.base_url):
            return url
        return url[len(self.base_url):]

    def compress_document(self, doc: Optional[Dict]) -> Optional[str]:
        """Compress document object to just the relative URL"""
        if not doc or not isinstance(doc, dict):
            return None
        
        url = doc.get('url', '')
        if not url:
            return None
            
        return self.compress_url(url)

    def compress_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compress the entire JSON structure"""
        logger.info("Compressing directory data...")
        
        original_data = data.get('data', [])
        compressed_data = []
        
        # Compress each data entry
        for i, item in enumerate(original_data):
            if i % 1000 == 0:
                logger.debug(f"  Compressed {i}/{len(original_data)} items...")
            
            compressed_item = {}
            
            for orig_key, value in item.items():
                # Map to short key
                short_key = self.column_map.get(orig_key, orig_key)
                
                # Skip null values to save space
                if value is None:
                    continue
                
                # Compress document objects
                if orig_key in ['Antrag', 'Datenblatt', 'Produkt-zulassung', 'SDB MSDS',
                              'Gefährdungsprüfungeurteilung', 'Gefährdungsprüfung', 
                              'Sonstiges', 'Schriftverkehr', 'Änd. Historie']:
                    compressed_doc = self.compress_document(value)
                    if compressed_doc:
                        compressed_item[short_key] = compressed_doc
                else:
                    compressed_item[short_key] = value
            
            compressed_data.append(compressed_item)
        
        # Create compressed metadata
        compressed_metadata = {
            "total_rows": data.get('metadata', {}).get('total_rows', 0),
            "base_url": self.base_url,
            "column_map": self.reverse_map,
            "compressed": True,
            "version": "1.0"
        }
        
        compressed_result = {
            "metadata": compressed_metadata,
            "data": compressed_data
        }
        
        logger.info(f"Compression complete. Processed {len(original_data)} items")
        return compressed_result

    def save_compressed(self, input_file: str, output_file: str) -> Dict[str, float]:
        """Load, compress and save JSON file. Returns size info."""
        logger.info(f"Loading data from {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        original_size = os.path.getsize(input_file)
        
        compressed_data = self.compress_data(data)
        
        logger.info(f"Saving compressed data to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(compressed_data, f, separators=(',', ':'))
        
        new_size = os.path.getsize(output_file)
        savings = (original_size - new_size) / original_size * 100
        
        size_info = {
            'original_mb': original_size / (1024 * 1024),
            'compressed_mb': new_size / (1024 * 1024),
            'savings_percent': savings
        }
        
        logger.info(f"File size: {size_info['original_mb']:.1f}MB → {size_info['compressed_mb']:.1f}MB ({size_info['savings_percent']:.1f}% smaller)")
        return size_info


class DirectoryUpdaterService:
    """Background service that updates directory data continuously."""
    
    def __init__(self):
        self.updater = None
        self.optimizer = JSONOptimizer()
        self.thread = None
        self.stop_event = threading.Event()
        self.interval = 5 * 60  # 5 minutes in seconds
        
        # Add the updater script path
        updater_path = Path(settings.BASE_DIR).parent / "normstelle" / "excelmigration" / "Verzeichnis" / "cu"
        sys.path.insert(0, str(updater_path))
        
        try:
            from continuous_updater import ContinuousExcelUpdater
            django_base = Path(settings.BASE_DIR)
            self.updater = ContinuousExcelUpdater(django_base_path=str(django_base))
            logger.info("Directory updater service initialized")
        except ImportError as e:
            logger.error(f"Cannot import ContinuousExcelUpdater: {e}")
            self.updater = None
        except Exception as e:
            logger.error(f"Failed to initialize updater: {e}")
            self.updater = None

    def start(self):
        """Start the background updater thread."""
        if self.updater is None:
            logger.warning("Updater not available, background service disabled")
            return

        if self.thread is not None and self.thread.is_alive():
            logger.warning("Directory updater already running")
            return

        logger.info("Starting directory updater service...")
        self.thread = threading.Thread(target=self._run_updates, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the background updater."""
        if self.thread is None or not self.thread.is_alive():
            return

        logger.info("Stopping directory updater service...")
        self.stop_event.set()
        self.thread.join(timeout=10)
        
        if self.thread.is_alive():
            logger.warning("Directory updater thread did not stop gracefully")

    def run_single_update(self) -> bool:
        """Run a single update cycle manually."""
        if self.updater is None:
            logger.error("Updater not available")
            return False
            
        return self._run_single_update()

    def optimize_json(self, input_file: str, output_file: str) -> Dict[str, float]:
        """Optimize a JSON file."""
        return self.optimizer.save_compressed(input_file, output_file)

    def _run_updates(self):
        """Main update loop running in background thread."""
        logger.info(f"Directory updater service started (interval: {self.interval/60:.0f} minutes)")
        
        # Run initial update
        self._run_single_update()
        
        while not self.stop_event.is_set():
            # Wait for next update or stop signal
            if self.stop_event.wait(timeout=self.interval):
                break  # Stop event was set
            
            # Run update
            self._run_single_update()

        logger.info("Directory updater service stopped")

    def _run_single_update(self) -> bool:
        """Run a single update cycle with optimization."""
        # Initialize COM for this background thread (needed for Excel operations)
        try:
            import pythoncom
            pythoncom.CoInitialize()
            com_initialized = True
        except ImportError:
            com_initialized = False
        except Exception as e:
            logger.warning(f"COM initialization failed: {e}")
            com_initialized = False
        
        try:
            logger.info("Starting directory update...")
            success = self.updater.run_single_update()
            
            if success:
                # After successful update, create optimized version
                try:
                    data_dir = Path(settings.BASE_DIR) / "normieapp" / "static" / "normieapp" / "data"
                    input_file = data_dir / "Verzeichnis.json"
                    output_file = data_dir / "Verzeichnis_compressed.json"
                    
                    if input_file.exists():
                        size_info = self.optimizer.save_compressed(str(input_file), str(output_file))
                        logger.info(f"Created optimized version: {size_info['compressed_mb']:.1f}MB ({size_info['savings_percent']:.1f}% savings)")
                    else:
                        logger.warning(f"Source file not found: {input_file}")
                        
                except Exception as e:
                    logger.error(f"Failed to create optimized version: {e}")
                
                logger.info("Directory update completed successfully")
            else:
                logger.error("Directory update failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Error during directory update: {e}")
            return False
        finally:
            # Clean up COM if we initialized it
            if com_initialized:
                try:
                    pythoncom.CoUninitialize()
                except Exception as e:
                    logger.warning(f"COM cleanup failed: {e}")


# Global service instance
directory_service = DirectoryUpdaterService()


def get_directory_service() -> DirectoryUpdaterService:
    """Get the global directory service instance."""
    return directory_service
