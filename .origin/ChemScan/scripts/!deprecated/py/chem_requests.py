import requests
import json
import re
from bs4 import BeautifulSoup
import chromedriver
import urllib3
from selenium import webdriver
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# get chemscan cookies
def get_new_cookies():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    driver.switch_to.window(driver.window_handles[-1])
    driver.get("https://app.chemscan.de/cadaster/organization/")
    cookies = driver.get_cookies()
    print(cookies)
    #driver.quit()
    with open('cookie2.json', 'w', encoding='utf-8') as f:
        save = f.write(str(cookies))
    return save

def test(cookies):
    c1 = cookies[0]
    c2 = cookies[1]
    c3 = cookies[2]
    csrf = c1['value']
    bapid = c2['value']
    baprm = c3['value']
    #print(csrf)
    #print(bapid)
    #print(baprm)

    cookies2 = {
        'https-_csrf': csrf,
        'BAPID': bapid,
        'BAPRM': baprm
    }

    url = "https://app.chemscan.de/cadaster/organization/"

    cooking = requests.get(url, cookies=cookies2, verify=False)
    print(cooking.status_code)

    if cooking.status_code == 200:
        print("Cookies are valid")
        return True
    else:
        print("Cookies are invalid")
        return False

    

def get_old_cookies():
    with open('cookie1.json', 'r') as f:
        cookie = json.load(f)
    cookies = []
    for c in cookie:
        cookies.append(c)
    return cookies

def fetch_data(internal_name_value):
    # Define the URL
    url = "https://app.chemscan.de/datagrid/uub-hazard-substance-organization-with-actions-grid?uub-hazard-substance-organization-with-actions-grid%5BoriginalRoute%5D=uub_cadaster_organization_index&appearanceType=grid&uub-hazard-substance-organization-with-actions-grid%5B_pager%5D%5B_page%5D=1&uub-hazard-substance-organization-with-actions-grid%5B_pager%5D%5B_per_page%5D=25&uub-hazard-substance-organization-with-actions-grid%5B_parameters%5D%5Bview%5D=__all__&uub-hazard-substance-organization-with-actions-grid%5B_appearance%5D%5B_type%5D=grid&uub-hazard-substance-organization-with-actions-grid%5B_filter%5D%5BinternalName%5D%5Bvalue%5D={internal_name_value}&uub-hazard-substance-organization-with-actions-grid%5B_filter%5D%5BinternalName%5D%5Btype%5D=1&uub-hazard-substance-organization-with-actions-grid%5B_columns%5D=active1.hsSds1.hsHa1.internalName1.name1.manufacturerName1.symbolSigns1.catalogRRates1.substanceName1.hazardSubstanceAssessmentBU1.hsNumber0.additionalInfo10.additionalInfo20.hsWaterHazardClass0.catalogWarehouseClass0.catalogUnNumber0.hsForm0.hsBoilingPoint0.hsFlamePoint0.sdsRequested0.sdsPrinted0.hsVocAmount0"

    # Define the headers
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache, no-store",
        "Cookie": "BAPRM=WjFZNEZHVm1PVHZMQ3hvbitvOFQyYzUySm9JYmZFbW10SjNHMGg1dW4xR0pzOVhHWmVQUzdVMllKaU9PSmhKVFZXRTcyVW55WU9qNlJoaUxNaEpBdXc9PTpnay9UdTdudTR1S0pacis5VlJhd3NjU05ySUdMaVpQN2UrUE9VSHhrNmVKQkh3ZGxuRCtoOTMzSUExZGlKcU5NUzNzNERrblpvRWVVamVYK0xLbi9xdz09",
        "Referer": "https://app.chemscan.de/cadaster/organization/?grid%5Buub-hazard-substance-organization-with-actions-grid%5D=i%3D1%26p%3D25%26f%255BinternalName%255D%255Bvalue%255D%3D01016215%26f%255BinternalName%255D%255Btype%255D%3D1%26c%3Dactive1.hsSds1.hsHa1.internalName1.name1.manufacturerName1.symbolSigns1.catalogRRates1.substanceName1.hazardSubstanceAssessmentBU1.hsNumber0.additionalInfo10.additionalInfo20.hsWaterHazardClass0.catalogWarehouseClass0.catalogUnNumber0.hsForm0.hsBoilingPoint0.hsFlamePoint0.sdsRequested0.sdsPrinted0.hsVocAmount0%26v%3D__all__%26a%3Dgrid%26g%255BoriginalRoute%255D%3Duub_cadaster_organization_index",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "X-Csrf-Header": "dCv9cifEz7dhwf4T5lhWEipXrv4AVcB-9T0hbLCI8-I",
        "X-Requested-With": "XMLHttpRequest"
    }

    # Define the payload (as a dictionary)
    payload = {
        "uub-hazard-substance-organization-with-actions-grid[originalRoute]": "uub_cadaster_organization_index",
        "appearanceType": "grid",
        "uub-hazard-substance-organization-with-actions-grid[_pager][_page]": 1,
        "uub-hazard-substance-organization-with-actions-grid[_pager][_per_page]": 25,
        "uub-hazard-substance-organization-with-actions-grid[_parameters][view]": "__all__",
        "uub-hazard-substance-organization-with-actions-grid[_appearance][_type]": "grid",
        "uub-hazard-substance-organization-with-actions-grid[_filter][internalName][value]": internal_name_value,
        "uub-hazard-substance-organization-with-actions-grid[_filter][internalName][type]": 1,
        "uub-hazard-substance-organization-with-actions-grid[_columns]": "active1.hsSds1.hsHa1.internalName1.name1.manufacturerName1.symbolSigns1.catalogRRates1.substanceName1.hazardSubstanceAssessmentBU1.hsNumber0.additionalInfo10.additionalInfo20.hsWaterHazardClass0.catalogWarehouseClass0.catalogUnNumber0.hsForm0.hsBoilingPoint0.hsFlamePoint0.sdsRequested0.sdsPrinted0.hsVocAmount0"
    }

    # Make the GET request with the cookies, headers, and payload
    response = requests.get(url, headers=headers, params=payload, verify=False)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Request successful!")
        
        # Parse the JSON response
        data = response.json().get('data', [])
        answer = process_data(data)
    else:
        print(f"Request failed with status code {response.status_code}")

