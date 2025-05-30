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

# Load env variables
load_dotenv()
user = os.getenv('USER')
key = os.getenv('PASS')

# Initialize driver
#driver = cd.init_driver() # we connect to a running session now
url = "https://app.chemscan.de/user/login"
driver.get(url)

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