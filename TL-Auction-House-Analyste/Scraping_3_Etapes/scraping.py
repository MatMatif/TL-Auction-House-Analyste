from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

# Chemin vers le fichier exécutable du driver Chrome (chromedriver)
driver_path = r'E:\ProgramationPerso\Drivers\chromedriver-win64\chromedriver.exe'  # Chaîne brute pour éviter les problèmes d'échappement

# Chemin vers le fichier exécutable du navigateur Brave
brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"  # Chaîne brute

# Configuration des options pour Selenium
options = Options()
options.binary_location = brave_path  # Spécifie l'utilisation de Brave au lieu de Chrome

# Configuration du service Selenium avec le chemin du driver
service = Service(driver_path)

# Initialisation du navigateur Brave via Selenium
driver = webdriver.Chrome(service=service, options=options)

# Ouvrir la page web cible
driver.get("https://tldb.info/auction-house")

# Attendre 3 secondes pour s'assurer que la page est complètement chargée
time.sleep(3)

# Trouver et cliquer sur le bouton du menu déroulant
dropdown_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-secondary.w-100.fw-semi-bold.dropdown-toggle")
dropdown_button.click()

# Attendre une seconde pour laisser le menu déroulant s'afficher
time.sleep(1)

# Sélectionner l'option "All" dans le menu déroulant
option_all = driver.find_element(By.XPATH, "//button[text()='All']")
option_all.click()

# Attendre 3 secondes pour laisser la page se mettre à jour
time.sleep(3)

# Trouver le premier élément avec la classe "align-middle" (présumé être un `<tbody>`)
tbody = driver.find_elements(By.CLASS_NAME, "align-middle")[0]  # Sélectionner le premier tbody avec cette classe

# Extraire tout le code HTML du tbody
table_html = tbody.get_attribute("outerHTML")

# Sauvegarder le HTML dans un fichier local
with open("table_raw.html", "w", encoding="utf-8") as f:
    f.write(table_html)

# Fermer le navigateur pour libérer les ressources
driver.quit()

# Confirmation de la sauvegarde
print("HTML extrait et sauvegardé dans 'table_raw.html'")