def process_data(data):
        # Extract and print the name from the first item in the response
        link = data[0].get('view_link', 'Link not found')
        print(f"Name: {link}")
        
        # Optionally, save the response to a json file
        #with open('response.json', 'w') as f:
        #    json.dump(data, f, indent=4)
        base_url = "https://app.chemscan.de"

        response2 = requests.get(base_url + link, verify=False)

        if response2.status_code == 200:
            print(response2.status_code)
            # save html
            with open('item.html', 'w', encoding='utf-8') as f:
                f.write(response2.text)

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(response2.text, 'html.parser')

        # Find the div with the 'data-page-component-options' attribute
        widget_div = soup.find('div', {'class': 'widget-content'})

        # Ensure we found the div, then get the data inside the 'data-page-component-options' attribute
        if widget_div:
            data_options = widget_div.find('div', {'data-page-component-options': True})

            if data_options:
                # Get the value of the 'data-page-component-options' attribute
                data_options_value = data_options.get('data-page-component-options')

                # Decode the escaped JSON into a Python dictionary
                decoded_options = json.loads(data_options_value.replace("&quot;", "\""))

                # Extract the 'data' part of the JSON object, which contains the filename data
                data_items = decoded_options.get('data', [])
                #print("data_items", data_items)
                #print(data_items["data"][1]["originalFilename"])

                del data_items["options"]

                processed_items = []
                
                for item in data_items["data"]:
                    original_filename = item["originalFilename"]
                    # parse the HTML content
                    soup = BeautifulSoup(original_filename, "html.parser")
                    
                    # Extract the link (href), filename (data-filename), and display (text inside <a>)
                    link = soup.find("a")["href"]
                    filename = soup.find("a")["data-filename"]
                    display = soup.find("a").text.strip()
                    
                    # remove original_filename
                    del item["originalFilename"]

                    new_data = {
                        "link": link,
                        "filename": filename,
                        "display": display,
                        "fileSize": item["fileSize"].strip(),
                        "createdAt": item["createdAt"],
                        "comment": item["comment"],
                        "id": item["id"]
                    }
                    item.update(new_data)
                    processed_items.append(new_data)

                with open('item.json', 'w', encoding='utf-8') as f:
                    json.dump(processed_items, f, indent=4)
            else:
                print("No 'data-page-component-options' found.")
        else:
            print("No 'widget-content' div found.")

# Input the internalName from the user
internal_name_value = input("Enter the internalName value: ")

# Fetch and display the data
#cookies = get_new_cookies()
fetch_data(internal_name_value)

""" cookies = get_old_cookies()
result = test(cookies)
if result != True:
    cookies = get_new_cookies()
    fetch_data(internal_name_value, cookies)
else:
    fetch_data(internal_name_value, cookies) """
