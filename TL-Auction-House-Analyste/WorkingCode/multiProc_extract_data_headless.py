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

def clean_string(s: str) -> str:
    """
    Nettoyer une chaine de caracteres en supprimant les espaces inutiles et en remplaçant les caracteres de saut de ligne et de tabulation par des espaces.

    Args:
        s (str): Chaine de caracteres a nettoyer

    Returns:
        str: Chaine de caracteres nettoyee
    """
    if s:
        return re.sub(r'\s+', ' ', s.strip().replace("\n", " ").replace("\t", " ").replace("\r", ""))
    return s

def clean_and_convert_to_number(value: str) -> Union[int, float]:
    """
    Convertir une valeur brute en un nombre (int ou float) si possible.

    Args:
        value (str): Valeur brute

    Returns:
        Union[int, float]: Nombre converti ou 0 si la conversion a echoue
    """
    # Supprimer les espaces inutiles
    value = value.strip()

    # Supprimer les virgules si presentes
    if "," in value:
        value = value.replace(",", "")

    try:
        # Tenter de convertir en nombre
        number = float(value)
        # Si c'est un entier, le renvoyer tel quel
        if number.is_integer():
            return int(number)
        # Sinon, le renvoyer comme float
        return number
    except ValueError:
        # Si la conversion a echoue, afficher un message d'erreur
        print(f"Failed to convert '{value}' to a number")
        # Et renvoyer 0
        return 0


def check_trait_column_in_html(table_html):
    """
    Verifier si une colonne nommee "Trait" est presente dans le tableau HTML fourni.

    Args:
        table_html (str): HTML du tableau

    Returns:
        bool: True si la colonne "Trait" est presente, False sinon
    """
    if table_html:
        soup = BeautifulSoup(table_html, "html.parser")
        thead = soup.find("thead")
        # Recherche de la colonne "Trait" dans le thead
        if thead:
            for th in thead.find_all("th"):
                if 'Trait' in th.get_text(strip=True):
                    #print("Trait trouver\n")
                    return True
    return False


def nettoyer_et_simplifier_html(contenu_html):
    """
    Nettoie et simplifie le contenu HTML fourni en supprimant les balises et attributs inutiles.

    Args:
        contenu_html (str): Le contenu HTML brut à nettoyer.

    Returns:
        str: Le contenu HTML nettoyé et simplifié.
    """
    try:
        # Parse le contenu HTML avec BeautifulSoup
        soup = BeautifulSoup(contenu_html, "html.parser")
        # Trouver le premier <tbody> avec la classe 'align-middle'
        tbody = soup.find("tbody", class_="align-middle")

        if not tbody:
            print("Aucun <tbody> avec la classe 'align-middle' trouvé.")
            return str(soup)

        # Supprimer les balises inutiles ou vides
        for tag in tbody.find_all(["span", "div", "svg", "img", "a", "path"]):
            if not tag.get_text(strip=True):
                tag.decompose()

        # Supprimer les lignes de tableau (tr) vides
        for ligne in tbody.find_all("tr"):
            cellules = ligne.find_all("td")
            if all(not cellule.get_text(strip=True) for cellule in cellules):
                ligne.decompose()

        # Supprimer les attributs inutiles des balises restantes
        for tag in tbody.find_all(True):
            tag.attrs = {key: value for key, value in tag.attrs.items() if key not in ["class", "style"]}

        return str(tbody)

    except Exception as e:
        print(f"Erreur lors du traitement : {e}")
        return contenu_html

def creer_fichier(contenu, nom_fichier):
    """
    Crée un fichier avec le contenu fourni.

    Args:
        contenu (str): Le contenu du fichier.
        nom_fichier (str): Le nom du fichier à créer.

    Raises:
        Exception: Si une erreur se produit lors de la création du fichier.
    """
    try:
        # Ouvrir le fichier en mode écriture (w) avec encodage UTF-8
        with open(nom_fichier, 'w', encoding='utf-8') as fichier:
            # Écrire le contenu dans le fichier
            fichier.write(contenu)
        # Afficher un message de confirmation
        print(f"Le fichier '{nom_fichier}' a été créé avec succès.")
    except Exception as e:
        # Afficher un message d'erreur si une erreur se produit
        print(f"Une erreur s'est produite lors de la création du fichier : {e}")


def print_pretty_data(data):
    """
    Fonction pour afficher les données extraites dans un joli tableau.

    Args:
        data (list): La liste de données à afficher.

    Returns:
        None
    """
    # Instancier un objet PrettyTable
    table = PrettyTable()
    # Définir les en-têtes du tableau
    table.field_names = ["Name", "Trait", "Price", "Quantity"]

    # Parcourir la liste de données et ajouter chaque élément au tableau
    for item in data:
        for row in item:
            # Ajouter une ligne au tableau avec les valeurs de l'élément
            table.add_row([row["Name"], row["Trait"], row["Price"], row["Quantity"]])

    # Afficher le tableau
    print(table)

def save_to_csv(data, filename="extracted_data.csv"):
    """
    Fonction pour sauvegarder les données dans un fichier CSV.

    Args:
        data (list): La liste de données à sauvegarder.
        filename (str): Le nom du fichier CSV à créer (par défaut : "extracted_data.csv").
    """
    # Définir les en-têtes du CSV
    headers = ["Name", "Trait", "Price", "Quantity"]

    # Ouvrir le fichier en mode écriture (w) avec encodage UTF-8
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        # Instancier un objet DictWriter
        writer = csv.DictWriter(file, fieldnames=headers)
        # Écrire l'en-tête
        writer.writeheader()

        # Parcourir la liste de données et écrire chaque élément dans le fichier
        for item in data:
            for row in item:
                # Convertir les valeurs en strings
                row["Name"] = str(row["Name"])
                row["Trait"] = str(row["Trait"])
                row["Price"] = str(row["Price"])
                row["Quantity"] = str(row["Quantity"])
                # Écrire la ligne dans le fichier
                writer.writerow(row)

    # Afficher un message de confirmation
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
                        itemName.click();  // Clic sur l'élément pour ouvrir ses détails
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

def get_total_entries():
    """Fonction pour récupérer dynamiquement le nombre de lignes (total_entries) de la page d'accueil de l'Auction House.

    Returns:
        int: Nombre de lignes (total_entries) de la page d'accueil de l'Auction House.
    """
    driver = webdriver.Chrome()  #! Ajoute le mode headless
    driver.get("https://tldb.info/auction-house")

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

    while True:
        start_time = time.time()
        main()
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Temps d'exécution du script : {execution_time:.2f} secondes")
        time.sleep(10)  
