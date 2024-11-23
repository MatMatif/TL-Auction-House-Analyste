import time
from multiprocessing import Pool
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import csv
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from datetime import datetime

from bs4 import BeautifulSoup

def nettoyer_et_simplifier_html(contenu_html):
    try:
        soup = BeautifulSoup(contenu_html, "html.parser")
        tbody = soup.find("tbody", class_="align-middle")

        if not tbody:
            print("Aucun <tbody> avec la classe 'align-middle' trouvé.")
            return str(soup)

        for tag in tbody.find_all(["span", "div", "svg", "img", "a", "path"]):
            if not tag.get_text(strip=True):
                tag.decompose()

        for ligne in tbody.find_all("tr"):
            cellules = ligne.find_all("td")
            if all(not cellule.get_text(strip=True) for cellule in cellules):
                ligne.decompose()

        for tag in tbody.find_all(True):
            tag.attrs = {key: value for key, value in tag.attrs.items() if key not in ["class", "style"]}

        return str(tbody)
    
    except Exception as e:
        print(f"Erreur lors du traitement : {e}")
        return contenu_html

def creer_fichier(contenu, nom_fichier):
    try:
        with open(nom_fichier, 'w', encoding='utf-8') as fichier:
            fichier.write(contenu)
        print(f"Le fichier '{nom_fichier}' a été créé avec succès.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du fichier : {e}")


def clean_and_convert_to_number(value):
    try:
        value = value.strip()
        if "," in value:
            value = value.replace(",", "")
        number = float(value)
        if number.is_integer():
            return int(number)
        return number
    except ValueError:
        print(f"Failed to convert '{value}' to a number")
        return 0

def check_trait_column_in_html(table_html):
    if table_html:
        soup = BeautifulSoup(table_html, "html.parser")
        thead = soup.find("thead")
        print("TH trouver\n")
        if thead:
            for th in thead.find_all("th"):
                if 'Trait' in th.get_text(strip=True):
                    print("Trait trouver\n")
                    return True
    return False

def clean_text(text):
    """
    Nettoie le texte en supprimant ou en remplaçant les caractères problématiques.
    """
    cleaned_text = text.replace("→", "")
    return cleaned_text

def clean_string(s):
    if s:
        return re.sub(r'\s+', ' ', s.strip().replace("\n", " ").replace("\t", " ").replace("\r", ""))
    return s

def print_pretty_data(data): # Fonction pour afficher les données extraites dans un joli tableau
    table = PrettyTable()
    table.field_names = ["Name", "Trait", "Price"]

    for item in data:
        for row in item:
            table.add_row([row["Name"], row["Trait"], row["Price"]])

    print(table)

def save_to_csv(data, filename="extracted_data.csv"):
    headers = ["Name", "Trait", "Price", "Quantity"]

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for item in data:
            for row in item:
                print("Processing row:", row)
                if isinstance(row, dict):
                    row["Name"] = clean_text(row.get("Name", ""))
                    row["Trait"] = clean_text(row.get("Trait", ""))
                    row["Price"] = clean_text(str(row.get("Price", "")))
                    row["Quantity"] = clean_text(str(row.get("Quantity", "")))
                    writer.writerow(row)
                #else:
                    #print(f"Skipping invalid row: {row}")

    print(f"Les données ont été sauvegardées dans le fichier {filename}")


