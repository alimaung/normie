
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def driver():
    print("\033[92mHELLO WORLD\033[0m")

    #service = Service(executable_path=r"C:\Users\u8064927\Desktop\Ali\normie\chemscanrestore\CS\chromedriver.exe")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    #driver.switch_to.window(driver.window_handles[-1]) # Pinned ChemScan
    return driver
