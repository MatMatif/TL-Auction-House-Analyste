import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

try:
    # Configuration de Selenium avec le navigateur Brave en mode headless
    driver_path = r'E:\ProgramationPerso\Drivers\chromedriver-win64\chromedriver.exe'
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    options = Options()
    options.binary_location = brave_path
    options.add_argument('--headless')  # Activer le mode headless
    options.add_argument('--disable-gpu')  # Désactiver l'accélération GPU (recommandé en mode headless)
    options.add_argument('--no-sandbox')  # Pour éviter certaines erreurs de sandboxing en mode headless
    options.add_argument('--disable-software-rasterizer')  # Optimisation en mode headless

    service = Service(driver_path)

    # Initialiser le navigateur avec les options et driver
    driver = webdriver.Chrome(service=service, options=options)

    # Étape 1 : Accéder à la page
    driver.get("https://tldb.info/auction-house")

    # Utiliser WebDriverWait pour attendre que la page se charge (jusqu'à 10 secondes)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'aside.dt-pagination-rowcount'))
    )

    # Étape 2 : Ouvrir le premier menu dropdown et cliquer sur "All"
    driver.execute_script("""
        const dropdownButtons = document.querySelectorAll('.btn.btn-secondary.w-100.fw-semi-bold.dropdown-toggle');
        if (dropdownButtons.length > 0) {
            dropdownButtons[0].click(); // Clic sur le premier bouton dropdown
            setTimeout(() => {
                const dropdownMenu = document.querySelector("div[start='true'].dropdown-menu.show");
                const allButton = Array.from(dropdownMenu.querySelectorAll("button"))
                    .find(button => button.textContent.trim() === "All");
                if (allButton) allButton.click(); // Clic sur le bouton "All"
            }, 500); // Délai pour permettre au menu de s'afficher
        }
    """)

    # Étape 3 : Ouvrir le deuxième menu dropdown et cliquer sur le deuxième "Europe"
    driver.execute_script("""
        const dropdownButtons = document.querySelectorAll('.btn.btn-secondary.w-100.fw-semi-bold.dropdown-toggle');
        if (dropdownButtons.length > 1) {
            dropdownButtons[1].click(); // Clic sur le deuxième bouton dropdown
            setTimeout(() => {
                const dropdownMenu = document.querySelector("div[start='true'].dropdown-menu.show");
                const europeButtons = Array.from(dropdownMenu.querySelectorAll("button"))
                    .filter(button => button.textContent.trim() === "Europe");
                if (europeButtons.length >= 2) europeButtons[1].click(); // Clic sur le deuxième bouton "Europe"
            }, 500); // Délai pour permettre au menu de s'afficher
        }
    """)

    # Étape 4 : Récupérer le nombre total d'entrées à partir de la pagination
    pagination_text = driver.execute_script("""
        const paginationElement = document.querySelector('aside.dt-pagination-rowcount');
        if (paginationElement) {
            return paginationElement.textContent.trim();
        } else {
            return null;
        }
    """)

    # Utiliser une expression régulière pour extraire le nombre total d'entrées après 'of'
    total_entries = 0
    if pagination_text:
        try:
            # Rechercher le nombre après 'of'
            match = re.search(r'of (\d+) entries', pagination_text)
            if match:
                total_entries = int(match.group(1))  # Extraire le nombre après 'of'
                print(f"Nombre total d'entrées : {total_entries}")
            else:
                print("Aucun nombre d'entrées trouvé dans le texte de pagination.")
        except Exception as e:
            print(f"Erreur lors de l'extraction du nombre d'entrées : {e}")
    else:
        print("Impossible de récupérer le texte de pagination.")
    
    # Étape 5 : Cliquer sur tous les éléments du tableau
    for index in range(total_entries):  # Itération basée sur le nombre total d'entrées
        # Étape 5.1 : Trouver et cliquer sur le nom de l'objet dans la ligne du tableau
        driver.execute_script(f"""
            const tableRows = document.querySelectorAll('tbody.align-middle > tr');
            if (tableRows.length > {index}) {{
                const row = tableRows[{index}];
                const itemName = row.querySelector('.item-name .text-truncate span');
                if (itemName) {{
                    itemName.click(); // Clic sur le nom de l'objet dans la ligne du tableau
                }} else {{
                    console.error("Nom de l'objet introuvable dans la ligne {index}.");
                }}
            }} else {{
                console.error("Ligne {index} introuvable.");
            }}
        """)

        # Étape 5.2 : Attendre que le bouton "Go Back" soit cliquable avant d'interagir
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0'))
        )

        driver.execute_script("""
            const goBackButton = document.querySelector('.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0');
            if (goBackButton) {
                goBackButton.click(); // Clic sur le bouton "Go Back"
            } else {
                console.error("Bouton 'Go Back' introuvable.");
            }
        """)

    print("Tout le contenu du tableau a bien été extrait.")

except Exception as e:
    print(f"Une erreur s'est produite : {e}")
finally:
    driver.quit()
