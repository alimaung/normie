import selenium_driver as cs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import win32gui
import win32con
import os
import CS_Classify as cl

# params: tkz, filepaths

def open_chem(driver, data):
    # Detect interne Bezeichnung button

    tkz = data["tkz"]
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]'))) 
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
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr/td[12]/div/div/a'))) 
    three_dot = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr/td[12]/div/div/a')
    hover = ActionChains(driver).move_to_element(three_dot)
    hover.perform()

    # eye
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr/td[12]/div/div/ul/li[2]/ul/li[4]/a'))) 
    eye = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr/td[12]/div/div/ul/li[2]/ul/li[4]/a')
    eye.click()

    # Scroll to bottom
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[1]/nav/a[12]'))) 
    info = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[1]/nav/a[12]')
    info.click()

    # Detect entries of requests and safety
    nothing = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[2]/div[2]/div/div/div[12]/div[2]/div/div/div/div/div/div/div[2]/div/div/div/div[2]/div[3]/p')
    if nothing.text == "Keine Einträge gefunden": print("nothing found")
    else: print("something there")

    return driver

def upload_files(driver, data):
    # ats, ats comment
    # sdb, sdb comment
    time.sleep(2)

    for row in data:
        # write the comment 
        # TODO: comment string generation based on file

        keys = [(data["ats"], data["ats_comment"]), (data["sdb"], data["sdb_comment"])]

        for value_key, comment_key in keys:
             # click upload an attachment btn
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[2]/div[2]/a')))
            driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[2]/div[2]/a').click()

            # enter the comment
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[8]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea")))
            driver.find_element(By.XPATH, '/html/body/div[8]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea').send_keys(comment_key)

            # attach the file
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "uploader.empty.input-widget-file")))
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
            win32gui.SendMessage(edit_box, win32con.WM_SETTEXT, None, value_key)

            # Find and click the "Open" button
            open_button = win32gui.FindWindowEx(hwnd, 0, "Button", "&Open")
            win32gui.SendMessage(hwnd, win32con.WM_COMMAND, 1, open_button)

            # detect change of file name in html
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]")))
            datei = driver.find_element(By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]")
            initial_text = datei.text

            # save when the initial string changes
            WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, "/html/body/div[9]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]").text != initial_text)
            driver.find_element(By.XPATH, '/html/body/div[9]/div[13]/div/div/div/span[2]/button').click()

            # detect upload state success/fail
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[1]/div/div/div')))
            fail = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[1]/div/div/div/div')
            if fail.text == "Attachment created successfully": print("UPLOAD SUCCESS")
            elif fail.text == "Sie haben keine Berechtigung um diese Aktion auszuführen.": print("UPLOAD FAILED")
            else: print("ALERT NOT FOUND")
            print(fail.text)

        return driver

def reset(driver):
    # back to home
    driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div/div/a').click()

    # reset the filter (not nessessarily)
    #WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]/span/span/span")))
    #driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]/span/span/span').click()

    # wait until page load
    WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.XPATH, '/html/body/div[10]')))

def preprocess_data(list):
    print(f"list: {list}")
    for row in list:
        print(f"row: {row}")
        tkz = row["tkz"]
        paths = []
        for key, value in row.items():
            if key in ["ats", "sdb"]: # filepaths

                # 1. Check if file exists
                if os.path.isfile(value) is True:
                    print(f"file {key}: {value} exists")
                    row["exists"] = True
                else:
                    print(f"file {key}: {value} doesnt exists")
                    row["exists"] = False
                    continue
                    #return None
                
                # 2. Check if file is .pdf
                ext = os.path.basename(value)
                if ext.endswith(".pdf"):
                    paths.append(value)
                    print("YESYES")
                    row["pdf"] = True
                else:
                    print("NONONO")
                    row["pdf"] = False

                # 3. Check if file is classified
                isclassified = cl.main(value)
                if isclassified == True:
                    print("classified")
                    row["class"] = isclassified
                else:
                    print(f"classification failed for: {value}")
                    row["class"] = isclassified

        print(f"new row: {row}")
    print(f"new list: {list}")
    return list
                

def main(dict):
    driver = cs.driver()
    data = preprocess_data(dict)
    
    for row in data:
        open = open_chem(driver, row)
        close = upload_files(open, row)
        reset(close)

    driver.quit()

    return driver