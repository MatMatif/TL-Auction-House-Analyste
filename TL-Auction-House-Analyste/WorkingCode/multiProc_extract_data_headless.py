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

def clean_string(s):
    """Nettoie une chaîne en supprimant les espaces superflus, les nouvelles lignes et autres caractères non désirés."""
    if s:
        return re.sub(r'\s+', ' ', s.strip().replace("\n", " ").replace("\t", " ").replace("\r", ""))
    return s

def print_pretty_data(data): # Fonction pour afficher les données extraites dans un joli tableau
    table = PrettyTable()
    table.field_names = ["Name", "Trait", "Price"]

    # Remplir le tableau avec les données extraites
    for item in data:
        for row in item:
            table.add_row([row["Name"], row["Trait"], row["Price"]])

    print(table)

def clean_and_convert_to_number(value):
    """Convertit une chaîne en float ou int, en gérant les séparateurs de milliers et décimaux."""
    try:
        value = value.strip()
        if "," in value:
            value = value.replace(",", "")
        number = float(value)
        if number.is_integer():
            return int(number)
        return number
    except ValueError:
        return 0

def save_to_csv(data, filename="extracted_data.csv"):
    headers = ["Name", "Trait", "Price"]

    # Ouvrir le fichier en mode écriture
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        # Écrire chaque ligne de données après nettoyage
        for item in data:
            for row in item:
                row["Name"] = row["Name"]
                row["Trait"] = row["Trait"]
                row["Price"] = str(row["Price"])
                writer.writerow(row)

    print(f"Les données ont été sauvegardées dans le fichier {filename}")

def init_driver():
    """Initialiser et retourner le driver Selenium."""
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
    return driver


def apply_filters(driver):
    """Appliquer les filtres 'All' et 'Europe'."""
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


def extract_total_entries(driver):
    """Extraire le nombre total d'entrées depuis la pagination."""
    pagination_text = driver.execute_script("""
        const paginationElement = document.querySelector('aside.dt-pagination-rowcount');
        return paginationElement ? paginationElement.textContent.trim() : null;
    """)
    total_entries = 0
    if pagination_text:
        match = re.search(r'of (\d+) entries', pagination_text)
        if match:
            total_entries = int(match.group(1))
    return total_entries

def parse_table_html(table_html):
    """Parse le HTML de la table et retourne les données extraites."""
    extracted_data = []
    if table_html:
        soup = BeautifulSoup(table_html, "html.parser")
        tbody = soup.find("tbody")
        if tbody:
            for row in tbody.find_all("tr"):
                try:
                    name = row.find_all("td")[2].get_text(strip=True)
                    trait = row.find_all("td")[3].get_text(strip=True)
                    price = row.find_all("td")[5].get_text(strip=True)

                    if name and trait and price:
                        price_int = clean_and_convert_to_number(price)  # Fonction de conversion
                        extracted_data.append({
                            "Name": name,
                            "Trait": trait,
                            "Price": price_int
                        })
                except IndexError:
                    continue
    return extracted_data

def click_and_get_table_html(driver, index):
    """Clique sur l'élément pour ouvrir les détails et retourne le HTML de la table."""
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
    table_html = driver.execute_script("""
        const table = document.querySelector('tbody.align-middle');
        return table ? table.outerHTML : null;
    """)

    return table_html

def extract_table_data(driver, index):
    """Extraire les données de la table d'une page."""
    table_html = click_and_get_table_html(driver, index)
    extracted_data = parse_table_html(table_html)

    return extracted_data


def run_selenium_instance(start_index, end_index):
    driver = init_driver()
    driver.get("https://tldb.info/auction-house")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'aside.dt-pagination-rowcount')))
    apply_filters(driver)

    total_entries = extract_total_entries(driver)
    print(f"Nombre total d'entrées : {total_entries}")

    extracted_data = []
    for index in range(start_index, min(end_index, total_entries)):
        page_data = extract_table_data(driver, index)
        extracted_data.extend(page_data)

        # Retourner à la page principale
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0')))
        driver.execute_script("""
            const goBackButton = document.querySelector('.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0');
            if (goBackButton) goBackButton.click();  // Retourner à la liste principale
        """)

    driver.quit()  # Fermer le driver une fois le travail terminé
    return extracted_data

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
    entries_per_instance = total_entries // num_instances

    # Diviser le travail en sous-ensembles pour chaque instance
    index_ranges = [(i * entries_per_instance, (i + 1) * entries_per_instance) for i in range(num_instances)]

    # Lancer les instances en parallèle avec multiprocessing.Pool
    with Pool(num_instances) as pool:
        results = pool.starmap(run_selenium_instance, index_ranges)

    all_extracted_data = []
    for result in results:
        all_extracted_data.extend(result)

    print(f"Nombre total de données extraites : {len(all_extracted_data)}")
    print_pretty_data(all_extracted_data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"extracted_data_{timestamp}.csv"
    
    save_to_csv(all_extracted_data, filename)

if __name__ == "__main__":

    while True:
        start_time = time.time()
        main()
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Temps d'exécution du script : {execution_time:.2f} secondes")
        
        time.sleep(10)
