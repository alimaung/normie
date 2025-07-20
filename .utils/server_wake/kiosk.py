import subprocess
import time
import os
import sys

def find_edge_executable():
    """Find Microsoft Edge executable path"""
    possible_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Microsoft', 'Edge', 'Application', 'msedge.exe')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def show_onscreen_keyboard():
    """Show Windows on-screen keyboard"""
    try:
        osk_process = subprocess.Popen("osk.exe")
        print("On-screen keyboard launched")
        return osk_process
    except Exception as e:
        print(f"Failed to launch on-screen keyboard: {e}")
        return None

def test_edge_kiosk(url="http://127.0.0.1:8001/"):
    """Test Edge kiosk mode with on-screen keyboard"""
    print(f"Testing Edge Kiosk Mode with URL: {url}")
    
    # Find Edge executable
    edge_path = find_edge_executable()
    if not edge_path:
        print("ERROR: Microsoft Edge not found!")
        print("Make sure Microsoft Edge is installed.")
        return False
    
    print(f"Found Edge at: {edge_path}")
    
    # Show on-screen keyboard first
    print("Launching on-screen keyboard...")
    osk_process = show_onscreen_keyboard()
    
    # Small delay to let keyboard appear
    time.sleep(2)
    
    # Kiosk command
    kiosk_args = [
        edge_path,
        "--kiosk", url,
        "--edge-kiosk-type=fullscreen",
        "--no-first-run",
        "--disable-features=TranslateUI",
        "--start-fullscreen",
        "--disable-web-security",
        "--allow-running-insecure-content",
        "--disable-features=VizDisplayCompositor"
    ]
    
    try:
        print("Launching Edge in FULLSCREEN kiosk mode...")
        print(f"URL: {url}")
        print("Duration: 20 seconds")
        print("On-screen keyboard should be visible")
        print("Kiosk will close automatically...")
        
        # Launch Edge in kiosk mode
        edge_process = subprocess.Popen(kiosk_args)
        print(f"Edge kiosk started with PID: {edge_process.pid}")
        
        # Wait 20 seconds
        print("Waiting 20 seconds...")
        time.sleep(20)
        
        # Kill the processes
        print("Closing kiosk mode...")
        edge_process.terminate()
        
        # Close on-screen keyboard too
        if osk_process:
            try:
                osk_process.terminate()
                print("On-screen keyboard closed")
            except:
                pass
        
        # Wait for Edge to close gracefully, then force kill if needed
        try:
            edge_process.wait(timeout=5)
            print("Edge closed gracefully")
        except subprocess.TimeoutExpired:
            print("Force killing Edge...")
            edge_process.kill()
            edge_process.wait()
        
        print("Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to launch Edge kiosk: {e}")
        # Clean up on-screen keyboard if there was an error
        if osk_process:
            try:
                osk_process.terminate()
            except:
                pass
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Edge Kiosk Mode with On-Screen Keyboard")
    print("=" * 50)
    
    test_edge_kiosk()
    
    print("\nPress Enter to exit...")
    input()