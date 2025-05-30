from selenium.webdriver.remote.webdriver import WebDriver

def attach_to_session(executor_url, session_id):
    from selenium.webdriver.remote.command import Command

    driver = WebDriver(command_executor=executor_url)
    driver.session_id = session_id

    try:

        driver.execute(Command.STATUS)
        print("connected")
        return driver
    except:
        print("failed")
        return None

executor_url = ""
session_id = ""

driver = attach_to_session(executor_url, session_id)

if driver:
    print(driver.title)
