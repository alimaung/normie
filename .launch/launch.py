#!/usr/bin/env python3
"""
Startup script for the Normie Django application.
This script starts the Django development server and opens the browser.
"""

import os
import sys
import time
import subprocess
import webbrowser
import requests
from pathlib import Path

def get_project_root():
    """Get the root directory of the project."""
    current_dir = Path(__file__).parent.absolute()
    # Go up one level from .launch to get to project root
    return current_dir.parent

def check_server_ready(url, max_attempts=30, delay=1):
    """
    Check if the server is ready by making HTTP requests.
    
    Args:
        url (str): The URL to check
        max_attempts (int): Maximum number of attempts
        delay (int): Delay between attempts in seconds
    
    Returns:
        bool: True if server is ready, False otherwise
    """
    print(f"Waiting for server to be ready at {url}...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ Server is ready! (attempt {attempt + 1})")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt < max_attempts - 1:
            print(f"  Attempt {attempt + 1}/{max_attempts} - waiting {delay}s...")
            time.sleep(delay)
    
    print(f"✗ Server did not become ready after {max_attempts} attempts")
    return False

def start_django_server(project_root, host="127.0.0.1", port="8000"):
    """
    Start the Django development server.
    
    Args:
        project_root (Path): Path to the project root
        host (str): Host to bind to
        port (str): Port to bind to
    
    Returns:
        subprocess.Popen: The server process
    """
    normie_dir = project_root / "normie"
    manage_py = normie_dir / "manage.py"
    
    if not manage_py.exists():
        raise FileNotFoundError(f"manage.py not found at {manage_py}")
    
    print(f"Starting Django server at {host}:{port}...")
    print(f"Project directory: {normie_dir}")
    
    # Start the Django development server
    cmd = [sys.executable, str(manage_py), "runserver", f"{host}:{port}"]
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(normie_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        print(f"✓ Django server started with PID {process.pid}")
        return process
    except Exception as e:
        print(f"✗ Failed to start Django server: {e}")
        raise

def open_browser_fullscreen(url, delay=2):
    """
    Open the default web browser to the specified URL in fullscreen mode.
    
    Args:
        url (str): URL to open
        delay (int): Delay before opening browser
    """
    print(f"Opening browser in fullscreen to {url} in {delay} seconds...")
    time.sleep(delay)
    
    try:
        import platform
        system = platform.system().lower()
        
        if system == "windows":
            # For Windows - try Chrome first, then Edge, then default browser
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ]
            
            # Try Chrome with fullscreen flag
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    subprocess.Popen([chrome_path, "--start-fullscreen", url])
                    print("✓ Chrome opened in fullscreen mode")
                    return
            
            # Try Edge with fullscreen flag
            try:
                subprocess.Popen(["msedge", "--start-fullscreen", url])
                print("✓ Edge opened in fullscreen mode")
                return
            except FileNotFoundError:
                pass
            
            # Fallback to default browser and send F11 key
            webbrowser.open(url)
            time.sleep(3)  # Wait for browser to load
            
            # Try to send F11 key to make it fullscreen
            try:
                import pyautogui
                pyautogui.press('f11')
                print("✓ Browser opened and F11 sent for fullscreen")
            except ImportError:
                print("✓ Browser opened (install pyautogui for automatic fullscreen)")
            
        elif system == "darwin":  # macOS
            # Try Chrome first
            try:
                subprocess.Popen([
                    "open", "-a", "Google Chrome", "--args", 
                    "--start-fullscreen", url
                ])
                print("✓ Chrome opened in fullscreen mode")
                return
            except:
                pass
            
            # Try Safari
            try:
                subprocess.Popen(["open", "-a", "Safari", url])
                time.sleep(3)
                # Send Cmd+Shift+F for Safari fullscreen
                subprocess.Popen([
                    "osascript", "-e", 
                    'tell application "System Events" to keystroke "f" using {command down, shift down}'
                ])
                print("✓ Safari opened in fullscreen mode")
                return
            except:
                pass
            
            # Fallback
            webbrowser.open(url)
            print("✓ Browser opened (manual fullscreen: Cmd+Shift+F)")
            
        elif system == "linux":
            # Try Chrome/Chromium first
            chrome_commands = ["google-chrome", "chromium-browser", "chromium"]
            for cmd in chrome_commands:
                try:
                    subprocess.Popen([cmd, "--start-fullscreen", url])
                    print(f"✓ {cmd} opened in fullscreen mode")
                    return
                except FileNotFoundError:
                    continue
            
            # Try Firefox
            try:
                subprocess.Popen(["firefox", "--kiosk", url])
                print("✓ Firefox opened in kiosk mode")
                return
            except FileNotFoundError:
                pass
            
            # Fallback
            webbrowser.open(url)
            print("✓ Browser opened (manual fullscreen: F11)")
            
        else:
            # Unknown system - use default browser
            webbrowser.open(url)
            print("✓ Browser opened (manual fullscreen: F11)")
            
    except Exception as e:
        print(f"✗ Failed to open browser in fullscreen: {e}")
        print(f"Please manually open your browser to: {url}")
        print("💡 Tip: Press F11 for fullscreen mode")

def open_browser(url, delay=2):
    """
    Open the default web browser to the specified URL.
    
    Args:
        url (str): URL to open
        delay (int): Delay before opening browser
    """
    print(f"Opening browser to {url} in {delay} seconds...")
    time.sleep(delay)
    
    try:
        webbrowser.open(url)
        print("✓ Browser opened successfully")
    except Exception as e:
        print(f"✗ Failed to open browser: {e}")
        print(f"Please manually open your browser to: {url}")

def main():
    """Main function to orchestrate the startup process."""
    print("=" * 60)
    print("🚀 Starting Normie Django Application")
    print("=" * 60)
    
    try:
        # Configuration
        HOST = "127.0.0.1"
        PORT = "8000"
        URL = f"http://{HOST}:{PORT}"
        
        # Get project root
        project_root = get_project_root()
        print(f"Project root: {project_root}")
        
        # Start Django server
        server_process = start_django_server(project_root, HOST, PORT)
        
        # Wait for server to be ready
        if check_server_ready(URL):
            # Open browser
            open_browser_fullscreen(URL)
            
            print("\n" + "=" * 60)
            print("🎉 Application started successfully!")
            print(f"📱 Server: {URL}")
            print("🔧 Press Ctrl+C to stop the server")
            print("=" * 60)
            
            # Keep the script running and monitor the server
            try:
                while True:
                    # Check if server process is still running
                    if server_process.poll() is not None:
                        print("\n⚠️  Server process has stopped")
                        break
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down...")
                
        else:
            print("✗ Server failed to start properly")
            
    except Exception as e:
        print(f"✗ Error during startup: {e}")
        return 1
    
    finally:
        # Clean up: terminate server process if it's still running
        try:
            if 'server_process' in locals() and server_process.poll() is None:
                print("🧹 Terminating server process...")
                server_process.terminate()
                server_process.wait(timeout=5)
                print("✓ Server process terminated")
        except Exception as e:
            print(f"⚠️  Error terminating server: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
