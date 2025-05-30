#import chromedriver as cd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.common.keys import Keys
import keyboard

""" 
1 Must use full XPATH due to variable class/selector  (same for btns)
2 Assume filtering is remembered throughout sessions..
3 Pin ChemScan in Chome so window_handle is always -1

"""

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
driver.switch_to.window(driver.window_handles[-1]) # Pinned ChemScan


tkz = "01041457"
wait = WebDriverWait(driver, 10) # Wait for page loading, 10s timeout

# Make sure its ChemScan # deprecated see top no 3
""" for handle in driver.window_handles:
    print(handle, driver.title)
    if driver.title == "Alle - Stoffregister" or "Dashboard":
        driver.switch_to.window(handle)
        print("switched to:", driver.title)
        break
    else:
        pass """

# remove filter if found (deprecated, see top no 2)
""" try:
    close_filter = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]/span/span/span')
    if not close_filter:
        pass
    else:
        alle = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]/span/span/b')
        if alle.text == "Alle":
            close_filter.click()
except:
    pass """

# other method for filter btn detection (also fails)
""" wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="grid-uub-hazard-substance-organization-with-actions-grid-1045400485"]/div[2]/div[2]/div[2]/div/table/thead[1]/tr/th[8]')))
filter_btn = driver.find_element(By.CLASS_NAME, 'action.btn.btn-icon.mode-icon-only')
filter_btn = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[1]/div/div[3]/div/div[2]/div/a[1]')
try:
    driver.find_element(By.CLASS_NAME, 'action btn btn-icon mode-icon-only pressed')
except Exception as e:
    print("DETECT 1 FAILED")

try:
    filter_btn = driver.find_element(By.CLASS_NAME, 'action btn btn-icon mode-icon-only')
    filter_btn.click()
except Exception as e:
    print("DETECT 2 FAILED") """

# Detect interne Bezeichnung button
try:
    intern_btn = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]')
    intern_btn.click()
    #print("FULL XPATH")
except Exception as e:
    print(f"FAILED CSS_SELECTOR: {e}")


tkz_input = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/input[1]')
tkz_input.send_keys(tkz)

send = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/button')
send.click()

# Get row txt elements
for t in driver.find_elements(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody'):
    print(t.text)

time.sleep(1)

# TODO: what behaviour to set for several rows? open each in a new tab? 
wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/a'))) 
three_dot = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/a')
hover = ActionChains(driver).move_to_element(three_dot)
hover.perform()

wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/ul/li[2]/ul/li[4]/a'))) 
eye = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/ul/li[2]/ul/li[4]/a')
eye.click()
#ActionChains(driver).key_down(Keys.CONTROL).click(eye).key_up(Keys.CONTROL).perform()

# reset the filter
#close = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]/span/span/span')
#close.click()

# switch to opened tab
#driver.switch_to.window(driver.window_handles[1])





# Scroll to bottom
wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[1]/nav/a[12]'))) 
info = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[1]/nav/a[12]')
info.click()

# Detect entries of requests and safety
nothing = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[2]/div/div/div[12]/div[2]/div/div/div/div/div/div/div[2]/div/div/div/div[2]/div[3]/p')
if nothing.text == "Keine Einträge gefunden": print("nothing found")
else: print("something there")

# upload an attachment
attach_btn = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[2]/div[2]/a')
attach_btn.click()

# attach the file
#wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/input")))
#file = driver.find_element(By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/input")
#file.click()
#file.send_keys("P:\k-z\Ofs\Dokumentenservice\TeileundStoffe\Antrag\2025\001-2025_01044234.pdf")

#time.sleep(2)
#keyboard.write(r"P:\k-z\Ofs\Dokumentenservice\TeileundStoffe\Antrag\2025\001-2025_01044234.pdf")
#keyboard.press("enter")

# write the comment TODO: comment string generation
comment = driver.find_element(By.XPATH, '/html/body/div[9]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea')
comment.click()
comment.send_keys("AT&S_001-2025_01044234_OU")