from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time


def getLocation():
    options = Options()
    options.add_argument("--use--fake-ui-for-media-stream")
    # Edit path of chromedriver accordingly
    driver = webdriver.Chrome(
        executable_path='./chromedriver', options=options)
    timeout = 20
    driver.get("https://mycurrentlocation.net/")
    wait = WebDriverWait(driver, timeout)
    time.sleep(3)
    longitude = driver.find_elements_by_xpath(
        '//*[@id="longitude"]')  # Replace with any XPath
    longitude = [x.text for x in longitude]
    longitude = str(longitude[0])
    latitude = driver.find_elements_by_xpath('//*[@id="latitude"]')
    latitude = [x.text for x in latitude]
    latitude = str(latitude[0])
    driver.quit()
    return (latitude, longitude)
