from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

driver_path = r'E:\ProgramationPerso\Drivers\chromedriver-win64\chromedriver.exe'  # Chaîne brute
brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"  # Chaîne brute

options = Options()
options.binary_location = brave_path

service = Service(driver_path)

driver = webdriver.Chrome(service=service, options=options)
driver.get("https://tldb.info/auction-house")

time.sleep(3)

dropdown_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-secondary.w-100.fw-semi-bold.dropdown-toggle")
dropdown_button.click()

time.sleep(1)

option_all = driver.find_element(By.XPATH, "//button[text()='All']")
option_all.click()

time.sleep(3)

rows = driver.find_elements(By.CLASS_NAME, "ah-table-row")

print("AAA")

for row in rows:
    try:
        name = row.find_element(By.CSS_SELECTOR, "td.item-name .fw-semi-bold.color-rarity-5")
        weapon_name = name.text if name else "Nom non disponible"
        
        quantity_element = row.find_element(By.CSS_SELECTOR, "td.text-end .fw-semi-bold.text-accent-light.tab-num")
        quantity = quantity_element.text if quantity_element else "Quantité non disponible"
        
        price_element = row.find_element(By.CSS_SELECTOR, "td.text-end .reward-item-small")
        price = price_element.text if price_element else "Prix non disponible"
        
        print(f"Nom de l'arme: {weapon_name}")
        print(f"Quantité: {quantity}")
        print(f"Prix: {price}")
        print("-" * 40)
        
    except Exception as e:
        print(f"Erreur dans la ligne: {e}")

driver.quit()
