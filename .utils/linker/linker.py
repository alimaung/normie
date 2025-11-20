import socket
import time
import os

# Root paths
#REAL LIVE_ROOT_PATH = r"\\deberdna-c010a\GlobalDE\DocumentManagement\NormstelleShare\normie.live"
LIVE_ROOT_PATH = r"\\deberdna-c010a\GlobalDE\DocumentManagement\Servicelines\Normstelle\.normie.dev"
DEV_ROOT_PATH = r"C:\Users\RAVEN\Desktop\normie\.utils\linker"

# Icon file path
#LIVE_ICON_FILE_PATH = LIVE_ROOT_PATH + "\normie.ico"
#DEV_ICON_FILE_PATH = DEV_ROOT_PATH + "\normie.ico"

# Constants for live file paths
LIVE_URL_FILE_PATH = LIVE_ROOT_PATH + r"\url\normie.url"
LIVE_VBS_FILE_PATH = LIVE_ROOT_PATH + r"\vbs\normie.vbs"

# Dev paths (alternative set)
DEV_URL_FILE_PATH = DEV_ROOT_PATH + r"\url\normie.url"
DEV_VBS_FILE_PATH = DEV_ROOT_PATH + r"\vbs\normie.vbs"

# Port constant
PORT = 8001

def get_current_ip():
    """Get the current local IP address using socket"""
    try:
        # Connect to a remote server to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return None

def update_url_file(ip_address, file_path=LIVE_URL_FILE_PATH):
    """Update the URL file with new IP address"""
    url_content = f"""[InternetShortcut]
URL=http://{ip_address}:{PORT}/
IconFile=C:\\Users\\u8064927\\Desktop\\normie.ico
IconIndex=0"""
    
    with open(file_path, 'w') as f:
        f.write(url_content)
    print(f"Updated URL file: {file_path}")

def update_vbs_file(ip_address, file_path=LIVE_VBS_FILE_PATH):
    """Update the VBS file with new IP address"""
    vbs_content = f'CreateObject("WScript.Shell").Run "cmd /c start http://{ip_address}:{PORT}", 0, False'
    
    with open(file_path, 'w') as f:
        f.write(vbs_content)
    print(f"Updated VBS file: {file_path}")

def monitor_ip_changes():
    """Monitor for IP changes and update files accordingly"""
    current_ip = None
    
    while True:
        new_ip = get_current_ip()
        
        if new_ip and new_ip != current_ip:
            print(f"IP changed from {current_ip} to {new_ip}")
            
            # Update production files
            #update_url_file(new_ip)
            #update_vbs_file(new_ip)
            
            # Update dev files (uncomment if needed)
            update_url_file(new_ip, DEV_URL_FILE_PATH)
            update_vbs_file(new_ip, DEV_VBS_FILE_PATH)
            
            current_ip = new_ip
        
        time.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    print("Starting IP monitor...")
    monitor_ip_changes()