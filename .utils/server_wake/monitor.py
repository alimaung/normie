import ctypes
import ctypes.wintypes
import keyboard
import threading
import time
import sys

# Windows API constants
HWND_BROADCAST = 0xFFFF
WM_SYSCOMMAND = 0x0112
SC_MONITORPOWER = 0xF170

# Monitor power states
MONITOR_ON = -1
MONITOR_OFF = 2
MONITOR_STANDBY = 1

class MonitorController:
    def __init__(self):
        self.is_monitoring = True
        self.monitor_state = MONITOR_ON
        
    def turn_off_monitor(self):
        """Turn off the monitor using Windows API"""
        try:
            # Get handle to the desktop window
            user32 = ctypes.windll.user32
            
            # Send monitor off command
            result = user32.SendMessageW(
                HWND_BROADCAST,
                WM_SYSCOMMAND,
                SC_MONITORPOWER,
                MONITOR_OFF
            )
            
            if result == 0:
                print("Monitor turned OFF")
                self.monitor_state = MONITOR_OFF
                return True
            else:
                print(f"Failed to turn off monitor. Result: {result}")
                return False
                
        except Exception as e:
            print(f"Error turning off monitor: {e}")
            return False
    
    def turn_on_monitor(self):
        """Turn on the monitor using Windows API"""
        try:
            # Get handle to the desktop window
            user32 = ctypes.windll.user32
            
            # Send monitor on command
            result = user32.SendMessageW(
                HWND_BROADCAST,
                WM_SYSCOMMAND,
                SC_MONITORPOWER,
                MONITOR_ON
            )
            
            if result == 0:
                print("Monitor turned ON")
                self.monitor_state = MONITOR_ON
                return True
            else:
                print(f"Failed to turn on monitor. Result: {result}")
                return False
                
        except Exception as e:
            print(f"Error turning on monitor: {e}")
            return False
    
    def on_turn_off_hotkey(self):
        """Callback for Ctrl+Alt+X hotkey"""
        print("Ctrl+Alt+X pressed - turning off monitor...")
        self.turn_off_monitor()
    
    def on_turn_on_hotkey(self):
        """Callback for Spacebar hotkey (only when monitor is off)"""
        if self.monitor_state == MONITOR_OFF:
            print("Spacebar pressed - turning on monitor...")
            self.turn_on_monitor()
    
    def setup_hotkeys(self):
        """Setup keyboard shortcuts"""
        try:
            # Register Ctrl+Alt+X to turn off monitor
            keyboard.add_hotkey('ctrl+alt+x', self.on_turn_off_hotkey)
            print("✓ Registered Ctrl+Alt+X to turn OFF monitor")
            
            # Register Spacebar to turn on monitor (only when off)
            keyboard.add_hotkey('space', self.on_turn_on_hotkey)
            print("✓ Registered Spacebar to turn ON monitor (when off)")
            
            return True
            
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
            return False
    
    def start_monitoring(self):
        """Start the keyboard monitoring loop"""
        print("\n=== Monitor Controller Started ===")
        print("Controls:")
        print("  Ctrl+Alt+X  : Turn OFF monitor")
        print("  Spacebar    : Turn ON monitor (when off)")
        print("  Ctrl+C      : Exit program")
        print("=====================================\n")
        
        if not self.setup_hotkeys():
            print("Failed to setup hotkeys. Exiting...")
            return
        
        try:
            # Keep the program running
            while self.is_monitoring:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nReceived Ctrl+C - shutting down...")
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        self.is_monitoring = False
        try:
            keyboard.unhook_all()
        except:
            pass
        print("Monitor controller stopped.")
    
    def test_monitor_control(self):
        """Test the monitor control functions"""
        print("Testing monitor control...")
        
        print("Turning off monitor in 3 seconds...")
        time.sleep(3)
        
        if self.turn_off_monitor():
            print("Monitor should be off. Turning back on in 5 seconds...")
            time.sleep(5)
            self.turn_on_monitor()
        else:
            print("Failed to turn off monitor.")

def main():
    """Main function"""
    controller = MonitorController()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            controller.test_monitor_control()
            return
        elif sys.argv[1] == '--off':
            controller.turn_off_monitor()
            return
        elif sys.argv[1] == '--on':
            controller.turn_on_monitor()
            return
        elif sys.argv[1] == '--help':
            print("Monitor Controller - Usage:")
            print("  python monitor.py           : Start with hotkey monitoring")
            print("  python monitor.py --test    : Test monitor control")
            print("  python monitor.py --off     : Turn off monitor once")
            print("  python monitor.py --on      : Turn on monitor once")
            print("  python monitor.py --help    : Show this help")
            return
    
    # Default: start monitoring with hotkeys
    try:
        controller.start_monitoring()
    except Exception as e:
        print(f"Fatal error: {e}")
        controller.cleanup()

if __name__ == "__main__":
    main()
