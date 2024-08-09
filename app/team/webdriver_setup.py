from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

def get_webdriver():
    # Nastavení cest k binárkám, které poskytuje Heroku
    chrome_bin = os.environ.get('GOOGLE_CHROME_BIN', "chromedriver")
    chrome_driver_bin = os.environ.get('CHROMEDRIVER_PATH', "/app/.chromedriver/bin/chromedriver")

    # Nastavení možností pro Chrome
    chrome_options = Options()
    chrome_options.binary_location = chrome_bin
    chrome_options.add_argument("--headless")  # Spuštění Chrome v headless režimu
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Inicializace WebDriveru
    driver = webdriver.Chrome(executable_path=chrome_driver_bin, options=chrome_options)
    return driver