def run_selenium_instance(start_index, end_index): # Fonction pour exécuter une instance de Selenium
    # Définir les chemins pour les drivers
    driver_path = r'E:\ProgramationPerso\Drivers\chromedriver-win64\chromedriver.exe'
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    # Configurer les options du navigateur
    options = Options()
    options.binary_location = brave_path
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('window-size=1920x1080')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://tldb.info/auction-house")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'aside.dt-pagination-rowcount')))

        # Sélectionner les filtres (All et Europe)
        driver.execute_script(""" 
            const dropdownButtons = document.querySelectorAll('.btn.btn-secondary.w-100.fw-semi-bold.dropdown-toggle');
            if (dropdownButtons.length > 0) {
                dropdownButtons[0].click();  // Clic sur le premier dropdown
            }
        """)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[start='true'].dropdown-menu.show")))

        driver.execute_script(""" 
            const dropdownMenu = document.querySelector("div[start='true'].dropdown-menu.show");
            const allButton = Array.from(dropdownMenu.querySelectorAll("button"))
                .find(button => button.textContent.trim() === "All");
            if (allButton) allButton.click();  // Clic sur le bouton "All"
        """)

        driver.execute_script(""" 
            const dropdownButtons = document.querySelectorAll('.btn.btn-secondary.w-100.fw-semi-bold.dropdown-toggle');
            if (dropdownButtons.length > 1) {
                dropdownButtons[1].click();  // Clic sur le deuxième dropdown
            }
        """)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[start='true'].dropdown-menu.show")))

        driver.execute_script(""" 
            const dropdownMenu = document.querySelector("div[start='true'].dropdown-menu.show");
            const europeButtons = Array.from(dropdownMenu.querySelectorAll("button"))
                .filter(button => button.textContent.trim() === "Europe");
            if (europeButtons.length >= 2) europeButtons[1].click();  // Clic sur le deuxième bouton "Europe"
        """)

        # Extraire le nombre total d'entrées depuis la pagination
        pagination_text = driver.execute_script(""" 
            const paginationElement = document.querySelector('aside.dt-pagination-rowcount');
            return paginationElement ? paginationElement.textContent.trim() : null;
        """)
        total_entries = 0
        if pagination_text:
            match = re.search(r'of (\d+) entries', pagination_text)
            if match:
                total_entries = int(match.group(1))

        print(f"Nombre total d'entrées : {total_entries}")  # Afficher le nombre total d'entrées

        i = 0

        # Parcourir les entrées entre start_index et end_index
        for index in range(start_index, min(end_index, total_entries)):
            driver.execute_script(f"""
                const tableRows = document.querySelectorAll('tbody.align-middle > tr');
                if (tableRows.length > {index}) {{
                    const row = tableRows[{index}];
                    const itemName = row.querySelector('.item-name .text-truncate span');
                    if (itemName) {{
                        itemName.click();  // Clic sur l'élément pour ouvrir ses détails
                    }}
                }}
            """)

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody.align-middle')))

            # Récupérer le HTML de la table des détails
            table_html = driver.execute_script(""" 
                const table = document.querySelector('table table-striped table-borderless svelte-vjrwi3');
                return table ? table.outerHTML : null;
            """)
            is_trait_column = check_trait_column_in_html(table_html)

            creer_fichier(table_html, f"FichierLog{i}.html")
            i += 1
            
            table_html = nettoyer_et_simplifier_html(table_html)
            table_data = []

            if is_trait_column == True:
                if table_html:
                    soup = BeautifulSoup(table_html, "html.parser")
                    tbody = soup.find("tbody")
                    if tbody:
                        for row in tbody.find_all("tr"):
                            try:
                                print("in trait\n")
                                name = clean_string(row.find_all("td")[2].get_text(strip=True))
                                trait = clean_string(row.find_all("td")[3].get_text(strip=True))
                                quantity = clean_string(row.find_all("td")[4].get_text(strip=True))
                                price = clean_string(row.find_all("td")[5].get_text(strip=True))
                                #print("TRAIT", "name:", name, "trait:", trait, "quantity:", quantity, "price:", price, "\n")
                                if name and trait and quantity and price:
                                    price_int = clean_and_convert_to_number(price)
                                    quantity_int = clean_and_convert_to_number(quantity)
                                    if quantity_int > 0:
                                        table_data.append({
                                            "Name": name,
                                            "Trait": trait,
                                            "Quantity": quantity_int,
                                            "Price": price_int
                                        })
                                        print(table_data[-1], "\n")
                                    else:
                                        print("\nrien na été append\n")
                                        continue
                                        print(row, "\n")
                                    #print(table_data[-1], "\n")

                            except IndexError:
                                continue
            else:
                if table_html:
                    soup = BeautifulSoup(table_html, "html.parser")
                    tbody = soup.find("tbody")

                    if tbody:
                        for row in tbody.find_all("tr"):
                            try:
                                print("in no trait\n")
                                name = clean_string(row.find_all("td")[2].get_text(strip=True))
                                quantity = clean_string(row.find_all("td")[3].get_text(strip=True))
                                price = clean_string(row.find_all("td")[4].get_text(strip=True))
                                #print("TRAITLESS", "name:", name, "quantity:", quantity, "price:", price, "\n")
                                if name and quantity and price:
                                    price_int = clean_and_convert_to_number(price)
                                    quantity_int = clean_and_convert_to_number(quantity)
                                    if quantity_int > 0:
                                        table_data.append({
                                            "Name": name,
                                            "Trait": "NONE",
                                            "Quantity": quantity_int,
                                            "Price": price_int
                                        })
                                        print(table_data[-1], "\n")
                                    else:
                                        continue
                                        print(row, "\n")
                                    #print(table_data[-1], "\n")
                            except IndexError:
                                continue

            # Retourner à la page principale
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0')))
            driver.execute_script(""" 
                const goBackButton = document.querySelector('.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0');
                if (goBackButton) goBackButton.click();  // Retourner à la liste principale
            """)
        print(table_data)
        return table_data

    except Exception as e:
        print(f"Une erreur s'est produite dans l'instance Selenium : {e}")
        return []  # Retourne une liste vide en cas d'erreur

    finally:
        driver.quit()  # Fermer le navigateur à la fin de l'exécution

