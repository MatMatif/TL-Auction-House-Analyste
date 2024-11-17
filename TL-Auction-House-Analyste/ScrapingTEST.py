from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Démarrer le navigateur (par exemple avec Chrome)
driver = webdriver.Chrome()

# Accéder à la page
driver.get("https://tldb.info/auction-house")

# Attendre un peu que la page charge complètement
time.sleep(3)

# Trouver toutes les lignes du tableau
rows = driver.find_elements(By.CLASS_NAME, "ah-table-row")

# Cliquer sur chaque ligne pour récupérer les informations supplémentaires
for row in rows:
    # Cliquer sur la ligne pour révéler les informations supplémentaires
    row.click()
    
    # Attendre que les informations se chargent après le clic
    time.sleep(2)

    # Extraire les informations visibles après le clic
    name = driver.find_element(By.CSS_SELECTOR, "span.fw-semi-bold.color-rarity-5")
    quantity = driver.find_element(By.CSS_SELECTOR, "span.fw-semi-bold.text-accent-light.tab-num")
    price = driver.find_element(By.CSS_SELECTOR, "div.reward-item-small")

    # Afficher les résultats
    print(f"Nom de l'arme: {name.text}")
    print(f"Quantité: {quantity.text}")
    print(f"Prix: {price.text}")
    print("-" * 40)

# Fermer le navigateur
driver.quit()
