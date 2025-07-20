import time
import win32gui
import win32con
import win32api
import win32process
import psutil
import json
from datetime import datetime
import re
import threading
import sys

class NetskopePopupCapture:
    def __init__(self):
        self.netskope_process_name = "stAgentUI.exe"
        self.captured_popups = []
        self.monitoring = False
        self.known_windows = set()
        
    def find_netskope_process(self):
        """Find running Netskope processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['name'] and self.netskope_process_name.lower() in proc.info['name'].lower():
                    processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
    
    def get_window_text(self, hwnd):
        """Get all text content from a window"""
        try:
            # Get window title
            title = win32gui.GetWindowText(hwnd)
            
            # Get window class name
            class_name = win32gui.GetClassName(hwnd)
            
            # Get window rect
            rect = win32gui.GetWindowRect(hwnd)
            
            # Collect all child window texts
            texts = []
            
            def enum_child_proc(child_hwnd, lparam):
                try:
                    child_text = win32gui.GetWindowText(child_hwnd)
                    child_class = win32gui.GetClassName(child_hwnd)
                    if child_text.strip():
                        texts.append({
                            'text': child_text,
                            'class': child_class
                        })
                except:
                    pass
                return True
            
            win32gui.EnumChildWindows(hwnd, enum_child_proc, None)
            
            return {
                'title': title,
                'class_name': class_name,
                'rect': rect,
                'child_texts': texts,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting window text: {e}")
            return None
    
    def is_netskope_window(self, hwnd):
        """Check if window belongs to Netskope process"""
        try:
            # Get process ID of the window
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process info
            try:
                process = psutil.Process(pid)
                process_name = process.name()
                
                # Check if it's a Netskope process
                if self.netskope_process_name.lower() in process_name.lower():
                    return True
                    
                # Also check window title and class for Netskope indicators
                title = win32gui.GetWindowText(hwnd).lower()
                class_name = win32gui.GetClassName(hwnd).lower()
                
                netskope_indicators = ['netskope', 'block', 'security', 'policy']
                if any(indicator in title or indicator in class_name for indicator in netskope_indicators):
                    return True
                    
            except psutil.NoSuchProcess:
                pass
                
        except Exception as e:
            pass
        
        return False
    
    def enum_windows_proc(self, hwnd, lparam):
        """Callback for enumerating windows"""
        try:
            # Check if window is visible
            if not win32gui.IsWindowVisible(hwnd):
                return True
                
            # Check if it's a Netskope window or looks like a popup
            if self.is_netskope_window(hwnd) or self.looks_like_popup(hwnd):
                
                # Skip if we've already captured this window
                window_id = f"{hwnd}_{win32gui.GetWindowText(hwnd)}"
                if window_id in self.known_windows:
                    return True
                
                window_data = self.get_window_text(hwnd)
                if window_data and (window_data['title'] or window_data['child_texts']):
                    self.known_windows.add(window_id)
                    self.captured_popups.append(window_data)
                    print(f"Captured popup: {window_data['title']}")
                    self.save_popup_data(window_data)
                    
        except Exception as e:
            pass
        
        return True
    
    def looks_like_popup(self, hwnd):
        """Check if window looks like a popup/dialog"""
        try:
            title = win32gui.GetWindowText(hwnd).lower()
            class_name = win32gui.GetClassName(hwnd).lower()
            
            # Common popup indicators
            popup_indicators = [
                'dialog', 'popup', 'alert', 'warning', 'error', 'block', 
                'security', 'policy', 'access', 'denied', 'restricted'
            ]
            
            if any(indicator in title or indicator in class_name for indicator in popup_indicators):
                return True
                
            # Check window style for dialog characteristics
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            
            # Dialog style indicators
            if (style & win32con.WS_DLGFRAME) or (ex_style & win32con.WS_EX_DLGMODALFRAME):
                return True
                
        except Exception as e:
            pass
            
        return False
    
    def scan_for_popups(self):
        """Scan for new popup windows"""
        try:
            win32gui.EnumWindows(self.enum_windows_proc, None)
        except Exception as e:
            print(f"Error scanning for popups: {e}")
    
    def save_popup_data(self, window_data):
        """Save captured popup data to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"netskope/netskope_popup_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(window_data, f, indent=2, ensure_ascii=False)
                
            print(f"Popup data saved to: {filename}")
            
        except Exception as e:
            print(f"Error saving popup data: {e}")
    
    def start_monitoring(self, interval=1):
        """Start monitoring for popup windows"""
        print(f"Starting Netskope popup monitoring...")
        print(f"Looking for process: {self.netskope_process_name}")
        
        # Check if Netskope is running
        processes = self.find_netskope_process()
        if processes:
            print(f"Found Netskope processes: {len(processes)}")
            for proc in processes:
                print(f"  PID: {proc['pid']}, Name: {proc['name']}")
        else:
            print("Warning: No Netskope processes found")
        
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    self.scan_for_popups()
                    time.sleep(interval)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error in monitoring loop: {e}")
                    time.sleep(interval)
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        try:
            print("Monitoring started. Press Ctrl+C to stop...")
            print("Now try opening a blocked link to capture the popup...")
            monitor_thread.join()
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            self.monitoring = False
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
    
    def get_captured_popups(self):
        """Get all captured popup data"""
        return self.captured_popups
    
    def print_summary(self):
        """Print summary of captured popups"""
        print(f"\nCaptured {len(self.captured_popups)} popup(s):")
        for i, popup in enumerate(self.captured_popups, 1):
            print(f"\n--- Popup {i} ---")
            print(f"Title: {popup['title']}")
            print(f"Class: {popup['class_name']}")
            print(f"Timestamp: {popup['timestamp']}")
            if popup['child_texts']:
                print("Content:")
                for child in popup['child_texts']:
                    if child['text'].strip():
                        print(f"  - {child['text']}")

def main():
    capture = NetskopePopupCapture()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Test mode - just scan once
        print("Test mode - scanning for current windows...")
        capture.scan_for_popups()
        capture.print_summary()
    else:
        # Normal monitoring mode
        try:
            capture.start_monitoring()
        finally:
            capture.print_summary()

if __name__ == "__main__":
    main()
