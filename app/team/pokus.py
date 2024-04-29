from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from time import sleep
import pandas as pd

# Nastavenie Selenium WebDriver
# driver = webdriver.Chrome(r'c:\club\frontend\node_modules\chromedriver\lib\chromedriver\chromedriver.exe')
s = Service(r'C:\Users\Dell\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')

# Vytvorenie instance WebDriveru s explicitným nastavením služby
driver = webdriver.Chrome(service=s)

driver.get("https://sportnet.sme.sk/futbalnet/z/obfz-bratislava-vidiek/s/4638/tabulky/")

# Čakanie na načítanie stránky (môže byť potrebné nastaviť dlhšie, závisí od rýchlosti načítania)
sleep(5)

# Získanie zdrojového kódu stránky po vykonaní JavaScriptu
html = driver.page_source

# Zatvorenie prehliadača
driver.quit()

# Použitie pandas na čítanie tabuliek
tables = pd.read_html(html)

# Vypísanie nájdených tabuliek
for i, table in enumerate(tables):
    print(f"Table {i}:")
    print(table.head())
