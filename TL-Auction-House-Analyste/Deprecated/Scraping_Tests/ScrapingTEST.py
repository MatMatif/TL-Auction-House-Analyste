from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get("https://tldb.info/auction-house")

time.sleep(3)

rows = driver.find_elements(By.CLASS_NAME, "ah-table-row")

for row in rows:
    row.click()
    time.sleep(2)

    name = driver.find_element(By.CSS_SELECTOR, "span.fw-semi-bold.color-rarity-5")
    quantity = driver.find_element(By.CSS_SELECTOR, "span.fw-semi-bold.text-accent-light.tab-num")
    price = driver.find_element(By.CSS_SELECTOR, "div.reward-item-small")

    print(f"Nom de l'arme: {name.text}")
    print(f"Quantité: {quantity.text}")
    print(f"Prix: {price.text}")
    print("-" * 40)

driver.quit()
