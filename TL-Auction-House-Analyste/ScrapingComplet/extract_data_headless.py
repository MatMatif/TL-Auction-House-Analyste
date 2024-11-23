import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import re

extracted_data = []

try:
    
    start_time = time.time()

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

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.execute_script(""" 
        const style = document.createElement('style');
        style.innerHTML = '*, *::before, *::after { transition: none !important; animation: none !important; }';
        document.head.appendChild(style);
    """)

    driver.get("https://tldb.info/auction-house")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'aside.dt-pagination-rowcount'))
    )

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

    pagination_text = driver.execute_script(""" 
        const paginationElement = document.querySelector('aside.dt-pagination-rowcount');
        if (paginationElement) {
            return paginationElement.textContent.trim();
        } else {
            return null;
        }
    """)

    total_entries = 0
    if pagination_text:
        try:
            match = re.search(r'of (\d+) entries', pagination_text)
            if match:
                total_entries = int(match.group(1))
                print(f"Nombre total d'entrees : {total_entries}")
            else:
                print("Aucun nombre d'entrees trouve dans le texte de pagination.")
        except Exception as e:
            print(f"Erreur lors de l'extraction du nombre d'entrees : {e}")
    else:
        print("Impossible de recuperer le texte de pagination.")

    for index in range(min(total_entries, 10)):
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

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody.align-middle'))
        )

        table_html = driver.execute_script(""" 
            const table = document.querySelector('tbody.align-middle');
            return table ? table.outerHTML : null;
        """)

        if table_html:
            with open(f"table_raw_{index}.html", "w", encoding="utf-8") as raw_file:
                raw_file.write(table_html)

            soup = BeautifulSoup(table_html, "html.parser")
            rows = soup.find_all("tr", class_="ah-table-row")

            tbody = soup.find_all("tbody", class_="align-middle")[0]
            for tag in tbody.find_all(["span", "div", "svg", "img", "a", "path"]):
                if not tag.get_text(strip=True):
                    tag.decompose()

            for tag in tbody.find_all(True):
                del tag['class']
                del tag['style']

            with open(f"table_cleaned_{index}.html", "w", encoding="utf-8") as cleaned_file:
                cleaned_file.write(str(tbody))

            with open(f"table_cleaned_{index}.html", "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            tbody = soup.find_all("tbody", class_="align-middle")[0]

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
                    continue

            df = pd.DataFrame(table_data)
            excel_file = f"table_data_{index}.xlsx"
            df.to_excel(excel_file, index=False, engine="openpyxl")

            print(f"Les donnees ont ete extraites et sauvegardees dans '{excel_file}'")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0'))
        )
        driver.execute_script(""" 
            const goBackButton = document.querySelector('.btn.btn-secondary.fw-semi-bold.d-flex.align-items-center.gap-1.svelte-o8inv0');
            if (goBackButton) goBackButton.click();
        """)

    end_time = time.time()
    execution_time = end_time - start_time

    print("Extraction terminee.")
    print(f"Temps d'execution du script : {execution_time:.2f} secondes")

except Exception as e:
    print(f"Une erreur s'est produite : {e}")
finally:
    driver.quit()
