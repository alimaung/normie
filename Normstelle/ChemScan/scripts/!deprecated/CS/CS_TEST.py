#import chromedriver as cd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
driver.switch_to.window(driver.window_handles[-1]) # Pinned ChemScan


tkz = "01041457"
wait = WebDriverWait(driver, 1) # Wait for page loading, 10s timeout

# TODO: what behaviour to set for several rows? open each in a new tab? 
three_dot = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/a')
#three_dot = driver.find_element(By.ID, 'actions-cell-dropdown-view1352')
#three_dot = driver.find_element(By.CLASS_NAME, 'dropdown-toggle')
#three_dot.click()

#wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/a')))
#driver.execute_script("return arguments[0].scrollIntoView(true);", three_dot)

hover = ActionChains(driver).move_to_element(three_dot)
hover.perform()

wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/ul/li[2]/ul/li[4]/a'))) 
eye = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/ul/li[2]/ul/li[4]/a')
eye.click()

print("hovered")
