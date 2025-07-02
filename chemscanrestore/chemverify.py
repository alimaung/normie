import json
import os
import sys
import time
from pathlib import Path

# Import local CS modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'CS'))
from CS import selenium_driver as cs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def verify_tkz_duplicates(test_mode=False):
    """
    Verify TKZ entries in ChemScan and identify duplicates
    
    Args:
        test_mode (bool): If True, only process the first item
    """
    # Load the JSON data
    json_path = os.path.join(os.path.dirname(__file__), 'existing_teilenummer_links.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data['teilenummer_links'])} entries from existing_teilenummer_links.json")
    
    # Get all TKZ numbers
    tkz_list = []
    for item in data['teilenummer_links']:
        tkz_list.append(str(item['Teile-nummer']).strip())
    
    # Apply test mode if requested
    if test_mode and tkz_list:
        tkz_list = [tkz_list[0]]
        print(f"TEST MODE: Only processing first TKZ: {tkz_list[0]}")
    
    # Initialize browser
    driver = cs.driver()
    
    # Navigate to ChemScan (assuming you're already logged in)
    print("Please make sure you're logged into ChemScan and on the main page")
    input("Press Enter when ready...")
    
    # File to save duplicates
    duplicates_file = os.path.join(os.path.dirname(__file__), 'duplicate_tkz.txt')
    duplicates = []
    
    try:
        for i, tkz in enumerate(tkz_list):
            print(f"\nProcessing {i+1}/{len(tkz_list)}: TKZ {tkz}")
            
            # Search for TKZ
            duplicate_count = search_and_check_duplicates(driver, tkz)
            
            if duplicate_count > 1:
                print(f"⚠️  DUPLICATE FOUND: TKZ {tkz} has {duplicate_count} entries")
                duplicates.append(f"{tkz} - {duplicate_count} entries")
            else:
                print(f"✅ TKZ {tkz} - Single entry (OK)")
            
            # Reset for next search
            reset_search(driver)
            time.sleep(1)
    
    except Exception as e:
        print(f"Error during verification: {e}")
    
    finally:
        # Save duplicates to file
        if duplicates:
            with open(duplicates_file, 'w', encoding='utf-8') as f:
                f.write("TKZ Numbers with Multiple Entries:\n")
                f.write("="*40 + "\n")
                for dup in duplicates:
                    f.write(f"{dup}\n")
            
            print(f"\n🔍 Found {len(duplicates)} TKZ numbers with duplicates")
            print(f"📄 Duplicates saved to: {duplicates_file}")
        else:
            print("\n✅ No duplicates found!")
        
        driver.quit()

def search_and_check_duplicates(driver, tkz):
    """
    Search for a TKZ and count how many rows are returned
    
    Args:
        driver: Selenium WebDriver
        tkz: TKZ number to search for
    
    Returns:
        int: Number of rows found for this TKZ
    """
    try:
        # Click on "Interne Bezeichnung" button
        # Try alternative selector
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]')))
        intern_btn = driver.find_element(By.XPATH, 
            '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]')
        intern_btn.click()

        # Enter TKZ in search field
        tkz_input = driver.find_element(By.XPATH, 
            '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/input[1]')
        tkz_input.clear()
        tkz_input.send_keys(tkz)

        # Click search button
        send = driver.find_element(By.XPATH, 
            '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/button')
        send.click()

        # Wait 5 seconds as requested
        time.sleep(1)

        # Count table rows
        row_count = count_table_rows(driver)
        return row_count

    except Exception as e:
        print(f"Error searching for TKZ {tkz}: {e}")
        return 0

def count_table_rows(driver):
    """
    Count the number of rows in the results table
    
    Args:
        driver: Selenium WebDriver
    
    Returns:
        int: Number of rows found
    """
    try:
        # Wait for table to load
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody')))
        
        # Count rows by looking for the action buttons in each row
        row_count = 0
        row_index = 1
        
        while True:
            try:
                # Try to find the action button for this row
                row_xpath = f'/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[{row_index}]/td[12]/div/div/a'
                driver.find_element(By.XPATH, row_xpath)
                row_count += 1
                row_index += 1
                print(f"  Found row {row_count}")
            except NoSuchElementException:
                # No more rows found
                break
        
        return row_count
        
    except TimeoutException:
        print("  No results table found or timeout")
        return 0
    except Exception as e:
        print(f"  Error counting rows: {e}")
        return 0

def reset_search(driver):
    """
    Reset the search to clear results by clicking the reset element
    
    Args:
        driver: Selenium WebDriver
    """
    try:
        # Click the reset element to clear the search
        reset_element = driver.find_element(By.XPATH, 
            '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[1]/span/span/span')
        reset_element.click()
        
        # Wait 2 seconds as requested
        time.sleep(2)
        
        print("  Search reset successfully")
        
    except Exception as e:
        print(f"Error resetting search: {e}")
        # Fallback: try the old method
        try:
            tkz_input = driver.find_element(By.XPATH, 
                '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/input[1]')
            tkz_input.clear()
            send = driver.find_element(By.XPATH, 
                '/html/body/div[6]/div[2]/main/div[2]/div[3]/div[3]/div[1]/div/span/div[2]/div[2]/div/div[2]/button')
            send.click()
            time.sleep(1)
        except Exception as fallback_e:
            print(f"Fallback reset also failed: {fallback_e}")

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Verify TKZ entries for duplicates in ChemScan')
    parser.add_argument('--test', action='store_true', help='Test mode - only process first item')
    args = parser.parse_args()
    
    # Run the verification process
    verify_tkz_duplicates(test_mode=args.test)
