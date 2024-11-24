import requests
import json
import zlib
import gzip
from io import BytesIO

# Fonction pour décompresser les données (gzip ou zlib)
def decompress_data(compressed_data):
    try:
        # Si les données sont gzip compressées
        if compressed_data.startswith(b'\x1f\x8b'):
            with gzip.GzipFile(fileobj=BytesIO(compressed_data)) as f:
                decompressed_data = f.read()
                return json.loads(decompressed_data.decode('utf-8'))
        # Si les données sont zlib compressées
        else:
            decompressed_data = zlib.decompress(compressed_data)
            return json.loads(decompressed_data.decode('utf-8'))
    except Exception as e:
        print(f"Erreur lors de la décompression: {e}")
        return None

# Fonction pour traiter les données sans décompression (si ce n'est pas compressé)
def process_data(raw_data):
    try:
        # Si les données sont déjà en format JSON, les analyser directement
        return json.loads(raw_data)
    except Exception as e:
        print(f"Erreur lors du traitement des données: {e}")
        return None

# Exemple d'utilisation de l'API : Récupérer les prix des objets
def fetch_item_prices():
    try:
        # Récupérer les prix des objets depuis l'API
        response = requests.get('https://tldb.info/api/ah/prices', headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # Si la requête échoue, elle lèvera une exception
        api_data = response.content  # Récupérer les données sous forme brute (bytes)

        # Vérifier si les données sont compressées (gzip ou zlib)
        if api_data.startswith(b'\x1f\x8b'):  # Gzip compression check
            print("Les données sont gzip-compressées.")
            processed_data = decompress_data(api_data)
        else:
            print("Les données ne semblent pas être compressées.")
            processed_data = process_data(api_data.decode('utf-8'))  # Décoder directement si ce n'est pas compressé

        if processed_data:
            list_data = processed_data.get('list', {})
            total = processed_data.get('total', 0)
            regions = processed_data.get('regions', {})

            # Créer un objet avec les données des prix à sauvegarder
            data_to_save = {
                'list': list_data,
                'total': total,
                'regions': regions
            }

            # Sauvegarder les données dans un fichier JSON
            with open('item_prices_data.json', 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            print('Données des prix des objets sauvegardées dans "item_prices_data.json"')

    except Exception as e:
        print(f'Erreur lors de la récupération des prix : {e}')

def fetch_auctionhouse():
    try:
        # Récupérer les prix des objets depuis l'API
        response = requests.get('https://tldb.info/auction-house/__data.json', headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # Si la requête échoue, elle lèvera une exception
        api_data = response.content  # Récupérer les données sous forme brute (bytes)

        # Vérifier si les données sont compressées (gzip ou zlib)
        if api_data.startswith(b'\x1f\x8b'):  # Gzip compression check
            print("Les données sont gzip-compressées.")
            processed_data = decompress_data(api_data)
        else:
            print("Les données ne semblent pas être compressées.")
            processed_data = process_data(api_data.decode('utf-8'))  # Décoder directement si ce n'est pas compressé

        if processed_data:
            items = processed_data.get('items', {})
            traits = processed_data.get('traits', {})

            # Créer un objet avec les données des prix à sauvegarder
            data_to_save = {
                'items': items,
                'traits': traits
            }

            # Sauvegarder les données dans un fichier JSON
            with open('item_auction.json', 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            print('Données des prix des objets sauvegardées dans "item_prices_data.json"')

    except Exception as e:
        print(f'Erreur lors de la récupération des prix : {e}')


# Appel à la fonction pour tester
fetch_item_prices()
fetch_auctionhouse()