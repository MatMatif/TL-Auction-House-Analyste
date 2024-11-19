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

# Fonction pour afficher les données extraites de manière jolie
def print_pretty_data(data):
    table = PrettyTable()
    table.field_names = ["Name", "Trait", "Price"]

    for item in data:
        for row in item:
            table.add_row([row["Name"], row["Trait"], row["Price"]])

    print(table)

def clean_and_convert_price(price_str):
    # Supprimer les espaces et symboles inutiles (comme $ ou €), puis convertir en int
    cleaned_price = price_str.replace(",", "").replace("€", "").replace("$", "").strip()
    try:
        # Convertir en entier
        return int(cleaned_price)
    except ValueError:
        # En cas d'erreur, retourner 0 ou une autre valeur par défaut
        return 0


def save_to_csv(data, filename="extracted_data.csv"):
    # Définir les en-têtes du CSV
    headers = ["Name", "Trait", "Price"]

    # Ouvrir le fichier en mode écriture
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        # Écrire l'en-tête du CSV
        writer.writeheader()

        # Écrire chaque ligne de données
        for item in data:
            for row in item:
                writer.writerow(row)
    
    print(f"Les données ont été sauvegardées dans le fichier {filename}")


# Fonction pour initialiser et exécuter une instance de Selenium
def run_selenium_instance(start_index, end_index):
    driver_path = r'E:\ProgramationPerso\Drivers\chromedriver-win64\chromedriver.exe'
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

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
        
        # Attendre la présence de la pagination
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'aside.dt-pagination-rowcount')))
        
        # Ouvrir le premier dropdown et cliquer sur "All" et "Europe"
        driver.execute_script(""" 
            const dropdownButtons = document.querySelectorAll('.btn.btn-secondary.w-100.fw-semi-bold.dropdown-toggle');
            if (dropdownButtons.length > 0) {
                dropdownButtons[0].click(); // Clic sur le premier bouton dropdown
            }
        """)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[start='true'].dropdown-menu.show")))
        
        driver.execute_script(""" 
            const dropdownMenu = document.querySelector("div[start='true'].dropdown-menu.show");
            const allButton = Array.from(dropdownMenu.querySelectorAll("button"))
                .find(button => button.textContent.trim() === "All");
            if (allButton) allButton.click(); // Clic sur le bouton "All"
        """)

        driver.execute_script(""" 
            const dropdownButtons = document.querySelectorAll('.btn.btn-secondary.w-100.fw-semi-bold.dropdown-toggle');
            if (dropdownButtons.length > 1) {
                dropdownButtons[1].click(); // Clic sur le deuxième bouton dropdown
            }
        """)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[start='true'].dropdown-menu.show")))

        driver.execute_script(""" 
            const dropdownMenu = document.querySelector("div[start='true'].dropdown-menu.show");
            const europeButtons = Array.from(dropdownMenu.querySelectorAll("button"))
                .filter(button => button.textContent.trim() === "Europe");
            if (europeButtons.length >= 2) europeButtons[1].click(); // Clic sur le deuxième bouton "Europe"
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
        
        print(f"Nombre total d'entrées : {total_entries}")

        # Parcourir les entrées entre start_index et end_index
        extracted_data = []
        for index in range(start_index, min(end_index, total_entries)):
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

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody.align-middle')))

            table_html = driver.execute_script(""" 
                const table = document.querySelector('tbody.align-middle');
                return table ? table.outerHTML : null;
            """)

            if table_html:
                soup = BeautifulSoup(table_html, "html.parser")
                tbody = soup.find("tbody")

                if tbody:
                    table_data = []
                    for row in tbody.find_all("tr"):
                        try:
                            name = row.find_all("td")[2].get_text(strip=True)
                            trait = row.find_all("td")[3].get_text(strip=True)
                            price = row.find_all("td")[5].get_text(strip=True)

                            if name and trait and price:
                                # Convertir le prix en entier
                                price_int = clean_and_convert_price(price)
                                table_data.append({
                                    "Name": name,
                                    "Trait": trait,
                                    "Price": price_int
                                })
                        except IndexError:
                            continue
                    
                    extracted_data.append(table_data)

            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0')))
            driver.execute_script(""" 
                const goBackButton = document.querySelector('.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0');
                if (goBackButton) goBackButton.click();
            """)

        return extracted_data

    except Exception as e:
        print(f"Une erreur s'est produite dans l'instance Selenium : {e}")
        return []  # Retourne une liste vide en cas d'erreur

    finally:
        driver.quit()  # Fermer le navigateur

# Fonction principale pour diviser la tâche et lancer les instances en parallèle
def main():
    # Récupérer dynamiquement le nombre total d'entrées
    total_entries = get_total_entries()  # Cette fonction récupère `total_entries`
    num_instances = 4  # Nombre d'instances (processus) à lancer en parallèle
    entries_per_instance = total_entries // num_instances

    # Diviser le travail en sous-ensembles pour chaque instance
    index_ranges = [(i * entries_per_instance, (i + 1) * entries_per_instance) for i in range(num_instances)]

    # Utiliser multiprocessing.Pool pour exécuter les instances en parallèle
    with Pool(num_instances) as pool:
        results = pool.starmap(run_selenium_instance, index_ranges)

    # Combiner les données extraites de toutes les instances
    all_extracted_data = []
    for result in results:
        all_extracted_data.extend(result)

    print(f"Nombre total de données extraites : {len(all_extracted_data)}")
    print_pretty_data(all_extracted_data)  # Affichage des données dans un joli tableau

    # Sauvegarder les données dans un fichier CSV
    save_to_csv(all_extracted_data)  # Sauvegarde dans un fichier CSV

# Fonction pour récupérer dynamiquement `total_entries`
def get_total_entries():
    driver = webdriver.Chrome()  # Créez une instance Selenium sans headless pour extraire le total
    driver.get("https://tldb.info/auction-house")
    
    # Attendre la présence de la pagination
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'aside.dt-pagination-rowcount')))
    
    pagination_text = driver.execute_script(""" 
        const paginationElement = document.querySelector('aside.dt-pagination-rowcount');
        return paginationElement ? paginationElement.textContent.trim() : null;
    """)
    total_entries = 0
    if pagination_text:
        match = re.search(r'of (\d+) entries', pagination_text)
        if match:
            total_entries = int(match.group(1))

    driver.quit()
    return total_entries

# Lancer l'exécution principale
if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Temps d'exécution du script : {execution_time:.2f} secondes")
