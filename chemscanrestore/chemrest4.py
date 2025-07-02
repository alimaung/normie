import json
import os
import sys
from pathlib import Path

# Import local CS modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'CS'))
from CS import CS_Control_V4 as cs_control
from CS import selenium_driver as cs

def upload_existing_ats(test_mode=False, prompt_for_tkz=False):
    """
    Upload ATS files from existing_teilenummer_links.json to ChemScan
    
    Args:
        test_mode (bool): If True, only process the first item
        prompt_for_tkz (bool): If True, prompt for TKZ numbers, otherwise use all
    """
    # Load the JSON data
    json_path = os.path.join(os.path.dirname(__file__), 'existing_teilenummer_links.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data['teilenummer_links'])} entries from existing_teilenummer_links.json")
    print(f"Filter criteria: {data['metadata']['filter_criteria']}")
    
    # Get TKZ list if prompted, otherwise use all
    tkz_list = None
    if prompt_for_tkz:
        input_tkz = input("Enter TKZ number(s) separated by commas (or press Enter for all): ")
        if input_tkz.strip():
            tkz_list = [tkz.strip() for tkz in input_tkz.split(',')]
    
    # Use all entries from the file
    filtered_items = []
    for item in data['teilenummer_links']:
        if not tkz_list or str(item['Teile-nummer']).strip() in tkz_list:
            filtered_items.append(item)
    
    if not filtered_items:
        print(f"No matching TKZ numbers found in the data.")
        return
    
    # Format data for CS_Control_V4
    upload_data = []
    for item in filtered_items:
        # Format the data as expected by CS_Control_V4
        entry = {
            "id": item['Antrag-nummer'].replace("/", "-"),
            "tkz": str(item['Teile-nummer']),
            "ats": item['File_URL'],
            "sdb": "",  # No SDB in this case
            "loc": item['Location'],
            "ats_comment": item['Comment'],
            "sdb_comment": "",
            "exists": None,
            "pdf": None,
            "class": None
        }
        upload_data.append(entry)
        print(f"Prepared for upload: TKZ {entry['tkz']} - {entry['ats']}")
    
    # Apply test mode if requested
    if test_mode and upload_data:
        upload_data = [upload_data[0]]
        print(f"TEST MODE: Only processing first item: {upload_data[0]['tkz']}")
    
    """ # Confirm before uploading
    confirm = input(f"Ready to upload {len(upload_data)} files. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Upload cancelled.")
        return """
    
    # Call modified upload function
    try:
        upload_ats_only(upload_data)
        print("Upload process completed.")
    except Exception as e:
        print(f"Error during upload: {e}")

def upload_ats_only(data_list):
    """
    Modified version of CS_Control_V4.main that only uploads ATS files
    
    Args:
        data_list (list): List of data dictionaries with ATS information
    """
    driver = cs.driver()
    processed_data = preprocess_ats_data(data_list)
    
    for row in processed_data:
        print(f"Processing TKZ: {row['tkz']}")

        # Open chemical details
        driver = cs_control.open_chem(driver, row)
        
        # Upload only ATS file (no SDB)
        driver = upload_ats_file(driver, row)
        
        # Reset browser for next item
        cs_control.reset(driver)
    
    driver.quit()
    return driver

def upload_ats_file(driver, data):
    """
    Upload only the ATS file (modified version of CS_Control_V4.upload_files)
    
    Args:
        driver: Selenium WebDriver
        data: Data dictionary with ATS information
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import win32gui
    import win32con
    import time
    
    # Skip if no ATS file or it doesn't exist
    if not data["ats"] or data.get("exists") is False:
        print(f"No valid ATS file for TKZ {data['tkz']} - skipping")
        return driver
    
    # Click upload attachment button
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[2]/div[2]/a')))
    driver.find_element(By.XPATH, 
        '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[2]/div[2]/a').click()
    
    # Enter comment
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.XPATH, "/html/body/div[10]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea")))
    driver.find_element(By.XPATH, 
        '/html/body/div[10]/div[4]/div/div/form/fieldset/div[2]/div[2]/textarea').send_keys(data["ats_comment"])
    
    # Click file upload area

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.CLASS_NAME, "uploader.empty.input-widget-file")))
    driver.find_element(By.CLASS_NAME, "uploader.empty.input-widget-file").click()
    print("\033[92mFILE UPLOAD\033[0m")
    # Handle file dialog
    def find_window():
        for _ in range(20):  # Try for 10 seconds
            hwnd = win32gui.FindWindow(None, "Open")
            if hwnd: 
                return hwnd
            time.sleep(0.5)
        return None
        
    hwnd = find_window()
    if not hwnd:
        print("File dialog not found - upload failed")
        return driver
    
    time.sleep(1)
    
    # Find edit box and set file path
    edit_box = win32gui.FindWindowEx(hwnd, 0, "ComboBoxEx32", None)
    edit_box = win32gui.FindWindowEx(edit_box, 0, "ComboBox", None)
    edit_box = win32gui.FindWindowEx(edit_box, 0, "Edit", None)
    
    # Set the file path
    win32gui.SendMessage(edit_box, win32con.WM_SETTEXT, None, data["ats"])
    
    # Find and click Open button
    open_button = win32gui.FindWindowEx(hwnd, 0, "Button", "&Open")
    win32gui.SendMessage(hwnd, win32con.WM_COMMAND, 1, open_button)
    
    # Wait for file name to change in the UI
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.XPATH, "/html/body/div[10]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]")))
    datei = driver.find_element(By.XPATH, 
        "/html/body/div[10]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]")
    initial_text = datei.text
    print(f"\033[92mNAME CHANGED: {datei.text}\033[0m")
    
    # Wait for file name to change (indicating upload)
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.XPATH, 
            "/html/body/div[10]/div[4]/div/div/form/fieldset/div[1]/div[2]/div/div/div/span[1]").text != initial_text)
    print("\033[92mUPLOAD INDICATOR\033[0m")
    # Click save button
    driver.find_element(By.XPATH, '/html/body/div[10]/div[13]/div/div/div/span[2]/button').click()
    print("\033[92mSAVE BUTTON\033[0m")
    # Check upload status
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located(
        (By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[1]/div/div/div')))
    status = driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[1]/div/div/div/div')
    
    if status.text == "Attachment created successfully":
        print(f"UPLOAD SUCCESS: {data['tkz']}")
    elif status.text == "Sie haben keine Berechtigung um diese Aktion auszuführen.":
        print(f"UPLOAD FAILED (Permission denied): {data['tkz']}")
    else:
        print(f"UPLOAD STATUS UNKNOWN: {status.text}")
    
    return driver

def preprocess_ats_data(data_list):
    """
    Preprocess only ATS files (modified version of CS_Control_V4.preprocess_data)
    
    Args:
        data_list: List of data dictionaries
    """
    import os
    from CS import CS_Classify as cl
    
    for row in data_list:
        if row["ats"]:  # Only process if ATS file exists
            # 1. Check if file exists
            if True:
                print(f"File exists: {row['ats']}")
                row["exists"] = True
            else:
                print(f"File doesn't exist: {row['ats']}")
                row["exists"] = False
                continue
            
            # 2. Check if file is .pdf
            if row["ats"].lower().endswith(".pdf"):
                print(f"Valid PDF: {row['ats']}")
                row["pdf"] = True
            else:
                print(f"Not a PDF: {row['ats']}")
                row["pdf"] = False
            
            # 3. Check if file is classified
            try:
                #isclassified = cl.main(row["ats"])
                isclassified = True
                row["class"] = isclassified
                print(f"Classification status: {isclassified}")
            except Exception as e:
                print(f"Classification check failed: {e}")
                row["class"] = False
    
    return data_list

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Upload ATS files to ChemScan from existing entries')
    parser.add_argument('--tkz', type=str, help='TKZ numbers separated by commas (optional)')
    parser.add_argument('--test', action='store_true', help='Test mode - only process first item')
    parser.add_argument('--prompt', action='store_true', help='Prompt for TKZ numbers')
    args = parser.parse_args()
    
    # Set parameters based on arguments
    test_mode = args.test
    prompt_for_tkz = args.prompt
    
    # If TKZ numbers provided via command line, set them up
    if args.tkz:
        tkz_list = args.tkz.split(',')
        prompt_for_tkz = True
        
    # Run the upload process
    upload_existing_ats(test_mode=test_mode, prompt_for_tkz=prompt_for_tkz) 