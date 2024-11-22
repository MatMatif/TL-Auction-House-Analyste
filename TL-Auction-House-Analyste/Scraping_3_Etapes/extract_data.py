import pandas as pd
from bs4 import BeautifulSoup

# Charger le fichier HTML nettoyé
with open("table_cleaned.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Trouver le premier élément <tbody> ayant la classe "align-middle"
tbody = soup.find_all("tbody", class_="align-middle")[0]
table_data = []

# Parcourir toutes les lignes (<tr>) du <tbody>
for row in tbody.find_all("tr"):
    # Extraire le contenu de la 3e cellule (<td>) pour le nom
    name = row.find_all("td")[2].get_text(strip=True)
    
    # Extraire le contenu de la 4e cellule (<td>) pour la quantité
    quantity = row.find_all("td")[3].get_text(strip=True)
    
    # Extraire le contenu de la 5e cellule (<td>) pour le prix
    price = row.find_all("td")[4].get_text(strip=True)
    
    # Ajouter les données extraites sous forme de dictionnaire
    table_data.append({
        "Name": name,
        "Quantity": quantity,
        "Price": price
    })

df = pd.DataFrame(table_data)
excel_file = "table_data.xlsx"
df.to_excel(excel_file, index=False, engine="openpyxl")
print(f"Les données ont été extraites et sauvegardées dans '{excel_file}'")
