import ctypes
import time
import signal
import sys
from ctypes import wintypes

# Windows API constants for SetThreadExecutionState
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002
ES_AWAYMODE_REQUIRED = 0x00000040

class WakeLock:
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.is_active = False
        
    def enable_wakelock(self):
        """Enable wakelock to prevent system sleep and display sleep"""
        # Combine flags to prevent system sleep, display sleep, and enable away mode
        flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED | ES_AWAYMODE_REQUIRED
        
        result = self.kernel32.SetThreadExecutionState(flags)
        if result:
            self.is_active = True
            print("✅ Wakelock enabled - System will not sleep")
            print("   - System sleep: DISABLED")
            print("   - Display sleep: DISABLED")
            print("   - Away mode: ENABLED")
            return True
        else:
            print("❌ Failed to enable wakelock")
            return False
    
    def disable_wakelock(self):
        """Disable wakelock and restore normal power management"""
        result = self.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        if result:
            self.is_active = False
            print("🔓 Wakelock disabled - Normal power management restored")
            return True
        else:
            print("❌ Failed to disable wakelock")
            return False
    
    def status(self):
        """Get current wakelock status"""
        return "ACTIVE" if self.is_active else "INACTIVE"

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Interrupt received, disabling wakelock...")
    wakelock.disable_wakelock()
    sys.exit(0)

def main():
    global wakelock
    wakelock = WakeLock()
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🔒 Windows Wakelock Script")
    print("=" * 40)
    
    # Enable wakelock
    if not wakelock.enable_wakelock():
        print("Failed to start wakelock. Exiting...")
        return
    
    try:
        print(f"\n📊 Status: {wakelock.status()}")
        print("💡 Press Ctrl+C to stop and restore normal power management")
        print("\n⏰ Wakelock is running...")
        
        # Keep the script running
        while True:
            time.sleep(60)  # Check every minute
            print(f"[{time.strftime('%H:%M:%S')}] Wakelock status: {wakelock.status()}")
            
    except KeyboardInterrupt:
        signal_handler(None, None)
    except Exception as e:
        print(f"❌ Error: {e}")
        wakelock.disable_wakelock()

if __name__ == "__main__":
    # Check if running on Windows
    if sys.platform != "win32":
        print("❌ This script only works on Windows systems")
        sys.exit(1)
    
    main()
