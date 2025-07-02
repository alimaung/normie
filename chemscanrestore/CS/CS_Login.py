#import chromedriver as cd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os

# Connect to a running Selenium session
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
driver.switch_to.window(driver.window_handles[0])

# Try to load env variables from different locations
load_dotenv()  # Try current directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))  # Try parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))  # Try root directory

# Get credentials from env or prompt user
user = os.getenv('CHEMSCAN_USER')
key = os.getenv('CHEMSCAN_KEY')

# If credentials not found in environment variables, prompt the user
if not user or not key:
    print("Credentials not found in environment variables.")
    user = input("Enter ChemScan username: ")
    key = input("Enter ChemScan password: ")

# Initialize driver
#driver = cd.init_driver() # we connect to a running session now
url = "https://app.chemscan.de/user/login"
driver.get(url)

time.sleep(10)
# Make login
wait = WebDriverWait(driver, 10) # Wait for page loading, 10s timeout

username = wait.until(EC.visibility_of_element_located((By.ID, 'prependedInput')))
username.send_keys(user)

password = wait.until(EC.visibility_of_element_located((By.ID, 'prependedInput2')))
password.send_keys(key)

remember = driver.find_element(By.ID, 'remember_me')
driver.execute_script("arguments[0].click()", remember)

btn = driver.find_element(By.ID, '_submit')
driver.execute_script("arguments[0].click()", btn)

# If above fails, we can extract csrf token and make requests
#csrf = driver.find_element(By.NAME, '_csrf_token')

print("Login attempt completed. Please check browser to confirm successful login.")