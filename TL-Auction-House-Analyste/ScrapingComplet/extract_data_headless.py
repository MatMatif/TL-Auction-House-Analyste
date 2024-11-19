import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import re  # Importation du module pour utiliser les expressions regulières

extracted_data = []  # Liste pour stocker les donnees extraites

try:
    
    start_time = time.time()

    # Configuration de Selenium avec le navigateur Brave
    driver_path = r'E:\ProgramationPerso\Drivers\chromedriver-win64\chromedriver.exe'  # Chemin vers le driver Chrome
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"  # Chemin vers Brave

    options = Options()
    options.binary_location = brave_path  # Utilisation du navigateur Brave au lieu de Chrome

    # Ajout d'options pour le mode headless (sans interface graphique)
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('window-size=1920x1080')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    # Initialisation du navigateur Brave avec Selenium
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # Desactivation de la detection de Selenium par les sites web (pour eviter d'être detecte)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Desactivation des animations pour accelerer le processus
    driver.execute_script(""" 
        const style = document.createElement('style');
        style.innerHTML = '*, *::before, *::after { transition: none !important; animation: none !important; }';
        document.head.appendChild(style);
    """)

    # Étape 1 : Acceder à la page
    driver.get("https://tldb.info/auction-house")

    # Attendre la presence de la pagination pour confirmer que la page est bien chargee
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'aside.dt-pagination-rowcount'))
    )

    # Étape 2 : Ouvrir le premier menu dropdown et cliquer sur "All"
    driver.execute_script(""" 
        const dropdownButtons = document.querySelectorAll('.btn.btn-secondary.w-100.fw-semi-bold.dropdown-toggle');
        if (dropdownButtons.length > 0) {
            dropdownButtons[0].click(); // Clic sur le premier bouton dropdown
        }
    """)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[start='true'].dropdown-menu.show"))
    )
    driver.execute_script(""" 
        const dropdownMenu = document.querySelector("div[start='true'].dropdown-menu.show");
        const allButton = Array.from(dropdownMenu.querySelectorAll("button"))
            .find(button => button.textContent.trim() === "All");
        if (allButton) allButton.click(); // Clic sur le bouton "All"
    """)

    # Étape 3 : Ouvrir le deuxième menu dropdown et cliquer sur le deuxième "Europe"
    driver.execute_script(""" 
        const dropdownButtons = document.querySelectorAll('.btn.btn-secondary.w-100.fw-semi-bold.dropdown-toggle');
        if (dropdownButtons.length > 1) {
            dropdownButtons[1].click(); // Clic sur le deuxième bouton dropdown
        }
    """)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[start='true'].dropdown-menu.show"))
    )
    driver.execute_script(""" 
        const dropdownMenu = document.querySelector("div[start='true'].dropdown-menu.show");
        const europeButtons = Array.from(dropdownMenu.querySelectorAll("button"))
            .filter(button => button.textContent.trim() === "Europe");
        if (europeButtons.length >= 2) europeButtons[1].click(); // Clic sur le deuxième bouton "Europe"
    """)

    # Étape 4 : Recuperer le nombre total d'entrees à partir de la pagination
    pagination_text = driver.execute_script(""" 
        const paginationElement = document.querySelector('aside.dt-pagination-rowcount');
        if (paginationElement) {
            return paginationElement.textContent.trim();
        } else {
            return null;
        }
    """)

    # Utiliser une expression regulière pour extraire le nombre total d'entrees
    total_entries = 0
    if pagination_text:
        try:
            match = re.search(r'of (\d+) entries', pagination_text)
            if match:
                total_entries = int(match.group(1))  # Extraire le nombre après 'of'
                print(f"Nombre total d'entrees : {total_entries}")
            else:
                print("Aucun nombre d'entrees trouve dans le texte de pagination.")
        except Exception as e:
            print(f"Erreur lors de l'extraction du nombre d'entrees : {e}")
    else:
        print("Impossible de recuperer le texte de pagination.")

    # Étape 5 : Iterer sur les elements du tableau et extraire les donnees
    for index in range(min(total_entries, 10)):  # Limite à 10 elements pour l'exemple
        # Selectionner une ligne du tableau et cliquer sur l'element pour charger les informations
        driver.execute_script(f"""
            const tableRows = document.querySelectorAll('tbody.align-middle > tr');
            if (tableRows.length > {index}) {{
                const row = tableRows[{index}];
                const itemName = row.querySelector('.item-name .text-truncate span');
                if (itemName) {{
                    itemName.click(); // Clic sur l'element
                }}
            }}
        """)

        # Attendre que la page des details soit chargee
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody.align-middle'))
        )

        # Recuperer le contenu HTML du tableau après chargement
        table_html = driver.execute_script(""" 
            const table = document.querySelector('tbody.align-middle');
            return table ? table.outerHTML : null;
        """)

        if table_html:
            # Sauvegarder le contenu HTML brut dans un fichier pour l'inspecter
            with open(f"table_raw_{index}.html", "w", encoding="utf-8") as raw_file:
                raw_file.write(table_html)

            # Nettoyer et extraire les donnees à l'aide de BeautifulSoup
            soup = BeautifulSoup(table_html, "html.parser")
            rows = soup.find_all("tr", class_="ah-table-row")  # Filtrer uniquement les lignes avec cette classe

            # Supprimer les balises inutiles et les attributs pour un meilleur nettoyage
            tbody = soup.find_all("tbody", class_="align-middle")[0]
            for tag in tbody.find_all(["span", "div", "svg", "img", "a", "path"]):
                if not tag.get_text(strip=True):
                    tag.decompose()  # Supprime la balise du DOM si elle est vide

            # Supprimer les attributs inutiles dans les balises restantes
            for tag in tbody.find_all(True):
                del tag['class']
                del tag['style']

            # Sauvegarder le tableau nettoye dans un nouveau fichier HTML
            with open(f"table_cleaned_{index}.html", "w", encoding="utf-8") as cleaned_file:
                cleaned_file.write(str(tbody))

            # EXTRAIRE LES DONNÉES DU FICHIER NETTOYÉ ET LES ENREGISTRER DANS UN FICHIER EXCEL
            with open(f"table_cleaned_{index}.html", "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            tbody = soup.find_all("tbody", class_="align-middle")[0]

            # Extraction des donnees du tableau
            table_data = []
            for row in tbody.find_all("tr"):
                try:
                    name = row.find_all("td")[2].get_text(strip=True)
                    trait = row.find_all("td")[3].get_text(strip=True)
                    price = row.find_all("td")[5].get_text(strip=True)

                    table_data.append({
                        "Name": name,
                        "Trait": trait,
                        "Price": price
                    })
                except IndexError:
                    continue  # Si une ligne est malformee, on l'ignore

            # Creer un DataFrame et le sauvegarder dans un fichier Excel
            df = pd.DataFrame(table_data)
            excel_file = f"table_data_{index}.xlsx"
            df.to_excel(excel_file, index=False, engine="openpyxl")

            print(f"Les donnees ont ete extraites et sauvegardees dans '{excel_file}'")

        # Retourner à la liste principale
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0'))
        )
        driver.execute_script(""" 
            const goBackButton = document.querySelector('.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0');
            if (goBackButton) goBackButton.click();
        """)

    end_time = time.time()
    execution_time = end_time - start_time  # Temps d'execution en secondes

    print("Extraction terminee.")
    # Afficher le temps d'execution
    print(f"Temps d'execution du script : {execution_time:.2f} secondes")

except Exception as e:
    print(f"Une erreur s'est produite : {e}")
finally:
    driver.quit()  # Fermer le navigateur