def get_total_entries(): # Fonction pour récupérer dynamiquement `total_entries`
    driver = webdriver.Chrome() #! Ajoute le mode headless
    driver.get("https://tldb.info/auction-house")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'aside.dt-pagination-rowcount')))

    pagination_text = driver.execute_script(""" 
        const paginationElement = document.querySelector('aside.dt-pagination-rowcount');
        return paginationElement ? paginationElement.textContent.trim() : null;
    """)
    
    if not pagination_text:
        print("Erreur : Impossible de récupérer le texte de pagination. Attente de 1 minute et relance...")
        time.sleep(60)  # Attendre 1 minute avant de relancer
        driver.quit()
        return get_total_entries()  # Relancer la fonction

    total_entries = 0
    if pagination_text:
        match = re.search(r'of (\d+) entries', pagination_text)
        if match:
            total_entries = int(match.group(1))

    driver.quit()
    return total_entries

def main(): # Fonction principale pour diviser le travail et lancer les instances en parallèle
    total_entries = get_total_entries()
    num_instances = 6  # Nombre d'instances (processus) à lancer en parallèle
    entries_per_instance = total_entries // num_instances  # Diviser les entrées entre les processus

    # Diviser le travail en sous-ensembles pour chaque instance
    index_ranges = [(i * entries_per_instance, (i + 1) * entries_per_instance) for i in range(num_instances)]

    # Lancer les instances en parallèle avec multiprocessing.Pool
    with Pool(num_instances) as pool:
        results = pool.starmap(run_selenium_instance, index_ranges)

    # Combiner les données extraites de toutes les instances
    all_extracted_data = []
    for result in results:
        all_extracted_data.extend(result)

    print(f"Nombre total de données extraites : {len(all_extracted_data)}")
    #print_pretty_data(all_extracted_data)

    # Ajouter un timestamp au nom du fichier CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"extracted_data_{timestamp}.csv"
    
    save_to_csv(all_extracted_data, filename)

if __name__ == "__main__": # Lancer l'exécution toutes les 10 minutes

    while True:
        start_time = time.time()
        main()  # Appeler la fonction principale
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Temps d'exécution du script : {execution_time:.2f} secondes")
        
        # Attendre 10 secondes avant la prochaine exécution
        time.sleep(10)
