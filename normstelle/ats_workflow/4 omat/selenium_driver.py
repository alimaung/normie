
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
driver.switch_to.window(driver.window_handles[-1]) # Pinned ChemScan
