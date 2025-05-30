#import chromedriver as cd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os
from selenium.webdriver.common.action_chains import ActionChains

# Must use full XPATH due to variable class/selector  (same for btns)
# Assume filtering is remembered throughout sessions..
# Pin ChemScan in Chome so window_handle is always 0


chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
driver.switch_to.window(driver.window_handles[-1])

# Make sure its ChemScan
#for handle in driver.window_handles:
#    print(handle, driver.title)
#    if driver.title == "Alle - Stoffregister" or "Dashboard":
#        driver.switch_to.window(handle)
#        print("switched to:", driver.title)
#        break
#    else:
#        pass

# 01041347 	01041457 	01041457
tkz = "01041457"

wait = WebDriverWait(driver, 10) # Wait for page loading, 10s timeout

# remove filter if found

#try:
#    close_filter = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]/span/span/span')
#    if not close_filter:
#        pass
#    else:
#        alle = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]/span/span/b')
#        if alle.text == "Alle":
#            close_filter.click()
#except:
#    pass
#
##wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="grid-uub-hazard-substance-organization-with-actions-grid-1045400485"]/div[2]/div[2]/div[2]/div/table/thead[1]/tr/th[8]')))
##filter_btn = driver.find_element(By.CLASS_NAME, 'action.btn.btn-icon.mode-icon-only')
##filter_btn = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[1]/div/div[3]/div/div[2]/div/a[1]')
##try:
##    driver.find_element(By.CLASS_NAME, 'action btn btn-icon mode-icon-only pressed')
##except Exception as e:
##    print("DETECT 1 FAILED")
##
##try:
##    filter_btn = driver.find_element(By.CLASS_NAME, 'action btn btn-icon mode-icon-only')
##    filter_btn.click()
##except Exception as e:
##    print("DETECT 2 FAILED")
#
#try:
#    intern_btn = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]')
#    intern_btn.click()
#    #print("FULL XPATH")
#except Exception as e:
#    print(f"FAILED CSS_SELECTOR: {e}")
#
#tkz_input = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/input[1]')
#tkz_input.send_keys(tkz)
#
#send = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/button')
#send.click()
#
## /html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/a
## /html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[2]/td[11]/div/div/a
## /html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody
##
##
#
## Get row txt elements
#for t in driver.find_elements(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody'):
#    print(t.text)

three_dot = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/a')
#three_dot = driver.find_element(By.ID, 'actions-cell-dropdown-view1352')
#three_dot = driver.find_element(By.CLASS_NAME, 'dropdown-toggle')

three_dot.click()

hover = ActionChains(driver).move_to_element(three_dot)
hover.perform()

print("hovered")

