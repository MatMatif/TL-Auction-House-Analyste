import time
from multiprocessing import Pool
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import csv
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from datetime import datetime

def input_text_in_search(driver, text_to_input):
    """
    Remplit un champ <input> avec le texte spécifié.

    :param driver: L'instance WebDriver en cours
    :param text_to_input: Le texte à insérer dans le champ <input>
    """
    try:
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.form-control.text-light.svelte-k1xh3p.css"))
        )
        
        search_input.clear()
        search_input.send_keys(text_to_input)

        search_input.send_keys(Keys.RETURN)
        print(f"Texte '{text_to_input}' inséré avec succès dans le champ de recherche.")
    except Exception as e:
        print(f"Erreur lors de l'insertion du texte dans le champ de recherche : {e}")

def clean_string(s):
    if s:
        return re.sub(r'\s+', ' ', s.strip().replace("\n", " ").replace("\t", " ").replace("\r", ""))
    return s

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
        #print("TH trouver\n")
        if thead:
            for th in thead.find_all("th"):
                if 'Trait' in th.get_text(strip=True):
                    #print("Trait trouver\n")
                    return True
    return False

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

def clean_text(text):
    return text.replace("→", "")

def print_pretty_data(data): # Fonction pour afficher les données extraites dans un joli tableau
    table = PrettyTable()
    table.field_names = ["Name", "Trait", "Price", "Quantity"]

    for item in data:
        for row in item:
            table.add_row([row["Name"], row["Trait"], row["Price"], row["Quantity"]])

    print(table)

def save_to_csv(data, filename="extracted_data.csv"):
    headers = ["Name", "Trait", "Price", "Quantity"]  # Définir les en-têtes du CSV

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for item in data:
            for row in item:
                row["Name"] = clean_text(row["Name"])
                row["Trait"] = clean_text(row["Trait"])
                row["Price"] = clean_text(str(row["Price"]))
                row["Quantity"] = clean_text(str(row["Quantity"]))
                writer.writerow(row)

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

        input_text_in_search(driver, "Extract")

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
                    if (itemName && itemName.textContent.trim().startsWith('Extract')) {{
                        itemName.click();
                    }}
                }}
            """)

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody.align-middle')))

            table_html = driver.execute_script("""
                const table = document.querySelector('table.table.table-striped.table-borderless.svelte-vjrwi3');
                return table ? table.outerHTML : null;
            """)

            is_trait_column = check_trait_column_in_html(table_html)

            table_html = nettoyer_et_simplifier_html(table_html)

            if is_trait_column:
                print("Trait trouver\n")
                if table_html:
                    soup = BeautifulSoup(table_html, "html.parser")
                    tbody = soup.find("tbody")

                if tbody:
                    table_data = []
                    for row in tbody.find_all("tr"):
                        try:
                            name = clean_string(row.find_all("td")[2].get_text(strip=True))
                            trait = clean_string(row.find_all("td")[3].get_text(strip=True))
                            quantity = clean_string(row.find_all("td")[4].get_text(strip=True))
                            price = clean_string(row.find_all("td")[5].get_text(strip=True))

                            if name and trait and price:
                                price_int = clean_and_convert_to_number(price)
                                quantity_int = clean_and_convert_to_number(quantity)

                                table_data.append({
                                    "Name": name,
                                    "Trait": trait,
                                    "Price": price_int,
                                    "Quantity": quantity_int
                                })
                        except IndexError:
                            continue
            else:
                print("Trait non trouver\n")
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
                                    table_data.append({
                                        "Name": name,
                                        "Trait": "NONE",
                                        "Quantity": quantity_int,
                                        "Price": price_int
                                    })
                            except IndexError:
                                continue          
            extracted_data.append(table_data)

            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0')))
            driver.execute_script(""" 
                const goBackButton = document.querySelector('.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0');
                if (goBackButton) goBackButton.click();  // Retourner à la liste principale
            """)

        return extracted_data

    except Exception as e:
        print(f"Une erreur s'est produite dans l'instance Selenium : {e}")
        return []

    finally:
        driver.quit()

def get_total_entries(): # Fonction pour récupérer dynamiquement `total_entries`
    # Définir les chemins pour les drivers
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

    driver.get("https://tldb.info/auction-house")

    input_text_in_search(driver, "Extract")

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

def main(): # Fonction principale pour diviser le travail et lancer les instances en parallèle
    total_entries = get_total_entries()

    num_instances = 16
    entries_per_instance = total_entries // num_instances

    index_ranges = [(i * entries_per_instance, (i + 1) * entries_per_instance) for i in range(num_instances)]

    with Pool(num_instances) as pool:
        results = pool.starmap(run_selenium_instance, index_ranges)

    all_extracted_data = []
    for result in results:
        all_extracted_data.extend(result)

    print(f"Nombre total de données extraites : {len(all_extracted_data)}")
    #print_pretty_data(all_extracted_data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"extracted_data_{timestamp}.csv"
    save_to_csv(all_extracted_data, filename)

if __name__ == "__main__":
    a = 0
    while a != 1:
        start_time = time.time()
        main()
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Temps d'exécution du script : {execution_time:.2f} secondes")
        a += 1
        time.sleep(1)  
