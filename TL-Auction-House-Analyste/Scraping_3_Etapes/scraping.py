from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

driver_path = r'E:\ProgramationPerso\Drivers\chromedriver-win64\chromedriver.exe'  # Chaîne brute pour éviter les problèmes d'échappement
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

tbody = driver.find_elements(By.CLASS_NAME, "align-middle")[0]  # Sélectionner le premier tbody avec cette classe
table_html = tbody.get_attribute("outerHTML")

with open("table_raw.html", "w", encoding="utf-8") as f:
    f.write(table_html)

driver.quit()
print("HTML extrait et sauvegardé dans 'table_raw.html'")
