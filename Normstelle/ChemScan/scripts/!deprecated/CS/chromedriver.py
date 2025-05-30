from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def init_driver():
    print("\033[34m[INFO] Initializing the web driver...\033[0m")  # Blue text for info
    
    chrome_options = Options()

    # Path to your user data (chrome profile)
    user_data_dir = r"C:\Users\u8064927\AppData\Local\Google\Chrome\User Data"
    profile_dir = "Default"  # The specific profile you're using

    prefs = {
        "download.prompt_for_download": False,  # Disable 'Save As' dialog
        "directory_upgrade": True,  # Automatically overwrite files
        "safebrowsing.enabled": True  # Enable safe browsing
    }

    chrome_options.add_experimental_option("prefs", prefs)

    # Arguments to pass to the chrome instance
    arguments = [
        f"--user-data-dir={user_data_dir}",  # Specify user data dir
        f"--profile-directory={profile_dir}",  # Specify the profile to use
        "--log-level=3",
        #"--window-size=800,600",
        "--no-sandbox",
        "--fast-start",
        "--disable-images",
        "--disable-plugins",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--silent",
        "--disable-background-timer-throttling",
    ]
    
    for argument in arguments:
        chrome_options.add_argument(argument)
    
    # Update with your ChromeDriver path
    driver_service = Service(r"C:\Users\u8064927\Desktop\Rolls-Royce-OU\ChemScan\py\chromedriver.exe")
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)
  
    return driver
