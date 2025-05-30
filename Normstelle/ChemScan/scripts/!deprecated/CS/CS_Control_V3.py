#import chromedriver as cd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import win32gui
import win32con

# params: tkz, filepaths

tkz = "01041457"
files = [
    r"P:\k-z\Ofs\Dokumentenservice\TeileundStoffe\Antrag\2025\002-2025_01041445_Freigabe.pdf",
    r"P:\k-z\Ofs\Dokumentenservice\TeileundStoffe\Gefährdungsbeurteilung\003-2019_10003461_Ardrox 311.pdf",
    r"C:\Users\u8064927\Desktop\AT&S\Datenblatt.pdf"
]

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
driver.switch_to.window(driver.window_handles[-1]) # Pinned ChemScan
wait = WebDriverWait(driver, 10) # Wait for page loading, 10s timeout

# Detect interne Bezeichnung button
try:
    intern_btn = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]')
    intern_btn.click()
    #print("FULL XPATH")
except Exception as e:
    print(f"FAILED CSS_SELECTOR: {e}")

# enter tkz
tkz_input = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/input[1]')
tkz_input.send_keys(tkz)

# send tkz
send = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/button')
send.click()

time.sleep(1)

# TODO: what behaviour to set for several rows? open each in a new tab? 
wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/a'))) 
three_dot = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/a')
hover = ActionChains(driver).move_to_element(three_dot)
hover.perform()

# eye
wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/ul/li[2]/ul/li[4]/a'))) 
eye = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[11]/div/div/ul/li[2]/ul/li[4]/a')
eye.click()

# Scroll to bottom
wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[1]/nav/a[12]'))) 
info = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[1]/nav/a[12]')
info.click()

# Detect entries of requests and safety
nothing = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[2]/div/div/div[12]/div[2]/div/div/div/div/div/div/div[2]/div/div/div/div[2]/div[3]/p')
if nothing.text == "Keine Einträge gefunden": print("nothing found")
else: print("something there")

def upload_files(file):
    # click upload an attachment btn
    driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[2]/div[2]/a').click()

    # write the comment 
    # TODO: comment string generation based on file
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea")))
    comment = driver.find_element(By.XPATH, '/html/body/div[9]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea').send_keys("TESTALITEST")

    # attach the file
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "uploader.empty.input-widget-file")))
    driver.find_element(By.CLASS_NAME, "uploader.empty.input-widget-file").click()


    # Find the file dialog window
    def find_window():
        while True:
            hwnd = win32gui.FindWindow(None, "Open")  # The title of the file dialog window
            if hwnd: return hwnd
            time.sleep(0.5)
    hwnd = find_window()

    time.sleep(1)
    # Find the edit box where the file path is entered
    edit_box = win32gui.FindWindowEx(hwnd, 0, "ComboBoxEx32", None)
    edit_box = win32gui.FindWindowEx(edit_box, 0, "ComboBox", None)
    edit_box = win32gui.FindWindowEx(edit_box, 0, "Edit", None)

    # Set the file path
    win32gui.SendMessage(edit_box, win32con.WM_SETTEXT, None, file)

    # Find and click the "Open" button
    open_button = win32gui.FindWindowEx(hwnd, 0, "Button", "&Open")
    win32gui.SendMessage(hwnd, win32con.WM_COMMAND, 1, open_button)

    # detect change of file name in html
    wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]")))
    datei = driver.find_element(By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]")
    initial_text = datei.text

    # save when the initial string changes
    wait.until(lambda driver: driver.find_element(By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]").text != initial_text)
    driver.find_element(By.XPATH, '/html/body/div[9]/div[13]/div/div/div/span[2]/button').click()

    # detect upload state success/fail
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[1]/div/div/div')))
    fail = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[1]/div/div/div/div')
    if fail.text == "Attachment created successfully": print("UPLOAD SUCCESS")
    elif fail.text == "Sie haben keine Berechtigung um diese Aktion auszuführen.": print("UPLOAD FAILED")
    else: print("ALERT NOT FOUND")
    print(fail.text)

    print("DONE")

for file in files:
    upload_files(file)












driver.quit()




