from bs4 import BeautifulSoup

with open('html.html', 'r', encoding='utf-8') as file:
    html = file.read()

soup = BeautifulSoup(html, 'html.parser')
rows = soup.find_all('tr', class_='ah-table-row')

for row in rows:
    name = row.find('span', class_='fw-semi-bold color-rarity-5 svelte-o8inv0')
    if name:
        name = name.get_text(strip=True)
    
    quantity = row.find('span', class_='fw-semi-bold text-accent-light tab-num svelte-o8inv0')
    if quantity:
        quantity = quantity.get_text(strip=True)
    
    price = row.find('div', class_='reward-item-small')
    if price:
        price = price.get_text(strip=True)

    print(f"Nom de l'arme: {name}")
    print(f"Quantite: {quantity}")
    print(f"Prix: {price}")
    print("-" * 40)
