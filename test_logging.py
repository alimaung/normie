#!/usr/bin/env python3
"""
Test script to verify logging configuration for OutlookService and PDF Service.
Run this from the Django project root directory.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent / 'normie'
sys.path.insert(0, str(project_root))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'normie.settings')
django.setup()

def test_outlook_logging():
    """Test OutlookService logging functionality."""
    print("=== Testing OutlookService Logging ===")
    
    try:
        from normieapp.services.outlook_service import OutlookService, logger
        
        # Create service instance (this should create log files)
        service = OutlookService()
        
        # Test various log levels
        logger.debug("This is a debug message for OutlookService")
        logger.info("This is an info message for OutlookService")
        logger.warning("This is a warning message for OutlookService")
        logger.error("This is an error message for OutlookService")
        
        # Test email-related logging
        logger.info("Testing email search functionality")
        logger.info("Testing email delete operation")
        logger.info("Testing email mark read functionality")
        
        # Test COM-related logging
        logger.info("Testing COM interface initialization")
        status = service.get_com_status()
        logger.info(f"COM status: {status}")
        
        print("✅ OutlookService logging test completed")
        
    except Exception as e:
        print(f"❌ Error testing OutlookService logging: {e}")

def test_pdf_logging():
    """Test PDF Service logging functionality."""
    print("\n=== Testing PDF Service Logging ===")
    
    try:
        from normieapp.services.pdf_service import pdf_logger
        
        # Test various log levels
        pdf_logger.debug("This is a debug message for PDF Service")
        pdf_logger.info("This is an info message for PDF Service")
        pdf_logger.warning("This is a warning message for PDF Service")
        pdf_logger.error("This is an error message for PDF Service")
        
        # Test field-related logging
        pdf_logger.info("Testing field extraction functionality")
        pdf_logger.info("Testing form field mapping")
        pdf_logger.info("Testing signature field handling")
        
        # Test generation-related logging
        pdf_logger.info("Testing PDF generation functionality")
        pdf_logger.info("Testing template filling")
        pdf_logger.info("Testing save operation")
        
        # Test performance logging
        pdf_logger.info("Testing performance monitoring - processing time: 2.5 seconds")
        
        print("✅ PDF Service logging test completed")
        
    except Exception as e:
        print(f"❌ Error testing PDF Service logging: {e}")

def check_log_files():
    """Check if log files were created."""
    print("\n=== Checking Log Files ===")
    
    log_dir = Path('normie/logs')
    
    # Check outlook logs
    outlook_log_dir = log_dir / 'outlook'
    if outlook_log_dir.exists():
        print(f"📁 Outlook log directory: {outlook_log_dir}")
        for log_file in outlook_log_dir.glob("*.log"):
            size = log_file.stat().st_size
            print(f"  📄 {log_file.name}: {size} bytes")
    else:
        print("❌ Outlook log directory not found")
    
    # Check PDF logs
    pdf_log_dir = log_dir / 'pdf'
    if pdf_log_dir.exists():
        print(f"📁 PDF log directory: {pdf_log_dir}")
        for log_file in pdf_log_dir.glob("*.log"):
            size = log_file.stat().st_size
            print(f"  📄 {log_file.name}: {size} bytes")
    else:
        print("❌ PDF log directory not found")

if __name__ == "__main__":
    print("🔧 Testing logging configuration for normie services")
    print("=" * 60)
    
    test_outlook_logging()
    test_pdf_logging()
    check_log_files()
    
    print("\n" + "=" * 60)
    print("✅ Logging test completed. Check the logs directory for generated files.")
    print("📍 Log files location: normie/logs/") 