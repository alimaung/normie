from selenium import webdriver

options = webdriver.ChromeOptions()
driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', 
                          options=options)

driver.get('https://www.google.com')

session_id = driver.session_id
executor_url = driver.command_executor._url

print(f'Session ID:{session_id}')
print(f'Executor URL:{executor_url}')
input("Press Enter...")
