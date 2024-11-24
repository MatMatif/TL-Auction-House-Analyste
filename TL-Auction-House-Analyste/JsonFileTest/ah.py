import aiohttp
import asyncio
import json
from aiofiles import open as aio_open

# Fonction pour décompresser les données (si nécessaire)
def decompress_data(compressed_data):
    try:
        # Implémentation de la décompression selon le besoin
        # Exemple de décompression, ajuster selon la logique de compression de vos données
        # Dans ce cas, on assume que c'est déjà au format JSON, et on ne décompresse pas
        return json.loads(compressed_data.decode('utf-8'))
    except Exception as e:
        print(f"Erreur lors de la décompression: {e}")
        return None

# Fonction pour "unflatten" les données, similaire à devalue.unflatten()
def unflatten_data(data):
    unflattened_data = {}
    for key, value in data.items():
        keys = key.split('.')
        d = unflattened_data
        for part in keys[:-1]:
            d = d.setdefault(part, {})
        d[keys[-1]] = value
    return unflattened_data

# Fonction asynchrone pour récupérer les données de l'API
async def fetch_auction_house_data():
    try:
        # Définir les en-têtes pour simuler une requête depuis un navigateur
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        # Faire une requête GET asynchrone pour récupérer les données de l'API avec l'en-tête 'User-Agent'
        async with aiohttp.ClientSession() as session:
            async with session.get('https://tldb.info/auction-house/__data.json', headers=headers) as response:
                response.raise_for_status()  # Si la requête échoue, elle lèvera une exception
                api_resp = await response.json()  # Analyser la réponse JSON

        # Extraire les données utiles avec unflatten (similaire à devalue.unflatten)
        api_data = next(item['data'] for item in api_resp['nodes'] if item.get('type') == 'data')

        # Décompresser les éléments de l'enchère
        items = decompress_data(api_data['items']) if 'items' in api_data else []
        traits = api_data.get('traits', {})

        # Créer un objet avec les données à sauvegarder
        data_to_save = {
            'items': items,
            'traits': traits
        }

        # Sauvegarder les données dans un fichier JSON de manière asynchrone
        async with aio_open('auction_house_data.json', 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data_to_save, ensure_ascii=False, indent=2))

        print('Données des enchères sauvegardées dans "auction_house_data.json"')

    except Exception as e:
        print(f'Erreur lors de la récupération des données de l\'API : {e}')

# Exécuter la fonction principale dans un boucle asyncio
if __name__ == '__main__':
    asyncio.run(fetch_auction_house_data())
