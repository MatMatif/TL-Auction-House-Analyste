from bs4 import BeautifulSoup

# Charger le fichier HTML brut
with open("table_raw.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Trouver le premier élément <tbody> ayant la classe "align-middle"
tbody = soup.find_all("tbody", class_="align-middle")[0]

# Supprimer les balises inutiles ou vides
for tag in tbody.find_all(["span", "div", "svg", "img", "a", "path"]):
    if not tag.get_text(strip=True):
        tag.decompose()  # Supprime la balise du DOM

# Supprimer les attributs inutiles dans les balises restantes
for tag in tbody.find_all(True):
    del tag['class']
    del tag['style']

# Sauvegarder le contenu nettoyé dans un nouveau fichier HTML
with open("table_cleaned.html", "w", encoding="utf-8") as f:
    f.write(str(tbody))

# Confirmation de la sauvegarde
print("HTML nettoyé sauvegardé dans 'table_cleaned.html'")
