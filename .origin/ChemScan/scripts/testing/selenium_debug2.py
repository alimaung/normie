from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Start Chrome with a remote debugging port
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

service = Service(r"C:\Users\u8064927\Desktop\Rolls-Royce-OU\ChemScan\py\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

print("Open windows:", driver.window_handles)

driver.switch_to.window(driver.window_handles[0])

driver.get("https://app.chemscan.de/user/login")

input("Press Enter to keep the session open...")  # Keeps script running