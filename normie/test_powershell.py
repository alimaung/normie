#!/usr/bin/env python3
"""
Test script to verify PowerShell execution works correctly
"""
import subprocess
import tempfile
import os

def test_powershell():
    """Test PowerShell execution"""
    
    # Simple test script
    test_script = '''
Write-Output "PowerShell is working"
Write-Output "Current directory: $(Get-Location)"
Write-Output "PowerShell version: $($PSVersionTable.PSVersion)"
    '''
    
    with tempfile.TemporaryDirectory() as temp_dir:
        script_path = os.path.join(temp_dir, 'test.ps1')
        
        # Write test script
        with open(script_path, 'w', encoding='utf-8-sig') as f:
            f.write(test_script)
        
        # Try different PowerShell executables
        for ps_exe in ['pwsh.exe', 'powershell.exe']:
            try:
                print(f"Testing {ps_exe}...")
                
                # Test if PowerShell exists
                version_result = subprocess.run([ps_exe, '-Version'], 
                                              capture_output=True, text=True, timeout=5)
                if version_result.returncode != 0:
                    print(f"  {ps_exe} not available")
                    continue
                
                print(f"  {ps_exe} found, version check passed")
                
                # Execute test script
                result = subprocess.run([
                    ps_exe,
                    '-ExecutionPolicy', 'Bypass',
                    '-NoProfile',
                    '-WindowStyle', 'Hidden',
                    '-File', script_path
                ], capture_output=True, text=True, timeout=30, cwd=temp_dir)
                
                print(f"  Return code: {result.returncode}")
                print(f"  STDOUT: {result.stdout}")
                if result.stderr:
                    print(f"  STDERR: {result.stderr}")
                
                if result.returncode == 0:
                    print(f"  ✓ {ps_exe} works correctly!")
                    return ps_exe
                else:
                    print(f"  ✗ {ps_exe} failed")
                    
            except Exception as e:
                print(f"  Exception with {ps_exe}: {e}")
    
    print("No working PowerShell found!")
    return None

def test_din_script():
    """Test the actual DIN search script"""
    script_path = os.path.join('normstelle', 'nrm_workflow', 'din', 'search.ps1')
    
    if not os.path.exists(script_path):
        print(f"DIN script not found at: {script_path}")
        return False
    
    print(f"DIN script found at: {script_path}")
    
    # Try reading with different encodings
    for encoding in ['utf-8-sig', 'utf-8', 'utf-16', 'cp1252', 'latin1']:
        try:
            with open(script_path, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"  ✓ Successfully read with {encoding}")
            print(f"  Content length: {len(content)} characters")
            print(f"  First 100 chars: {repr(content[:100])}")
            return True
        except Exception as e:
            print(f"  ✗ Failed with {encoding}: {e}")
    
    return False

if __name__ == '__main__':
    print("=== PowerShell Test ===")
    working_ps = test_powershell()
    
    print("\n=== DIN Script Test ===")
    script_readable = test_din_script()
    
    print(f"\n=== Summary ===")
    print(f"PowerShell available: {working_ps is not None}")
    print(f"DIN script readable: {script_readable}")
    
    if working_ps and script_readable:
        print("✓ System should be ready for DIN search functionality")
    else:
        print("✗ System needs fixes before DIN search will work") 