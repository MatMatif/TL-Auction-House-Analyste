from bs4 import BeautifulSoup

# Ouvrir le fichier HTML local
with open('html.html', 'r', encoding='utf-8') as file:
    html = file.read()

# Parser le contenu du fichier HTML
soup = BeautifulSoup(html, 'html.parser')

# Extraire les lignes du tableau
rows = soup.find_all('tr', class_='ah-table-row')

# Boucle pour extraire les informations de chaque ligne
for row in rows:
    # Extraire le nom de l'arme
    name = row.find('span', class_='fw-semi-bold color-rarity-5 svelte-o8inv0')
    if name:
        name = name.get_text(strip=True)
    
    # Extraire la quantité
    quantity = row.find('span', class_='fw-semi-bold text-accent-light tab-num svelte-o8inv0')
    if quantity:
        quantity = quantity.get_text(strip=True)
    
    # Extraire le prix
    price = row.find('div', class_='reward-item-small')
    if price:
        price = price.get_text(strip=True)

    # Afficher les résultats
    print(f"Nom de l'arme: {name}")
    print(f"Quantite: {quantity}")
    print(f"Prix: {price}")
    print("-" * 40)
