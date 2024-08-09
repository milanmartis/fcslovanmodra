from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

def get_webdriver():
    chrome_options = Options()
    chrome_options.binary_location = os.getenv('GOOGLE_CHROME_BIN')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_driver_path = os.getenv('CHROMEDRIVER_PATH')

    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
    return driver