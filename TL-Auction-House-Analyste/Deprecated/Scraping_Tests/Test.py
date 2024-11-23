import re
from bs4 import BeautifulSoup

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
        return 0

def lire_fichier(nom_fichier):
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as fichier:
            contenu = fichier.read()
        return contenu
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier : {e}")
        return None

def nettoyer_et_simplifier_tableau(fichier_html, fichier_sortie):
    try:
        # Charger le fichier HTML brut
        with open(fichier_html, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # Trouver le premier élément <tbody> ayant la classe "align-middle"
        tbody = soup.find("tbody", class_="align-middle")

        if not tbody:
            print("Aucun <tbody> avec la classe 'align-middle' trouvé.")
            return

        # Supprimer les balises inutiles ou vides
        for tag in tbody.find_all(["span", "div", "svg", "img", "a", "path"]):
            if not tag.get_text(strip=True):
                tag.decompose()  # Supprime la balise du DOM

        # Supprimer les lignes vides
        for ligne in tbody.find_all("tr"):
            cellules = ligne.find_all("td")
            if all(not cellule.get_text(strip=True) for cellule in cellules):
                ligne.decompose()  # Supprime la ligne si toutes les cellules sont vides

        # Supprimer les attributs inutiles dans les balises restantes
        for tag in tbody.find_all(True):  # Trouver toutes les balises
            tag.attrs = {key: value for key, value in tag.attrs.items() if key not in ["class", "style"]}

        # Sauvegarder le contenu nettoyé dans un nouveau fichier HTML
        with open(fichier_sortie, "w", encoding="utf-8") as f:
            f.write(str(tbody))

        print(f"Tableau nettoyé et simplifié écrit dans : {fichier_sortie}")

    except Exception as e:
        print(f"Erreur lors du traitement : {e}")

fichier_source = "aa.html" 
fichier_sortie = "table_cleaned.html"
nettoyer_et_simplifier_tableau(fichier_source, fichier_sortie)
table_html = lire_fichier("table_cleaned.html")
table_data=[]

if table_html:
    soup = BeautifulSoup(table_html, "html.parser")
    tbody = soup.find("tbody")
    if tbody:
        for row in tbody.find_all("tr"):
            try:
                name = clean_string(row.find_all("td")[2].get_text(strip=True))
                trait = clean_string(row.find_all("td")[3].get_text(strip=True))
                quantity = clean_string(row.find_all("td")[4].get_text(strip=True))
                price = clean_string(row.find_all("td")[5].get_text(strip=True))
                print("TRAIT", "name:", name, "trait:", trait, "quantity:", quantity, "price:", price, "\n")
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
                    else:
                        print(row, "\n")
                    print(table_data[-1], "\n")
            except IndexError:
                continue

print(table_data)