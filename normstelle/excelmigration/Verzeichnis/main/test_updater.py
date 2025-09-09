#!/usr/bin/env python3
"""
Test script for data_updater.py
Performs basic validation and testing
"""

import json
import os
import sys
from pathlib import Path
from data_updater import DataUpdater

def test_paths():
    """Test that all required paths are accessible."""
    print("Testing paths...")
    
    # Test temp directory creation
    temp_dir = Path(r"C:\Users\RAVEN\Desktop\normie\normie\normieapp\static\normieapp\temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Temp directory: {temp_dir}")
    
    # Test data directory creation
    data_file = Path(r"C:\Users\RAVEN\Desktop\normie\normie\normieapp\static\normieapp\data\Verzeichnis.json")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    print(f"✓ Data directory: {data_file.parent}")
    
    return True

def test_source_availability():
    """Test source file availability."""
    print("\nTesting source file availability...")
    
    updater = DataUpdater()
    try:
        src_path = updater.pick_source_path()
        print(f"✓ Source file found: {src_path}")
        return True
    except FileNotFoundError as e:
        print(f"✗ Source file not found: {e}")
        return False

def test_dependencies():
    """Test required dependencies."""
    print("\nTesting dependencies...")
    
    try:
        import win32com.client
        print("✓ pywin32 available")
    except ImportError:
        print("✗ pywin32 missing - install with: pip install pywin32")
        return False
    
    try:
        import pythoncom
        print("✓ pythoncom available")
    except ImportError:
        print("✗ pythoncom missing")
        return False
    
    return True

def test_replace_file():
    """Test replace file configuration."""
    print("\nTesting replace file...")
    
    replace_file = Path("replace")
    if replace_file.exists():
        print(f"✓ Replace file found: {replace_file}")
        
        updater = DataUpdater()
        updater.load_replacement_rules()
        
        if updater.replacement_rules:
            print(f"✓ Loaded {len(updater.replacement_rules)} replacement rules")
            print(f"  Target: {updater.target_replacement}")
        else:
            print("⚠ No replacement rules found in file")
        
        return True
    else:
        print("⚠ Replace file not found - URL cleanup will be skipped")
        return False

def test_single_update():
    """Test a single update cycle."""
    print("\nTesting single update...")
    
    updater = DataUpdater()
    
    try:
        success = updater.update_data()
        if success:
            print("✓ Single update completed successfully")
            
            # Check if data file was created
            if updater.data_file.exists():
                print(f"✓ Data file created: {updater.data_file}")
                
                # Check file contents
                with open(updater.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                rows = len(data.get('data', []))
                print(f"✓ Data contains {rows} rows")
                
                if 'metadata' in data:
                    metadata = data['metadata']
                    print(f"  - Source: {metadata.get('source_file', 'Unknown')}")
                    print(f"  - Columns: {metadata.get('total_columns', 0)}")
                    print(f"  - Timestamp: {metadata.get('update_timestamp', 'Unknown')}")
                
                return True
            else:
                print("✗ Data file was not created")
                return False
        else:
            print("✗ Single update failed")
            return False
            
    except Exception as e:
        print(f"✗ Update failed with error: {e}")
        return False

def main():
    """Run all tests."""
    print("Data Updater Test Suite")
    print("=" * 50)
    
    tests = [
        ("Path Setup", test_paths),
        ("Dependencies", test_dependencies),
        ("Source Availability", test_source_availability),
        ("Replace File", test_replace_file),
        ("Single Update", test_single_update)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The data updater is ready to use.")
        print("Run: python data_updater.py --once")
    else:
        print(f"\n⚠ {len(results) - passed} test(s) failed. Please fix issues before using.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
