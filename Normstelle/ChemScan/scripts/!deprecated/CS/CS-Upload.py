from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import win32gui
import win32con

# Connect to session
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
driver.switch_to.window(driver.window_handles[0]) # Pinned ChemScan

wait = WebDriverWait(driver, 10) # Wait timer, 10s timeout

# Scroll to bottom "Zusätzliche Informationen" by click
driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[1]/nav/a[12]').click()

# Detect attachment entries 
# TODO: if detected, find the attachments
nothing = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[2]/div/div/div[12]/div[2]/div/div/div/div/div/div/div[2]/div/div/div/div[2]/div[3]/p')
if nothing.text == "Keine Einträge gefunden": print("nothing found")
else: print("something there")

# click upload an attachment btn
driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[2]/div[2]/a').click()

# write the comment 
# TODO: comment string generation based on file
wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea")))
comment = driver.find_element(By.XPATH, '/html/body/div[9]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea').send_keys("TESTALITEST")

# attach the file
wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "uploader.empty.input-widget-file")))
driver.find_element(By.CLASS_NAME, "uploader.empty.input-widget-file").click()

time.sleep(0.5)


# Find the file dialog window
def find_window():
    while True:
        hwnd = win32gui.FindWindow(None, "Open")  # The title of the file dialog window
        if hwnd: return hwnd
        time.sleep(0.5)
hwnd = find_window()

# Find the edit box where the file path is entered
edit_box = win32gui.FindWindowEx(hwnd, 0, "ComboBoxEx32", None)
edit_box = win32gui.FindWindowEx(edit_box, 0, "ComboBox", None)
edit_box = win32gui.FindWindowEx(edit_box, 0, "Edit", None)

# Set the file path
#file_path = r"P:\k-z\Ofs\Dokumentenservice\TeileundStoffe\Antrag\2025\002-2025_01041445_Freigabe.pdf" # fail
file_path = r"P:\k-z\Ofs\Dokumentenservice\TeileundStoffe\Gefährdungsbeurteilung\003-2019_10003461_Ardrox 311.pdf" # succ
#file_path = r"C:\Users\u8064927\Desktop\AT&S\Datenblatt.pdf" # succ
win32gui.SendMessage(edit_box, win32con.WM_SETTEXT, None, file_path)

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

# Alternatively wait until loading overlay is gone
#WebDriverWait(driver, 300).until(EC.invisibility_of_element_located((By.XPATH, '/html/body/div[10]')))


print("DONE")
driver.quit()




